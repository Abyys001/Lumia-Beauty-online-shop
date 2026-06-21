import uuid

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from PIL import Image


def product_image_path(instance, filename):
    ext = filename.rsplit('.', 1)[-1]
    return f'products/{instance.product_id}/{uuid.uuid4()}.{ext}'


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('نام', max_length=200)
    slug = models.SlugField('اسلاگ', max_length=200, unique=True, allow_unicode=True)
    description = models.TextField('توضیحات', blank=True)
    image = models.ImageField('تصویر', upload_to='categories/', blank=True, null=True)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True,
        related_name='children', verbose_name='دسته والد',
    )
    mood = models.CharField(
        'حس/تم', max_length=50, blank=True,
        help_text='مثلاً: خنک، شیرین، مراقبت پوست',
    )
    is_active = models.BooleanField('فعال', default=True)
    sort_order = models.PositiveIntegerField('ترتیب', default=0)
    meta_title = models.CharField('عنوان سئو', max_length=200, blank=True)
    meta_description = models.TextField('توضیحات سئو', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'دسته‌بندی'
        verbose_name_plural = 'دسته‌بندی‌ها'
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name


class Brand(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('نام برند', max_length=200)
    slug = models.SlugField('اسلاگ', max_length=200, unique=True, allow_unicode=True)
    logo = models.ImageField('لوگو', upload_to='brands/', blank=True, null=True)
    is_active = models.BooleanField('فعال', default=True)

    class Meta:
        verbose_name = 'برند'
        verbose_name_plural = 'برندها'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('نام محصول', max_length=300)
    slug = models.SlugField('اسلاگ', max_length=300, unique=True, allow_unicode=True, db_index=True)
    description = models.TextField('توضیحات')
    short_description = models.CharField('توضیح کوتاه', max_length=500, blank=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products', verbose_name='دسته')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name='products', verbose_name='برند')
    price = models.PositiveBigIntegerField('قیمت (تومان)', db_index=True)
    compare_at_price = models.PositiveBigIntegerField('قیمت قبل از تخفیف', null=True, blank=True)
    stock = models.PositiveIntegerField('موجودی', default=0)
    sku = models.CharField('کد محصول', max_length=100, unique=True, blank=True)
    is_active = models.BooleanField('فعال', default=True, db_index=True)
    is_featured = models.BooleanField('ویژه/پرفروش', default=False)
    sales_count = models.PositiveIntegerField('تعداد فروش', default=0)
    meta_title = models.CharField('عنوان سئو', max_length=200, blank=True)
    meta_description = models.TextField('توضیحات سئو', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'محصول'
        verbose_name_plural = 'محصولات'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['brand', 'is_active']),
            models.Index(fields=['-sales_count']),
        ]

    def __str__(self):
        return self.name

    @property
    def is_in_stock(self):
        return self.stock > 0

    @property
    def discount_percent(self):
        if self.compare_at_price and self.compare_at_price > self.price:
            return int((1 - self.price / self.compare_at_price) * 100)
        return 0


class ProductImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name='محصول')
    image = models.ImageField('تصویر', upload_to=product_image_path)
    alt_text = models.CharField('متن جایگزین', max_length=200, blank=True)
    is_primary = models.BooleanField('تصویر اصلی', default=False)
    sort_order = models.PositiveIntegerField('ترتیب', default=0)

    class Meta:
        verbose_name = 'تصویر محصول'
        verbose_name_plural = 'تصاویر محصول'
        ordering = ['sort_order']

    def __str__(self):
        return f'{self.product.name} - تصویر {self.sort_order}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image:
            try:
                img = Image.open(self.image.path)
                if img.width > 1200:
                    ratio = 1200 / img.width
                    new_size = (1200, int(img.height * ratio))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                    img.save(self.image.path, quality=85, optimize=True)
            except Exception:
                pass


class ProductAttribute(models.Model):
    ATTR_SCENT = 'scent'
    ATTR_SKIN_TYPE = 'skin_type'
    ATTR_VOLUME = 'volume'
    ATTR_TYPE = 'product_type'

    ATTR_CHOICES = [
        (ATTR_SCENT, 'رایحه'),
        (ATTR_SKIN_TYPE, 'نوع پوست'),
        (ATTR_VOLUME, 'حجم'),
        (ATTR_TYPE, 'نوع محصول'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='attributes', verbose_name='محصول')
    key = models.CharField('کلید', max_length=50, choices=ATTR_CHOICES)
    value = models.CharField('مقدار', max_length=200)

    class Meta:
        verbose_name = 'ویژگی محصول'
        verbose_name_plural = 'ویژگی‌های محصول'
        unique_together = [['product', 'key']]

    def __str__(self):
        return f'{self.get_key_display()}: {self.value}'


class Review(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', verbose_name='محصول')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(
        'امتیاز', validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    comment = models.TextField('نظر')
    is_approved = models.BooleanField('تأیید شده', default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'نظر'
        verbose_name_plural = 'نظرات'
        ordering = ['-created_at']
        unique_together = [['product', 'user']]

    def __str__(self):
        return f'{self.user} - {self.product.name}'


class InstagramPost(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.ImageField('تصویر', upload_to='instagram/')
    post_url = models.URLField('لینک پست اینستاگرام')
    caption = models.CharField('توضیح کوتاه', max_length=300, blank=True)
    sort_order = models.PositiveIntegerField('ترتیب', default=0)
    is_active = models.BooleanField('فعال', default=True)

    class Meta:
        verbose_name = 'پست اینستاگرام'
        verbose_name_plural = 'پست‌های اینستاگرام'
        ordering = ['sort_order']

    def __str__(self):
        return self.caption or self.post_url[:50]


class StoreSettings(models.Model):
    zarinpal_merchant_id = models.CharField('کد مرچنت زرین‌پال', max_length=100, blank=True)
    kavenegar_api_key = models.CharField('کلید API کاوه‌نگار', max_length=200, blank=True)
    kavenegar_template = models.CharField('قالب پیامک', max_length=100, default='verify', blank=True)

    class Meta:
        verbose_name = 'تنظیمات پایه'
        verbose_name_plural = 'تنظیمات پایه'

    def __str__(self):
        return 'تنظیمات فروشگاه'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

