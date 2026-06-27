import logging
from dataclasses import dataclass, field
from typing import Any

import requests

from apps.accounts.models import OtpTemplate, SmsProviderProfile
from apps.accounts.services.sms_config import SmsConfigService
from apps.accounts.sms.base import SmsProvider, SmsResult
from apps.accounts.sms.iranpayamak_utils import (
    format_mobile_for_iranpayamak,
    map_iranpayamak_error,
    normalize_number_format,
    to_ascii_digits,
    validate_iran_mobile_for_iranpayamak,
)

logger = logging.getLogger('accounts.sms')

IRANPAYAMAK_BASE_URL = 'https://api.iranpayamak.com'


@dataclass
class IranPayamakApiResult:
    success: bool
    status: str = ''
    message: Any = None
    data: Any = None
    http_status: int = 0
    raw: dict = field(default_factory=dict)
    error_hint: str = ''


class IranPayamakClient:
    def __init__(
        self,
        api_key: str,
        base_url: str = IRANPAYAMAK_BASE_URL,
        bearer_token: str = '',
    ):
        self.api_key = api_key.strip()
        self.base_url = (base_url or IRANPAYAMAK_BASE_URL).rstrip('/')
        self.bearer_token = bearer_token.strip()

    def _headers(self, *, use_bearer: bool = False) -> dict:
        headers = {
            'Api-Key': self.api_key,
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        if use_bearer and self.bearer_token:
            headers['Authorization'] = f'Bearer {self.bearer_token}'
        return headers

    def _parse_response(self, response: requests.Response) -> IranPayamakApiResult:
        data = response.json() if response.content else {}
        api_status = data.get('status', '')
        message = data.get('message') or data.get('messages')
        success = response.status_code in (200, 201) and api_status == 'success'
        error_hint = ''
        if not success:
            error_hint = map_iranpayamak_error(message, response.status_code)
        return IranPayamakApiResult(
            success=success,
            status=api_status,
            message=message,
            data=data.get('data'),
            http_status=response.status_code,
            raw=data,
            error_hint=error_hint,
        )

    def _request(self, method: str, path: str, *, use_bearer: bool = False, **kwargs) -> IranPayamakApiResult:
        url = f'{self.base_url}/{path.lstrip("/")}'
        try:
            response = requests.request(
                method,
                url,
                headers=self._headers(use_bearer=use_bearer),
                timeout=20,
                **kwargs,
            )
            return self._parse_response(response)
        except requests.RequestException as exc:
            return IranPayamakApiResult(success=False, message=str(exc), error_hint=str(exc))

    def login(self, username: str, password: str, method: str | None = None) -> IranPayamakApiResult:
        payload: dict[str, Any] = {'username': username, 'password': password}
        if method:
            payload['method'] = method
        return self._request('POST', '/ws/v1/auth/login', json=payload)

    def verify_2fa(self, token: str, code: str, method: str = 'sms') -> IranPayamakApiResult:
        return self._request(
            'POST',
            '/ws/v1/auth/verify-2fa',
            json={'token': token, 'code': code, 'method': method},
        )

    def get_profile(self) -> IranPayamakApiResult:
        return self._request('GET', '/ws/v1/account/profile')

    def get_balance(self) -> IranPayamakApiResult:
        return self._request('GET', '/ws/v1/account/balance')

    def get_lines(self, search: str = '', is_dedicated: bool | None = None) -> IranPayamakApiResult:
        params: dict[str, Any] = {}
        if search:
            params['search'] = search
        if is_dedicated is not None:
            params['is_dedicated'] = str(is_dedicated).lower()
        return self._request('GET', '/ws/v1/lines/accessible', use_bearer=True, params=params)

    def send_pattern(
        self,
        code: str,
        recipient: str,
        line_number: str,
        attributes: dict[str, str],
        number_format: str = 'english',
    ) -> tuple[IranPayamakApiResult, dict]:
        formatted, error = validate_iran_mobile_for_iranpayamak(recipient)
        if error:
            return IranPayamakApiResult(success=False, message=error, error_hint=error), {}
        payload = {
            'code': code,
            'recipient': formatted,
            'line_number': line_number,
            'attributes': attributes,
            'number_format': normalize_number_format(number_format),
        }
        result = self._request('POST', '/ws/v1/sms/pattern', json=payload)
        return result, payload

    def send_sample(
        self,
        text: str,
        line_number: str,
        number_format: str = 'english',
    ) -> tuple[IranPayamakApiResult, dict]:
        payload = {
            'text': text,
            'line_number': line_number,
            'number_format': normalize_number_format(number_format),
        }
        result = self._request('POST', '/ws/v1/sms/sample', json=payload)
        return result, payload


def validate_iranpayamak_api_key(api_key: str, base_url: str = IRANPAYAMAK_BASE_URL) -> tuple[dict | None, str]:
    if not api_key or not api_key.strip():
        return None, 'API key not configured'
    result = IranPayamakClient(api_key, base_url).get_profile()
    if result.success:
        return result.data if isinstance(result.data, dict) else {}, ''
    return None, result.error_hint or map_iranpayamak_error(result.message, result.http_status)


def get_iranpayamak_client(*, with_bearer: bool = False, profile: SmsProviderProfile | None = None) -> IranPayamakClient | None:
    profile = profile or SmsConfigService.get_active_profile()
    api_key = SmsConfigService.resolve_iranpayamak_api_key(profile=profile)
    if not api_key:
        return None
    bearer = SmsConfigService.resolve_bearer_token(profile=profile) if with_bearer else ''
    return IranPayamakClient(
        api_key,
        profile.base_url or IRANPAYAMAK_BASE_URL,
        bearer_token=bearer,
    )


class IranPayamakProvider(SmsProvider):
    def __init__(self, settings_obj: SmsProviderProfile | None = None):
        self.settings_obj = settings_obj or SmsConfigService.get_active_profile()

    def _client(self) -> IranPayamakClient | None:
        return get_iranpayamak_client(profile=self.settings_obj)

    def send_otp(self, phone: str, code: str, template: OtpTemplate | None) -> SmsResult:
        client = self._client()
        if not client:
            return SmsResult(success=False, provider_response={}, error='IranPayamak API key not configured')

        if not template:
            return SmsResult(success=False, provider_response={}, error='No active OTP template configured')

        pattern_code = (template.pattern_code or '').strip()
        if not pattern_code:
            return SmsResult(
                success=False,
                provider_response={},
                error='کد Pattern IranPayamak تنظیم نشده — از پنل ادمین → تنظیمات SMS → قالب OTP، کد Pattern پنل IranPayamak را وارد کنید',
            )

        line_number = to_ascii_digits((self.settings_obj.line_number or '').strip())
        if not line_number:
            return SmsResult(
                success=False,
                provider_response={},
                error='شماره خط IranPayamak تنظیم نشده است',
            )

        param_name = (template.parameter_name or 'CODE').strip()
        attributes = {param_name: to_ascii_digits(str(code))}
        result, payload = client.send_pattern(
            pattern_code,
            phone,
            line_number,
            attributes,
            self.settings_obj.number_format,
        )

        if result.success:
            message_id = str(result.data) if result.data is not None else ''
            logger.info(
                'IranPayamak OTP sent | phone=%s | pattern=%s | line=%s',
                phone[:4] + '****',
                pattern_code,
                line_number,
            )
            return SmsResult(
                success=True,
                provider_response={**result.raw, '_payload': payload},
                message_id=message_id,
            )

        logger.error('IranPayamak error | status=%s body=%s', result.status, result.raw)
        return SmsResult(
            success=False,
            provider_response={**result.raw, '_payload': payload},
            error=result.error_hint or map_iranpayamak_error(result.message, result.http_status),
        )

    def get_credit(self) -> tuple[float | None, str]:
        client = self._client()
        if not client:
            return None, 'API key not configured'
        result = client.get_balance()
        if result.success and isinstance(result.data, dict):
            return float(result.data.get('balanceAmount', 0)), ''
        return None, result.error_hint or map_iranpayamak_error(result.message, result.http_status)

    def get_balance_details(self) -> tuple[dict | None, str]:
        client = self._client()
        if not client:
            return None, 'API key not configured'
        result = client.get_balance()
        if result.success and isinstance(result.data, dict):
            return result.data, ''
        return None, result.error_hint or map_iranpayamak_error(result.message, result.http_status)

    def test_connection(self) -> SmsResult:
        client = self._client()
        if not client:
            return SmsResult(success=False, provider_response={}, error='API key not configured')
        profile = client.get_profile()
        if not profile.success:
            return SmsResult(
                success=False,
                provider_response=profile.raw,
                error=profile.error_hint or map_iranpayamak_error(profile.message, profile.http_status),
            )
        balance, balance_error = self.get_credit()
        if balance is None:
            return SmsResult(
                success=False,
                provider_response=profile.raw,
                error=balance_error or 'Could not fetch balance',
            )
        return SmsResult(
            success=True,
            provider_response={
                'profile': profile.data,
                'credit': balance,
                'line_number': self.settings_obj.line_number,
            },
        )
