import uuid

from django.conf import settings
from django.db import models


class ZarinpalSettings(models.Model):
    CURRENCY_IRR = 'IRR'
    CURRENCY_IRT = 'IRT'
    CURRENCY_CHOICES = [
        (CURRENCY_IRR, 'ریال'),
        (CURRENCY_IRT, 'تومان'),
    ]

    id = models.PositiveSmallIntegerField(primary_key=True, default=1, editable=False)
    merchant_id = models.CharField('کد مرچنت', max_length=100, blank=True)
    is_sandbox = models.BooleanField('حالت Sandbox', default=True)
    is_mock = models.BooleanField('Mock محلی (بدون HTTP)', default=True)
    callback_url = models.URLField('آدرس Callback', blank=True)
    currency = models.CharField('ارز', max_length=3, choices=CURRENCY_CHOICES, default=CURRENCY_IRR)
    client_id = models.CharField('OAuth Client ID', max_length=100, blank=True)
    client_secret_encrypted = models.TextField('OAuth Client Secret', blank=True)
    terminal_id = models.CharField('Terminal ID', max_length=50, blank=True)
    access_token_encrypted = models.TextField(blank=True)
    refresh_token_encrypted = models.TextField(blank=True)
    token_expires_at = models.DateTimeField(null=True, blank=True)
    auto_reconcile = models.BooleanField('تسویه خودکار', default=False)
    max_retry_attempts = models.PositiveSmallIntegerField('حداکثر تلاش مجدد', default=3)
    enable_api_logging = models.BooleanField('لاگ API', default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'تنظیمات زرین‌پال'
        verbose_name_plural = 'تنظیمات زرین‌پال'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return 'تنظیمات زرین‌پال'


class Payment(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_SUCCESS = 'success'
    STATUS_FAILED = 'failed'
    STATUS_NEEDS_REVIEW = 'needs_review'
    STATUS_REFUNDED = 'refunded'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'در انتظار'),
        (STATUS_SUCCESS, 'موفق'),
        (STATUS_FAILED, 'ناموفق'),
        (STATUS_NEEDS_REVIEW, 'نیازمند بررسی'),
        (STATUS_REFUNDED, 'مرجوع'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.OneToOneField('orders.Order', on_delete=models.CASCADE, related_name='payment')
    amount = models.PositiveBigIntegerField('مبلغ')
    authority = models.CharField('Authority', max_length=100, blank=True, db_index=True)
    ref_id = models.CharField('Ref ID', max_length=100, blank=True)
    session_id = models.CharField('Session ID', max_length=100, blank=True)
    card_pan = models.CharField('شماره کارت', max_length=20, blank=True)
    fee = models.PositiveBigIntegerField('کارمزد', null=True, blank=True)
    fee_type = models.CharField('نوع کارمزد', max_length=20, blank=True)
    error_code = models.IntegerField('کد خطا', null=True, blank=True)
    status = models.CharField('وضعیت', max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    gateway_response = models.JSONField('پاسخ درگاه', default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'پرداخت'
        verbose_name_plural = 'پرداخت‌ها'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.order.order_number} - {self.status}'

    @property
    def is_recent(self):
        """Within 30 minutes of successful payment — eligible for instant reverse."""
        if not self.paid_at:
            return False
        from django.utils import timezone
        return (timezone.now() - self.paid_at).total_seconds() < 1800


class PaymentLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='logs')
    action = models.CharField('عملیات', max_length=100)
    request_data = models.JSONField(default=dict, blank=True)
    response_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'لاگ پرداخت'
        verbose_name_plural = 'لاگ‌های پرداخت'
        ordering = ['-created_at']


class Refund(models.Model):
    METHOD_REVERSE = 'reverse'
    METHOD_CARD = 'card'
    METHOD_PAYA = 'paya'
    METHOD_CHOICES = [
        (METHOD_REVERSE, 'برگشت فوری (Reverse)'),
        (METHOD_CARD, 'کارت (GraphQL)'),
        (METHOD_PAYA, 'پایا (GraphQL)'),
    ]

    STATUS_PENDING = 'pending'
    STATUS_COMPLETED = 'completed'
    STATUS_FAILED = 'failed'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'در انتظار'),
        (STATUS_COMPLETED, 'تکمیل شده'),
        (STATUS_FAILED, 'ناموفق'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='refunds')
    amount = models.PositiveBigIntegerField('مبلغ')
    method = models.CharField('روش', max_length=20, choices=METHOD_CHOICES)
    reason = models.CharField('دلیل', max_length=100, blank=True)
    status = models.CharField('وضعیت', max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    gateway_refund_id = models.CharField('شناسه مرجوعی درگاه', max_length=100, blank=True)
    gateway_response = models.JSONField(default=dict, blank=True)
    initiated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='initiated_refunds',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'مرجوعی'
        verbose_name_plural = 'مرجوعی‌ها'
        ordering = ['-created_at']

    def __str__(self):
        return f'Refund {self.id} - {self.status}'
