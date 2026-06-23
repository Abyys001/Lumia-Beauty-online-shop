import logging

import requests

from apps.accounts.models import OtpTemplate, SmsProviderSettings
from apps.accounts.services.sms_config import SmsConfigService
from apps.accounts.sms.base import SmsProvider, SmsResult

logger = logging.getLogger('accounts.sms')


class SmsIrProvider(SmsProvider):
    def __init__(self, settings_obj: SmsProviderSettings | None = None):
        self.settings_obj = settings_obj or SmsConfigService.get_provider_settings()

    def _headers(self) -> dict:
        return {
            'X-API-KEY': SmsConfigService.resolve_api_key(),
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

    def _base_url(self) -> str:
        return (self.settings_obj.base_url or 'https://api.sms.ir/v1').rstrip('/')

    def send_otp(self, phone: str, code: str, template: OtpTemplate | None) -> SmsResult:
        api_key = SmsConfigService.resolve_api_key()
        if not api_key:
            return SmsResult(success=False, provider_response={}, error='SMS_IR API key not configured')

        if not template:
            return SmsResult(success=False, provider_response={}, error='No active OTP template configured')

        url = f'{self._base_url()}/send/verify'
        param_name = template.parameter_name or 'Code'
        payload = {
            'mobile': phone,
            'templateId': int(template.sms_ir_template_id),
            'parameters': [{'name': param_name, 'value': code}],
        }

        try:
            response = requests.post(url, json=payload, headers=self._headers(), timeout=10)
            data = response.json() if response.content else {}
            if response.status_code == 200 and data.get('status') == 1:
                message_id = str(data.get('data', {}).get('messageId', '') or data.get('messageId', ''))
                logger.info('SMS.ir OTP sent | phone=%s | sandbox=%s', phone[:4] + '****', self.settings_obj.is_sandbox)
                return SmsResult(success=True, provider_response=data, message_id=message_id)
            error = data.get('message') or str(data)
            logger.error('SMS.ir error | status=%s body=%s', response.status_code, data)
            return SmsResult(success=False, provider_response=data, error=error)
        except requests.RequestException as exc:
            logger.error('SMS.ir request failed | phone=%s | error=%s', phone[:4] + '****', exc)
            return SmsResult(success=False, provider_response={}, error=str(exc))

    def test_connection(self) -> SmsResult:
        credit = self.get_credit()
        if credit is None:
            api_key = SmsConfigService.resolve_api_key()
            if not api_key:
                return SmsResult(success=False, provider_response={}, error='API key not configured')
            return SmsResult(success=False, provider_response={}, error='Could not fetch credit from SMS.ir')
        return SmsResult(
            success=True,
            provider_response={'credit': credit, 'sandbox': self.settings_obj.is_sandbox},
        )

    def get_credit(self) -> float | None:
        api_key = SmsConfigService.resolve_api_key()
        if not api_key:
            return None
        url = f'{self._base_url()}/credit'
        try:
            response = requests.get(url, headers=self._headers(), timeout=10)
            data = response.json() if response.content else {}
            if response.status_code == 200 and data.get('status') == 1:
                return float(data.get('data', 0))
            return None
        except (requests.RequestException, ValueError, TypeError):
            return None
