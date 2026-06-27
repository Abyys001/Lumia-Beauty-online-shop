import re
import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models, transaction


def normalize_phone(phone: str) -> str:
    phone = phone.translate(str.maketrans('۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩', '01234567890123456789'))
    phone = re.sub(r'\D', '', phone)
    if phone.startswith('98') and len(phone) == 12:
        phone = '0' + phone[2:]
    if phone.startswith('9') and len(phone) == 10:
        phone = '0' + phone
    return phone


class UserManager(BaseUserManager):
    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError('شماره موبایل الزامی است')
        phone = normalize_phone(phone)
        user = self.model(phone=phone, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(phone, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone = models.CharField('شماره موبایل', max_length=11, unique=True, db_index=True)
    first_name = models.CharField('نام', max_length=100, blank=True)
    last_name = models.CharField('نام خانوادگی', max_length=100, blank=True)
    email = models.EmailField('ایمیل', blank=True)
    is_active = models.BooleanField('فعال', default=True)
    is_staff = models.BooleanField('کارمند', default=False)
    date_joined = models.DateTimeField('تاریخ عضویت', auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'

    def __str__(self):
        return self.phone

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'.strip() or self.phone


class Address(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses', verbose_name='کاربر')
    title = models.CharField('عنوان', max_length=100, default='خانه')
    province = models.CharField('استان', max_length=100)
    city = models.CharField('شهر', max_length=100)
    address_line = models.TextField('آدرس کامل')
    postal_code = models.CharField('کد پستی', max_length=10)
    receiver_name = models.CharField('نام گیرنده', max_length=200)
    receiver_phone = models.CharField('شماره گیرنده', max_length=11)
    is_default = models.BooleanField('پیش‌فرض', default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'آدرس'
        verbose_name_plural = 'آدرس‌ها'
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f'{self.title} - {self.city}'

    def save(self, *args, **kwargs):
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)


class SmsProviderSettings(models.Model):
    PROVIDER_MOCK = 'mock'
    PROVIDER_SMSIR = 'smsir'
    PROVIDER_IRANPAYAMAK = 'iranpayamak'
    PROVIDER_CHOICES = [
        (PROVIDER_MOCK, 'Mock (توسعه)'),
        (PROVIDER_SMSIR, 'SMS.ir'),
        (PROVIDER_IRANPAYAMAK, 'IranPayamak'),
    ]
    NUMBER_FORMAT_ENGLISH = 'english'
    NUMBER_FORMAT_PERSIAN = 'persian'
    NUMBER_FORMAT_CHOICES = [
        (NUMBER_FORMAT_ENGLISH, 'English'),
        (NUMBER_FORMAT_PERSIAN, 'Persian'),
    ]
    TEST_OK = 'ok'
    TEST_FAILED = 'failed'
    TEST_UNKNOWN = 'unknown'
    TEST_CHOICES = [
        (TEST_OK, 'موفق'),
        (TEST_FAILED, 'ناموفق'),
        (TEST_UNKNOWN, 'نامشخص'),
    ]

    provider_mode = models.CharField('ارائه‌دهنده', max_length=20, choices=PROVIDER_CHOICES, default=PROVIDER_MOCK)
    api_key_encrypted = models.TextField('کلید Production رمزنگاری‌شده', blank=True)
    sandbox_api_key_encrypted = models.TextField('کلید Sandbox رمزنگاری‌شده', blank=True)
    base_url = models.CharField('Base URL', max_length=200, default='https://api.sms.ir/v1')
    is_sandbox = models.BooleanField('حالت Sandbox', default=False)
    is_active = models.BooleanField('فعال', default=True)
    last_test_at = models.DateTimeField('آخرین تست', null=True, blank=True)
    last_test_status = models.CharField('وضعیت تست', max_length=20, choices=TEST_CHOICES, default=TEST_UNKNOWN)
    last_test_message = models.TextField('پیام تست', blank=True)
    line_number = models.CharField('شماره خط IranPayamak', max_length=30, blank=True)
    number_format = models.CharField(
        'فرمت اعداد پیامک',
        max_length=10,
        choices=NUMBER_FORMAT_CHOICES,
        default=NUMBER_FORMAT_ENGLISH,
    )
    panel_username = models.CharField('نام کاربری پنل', max_length=100, blank=True)
    panel_password_encrypted = models.TextField('رمز پنل رمزنگاری‌شده', blank=True)
    bearer_token_encrypted = models.TextField('توکن Bearer رمزنگاری‌شده', blank=True)
    bearer_token_expires_at = models.DateTimeField('انقضای Bearer', null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'تنظیمات SMS'
        verbose_name_plural = 'تنظیمات SMS'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class SmsProviderProfile(models.Model):
    """Per-provider SMS credentials — only one profile may be active at a time."""

    PROVIDER_MOCK = SmsProviderSettings.PROVIDER_MOCK
    PROVIDER_SMSIR = SmsProviderSettings.PROVIDER_SMSIR
    PROVIDER_IRANPAYAMAK = SmsProviderSettings.PROVIDER_IRANPAYAMAK
    PROVIDER_CHOICES = SmsProviderSettings.PROVIDER_CHOICES
    NUMBER_FORMAT_ENGLISH = SmsProviderSettings.NUMBER_FORMAT_ENGLISH
    NUMBER_FORMAT_PERSIAN = SmsProviderSettings.NUMBER_FORMAT_PERSIAN
    NUMBER_FORMAT_CHOICES = SmsProviderSettings.NUMBER_FORMAT_CHOICES
    TEST_OK = SmsProviderSettings.TEST_OK
    TEST_FAILED = SmsProviderSettings.TEST_FAILED
    TEST_UNKNOWN = SmsProviderSettings.TEST_UNKNOWN
    TEST_CHOICES = SmsProviderSettings.TEST_CHOICES

    provider_type = models.CharField('ارائه‌دهنده', max_length=20, choices=PROVIDER_CHOICES, unique=True)
    api_key_encrypted = models.TextField('کلید Production رمزنگاری‌شده', blank=True)
    sandbox_api_key_encrypted = models.TextField('کلید Sandbox رمزنگاری‌شده', blank=True)
    base_url = models.CharField('Base URL', max_length=200, blank=True, default='')
    is_sandbox = models.BooleanField('حالت Sandbox', default=False)
    is_active = models.BooleanField('فعال', default=False)
    last_test_at = models.DateTimeField('آخرین تست', null=True, blank=True)
    last_test_status = models.CharField(
        'وضعیت تست', max_length=20, choices=TEST_CHOICES, default=TEST_UNKNOWN,
    )
    last_test_message = models.TextField('پیام تست', blank=True)
    line_number = models.CharField('شماره خط IranPayamak', max_length=30, blank=True)
    number_format = models.CharField(
        'فرمت اعداد پیامک',
        max_length=10,
        choices=NUMBER_FORMAT_CHOICES,
        default=NUMBER_FORMAT_ENGLISH,
    )
    panel_username = models.CharField('نام کاربری پنل', max_length=100, blank=True)
    panel_password_encrypted = models.TextField('رمز پنل رمزنگاری‌شده', blank=True)
    bearer_token_encrypted = models.TextField('توکن Bearer رمزنگاری‌شده', blank=True)
    bearer_token_expires_at = models.DateTimeField('انقضای Bearer', null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'پروفایل SMS'
        verbose_name_plural = 'پروفایل‌های SMS'
        ordering = ['provider_type']

    def __str__(self):
        return self.get_provider_type_display()

    @classmethod
    def default_base_url(cls, provider_type: str) -> str:
        if provider_type == cls.PROVIDER_IRANPAYAMAK:
            return 'https://api.iranpayamak.com'
        if provider_type == cls.PROVIDER_SMSIR:
            return 'https://api.sms.ir/v1'
        return ''

    @classmethod
    def ensure_profiles(cls):
        for provider_type in (cls.PROVIDER_MOCK, cls.PROVIDER_SMSIR, cls.PROVIDER_IRANPAYAMAK):
            cls.objects.get_or_create(
                provider_type=provider_type,
                defaults={'base_url': cls.default_base_url(provider_type)},
            )

    @classmethod
    def get_active(cls):
        cls.ensure_profiles()
        active = cls.objects.filter(is_active=True).first()
        if active:
            return active
        mock = cls.objects.get(provider_type=cls.PROVIDER_MOCK)
        if not cls.objects.filter(is_active=True).exists():
            mock.is_active = True
            mock.save(update_fields=['is_active', 'updated_at'])
        return mock

    @classmethod
    def get_profile(cls, provider_type: str):
        cls.ensure_profiles()
        return cls.objects.get(provider_type=provider_type)

    @classmethod
    def activate(cls, provider_type: str):
        cls.ensure_profiles()
        with transaction.atomic():
            cls.objects.update(is_active=False)
            profile = cls.objects.select_for_update().get(provider_type=provider_type)
            profile.is_active = True
            profile.save(update_fields=['is_active', 'updated_at'])
            singleton = SmsProviderSettings.get_settings()
            singleton.provider_mode = provider_type
            singleton.is_active = True
            singleton.save(update_fields=['provider_mode', 'is_active', 'updated_at'])
        return profile


class OtpTemplate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('نام قالب', max_length=100)
    sms_ir_template_id = models.PositiveIntegerField('شناسه قالب SMS.ir', null=True, blank=True)
    pattern_code = models.CharField('کد Pattern IranPayamak', max_length=50, blank=True)
    provider_type = models.CharField(
        'ارائه‌دهنده',
        max_length=20,
        choices=SmsProviderSettings.PROVIDER_CHOICES,
        blank=True,
        default='',
    )
    parameter_name = models.CharField('نام پارامتر', max_length=50, default='Code')
    body_preview = models.TextField('پیش‌نمایش متن', blank=True, default='کد تایید شما: {Code}')
    is_active = models.BooleanField('فعال', default=True)
    is_default = models.BooleanField('پیش‌فرض', default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'قالب OTP'
        verbose_name_plural = 'قالب‌های OTP'
        ordering = ['-is_default', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.is_default:
            OtpTemplate.objects.filter(is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)


class OtpSettings(models.Model):
    otp_length = models.PositiveSmallIntegerField('طول OTP', default=6)
    expiry_seconds = models.PositiveIntegerField('انقضا (ثانیه)', default=120)
    max_verify_attempts = models.PositiveSmallIntegerField('حداکثر تلاش تأیید', default=5)
    verify_window_seconds = models.PositiveIntegerField('پنجره تلاش (ثانیه)', default=900)
    rate_limit_count = models.PositiveSmallIntegerField('محدودیت درخواست', default=5)
    rate_limit_window_seconds = models.PositiveIntegerField('پنجره درخواست (ثانیه)', default=900)
    resend_delay_seconds = models.PositiveIntegerField('تأخیر ارسال مجدد (ثانیه)', default=60)
    ip_rate_limit_count = models.PositiveSmallIntegerField('محدودیت IP', default=20)
    ip_rate_limit_window_seconds = models.PositiveIntegerField('پنجره IP (ثانیه)', default=3600)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'تنظیمات OTP'
        verbose_name_plural = 'تنظیمات OTP'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class AuthSettings(models.Model):
    otp_login_enabled = models.BooleanField('ورود با OTP', default=True)
    access_token_lifetime_minutes = models.PositiveSmallIntegerField('عمر Access Token (دقیقه)', default=15)
    refresh_token_lifetime_days = models.PositiveSmallIntegerField('عمر Refresh Token (روز)', default=7)
    rotate_refresh_tokens = models.BooleanField('چرخش Refresh Token', default=True)
    admin_bypass_phone = models.CharField('شماره bypass ادمین', max_length=11, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'تنظیمات احراز هویت'
        verbose_name_plural = 'تنظیمات احراز هویت'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class OtpRequest(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_VERIFIED = 'verified'
    STATUS_EXPIRED = 'expired'
    STATUS_FAILED = 'failed'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'در انتظار'),
        (STATUS_VERIFIED, 'تأیید شده'),
        (STATUS_EXPIRED, 'منقضی'),
        (STATUS_FAILED, 'ناموفق'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone = models.CharField('شماره', max_length=11, db_index=True)
    code_hash = models.CharField('هش کد', max_length=64)
    ip_address = models.GenericIPAddressField('IP', null=True, blank=True)
    user_agent = models.TextField('User Agent', blank=True)
    status = models.CharField('وضعیت', max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    attempts = models.PositiveSmallIntegerField('تلاش‌ها', default=0)
    template = models.ForeignKey(
        OtpTemplate, on_delete=models.SET_NULL, null=True, blank=True, related_name='otp_requests',
    )
    expires_at = models.DateTimeField('انقضا')
    verified_at = models.DateTimeField('تأیید', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'درخواست OTP'
        verbose_name_plural = 'درخواست‌های OTP'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.phone} ({self.status})'


class SmsLog(models.Model):
    STATUS_SENT = 'sent'
    STATUS_FAILED = 'failed'
    STATUS_SIMULATED = 'simulated'
    STATUS_CHOICES = [
        (STATUS_SENT, 'ارسال شده'),
        (STATUS_FAILED, 'ناموفق'),
        (STATUS_SIMULATED, 'شبیه‌سازی'),
    ]
    MESSAGE_OTP = 'otp'
    MESSAGE_CHOICES = [(MESSAGE_OTP, 'OTP')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone = models.CharField('شماره', max_length=11, db_index=True)
    message_type = models.CharField('نوع', max_length=20, choices=MESSAGE_CHOICES, default=MESSAGE_OTP)
    template = models.ForeignKey(OtpTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    provider = models.CharField('ارائه‌دهنده', max_length=20)
    status = models.CharField('وضعیت', max_length=20, choices=STATUS_CHOICES)
    request_data = models.JSONField('درخواست', default=dict, blank=True)
    response_data = models.JSONField('پاسخ', default=dict, blank=True)
    provider_message_id = models.CharField('شناسه پیام', max_length=100, blank=True)
    error_message = models.TextField('خطا', blank=True)
    ip_address = models.GenericIPAddressField('IP', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'لاگ SMS'
        verbose_name_plural = 'لاگ‌های SMS'
        ordering = ['-created_at']


class AuthAuditLog(models.Model):
    ACTION_OTP_REQUESTED = 'otp_requested'
    ACTION_OTP_VERIFIED = 'otp_verified'
    ACTION_OTP_FAILED = 'otp_failed'
    ACTION_LOGIN_SUCCESS = 'login_success'
    ACTION_LOGIN_BLOCKED = 'login_blocked'
    ACTION_TOKEN_REFRESHED = 'token_refreshed'
    ACTION_LOGOUT = 'logout'
    ACTION_CHOICES = [
        (ACTION_OTP_REQUESTED, 'درخواست OTP'),
        (ACTION_OTP_VERIFIED, 'تأیید OTP'),
        (ACTION_OTP_FAILED, 'OTP ناموفق'),
        (ACTION_LOGIN_SUCCESS, 'ورود موفق'),
        (ACTION_LOGIN_BLOCKED, 'مسدود شده'),
        (ACTION_TOKEN_REFRESHED, 'تازه‌سازی توکن'),
        (ACTION_LOGOUT, 'خروج'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    action = models.CharField('عملیات', max_length=30, choices=ACTION_CHOICES, db_index=True)
    phone = models.CharField('شماره', max_length=11, blank=True, db_index=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField('IP', null=True, blank=True)
    metadata = models.JSONField('متادیتا', default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'لاگ احراز هویت'
        verbose_name_plural = 'لاگ‌های احراز هویت'
        ordering = ['-created_at']


class WishlistItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist_items', verbose_name='کاربر')
    product = models.ForeignKey(
        'catalog.Product',
        on_delete=models.CASCADE,
        related_name='wishlisted_by',
        verbose_name='محصول',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'علاقه‌مندی'
        verbose_name_plural = 'علاقه‌مندی‌ها'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['user', 'product'], name='unique_wishlist_per_user_product'),
        ]

    def __str__(self):
        return f'{self.user.phone} → {self.product.name}'
