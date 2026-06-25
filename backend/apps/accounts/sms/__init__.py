from apps.accounts.models import SmsProviderSettings
from apps.accounts.services.sms_config import SmsConfigService
from apps.accounts.sms.base import SmsProvider
from apps.accounts.sms.iranpayamak import IranPayamakProvider
from apps.accounts.sms.mock import MockSmsProvider
from apps.accounts.sms.smsir import SmsIrProvider

__all__ = [
    'SmsProvider',
    'SmsIrProvider',
    'IranPayamakProvider',
    'MockSmsProvider',
    'get_sms_provider',
]


def get_sms_provider() -> SmsProvider:
    SmsConfigService.bootstrap_from_env()
    settings = SmsConfigService.get_provider_settings()
    mode = settings.provider_mode or SmsConfigService.resolve_provider_mode()
    if mode == SmsProviderSettings.PROVIDER_SMSIR and settings.is_active:
        return SmsIrProvider(settings)
    if mode == SmsProviderSettings.PROVIDER_IRANPAYAMAK and settings.is_active:
        return IranPayamakProvider(settings)
    return MockSmsProvider()
