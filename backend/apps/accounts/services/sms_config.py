import os

from django.conf import settings as django_settings

from apps.accounts.models import AuthSettings, OtpSettings, OtpTemplate, SmsProviderSettings
from apps.accounts.utils.encryption import decrypt_value, encrypt_value


class SmsConfigService:
    @staticmethod
    def get_provider_settings() -> SmsProviderSettings:
        obj = SmsProviderSettings.get_settings()
        if not obj.base_url:
            obj.base_url = 'https://api.sms.ir/v1'
        return obj

    @staticmethod
    def get_otp_settings() -> OtpSettings:
        return OtpSettings.get_settings()

    @staticmethod
    def get_auth_settings() -> AuthSettings:
        return AuthSettings.get_settings()

    @staticmethod
    def get_default_template() -> OtpTemplate | None:
        template = OtpTemplate.objects.filter(is_active=True, is_default=True).first()
        if template:
            return template
        return OtpTemplate.objects.filter(is_active=True).first()

    @staticmethod
    def resolve_api_key() -> str:
        provider = SmsConfigService.get_provider_settings()
        if provider.api_key_encrypted:
            decrypted = decrypt_value(provider.api_key_encrypted)
            if decrypted:
                return decrypted
        return os.environ.get('SMS_IR_API_KEY', '') or getattr(django_settings, 'SMS_IR_API_KEY', '')

    @staticmethod
    def set_api_key(raw_key: str) -> None:
        provider = SmsConfigService.get_provider_settings()
        provider.api_key_encrypted = encrypt_value(raw_key.strip()) if raw_key else ''
        provider.save(update_fields=['api_key_encrypted', 'updated_at'])

    @staticmethod
    def resolve_provider_mode() -> str:
        provider = SmsConfigService.get_provider_settings()
        if provider.provider_mode:
            return provider.provider_mode
        env_mode = os.environ.get('SMS_PROVIDER', 'mock')
        return SmsProviderSettings.PROVIDER_SMSIR if env_mode == 'smsir' else SmsProviderSettings.PROVIDER_MOCK

    @staticmethod
    def resolve_admin_bypass_phone() -> str:
        from apps.accounts.models import normalize_phone

        auth = SmsConfigService.get_auth_settings()
        if auth.admin_bypass_phone:
            return normalize_phone(auth.admin_bypass_phone)
        env_phone = os.environ.get('ADMIN_BYPASS_PHONE', '') or getattr(django_settings, 'ADMIN_BYPASS_PHONE', '')
        return normalize_phone(env_phone) if env_phone else ''

    @staticmethod
    def bootstrap_from_env() -> None:
        """Seed singleton rows and optional env API key on first run."""
        provider = SmsConfigService.get_provider_settings()
        OtpSettings.get_settings()
        auth = AuthSettings.get_settings()

        updated = []
        if not provider.api_key_encrypted:
            env_key = os.environ.get('SMS_IR_API_KEY', '')
            if env_key:
                provider.api_key_encrypted = encrypt_value(env_key)
                updated.append('api_key_encrypted')
        env_mode = os.environ.get('SMS_PROVIDER', '')
        if env_mode == 'smsir' and provider.provider_mode == SmsProviderSettings.PROVIDER_MOCK:
            provider.provider_mode = SmsProviderSettings.PROVIDER_SMSIR
            updated.append('provider_mode')
        env_sandbox = os.environ.get('SMS_IR_SANDBOX', 'true').lower() in ('true', '1', 'yes')
        if env_sandbox != provider.is_sandbox:
            provider.is_sandbox = env_sandbox
            updated.append('is_sandbox')
        if updated:
            provider.save(update_fields=updated + ['updated_at'])

        if not auth.admin_bypass_phone:
            env_bypass = os.environ.get('ADMIN_BYPASS_PHONE', '')
            if env_bypass:
                from apps.accounts.models import normalize_phone
                auth.admin_bypass_phone = normalize_phone(env_bypass)
                auth.save(update_fields=['admin_bypass_phone', 'updated_at'])

        if not OtpTemplate.objects.exists():
            OtpTemplate.objects.create(
                name='Sandbox OTP',
                sms_ir_template_id=123456,
                parameter_name='CODE',
                body_preview='کد تایید شما: {CODE}',
                is_active=True,
                is_default=True,
            )
