"""SMS.ir helpers: digit normalization, mobile validation, status mapping."""

import re

from apps.accounts.models import normalize_phone

# Iranian mobile operator prefixes (after leading 9)
VALID_MOBILE_PREFIXES = (
    '901', '902', '903', '905', '910', '911', '912', '913', '914', '915',
    '916', '917', '918', '919', '920', '921', '922', '923', '930', '933',
    '934', '935', '936', '937', '938', '939', '990', '991', '992', '993', '994', '996', '999',
)

SMSIR_STATUS_MESSAGES: dict[int, str] = {
    0: 'درخواست شما با خطا مواجه شده‌است',
    1: 'عملیات با موفقیت انجام شد',
    10: 'کلید وب سرویس نامعتبر است',
    11: 'کلید وب سرویس غیرفعال است',
    12: 'کلید وب سرویس محدود به آی‌پی‌های تعریف شده می‌باشد',
    13: 'حساب کاربری غیرفعال است',
    14: 'حساب کاربری در حالت تعلیق قرار دارد',
    15: 'به منظور استفاده از وب سرویس پلن خود را ارتقا دهید',
    16: 'مقدار ارسالی پارامتر نادرست می‌باشد',
    20: 'تعداد درخواست بیشتر از حد مجاز است',
    101: 'شماره خط نامعتبر می‌باشد',
    102: 'اعتبار کافی نمی‌باشد',
    103: 'درخواست شما دارای متن (های) خالی است',
    104: 'درخواست شما دارای موبایل (های) نادرست است — شماره واقعی ایرانی با فرمت 09xxxxxxxxx وارد کنید',
    105: 'تعداد موبایل‌ها بیشتر از حد مجاز (100 عدد) می‌باشد',
    106: 'تعداد متن‌ها بیشتر از حد مجاز (100 عدد) می‌باشد',
    107: 'لیست موبایل‌ها خالی می‌باشد',
    108: 'لیست متن‌ها خالی می‌باشد',
    109: 'زمان ارسال نامعتبر می‌باشد',
    110: 'تعداد شماره موبایل‌ها و تعداد متن‌ها برابر نیستند',
    111: 'با این شناسه ارسالی ثبت نشده است',
    112: 'رکوردی برای حذف یافت نشد',
    113: 'قالب یافت نشد',
    114: 'طول رشته مقدار پارامتر بیش از حد مجاز (25 کاراکتر) می‌باشد',
    115: 'شماره موبایل(ها) در لیست سیاه سامانه می‌باشند',
    116: 'نام یک یا چند پارامتر مقداردهی نشده‌است',
    117: 'متن ارسال شده مورد تایید نمی‌باشد',
    118: 'تعداد پیام‌ها بیشتر از حد مجاز می‌باشد',
    119: 'به منظور استفاده از قالب شخصی‌سازی شده پلن خود را ارتقا دهید',
    123: 'خط ارسال‌کننده نیاز به فعال‌سازی دارد',
    124: 'درحال حاضر فقط امکان ارسال پیامک OTP وجود دارد',
}

DELIVERY_STATE_MESSAGES: dict[int, str] = {
    1: 'رسیده به گوشی',
    2: 'نرسیده به گوشی',
    3: 'رسیده به مخابرات',
    4: 'نرسیده به مخابرات',
    5: 'رسیده به اپراتور',
    6: 'ناموفق',
    7: 'لیست سیاه',
    8: 'نامشخص',
}


def to_ascii_digits(value: str) -> str:
    if not value:
        return ''
    return value.translate(str.maketrans('۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩', '01234567890123456789'))


def format_mobile_for_smsir(phone: str) -> str:
    """Convert to SMS.ir format: 9xxxxxxxxx (ASCII digits only)."""
    normalized = normalize_phone(to_ascii_digits(phone))
    if normalized.startswith('0'):
        return normalized[1:]
    if normalized.startswith('98') and len(normalized) == 12:
        return normalized[2:]
    return to_ascii_digits(normalized)


def validate_iran_mobile_for_smsir(phone: str) -> tuple[str, str]:
    """Return (formatted_mobile, error_message). error empty on success."""
    formatted = format_mobile_for_smsir(phone)
    if not re.fullmatch(r'9\d{9}', formatted):
        return '', SMSIR_STATUS_MESSAGES[104]
    prefix = formatted[:3]
    if prefix not in VALID_MOBILE_PREFIXES:
        return '', SMSIR_STATUS_MESSAGES[104]
    return formatted, ''


def normalize_verify_parameters(parameters: list[dict]) -> list[dict]:
    return [
        {
            'name': str(p.get('name', '')).strip('#'),
            'value': to_ascii_digits(str(p.get('value', ''))),
        }
        for p in parameters
    ]


def map_smsir_status(status: int | None, fallback_message: str = '') -> str:
    if status is None:
        return fallback_message or 'خطای نامشخص'
    mapped = SMSIR_STATUS_MESSAGES.get(int(status))
    if mapped:
        if int(status) in (10, 12):
            mapped += ' — کلید را کامل paste کنید یا محدودیت IP را در پنل SMS.ir بررسی کنید'
        return mapped
    return fallback_message or f'خطای SMS.ir (کد {status})'


def map_delivery_state(state: int | None) -> str:
    if state is None:
        return 'نامشخص'
    return DELIVERY_STATE_MESSAGES.get(int(state), f'وضعیت {state}')
