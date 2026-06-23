from django.db.models import F

from .models import Coupon, CouponUsage


def validate_coupon(code, user, subtotal, lock=False):
    queryset = Coupon.objects
    if lock:
        queryset = queryset.select_for_update()

    try:
        coupon = queryset.get(code__iexact=code.strip())
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
    if coupon.max_uses and coupon.used_count >= coupon.max_uses:
        return 'کد تخفیف منقضی شده یا غیرفعال است'

    user_usage = CouponUsage.objects.filter(coupon=coupon, user=user).count()
    if user_usage >= coupon.per_user_limit:
        return 'شما قبلاً از این کد استفاده کرده‌اید'

    _, created = CouponUsage.objects.get_or_create(coupon=coupon, user=user, order=order)
    if created:
        Coupon.objects.filter(pk=coupon.pk).update(used_count=F('used_count') + 1)
    return None
