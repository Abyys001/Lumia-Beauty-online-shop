import re
import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


def normalize_phone(phone: str) -> str:
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
