import logging
from dataclasses import dataclass, field
from typing import Any

import requests

from apps.accounts.models import OtpTemplate, SmsProviderProfile
from apps.accounts.services.sms_config import SmsConfigService
from apps.accounts.sms.base import SmsProvider, SmsResult
from apps.accounts.sms.smsir_utils import (
    format_mobile_for_smsir,
    map_smsir_status,
    normalize_verify_parameters,
    to_ascii_digits,
    validate_iran_mobile_for_smsir,
)

logger = logging.getLogger('accounts.sms')

SMS_IR_BASE_URL = 'https://api.sms.ir/v1'


@dataclass
class SmsIrApiResult:
    success: bool
    status: int | None = None
    message: str = ''
    data: Any = None
    http_status: int = 0
    raw: dict = field(default_factory=dict)
    error_hint: str = ''


class SmsIrClient:
    def __init__(self, api_key: str, base_url: str = SMS_IR_BASE_URL):
        self.api_key = api_key.strip()
        self.base_url = (base_url or SMS_IR_BASE_URL).rstrip('/')

    def _headers(self) -> dict:
        return {
            'X-API-KEY': self.api_key,
            'Content-Type': 'application/json',
            'Accept': 'text/plain',
        }

    def _parse_response(self, response: requests.Response) -> SmsIrApiResult:
        data = response.json() if response.content else {}
        status = data.get('status')
        message = data.get('message') or ''
        success = response.status_code == 200 and status == 1
        error_hint = ''
        if not success:
            error_hint = map_smsir_status(status, message)
            if response.status_code == 401:
                error_hint += ' — کلید را کامل paste کنید یا محدودیت IP را در پنل SMS.ir بررسی کنید'
        return SmsIrApiResult(
            success=success,
            status=status,
            message=message,
            data=data.get('data'),
            http_status=response.status_code,
            raw=data,
            error_hint=error_hint,
        )

    def _request(self, method: str, path: str, **kwargs) -> SmsIrApiResult:
        url = f'{self.base_url}/{path.lstrip("/")}'
        try:
            response = requests.request(method, url, headers=self._headers(), timeout=15, **kwargs)
            return self._parse_response(response)
        except requests.RequestException as exc:
            return SmsIrApiResult(success=False, message=str(exc), error_hint=str(exc))

    def get_credit(self) -> SmsIrApiResult:
        return self._request('GET', '/credit')

    def send_verify(
        self,
        mobile: str,
        template_id: int,
        parameters: list[dict],
    ) -> tuple[SmsIrApiResult, dict]:
        formatted, error = validate_iran_mobile_for_smsir(mobile)
        if error:
            return SmsIrApiResult(success=False, status=104, message=error, error_hint=error), {}
        payload = {
            'mobile': formatted,
            'templateId': int(template_id),
            'parameters': normalize_verify_parameters(parameters),
        }
        result = self._request('POST', '/send/verify', json=payload)
        return result, payload

    def get_message_report(self, message_id: int | str) -> SmsIrApiResult:
        return self._request('GET', f'/send/{message_id}')

    def get_send_packs(self, page_number: int = 1, page_size: int = 100) -> SmsIrApiResult:
        return self._request('GET', '/send/pack', params={'pageNumber': page_number, 'pageSize': page_size})

    def get_pack_detail(self, pack_id: str) -> SmsIrApiResult:
        return self._request('GET', f'/send/pack/{pack_id}')

    def get_live_sends(self, page_number: int = 1, page_size: int = 100) -> SmsIrApiResult:
        return self._request('GET', '/send/live', params={'pageNumber': page_number, 'pageSize': page_size})

    def get_latest_received(self, count: int = 100) -> SmsIrApiResult:
        return self._request('GET', '/receive/latest', params={'count': min(count, 100)})

    def get_line_numbers(self) -> SmsIrApiResult:
        return self._request('GET', '/line')


def validate_sms_ir_api_key(api_key: str, base_url: str = SMS_IR_BASE_URL) -> tuple[float | None, str]:
    if not api_key or not api_key.strip():
        return None, 'API key not configured'
    result = SmsIrClient(api_key, base_url).get_credit()
    if result.success:
        return float(result.data or 0), ''
    return None, result.error_hint or result.message


def get_sms_ir_client(profile: SmsProviderProfile | None = None) -> SmsIrClient | None:
    profile = profile or SmsConfigService.get_active_profile()
    api_key = SmsConfigService.resolve_api_key(profile=profile)
    if not api_key:
        return None
    return SmsIrClient(api_key, profile.base_url or SMS_IR_BASE_URL)


class SmsIrProvider(SmsProvider):
    def __init__(self, settings_obj: SmsProviderProfile | None = None):
        self.settings_obj = settings_obj or SmsConfigService.get_active_profile()

    def _client(self) -> SmsIrClient | None:
        api_key = SmsConfigService.resolve_api_key(profile=self.settings_obj)
        if not api_key:
            return None
        return SmsIrClient(api_key, self.settings_obj.base_url or SMS_IR_BASE_URL)

    def send_otp(self, phone: str, code: str, template: OtpTemplate | None) -> SmsResult:
        client = self._client()
        if not client:
            return SmsResult(success=False, provider_response={}, error='SMS_IR API key not configured')

        if not template:
            return SmsResult(success=False, provider_response={}, error='No active OTP template configured')

        if not template.sms_ir_template_id:
            return SmsResult(success=False, provider_response={}, error='شناسه قالب SMS.ir تنظیم نشده است')

        if self.settings_obj.is_sandbox and template.sms_ir_template_id != 123456:
            return SmsResult(
                success=False,
                provider_response={},
                error='در حالت Sandbox فقط قالب 123456 مجاز است (مستندات SMS.ir)',
            )
        if not self.settings_obj.is_sandbox and template.sms_ir_template_id == 123456:
            return SmsResult(
                success=False,
                provider_response={},
                error='قالب 123456 فقط برای Sandbox است — قالب Production (مثلاً 394212) را انتخاب کنید',
            )

        param_name = (template.parameter_name or 'CODE').strip('#')
        parameters = [{'name': param_name, 'value': to_ascii_digits(str(code))}]
        result, payload = client.send_verify(phone, int(template.sms_ir_template_id), parameters)

        if result.success:
            message_id = ''
            if isinstance(result.data, dict):
                message_id = str(result.data.get('messageId', ''))
            logger.info(
                'SMS.ir OTP sent | phone=%s | sandbox=%s | template=%s',
                phone[:4] + '****',
                self.settings_obj.is_sandbox,
                template.sms_ir_template_id,
            )
            return SmsResult(
                success=True,
                provider_response={**result.raw, '_payload': payload},
                message_id=message_id,
            )

        logger.error('SMS.ir error | status=%s body=%s', result.status, result.raw)
        return SmsResult(
            success=False,
            provider_response={**result.raw, '_payload': payload},
            error=result.error_hint or result.message,
        )

    def get_credit(self) -> tuple[float | None, str]:
        client = self._client()
        if not client:
            return None, 'API key not configured'
        result = client.get_credit()
        if result.success:
            return float(result.data or 0), ''
        return None, result.error_hint or result.message

    def test_connection(self) -> SmsResult:
        credit, error = self.get_credit()
        if credit is None:
            if not SmsConfigService.resolve_api_key(profile=self.settings_obj):
                return SmsResult(success=False, provider_response={}, error='API key not configured')
            return SmsResult(success=False, provider_response={}, error=error or 'Could not fetch credit from SMS.ir')
        return SmsResult(
            success=True,
            provider_response={'credit': credit, 'sandbox': self.settings_obj.is_sandbox},
        )
