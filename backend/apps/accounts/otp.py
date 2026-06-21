import random
import string

from django.conf import settings
from django.core.cache import cache


def generate_otp_code(length=6):
    return ''.join(random.choices(string.digits, k=length))


def otp_cache_key(phone: str) -> str:
    return f'otp:{phone}'


def otp_rate_key(phone: str) -> str:
    return f'otp_rate:{phone}'


def store_otp(phone: str, code: str) -> None:
    cache.set(otp_cache_key(phone), code, timeout=settings.OTP_EXPIRY_SECONDS)


def verify_otp(phone: str, code: str) -> bool:
    stored = cache.get(otp_cache_key(phone))
    if stored and stored == code:
        cache.delete(otp_cache_key(phone))
        return True
    return False


def check_otp_rate_limit(phone: str) -> bool:
    key = otp_rate_key(phone)
    count = cache.get(key, 0)
    if count >= settings.OTP_RATE_LIMIT:
        return False
    cache.set(key, count + 1, timeout=settings.OTP_RATE_WINDOW_SECONDS)
    return True
