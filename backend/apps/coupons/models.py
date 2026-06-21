import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class Coupon(models.Model):
    TYPE_PERCENT = 'percent'
    TYPE_FIXED = 'fixed'
    TYPE_FREE_SHIPPING = 'free_shipping'

    TYPE_CHOICES = [
        (TYPE_PERCENT, 'درصدی'),
        (TYPE_FIXED, 'مبلغ ثابت'),
        (TYPE_FREE_SHIPPING, 'ارسال رایگان'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField('کد', max_length=50, unique=True, db_index=True)
    coupon_type = models.CharField('نوع', max_length=20, choices=TYPE_CHOICES)
    value = models.PositiveBigIntegerField('مقدار', help_text='درصد یا مبلغ تومان')
    min_order_amount = models.PositiveBigIntegerField('حداقل خرید', default=0)
    max_uses = models.PositiveIntegerField('حداکثر استفاده', null=True, blank=True)
    used_count = models.PositiveIntegerField('تعداد استفاده', default=0)
    per_user_limit = models.PositiveIntegerField('محدودیت هر کاربر', default=1)
    is_active = models.BooleanField('فعال', default=True)
    valid_from = models.DateTimeField('از تاریخ', default=timezone.now)
    valid_until = models.DateTimeField('تا تاریخ', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'کد تخفیف'
        verbose_name_plural = 'کدهای تخفیف'

    def __str__(self):
        return self.code

    def is_valid_now(self):
        now = timezone.now()
        if not self.is_active:
            return False
        if self.valid_from > now:
            return False
        if self.valid_until and self.valid_until < now:
            return False
        if self.max_uses and self.used_count >= self.max_uses:
            return False
        return True


class CouponUsage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='usages')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order = models.ForeignKey('orders.Order', on_delete=models.SET_NULL, null=True, blank=True)
    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'استفاده از کد تخفیف'
        verbose_name_plural = 'استفاده‌های کد تخفیف'
