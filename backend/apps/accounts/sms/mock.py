import logging

from apps.accounts.models import OtpTemplate, SmsLog
from apps.accounts.sms.base import SmsProvider, SmsResult

logger = logging.getLogger('accounts.sms')


class MockSmsProvider(SmsProvider):
    def send_otp(self, phone: str, code: str, template: OtpTemplate | None) -> SmsResult:
        masked = f'{phone[:4]}****{phone[-3:]}' if len(phone) >= 7 else phone
        logger.warning('MOCK SMS | phone=%s | OTP=%s | template=%s', masked, code, template.name if template else '-')
        return SmsResult(
            success=True,
            provider_response={'status': 1, 'message': 'mock'},
            message_id='mock',
        )

    def test_connection(self) -> SmsResult:
        return SmsResult(success=True, provider_response={'message': 'mock mode active'})

    def get_credit(self) -> float | None:
        return None


def log_sms_attempt(
    *,
    phone: str,
    provider: str,
    status: str,
    request_data: dict,
    response_data: dict,
    template: OtpTemplate | None = None,
    message_id: str = '',
    error_message: str = '',
    ip_address=None,
) -> SmsLog:
    return SmsLog.objects.create(
        phone=phone,
        message_type=SmsLog.MESSAGE_OTP,
        template=template,
        provider=provider,
        status=status,
        request_data=request_data,
        response_data=response_data,
        provider_message_id=message_id or '',
        error_message=error_message,
        ip_address=ip_address,
    )
