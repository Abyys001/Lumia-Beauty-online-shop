"""Zarinpal API error code mapping."""

ZARINPAL_ERRORS = {
    -9: 'خطای اعتبارسنجی درخواست',
    -10: 'IP یا مرچنت کد نامعتبر است',
    -11: 'درخواست یافت نشد',
    -12: 'امکان ویرایش درخواست وجود ندارد',
    -15: 'ترمینال شما به حالت تعلیق درآمده است',
    -16: 'سطح تأیید پذیرنده پایین‌تر از سطح نقره‌ای است',
    -17: 'محدودیت درخواست — لطفاً کمی بعد تلاش کنید',
    -21: 'عملیات مالی یافت نشد',
    -22: 'تراکنش ناموفق',
    -33: 'مبلغ با مقدار پرداخت شده مطابقت ندارد',
    -34: 'محدودیت تعداد درخواست',
    -40: 'اجازه دسترسی به این متد وجود ندارد',
    -41: 'اطلاعات ارسالی نامعتبر است',
    -42: 'مدت زمان معتبر بودن درخواست به پایان رسیده',
    -50: 'مبلغ پرداخت شده با مقدار مبلغ درخواستی متفاوت است',
    -51: 'پرداخت ناموفق',
    -52: 'خطای غیرمنتظره — با پشتیبانی تماس بگیرید',
    -53: 'اتوریتی برای این مرچنت کد نیست',
    -54: 'اتوریتی نامعتبر است',
    -55: 'تراکنش مورد نظر یافت نشد',
    -60: 'امکان ریورس وجود ندارد',
    -61: 'تراکنش قبلاً ریورس شده است',
    -62: 'IP سرور در پنل زرین‌پال ثبت نشده است',
    -63: 'مهلت ریورس (۳۰ دقیقه) به پایان رسیده است',
    100: 'عملیات موفق',
    101: 'تراکنش قبلاً تأیید شده است',
}


def get_error_message(code: int | None, fallback: str = 'خطای نامشخص درگاه پرداخت') -> str:
    if code is None:
        return fallback
    return ZARINPAL_ERRORS.get(code, fallback)


def parse_api_response(result: dict) -> tuple[bool, dict, str, int | None]:
    """
    Parse a Zarinpal REST v4 response.
    Returns (success, data_dict, user_message, error_code).
    """
    if not isinstance(result, dict):
        return False, {}, 'پاسخ نامعتبر از درگاه پرداخت', None

    errors = result.get('errors') or []
    if errors and not result.get('data'):
        first = errors[0] if errors else {}
        code = first.get('code')
        if isinstance(code, str) and code.isdigit():
            code = int(code)
        message = first.get('message') or get_error_message(code)
        return False, {}, message, code

    data = result.get('data') or {}
    code = data.get('code')
    if code is not None:
        try:
            code = int(code)
        except (TypeError, ValueError):
            pass

    if code in (100, 101):
        return True, data, data.get('message', 'موفق'), code

    if code is not None:
        return False, data, get_error_message(code, data.get('message', '')), code

    return False, data, 'خطا در ارتباط با درگاه پرداخت', None
