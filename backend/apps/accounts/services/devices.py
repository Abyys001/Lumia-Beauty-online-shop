import hashlib
import secrets
from datetime import timedelta

from django.utils import timezone

from apps.accounts.models import AuthAuditLog, AuthSettings, TrustedDevice
from apps.accounts.services.audit import AuthAuditService

TOKEN_BYTES = 32

_BROWSERS = [('Edg/', 'Edge'), ('OPR/', 'Opera'), ('Chrome/', 'Chrome'), ('Firefox/', 'Firefox'), ('Safari/', 'Safari')]
_PLATFORMS = [
    ('Android', 'اندروید'), ('iPhone', 'آیفون'), ('iPad', 'آیپد'),
    ('Windows', 'ویندوز'), ('Mac OS', 'مک'), ('Linux', 'لینوکس'),
]


def hash_token(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()


def describe_user_agent(user_agent: str) -> str:
    """A label the customer can recognise in the device list, e.g. «Chrome روی ویندوز»."""
    ua = user_agent or ''
    browser = next((label for needle, label in _BROWSERS if needle in ua), '')
    platform = next((label for needle, label in _PLATFORMS if needle in ua), '')
    if browser and platform:
        return f'{browser} روی {platform}'
    return browser or platform or 'دستگاه ناشناس'


def _lifetime() -> timedelta:
    return timedelta(days=AuthSettings.get_settings().trusted_device_lifetime_days or 180)


def trust_device(user, *, name: str = '', user_agent: str = '', ip_address=None) -> dict:
    """Remember this browser. Returns the raw secret — it is never stored or shown again."""
    raw = secrets.token_urlsafe(TOKEN_BYTES)
    device = TrustedDevice.objects.create(
        user=user,
        token_hash=hash_token(raw),
        name=(name or describe_user_agent(user_agent))[:120],
        user_agent=(user_agent or '')[:400],
        ip_address=ip_address,
        expires_at=timezone.now() + _lifetime(),
    )
    AuthAuditService.log(
        AuthAuditLog.ACTION_DEVICE_TRUSTED,
        phone=user.phone, user=user, ip_address=ip_address,
        metadata={'device_id': str(device.id), 'name': device.name},
    )
    return {'device': device, 'token': raw}


def rotate_device(device: TrustedDevice, *, user_agent: str = '', ip_address=None) -> str:
    """Spend the current secret and issue the next one, keeping the device row."""
    raw = secrets.token_urlsafe(TOKEN_BYTES)
    device.previous_token_hash = device.token_hash
    device.token_hash = hash_token(raw)
    device.last_used_at = timezone.now()
    device.expires_at = timezone.now() + _lifetime()
    if user_agent:
        device.user_agent = user_agent[:400]
    if ip_address:
        device.ip_address = ip_address
    device.save(update_fields=[
        'previous_token_hash', 'token_hash', 'last_used_at', 'expires_at', 'user_agent', 'ip_address',
    ])
    return raw


def resolve_device(device_id, raw_token: str, *, ip_address=None) -> TrustedDevice | None:
    """Return the device this secret unlocks, or None — revoking the chain on replay."""
    if not device_id or not raw_token:
        return None
    device = TrustedDevice.objects.select_related('user').filter(id=device_id).first()
    if device is None:
        return None

    token_hash = hash_token(raw_token)
    if device.token_hash == token_hash:
        return device if device.is_valid and device.user.is_active else None

    if device.previous_token_hash and device.previous_token_hash == token_hash:
        # A spent secret came back: either a copy leaked, or the real device
        # never saw its replacement. Either way the chain is no longer trustworthy.
        device.revoke()
        device.user.revoke_sessions()
        AuthAuditService.log(
            AuthAuditLog.ACTION_DEVICE_REUSE,
            phone=device.user.phone, user=device.user, ip_address=ip_address,
            metadata={'device_id': str(device.id)},
        )
    return None
