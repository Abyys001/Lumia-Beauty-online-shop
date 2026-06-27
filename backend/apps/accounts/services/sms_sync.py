"""Sync SMS provider profiles, OTP templates, and optional API keys from environment."""

import os

from apps.accounts.models import OtpTemplate, SmsProviderProfile, SmsProviderSettings
from apps.accounts.utils.encryption import encrypt_value

DEFAULT_TEMPLATE_ID = 394212
DEFAULT_TEMPLATE_NAME = 'ورود ادمین'
DEFAULT_PARAMETER_NAME = 'CODE'
DEFAULT_BODY_PREVIEW = (
    'این یک پیام تست است\n'
    'کد تایید ورود شما: {CODE}\n\n'
    'این کد تا ۲ دقیقه معتبر است.'
)

SANDBOX_TEMPLATE_ID = 123456
SANDBOX_TEMPLATE_NAME = 'Sandbox OTP'
SANDBOX_PARAMETER_NAME = 'Code'
SANDBOX_BODY_PREVIEW = 'کد تایید شما: {Code}'

IRANPAYAMAK_DEFAULT_PATTERN_CODE = ''
IRANPAYAMAK_DEFAULT_TEMPLATE_NAME = 'ورود لومیا بیوتی'
IRANPAYAMAK_DEFAULT_BODY_PREVIEW = (
    'لومیا بیوتی\n'
    'کد ورود شما: {CODE}\n'
    'این کد تا ۲ دقیقه اعتبار دارد.'
)

SMS_IR_KNOWN_TEMPLATE_IDS = {123456, 394212, 100000}


def _resolve_iranpayamak_pattern_code(explicit: str | None = None) -> str:
    code = (explicit or os.environ.get('IRANPAYAMAK_PATTERN_CODE') or IRANPAYAMAK_DEFAULT_PATTERN_CODE).strip()
    if code:
        return code
    existing = OtpTemplate.objects.filter(is_active=True).exclude(pattern_code='').first()
    if existing and (existing.pattern_code or '').strip():
        candidate = existing.pattern_code.strip()
        if candidate not in {str(i) for i in SMS_IR_KNOWN_TEMPLATE_IDS}:
            return candidate
    return ''


def sync_iranpayamak_default_template(*, pattern_code: str | None = None) -> OtpTemplate:
    """Ensure an active default OTP template exists for IranPayamak Pattern API."""
    code = _resolve_iranpayamak_pattern_code(pattern_code)
    template, _ = OtpTemplate.objects.update_or_create(
        name=IRANPAYAMAK_DEFAULT_TEMPLATE_NAME,
        defaults={
            'parameter_name': DEFAULT_PARAMETER_NAME,
            'body_preview': IRANPAYAMAK_DEFAULT_BODY_PREVIEW,
            'is_active': True,
            'sms_ir_template_id': None,
            'provider_type': SmsProviderProfile.PROVIDER_IRANPAYAMAK,
        },
    )
    if code:
        template.pattern_code = code
    template.is_default = True
    template.is_active = True
    template.provider_type = SmsProviderProfile.PROVIDER_IRANPAYAMAK
    template.save(update_fields=[
        'pattern_code', 'is_default', 'is_active', 'provider_type',
        'parameter_name', 'body_preview', 'updated_at',
    ])
    OtpTemplate.objects.exclude(pk=template.pk).filter(
        provider_type=SmsProviderProfile.PROVIDER_IRANPAYAMAK,
    ).update(is_default=False)
    return template


def sync_default_template_for_mode(is_sandbox: bool) -> OtpTemplate:
    """Activate the correct default OTP template per SMS.ir docs."""
    if is_sandbox:
        template_id = SANDBOX_TEMPLATE_ID
        defaults = {
            'name': SANDBOX_TEMPLATE_NAME,
            'parameter_name': SANDBOX_PARAMETER_NAME,
            'body_preview': SANDBOX_BODY_PREVIEW,
            'is_active': True,
            'provider_type': SmsProviderProfile.PROVIDER_SMSIR,
        }
        deactivate_id = DEFAULT_TEMPLATE_ID
    else:
        template_id = DEFAULT_TEMPLATE_ID
        defaults = {
            'name': DEFAULT_TEMPLATE_NAME,
            'parameter_name': DEFAULT_PARAMETER_NAME,
            'body_preview': DEFAULT_BODY_PREVIEW,
            'is_active': True,
            'provider_type': SmsProviderProfile.PROVIDER_SMSIR,
        }
        deactivate_id = SANDBOX_TEMPLATE_ID

    template, _ = OtpTemplate.objects.update_or_create(
        sms_ir_template_id=template_id,
        defaults=defaults,
    )
    OtpTemplate.objects.filter(provider_type=SmsProviderProfile.PROVIDER_SMSIR).exclude(
        pk=template.pk,
    ).update(is_default=False)
    if not template.is_default:
        template.is_default = True
        template.save(update_fields=['is_default', 'updated_at'])

    OtpTemplate.objects.filter(sms_ir_template_id=deactivate_id).exclude(pk=template.pk).update(
        is_active=False,
        is_default=False,
    )
    return template


def sync_sms_settings() -> None:
    """Seed missing profile values from env — never overwrite admin panel settings."""
    SmsProviderProfile.ensure_profiles()
    smsir = SmsProviderProfile.get_profile(SmsProviderProfile.PROVIDER_SMSIR)
    iranpayamak = SmsProviderProfile.get_profile(SmsProviderProfile.PROVIDER_IRANPAYAMAK)

    updated_smsir: list[str] = []
    env_key = (os.environ.get('SMS_IR_API_KEY') or '').strip()
    if env_key and not smsir.api_key_encrypted:
        smsir.api_key_encrypted = encrypt_value(env_key)
        updated_smsir.append('api_key_encrypted')

    env_sandbox_key = (os.environ.get('SMS_IR_SANDBOX_API_KEY') or '').strip()
    if env_sandbox_key and not smsir.sandbox_api_key_encrypted:
        smsir.sandbox_api_key_encrypted = encrypt_value(env_sandbox_key)
        updated_smsir.append('sandbox_api_key_encrypted')

    if not smsir.base_url:
        smsir.base_url = os.environ.get('SMS_IR_BASE_URL', 'https://api.sms.ir/v1')
        updated_smsir.append('base_url')

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

    if not iranpayamak.base_url:
        iranpayamak.base_url = os.environ.get('IRANPAYAMAK_BASE_URL', 'https://api.iranpayamak.com')
        updated_ip.append('base_url')

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

    active = SmsProviderProfile.get_active()
    if active.provider_type == SmsProviderProfile.PROVIDER_IRANPAYAMAK:
        sync_iranpayamak_default_template()
    elif not OtpTemplate.objects.exists():
        template_id = int(os.environ.get('SMS_IR_TEMPLATE_ID', DEFAULT_TEMPLATE_ID))
        OtpTemplate.objects.create(
            name=DEFAULT_TEMPLATE_NAME,
            sms_ir_template_id=template_id,
            parameter_name=DEFAULT_PARAMETER_NAME,
            body_preview=DEFAULT_BODY_PREVIEW,
            provider_type=SmsProviderProfile.PROVIDER_SMSIR,
            is_active=True,
            is_default=True,
        )
    elif not OtpTemplate.objects.filter(is_default=True).exists():
        sync_default_template_for_mode(smsir.is_sandbox)

    # Keep singleton provider_mode in sync for legacy readers
    singleton = SmsProviderSettings.get_settings()
    if singleton.provider_mode != active.provider_type:
        singleton.provider_mode = active.provider_type
        singleton.save(update_fields=['provider_mode', 'updated_at'])
