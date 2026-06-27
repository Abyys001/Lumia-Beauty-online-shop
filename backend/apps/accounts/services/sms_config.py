import os

from django.conf import settings as django_settings
from django.db.utils import OperationalError, ProgrammingError

from apps.accounts.models import AuthSettings, OtpSettings, OtpTemplate, SmsProviderProfile, SmsProviderSettings
from apps.accounts.utils.encryption import decrypt_value, encrypt_value


class SmsConfigService:
    @staticmethod
    def get_active_profile() -> SmsProviderProfile:
        try:
            return SmsProviderProfile.get_active()
        except (ProgrammingError, OperationalError):
            raise

    @staticmethod
    def get_profile(provider_type: str) -> SmsProviderProfile:
        return SmsProviderProfile.get_profile(provider_type)

    @staticmethod
    def activate_provider(provider_type: str) -> SmsProviderProfile:
        return SmsProviderProfile.activate(provider_type)

    @staticmethod
    def get_provider_settings() -> SmsProviderSettings:
        """Backward-compatible singleton — provider_mode synced on activate."""
        return SmsProviderSettings.get_settings()

    @staticmethod
    def _normalize_profile_line(profile: SmsProviderProfile) -> SmsProviderProfile:
        if not profile.base_url:
            profile.base_url = SmsProviderProfile.default_base_url(profile.provider_type)
        normalized_line = (profile.line_number or '').strip().translate(
            str.maketrans('۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩', '01234567890123456789')
        )
        if profile.line_number and normalized_line != profile.line_number:
            profile.line_number = normalized_line
            profile.save(update_fields=['line_number', 'updated_at'])
        return profile

    @staticmethod
    def get_otp_settings() -> OtpSettings:
        return OtpSettings.get_settings()

    @staticmethod
    def get_auth_settings() -> AuthSettings:
        return AuthSettings.get_settings()

    @staticmethod
    def get_default_template() -> OtpTemplate | None:
        profile = SmsConfigService.get_active_profile()
        provider_type = profile.provider_type

        if provider_type:
            template = OtpTemplate.objects.filter(
                is_active=True, is_default=True, provider_type=provider_type,
            ).first()
            if template:
                return template

        if provider_type == SmsProviderProfile.PROVIDER_IRANPAYAMAK:
            template = OtpTemplate.objects.filter(
                is_active=True, is_default=True,
            ).filter(provider_type__in=['', SmsProviderProfile.PROVIDER_IRANPAYAMAK]).first()
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

        template = OtpTemplate.objects.filter(
            is_active=True, is_default=True,
        ).filter(provider_type__in=['', SmsProviderProfile.PROVIDER_SMSIR]).first()
        if template:
            return template
        return OtpTemplate.objects.filter(is_active=True).first()

    @staticmethod
    def resolve_api_key(*, sandbox: bool | None = None, profile: SmsProviderProfile | None = None) -> str:
        profile = profile or SmsConfigService.get_active_profile()
        use_sandbox = profile.is_sandbox if sandbox is None else sandbox
        encrypted = (
            profile.sandbox_api_key_encrypted
            if use_sandbox
            else profile.api_key_encrypted
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
            if profile.api_key_encrypted:
                decrypted = decrypt_value(profile.api_key_encrypted)
                if decrypted:
                    return decrypted
            return ''
        return (
            os.environ.get('SMS_IR_API_KEY', '')
            or getattr(django_settings, 'SMS_IR_API_KEY', '')
        )

    @staticmethod
    def set_api_key(raw_key: str, *, sandbox: bool = False, profile: SmsProviderProfile | None = None) -> None:
        profile = profile or SmsConfigService.get_active_profile()
        field_name = 'sandbox_api_key_encrypted' if sandbox else 'api_key_encrypted'
        setattr(profile, field_name, encrypt_value(raw_key.strip()) if raw_key else '')
        profile.save(update_fields=[field_name, 'updated_at'])

    @staticmethod
    def mask_api_key(encrypted: str) -> str:
        from apps.accounts.utils.encryption import mask_secret

        if not encrypted:
            return ''
        raw = decrypt_value(encrypted)
        return mask_secret(raw) if raw else ''

    @staticmethod
    def resolve_iranpayamak_api_key(profile: SmsProviderProfile | None = None) -> str:
        profile = profile or SmsConfigService.get_active_profile()
        if profile.api_key_encrypted:
            decrypted = decrypt_value(profile.api_key_encrypted)
            if decrypted:
                return decrypted
        return (
            os.environ.get('IRANPAYAMAK_API_KEY', '')
            or getattr(django_settings, 'IRANPAYAMAK_API_KEY', '')
        )

    @staticmethod
    def set_panel_password(raw_password: str, profile: SmsProviderProfile | None = None) -> None:
        profile = profile or SmsConfigService.get_active_profile()
        profile.panel_password_encrypted = encrypt_value(raw_password.strip()) if raw_password else ''
        profile.save(update_fields=['panel_password_encrypted', 'updated_at'])

    @staticmethod
    def resolve_panel_password(profile: SmsProviderProfile | None = None) -> str:
        profile = profile or SmsConfigService.get_active_profile()
        if profile.panel_password_encrypted:
            return decrypt_value(profile.panel_password_encrypted)
        return ''

    @staticmethod
    def resolve_bearer_token(profile: SmsProviderProfile | None = None) -> str:
        from django.utils import timezone

        profile = profile or SmsConfigService.get_active_profile()
        if not profile.bearer_token_encrypted:
            return ''
        if profile.bearer_token_expires_at and profile.bearer_token_expires_at <= timezone.now():
            return ''
        return decrypt_value(profile.bearer_token_encrypted)

    @staticmethod
    def cache_bearer_token(token: str, expires_at=None, profile: SmsProviderProfile | None = None) -> None:
        profile = profile or SmsConfigService.get_active_profile()
        profile.bearer_token_encrypted = encrypt_value(token.strip()) if token else ''
        profile.bearer_token_expires_at = expires_at
        profile.save(update_fields=['bearer_token_encrypted', 'bearer_token_expires_at', 'updated_at'])

    @staticmethod
    def mask_panel_password(encrypted: str) -> str:
        from apps.accounts.utils.encryption import mask_secret

        if not encrypted:
            return ''
        raw = decrypt_value(encrypted)
        return mask_secret(raw) if raw else ''

    @staticmethod
    def resolve_provider_mode() -> str:
        try:
            return SmsConfigService.get_active_profile().provider_type
        except (ProgrammingError, OperationalError):
            pass
        env_mode = os.environ.get('SMS_PROVIDER', 'mock')
        if env_mode == 'smsir':
            return SmsProviderProfile.PROVIDER_SMSIR
        if env_mode == 'iranpayamak':
            return SmsProviderProfile.PROVIDER_IRANPAYAMAK
        return SmsProviderProfile.PROVIDER_MOCK

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
        """Seed profiles and singleton rows from environment on first run."""
        try:
            SmsProviderProfile.ensure_profiles()
            provider = SmsConfigService.get_active_profile()
            OtpSettings.get_settings()
            auth = AuthSettings.get_settings()
            SmsProviderSettings.get_settings()
        except (ProgrammingError, OperationalError):
            return

        smsir = SmsProviderProfile.get_profile(SmsProviderProfile.PROVIDER_SMSIR)
        iranpayamak = SmsProviderProfile.get_profile(SmsProviderProfile.PROVIDER_IRANPAYAMAK)

        updated_smsir: list[str] = []
        if not smsir.api_key_encrypted:
            env_key = os.environ.get('SMS_IR_API_KEY', '')
            if env_key:
                smsir.api_key_encrypted = encrypt_value(env_key)
                updated_smsir.append('api_key_encrypted')
        if not smsir.sandbox_api_key_encrypted:
            env_sandbox_key = os.environ.get('SMS_IR_SANDBOX_API_KEY', '')
            if env_sandbox_key:
                smsir.sandbox_api_key_encrypted = encrypt_value(env_sandbox_key)
                updated_smsir.append('sandbox_api_key_encrypted')
        if updated_smsir:
            smsir.save(update_fields=list(dict.fromkeys(updated_smsir + ['updated_at'])))

        updated_ip: list[str] = []
        env_ip_key = (os.environ.get('IRANPAYAMAK_API_KEY') or '').strip()
        if env_ip_key and not iranpayamak.api_key_encrypted:
            iranpayamak.api_key_encrypted = encrypt_value(env_ip_key)
            updated_ip.append('api_key_encrypted')
        env_line = (os.environ.get('IRANPAYAMAK_LINE_NUMBER') or '').strip()
        if env_line and not iranpayamak.line_number:
            iranpayamak.line_number = env_line
            updated_ip.append('line_number')
        if updated_ip:
            iranpayamak.save(update_fields=list(dict.fromkeys(updated_ip + ['updated_at'])))

        env_mode = os.environ.get('SMS_PROVIDER', '')
        if env_mode == 'smsir' and not SmsProviderProfile.objects.filter(is_active=True).exclude(
            provider_type=SmsProviderProfile.PROVIDER_MOCK,
        ).exists():
            SmsProviderProfile.activate(SmsProviderProfile.PROVIDER_SMSIR)
        elif env_mode == 'iranpayamak' and not SmsProviderProfile.objects.filter(is_active=True).exclude(
            provider_type=SmsProviderProfile.PROVIDER_MOCK,
        ).exists():
            SmsProviderProfile.activate(SmsProviderProfile.PROVIDER_IRANPAYAMAK)

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
                provider_type=SmsProviderProfile.PROVIDER_SMSIR,
                is_active=True,
                is_default=True,
            )
