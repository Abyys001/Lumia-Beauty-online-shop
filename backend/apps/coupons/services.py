from django.utils import timezone

from .models import Coupon, CouponUsage


def validate_coupon(code, user, subtotal):
    try:
        coupon = Coupon.objects.get(code__iexact=code.strip())
    except Coupon.DoesNotExist:
        return None, 'کد تخفیف نامعتبر است'

    if not coupon.is_valid_now():
        return None, 'کد تخفیف منقضی شده یا غیرفعال است'

    if subtotal < coupon.min_order_amount:
        return None, f'حداقل مبلغ خرید برای این کد {coupon.min_order_amount:,} تومان است'

    user_usage = CouponUsage.objects.filter(coupon=coupon, user=user).count()
    if user_usage >= coupon.per_user_limit:
        return None, 'شما قبلاً از این کد استفاده کرده‌اید'

    return coupon, None


def apply_coupon(coupon, subtotal):
    discount_amount = 0
    free_shipping = False

    if coupon.coupon_type == Coupon.TYPE_PERCENT:
        discount_amount = int(subtotal * coupon.value / 100)
    elif coupon.coupon_type == Coupon.TYPE_FIXED:
        discount_amount = min(coupon.value, subtotal)
    elif coupon.coupon_type == Coupon.TYPE_FREE_SHIPPING:
        free_shipping = True

    return discount_amount, free_shipping


def record_coupon_usage(coupon, user, order):
    CouponUsage.objects.create(coupon=coupon, user=user, order=order)
    coupon.used_count += 1
    coupon.save(update_fields=['used_count'])
