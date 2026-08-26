import re
import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


_EN_DIGITS = str.maketrans('۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩', '01234567890123456789')


def to_en_digits(value: str) -> str:
    """Fold Persian and Arabic-Indic digits to ASCII, so keyboards don't matter."""
    return value.translate(_EN_DIGITS)


def normalize_phone(phone: str) -> str:
    phone = to_en_digits(phone)
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
    # Bumped to invalidate every token already handed out for this user — the
    # only revocation lever we have without a token blacklist table.
    session_epoch = models.PositiveIntegerField('نسل نشست', default=0)

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

    def revoke_sessions(self, keep_devices: bool = False) -> None:
        """Sign the user out everywhere: old access/refresh tokens stop validating."""
        self.session_epoch = models.F('session_epoch') + 1
        self.save(update_fields=['session_epoch'])
        self.refresh_from_db(fields=['session_epoch'])
        if not keep_devices:
            self.trusted_devices.filter(revoked_at__isnull=True).update(revoked_at=timezone.now())


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


class AuthSettings(models.Model):
    access_token_lifetime_minutes = models.PositiveSmallIntegerField('عمر Access Token (دقیقه)', default=15)
    refresh_token_lifetime_days = models.PositiveSmallIntegerField('عمر Refresh Token (روز)', default=90)
    rotate_refresh_tokens = models.BooleanField('چرخش Refresh Token', default=True)
    admin_bypass_phone = models.CharField('شماره bypass ادمین', max_length=11, blank=True)
    admin_phones = models.JSONField(
        'شماره‌های ادمین',
        default=list,
        blank=True,
        help_text='هر شماره در این لیست هنگام ثبت‌نام به‌صورت خودکار ادمین می‌شود.',
    )
    trusted_device_lifetime_days = models.PositiveSmallIntegerField(
        'عمر دستگاه مطمئن (روز)',
        default=180,
        help_text='مدتی که «مرا به خاطر بسپار» بدون ورود مجدد کار می‌کند.',
    )
    remember_device_default = models.BooleanField(
        'تیک «مرا به خاطر بسپار» به‌صورت پیش‌فرض',
        default=True,
    )
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

    @classmethod
    def admin_phone_set(cls) -> set:
        """Every phone that grants admin access: DB list + bypass phone + env defaults."""
        from django.conf import settings as django_settings

        phones = set()
        try:
            obj = cls.get_settings()
        except Exception:
            obj = None
        if obj is not None:
            phones.update(obj.admin_phones or [])
            if obj.admin_bypass_phone:
                phones.add(obj.admin_bypass_phone)
        phones.update(getattr(django_settings, 'ADMIN_PHONES', []) or [])
        env_bypass = getattr(django_settings, 'ADMIN_BYPASS_PHONE', '') or ''
        if env_bypass:
            phones.add(env_bypass)
        return {normalize_phone(p) for p in phones if p and normalize_phone(p)}


def is_admin_phone(phone: str) -> bool:
    return normalize_phone(phone) in AuthSettings.admin_phone_set()


def promote_to_admin(user) -> None:
    """Give an admin phone staff + superuser rights (no-op if it already has them)."""
    if user.is_staff and user.is_superuser:
        return
    user.is_staff = True
    user.is_superuser = True
    if user.pk:
        user.save(update_fields=['is_staff', 'is_superuser'])


class AuthAuditLog(models.Model):
    ACTION_LOGIN_SUCCESS = 'login_success'
    ACTION_LOGIN_BLOCKED = 'login_blocked'
    ACTION_TOKEN_REFRESHED = 'token_refreshed'
    ACTION_LOGOUT = 'logout'
    ACTION_PASSWORD_CHANGED = 'password_changed'
    ACTION_DEVICE_LOGIN = 'device_login'
    ACTION_DEVICE_TRUSTED = 'device_trusted'
    ACTION_DEVICE_REVOKED = 'device_revoked'
    ACTION_DEVICE_REUSE = 'device_reuse'
    ACTION_SESSIONS_REVOKED = 'sessions_revoked'
    ACTION_ADMIN_PASSWORD_SET = 'admin_password_set'
    ACTION_ROLE_CHANGED = 'role_changed'
    ACTION_CHOICES = [
        (ACTION_LOGIN_SUCCESS, 'ورود موفق'),
        (ACTION_LOGIN_BLOCKED, 'مسدود شده'),
        (ACTION_TOKEN_REFRESHED, 'تازه‌سازی توکن'),
        (ACTION_LOGOUT, 'خروج'),
        (ACTION_PASSWORD_CHANGED, 'تغییر رمز عبور'),
        (ACTION_DEVICE_LOGIN, 'ورود خودکار دستگاه'),
        (ACTION_DEVICE_TRUSTED, 'ثبت دستگاه مطمئن'),
        (ACTION_DEVICE_REVOKED, 'حذف دستگاه مطمئن'),
        (ACTION_DEVICE_REUSE, 'استفاده مجدد از توکن دستگاه'),
        (ACTION_SESSIONS_REVOKED, 'ابطال نشست‌ها'),
        (ACTION_ADMIN_PASSWORD_SET, 'تغییر رمز توسط ادمین'),
        (ACTION_ROLE_CHANGED, 'تغییر سطح دسترسی'),
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


class TrustedDevice(models.Model):
    """A browser the customer ticked «این دستگاه را به خاطر بسپار» on.

    Holds only the SHA-256 of a random secret, and rotates that secret on every
    auto-login. `previous_token_hash` is kept for exactly one generation so a
    replay of an already-spent token is recognisable as theft rather than
    silently ignored.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trusted_devices', verbose_name='کاربر')
    token_hash = models.CharField(max_length=64, unique=True, db_index=True)
    previous_token_hash = models.CharField(max_length=64, blank=True, db_index=True)
    name = models.CharField('نام دستگاه', max_length=120, blank=True)
    user_agent = models.CharField('User-Agent', max_length=400, blank=True)
    ip_address = models.GenericIPAddressField('IP', null=True, blank=True)
    created_at = models.DateTimeField('ایجاد', auto_now_add=True)
    last_used_at = models.DateTimeField('آخرین استفاده', auto_now_add=True)
    expires_at = models.DateTimeField('انقضا')
    revoked_at = models.DateTimeField('ابطال', null=True, blank=True)

    class Meta:
        verbose_name = 'دستگاه مطمئن'
        verbose_name_plural = 'دستگاه‌های مطمئن'
        ordering = ['-last_used_at']

    def __str__(self):
        return f'{self.user.phone} — {self.name or "دستگاه ناشناس"}'

    @property
    def is_valid(self) -> bool:
        return self.revoked_at is None and self.expires_at > timezone.now()

    def revoke(self) -> None:
        if self.revoked_at is None:
            self.revoked_at = timezone.now()
            self.save(update_fields=['revoked_at'])
