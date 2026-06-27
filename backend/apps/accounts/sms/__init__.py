from apps.accounts.models import SmsProviderProfile
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
    'get_sms_provider_for_profile',
]


def get_sms_provider_for_profile(profile: SmsProviderProfile) -> SmsProvider:
    if profile.provider_type == SmsProviderProfile.PROVIDER_SMSIR and profile.is_active:
        return SmsIrProvider(profile)
    if profile.provider_type == SmsProviderProfile.PROVIDER_IRANPAYAMAK and profile.is_active:
        return IranPayamakProvider(profile)
    if profile.provider_type == SmsProviderProfile.PROVIDER_MOCK:
        return MockSmsProvider()
    # Inactive non-mock profiles still instantiate for test_connection
    if profile.provider_type == SmsProviderProfile.PROVIDER_SMSIR:
        return SmsIrProvider(profile)
    if profile.provider_type == SmsProviderProfile.PROVIDER_IRANPAYAMAK:
        return IranPayamakProvider(profile)
    return MockSmsProvider()


def get_sms_provider() -> SmsProvider:
    SmsConfigService.bootstrap_from_env()
    profile = SmsConfigService.get_active_profile()
    if profile.provider_type == SmsProviderProfile.PROVIDER_SMSIR and profile.is_active:
        return SmsIrProvider(profile)
    if profile.provider_type == SmsProviderProfile.PROVIDER_IRANPAYAMAK and profile.is_active:
        return IranPayamakProvider(profile)
    return MockSmsProvider()
