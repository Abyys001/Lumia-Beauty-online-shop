"""IranPayamak helpers: digit normalization, mobile validation, error mapping."""

import re

from apps.accounts.models import normalize_phone

VALID_MOBILE_PREFIXES = (
    '901', '902', '903', '905', '910', '911', '912', '913', '914', '915',
    '916', '917', '918', '919', '920', '921', '922', '923', '930', '933',
    '934', '935', '936', '937', '938', '939', '990', '991', '992', '993', '994', '996', '999',
)


def to_ascii_digits(value: str) -> str:
    if not value:
        return ''
    return value.translate(str.maketrans('۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩', '01234567890123456789'))


def format_mobile_for_iranpayamak(phone: str) -> str:
    """IranPayamak pattern API expects 09xxxxxxxxx."""
    normalized = normalize_phone(to_ascii_digits(phone))
    if normalized.startswith('9') and len(normalized) == 10:
        return '0' + normalized
    return normalized


def validate_iran_mobile_for_iranpayamak(phone: str) -> tuple[str, str]:
    formatted = format_mobile_for_iranpayamak(phone)
    if not re.fullmatch(r'09\d{9}', formatted):
        return '', 'شماره موبایل نامعتبر است — فرمت 09xxxxxxxxx'
    prefix = formatted[1:4]
    if prefix not in VALID_MOBILE_PREFIXES:
        return '', 'شماره موبایل نامعتبر است — پیش‌شماره اپراتور شناخته نشد'
    return formatted, ''


def normalize_number_format(value: str) -> str:
    cleaned = (value or 'english').strip().lower()
    if cleaned in ('fa', 'persian', 'farsi'):
        return 'persian'
    return 'english'


def map_iranpayamak_error(message: str | list | dict | None, http_status: int = 0) -> str:
    if isinstance(message, list):
        return '; '.join(str(m) for m in message)
    if isinstance(message, dict):
        parts = []
        for key, val in message.items():
            if isinstance(val, list):
                parts.append(f'{key}: {"; ".join(str(v) for v in val)}')
            else:
                parts.append(f'{key}: {val}')
        return '; '.join(parts) if parts else 'خطای نامشخص'
    if message:
        return str(message)
    if http_status == 401:
        return 'Unauthorized — کلید Api-Key یا توکن Bearer نامعتبر است'
    return 'خطای نامشخص IranPayamak'
