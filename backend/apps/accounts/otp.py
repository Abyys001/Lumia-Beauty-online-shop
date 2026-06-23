import logging
import secrets
import string

from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger('accounts.otp')


def generate_otp_code(length=6):
    return ''.join(secrets.choice(string.digits) for _ in range(length))


def otp_cache_key(phone: str) -> str:
    return f'otp:{phone}'


def otp_rate_key(phone: str) -> str:
    return f'otp_rate:{phone}'


def otp_verify_rate_key(phone: str) -> str:
    return f'otp_verify_rate:{phone}'


def store_otp(phone: str, code: str) -> None:
    cache.set(otp_cache_key(phone), code, timeout=settings.OTP_EXPIRY_SECONDS)


def verify_otp(phone: str, code: str) -> bool:
    stored = cache.get(otp_cache_key(phone))
    if stored and stored == code:
        cache.delete(otp_cache_key(phone))
        return True
    return False


def _check_rate_limit(key: str, limit: int, timeout: int) -> bool:
    if cache.add(key, 1, timeout=timeout):
        return True

    try:
        count = cache.incr(key)
    except ValueError:
        cache.set(key, 1, timeout=timeout)
        return True

    return count <= limit


def check_otp_rate_limit(phone: str) -> bool:
    key = otp_rate_key(phone)
    allowed = _check_rate_limit(key, settings.OTP_RATE_LIMIT, settings.OTP_RATE_WINDOW_SECONDS)
    if not allowed:
        logger.warning('OTP request rate limit hit | phone=%s', phone)
    return allowed


def check_otp_verify_rate_limit(phone: str) -> bool:
    key = otp_verify_rate_key(phone)
    allowed = _check_rate_limit(key, settings.OTP_VERIFY_RATE_LIMIT, settings.OTP_VERIFY_RATE_WINDOW_SECONDS)
    if not allowed:
        logger.warning('OTP verify rate limit hit | phone=%s', phone)
    return allowed
