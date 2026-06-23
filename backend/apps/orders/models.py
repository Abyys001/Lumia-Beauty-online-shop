import uuid

from django.conf import settings
from django.db import models

from apps.catalog.models import Product


class Order(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_PAID = 'paid'
    STATUS_PROCESSING = 'processing'
    STATUS_SHIPPED = 'shipped'
    STATUS_DELIVERED = 'delivered'
    STATUS_CANCELLED = 'cancelled'
    STATUS_REFUNDED = 'refunded'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'در انتظار پرداخت'),
        (STATUS_PAID, 'پرداخت شده'),
        (STATUS_PROCESSING, 'در حال پردازش'),
        (STATUS_SHIPPED, 'ارسال شده'),
        (STATUS_DELIVERED, 'تحویل داده شده'),
        (STATUS_CANCELLED, 'لغو شده'),
        (STATUS_REFUNDED, 'مرجوع شده'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField('شماره سفارش', max_length=20, unique=True, db_index=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='orders')
    status = models.CharField('وضعیت', max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING, db_index=True)

    subtotal = models.PositiveBigIntegerField('جمع جزء')
    discount_amount = models.PositiveBigIntegerField('تخفیف', default=0)
    shipping_cost = models.PositiveBigIntegerField('هزینه ارسال', default=0)
    total = models.PositiveBigIntegerField('مبلغ نهایی')

    coupon_code = models.CharField('کد تخفیف', max_length=50, blank=True)
    free_shipping = models.BooleanField('ارسال رایگان', default=False)

    shipping_name = models.CharField('نام گیرنده', max_length=200)
    shipping_phone = models.CharField('شماره گیرنده', max_length=11)
    shipping_province = models.CharField('استان', max_length=100)
    shipping_city = models.CharField('شهر', max_length=100)
    shipping_address = models.TextField('آدرس')
    shipping_postal_code = models.CharField('کد پستی', max_length=10, blank=True)
    tracking_number = models.CharField('کد رهگیری پست', max_length=24, blank=True, null=True)

    note = models.TextField('یادداشت', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'سفارش'
        verbose_name_plural = 'سفارشات'
        ordering = ['-created_at']

    def __str__(self):
        return self.order_number

    @property
    def total_formatted(self):
        return f"{self.total:,}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            import random
            import string
            self.order_number = 'LB' + ''.join(random.choices(string.digits, k=8))
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    product_name = models.CharField('نام محصول', max_length=300)
    product_price = models.PositiveBigIntegerField('قیمت واحد')
    quantity = models.PositiveIntegerField('تعداد')
    subtotal = models.PositiveBigIntegerField('جمع')

    class Meta:
        verbose_name = 'آیتم سفارش'
        verbose_name_plural = 'آیتم‌های سفارش'

    def __str__(self):
        return f'{self.product_name} x {self.quantity}'
