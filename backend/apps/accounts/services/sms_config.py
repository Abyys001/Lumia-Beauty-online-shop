import os

from django.conf import settings as django_settings
from django.db.utils import OperationalError, ProgrammingError

from apps.accounts.models import AuthSettings, OtpSettings, OtpTemplate, SmsProviderSettings
from apps.accounts.utils.encryption import decrypt_value, encrypt_value


class SmsConfigService:
    @staticmethod
    def get_provider_settings() -> SmsProviderSettings:
        obj = SmsProviderSettings.get_settings()
        if not obj.base_url:
            if obj.provider_mode == SmsProviderSettings.PROVIDER_IRANPAYAMAK:
                obj.base_url = 'https://api.iranpayamak.com'
            else:
                obj.base_url = 'https://api.sms.ir/v1'
        normalized_line = (obj.line_number or '').strip().translate(
            str.maketrans('۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩', '01234567890123456789')
        )
        if obj.line_number and normalized_line != obj.line_number:
            obj.line_number = normalized_line
            obj.save(update_fields=['line_number', 'updated_at'])
        return obj

    @staticmethod
    def get_otp_settings() -> OtpSettings:
        return OtpSettings.get_settings()

    @staticmethod
    def get_auth_settings() -> AuthSettings:
        return AuthSettings.get_settings()

    @staticmethod
    def get_default_template() -> OtpTemplate | None:
        provider = SmsConfigService.get_provider_settings()
        if provider.provider_mode == SmsProviderSettings.PROVIDER_IRANPAYAMAK:
            template = OtpTemplate.objects.filter(is_active=True, is_default=True).first()
            if template and (template.pattern_code or '').strip():
                return template
            template = OtpTemplate.objects.filter(is_active=True).exclude(pattern_code='').first()
            if template:
                return template
            from apps.accounts.services.sms_sync import sync_iranpayamak_default_template
            template = sync_iranpayamak_default_template()
            if (template.pattern_code or '').strip():
                return template
            return None
        template = OtpTemplate.objects.filter(is_active=True, is_default=True).first()
        if template:
            return template
        return OtpTemplate.objects.filter(is_active=True).first()

    @staticmethod
    def resolve_api_key(*, sandbox: bool | None = None) -> str:
        provider = SmsConfigService.get_provider_settings()
        use_sandbox = provider.is_sandbox if sandbox is None else sandbox
        encrypted = (
            provider.sandbox_api_key_encrypted
            if use_sandbox
            else provider.api_key_encrypted
        )
        if encrypted:
            decrypted = decrypt_value(encrypted)
            if decrypted:
                return decrypted
        if use_sandbox:
            env_key = (
                os.environ.get('SMS_IR_SANDBOX_API_KEY', '')
                or getattr(django_settings, 'SMS_IR_SANDBOX_API_KEY', '')
            )
            if env_key:
                return env_key
            # Fallback: key stored only in production field (legacy / single-field setup).
            if provider.api_key_encrypted:
                decrypted = decrypt_value(provider.api_key_encrypted)
                if decrypted:
                    return decrypted
            return ''
        return (
            os.environ.get('SMS_IR_API_KEY', '')
            or getattr(django_settings, 'SMS_IR_API_KEY', '')
        )

    @staticmethod
    def set_api_key(raw_key: str, *, sandbox: bool = False) -> None:
        provider = SmsConfigService.get_provider_settings()
        field_name = 'sandbox_api_key_encrypted' if sandbox else 'api_key_encrypted'
        setattr(provider, field_name, encrypt_value(raw_key.strip()) if raw_key else '')
        provider.save(update_fields=[field_name, 'updated_at'])

    @staticmethod
    def mask_api_key(encrypted: str) -> str:
        from apps.accounts.utils.encryption import mask_secret

        if not encrypted:
            return ''
        raw = decrypt_value(encrypted)
        return mask_secret(raw) if raw else ''

    @staticmethod
    def resolve_iranpayamak_api_key() -> str:
        provider = SmsConfigService.get_provider_settings()
        if provider.api_key_encrypted:
            decrypted = decrypt_value(provider.api_key_encrypted)
            if decrypted:
                return decrypted
        return (
            os.environ.get('IRANPAYAMAK_API_KEY', '')
            or getattr(django_settings, 'IRANPAYAMAK_API_KEY', '')
        )

    @staticmethod
    def set_panel_password(raw_password: str) -> None:
        provider = SmsConfigService.get_provider_settings()
        provider.panel_password_encrypted = encrypt_value(raw_password.strip()) if raw_password else ''
        provider.save(update_fields=['panel_password_encrypted', 'updated_at'])

    @staticmethod
    def resolve_panel_password() -> str:
        provider = SmsConfigService.get_provider_settings()
        if provider.panel_password_encrypted:
            return decrypt_value(provider.panel_password_encrypted)
        return ''

    @staticmethod
    def resolve_bearer_token() -> str:
        from django.utils import timezone

        provider = SmsConfigService.get_provider_settings()
        if not provider.bearer_token_encrypted:
            return ''
        if provider.bearer_token_expires_at and provider.bearer_token_expires_at <= timezone.now():
            return ''
        return decrypt_value(provider.bearer_token_encrypted)

    @staticmethod
    def cache_bearer_token(token: str, expires_at=None) -> None:
        provider = SmsConfigService.get_provider_settings()
        provider.bearer_token_encrypted = encrypt_value(token.strip()) if token else ''
        provider.bearer_token_expires_at = expires_at
        provider.save(update_fields=['bearer_token_encrypted', 'bearer_token_expires_at', 'updated_at'])

    @staticmethod
    def mask_panel_password(encrypted: str) -> str:
        from apps.accounts.utils.encryption import mask_secret

        if not encrypted:
            return ''
        raw = decrypt_value(encrypted)
        return mask_secret(raw) if raw else ''

    @staticmethod
    def resolve_provider_mode() -> str:
        provider = SmsConfigService.get_provider_settings()
        if provider.provider_mode:
            return provider.provider_mode
        env_mode = os.environ.get('SMS_PROVIDER', 'mock')
        if env_mode == 'smsir':
            return SmsProviderSettings.PROVIDER_SMSIR
        if env_mode == 'iranpayamak':
            return SmsProviderSettings.PROVIDER_IRANPAYAMAK
        return SmsProviderSettings.PROVIDER_MOCK

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
        try:
            provider = SmsConfigService.get_provider_settings()
            OtpSettings.get_settings()
            auth = AuthSettings.get_settings()
        except (ProgrammingError, OperationalError):
            return

        updated = []
        if not provider.api_key_encrypted:
            env_key = os.environ.get('SMS_IR_API_KEY', '')
            if env_key:
                provider.api_key_encrypted = encrypt_value(env_key)
                updated.append('api_key_encrypted')
        if not provider.sandbox_api_key_encrypted:
            env_sandbox_key = os.environ.get('SMS_IR_SANDBOX_API_KEY', '')
            if env_sandbox_key:
                provider.sandbox_api_key_encrypted = encrypt_value(env_sandbox_key)
                updated.append('sandbox_api_key_encrypted')
        env_mode = os.environ.get('SMS_PROVIDER', '')
        if env_mode == 'smsir' and provider.provider_mode == SmsProviderSettings.PROVIDER_MOCK:
            provider.provider_mode = SmsProviderSettings.PROVIDER_SMSIR
            updated.append('provider_mode')
        if env_mode == 'iranpayamak' and provider.provider_mode == SmsProviderSettings.PROVIDER_MOCK:
            provider.provider_mode = SmsProviderSettings.PROVIDER_IRANPAYAMAK
            updated.append('provider_mode')
            if not provider.base_url or 'sms.ir' in provider.base_url:
                provider.base_url = os.environ.get(
                    'IRANPAYAMAK_BASE_URL',
                    'https://api.iranpayamak.com',
                )
                updated.append('base_url')
        env_ip_key = (os.environ.get('IRANPAYAMAK_API_KEY') or '').strip()
        if env_ip_key and not provider.api_key_encrypted:
            provider.api_key_encrypted = encrypt_value(env_ip_key)
            updated.append('api_key_encrypted')
        env_line = (os.environ.get('IRANPAYAMAK_LINE_NUMBER') or '').strip()
        if env_line and not provider.line_number:
            provider.line_number = env_line
            updated.append('line_number')
        if updated:
            provider.save(update_fields=list(dict.fromkeys(updated + ['updated_at'])))

        from apps.accounts.services.sms_sync import sync_sms_settings
        sync_sms_settings()

        if not auth.admin_bypass_phone:
            env_bypass = os.environ.get('ADMIN_BYPASS_PHONE', '')
            if env_bypass:
                from apps.accounts.models import normalize_phone
                auth.admin_bypass_phone = normalize_phone(env_bypass)
                auth.save(update_fields=['admin_bypass_phone', 'updated_at'])

        if not OtpTemplate.objects.exists():
            from apps.accounts.services.sms_sync import (
                DEFAULT_BODY_PREVIEW,
                DEFAULT_PARAMETER_NAME,
                DEFAULT_TEMPLATE_ID,
                DEFAULT_TEMPLATE_NAME,
            )
            OtpTemplate.objects.create(
                name=DEFAULT_TEMPLATE_NAME,
                sms_ir_template_id=DEFAULT_TEMPLATE_ID,
                parameter_name=DEFAULT_PARAMETER_NAME,
                body_preview=DEFAULT_BODY_PREVIEW,
                is_active=True,
                is_default=True,
            )
