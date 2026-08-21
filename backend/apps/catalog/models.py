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
    sort_order = models.PositiveIntegerField('ترتیب', default=0, editable=False)
    meta_title = models.CharField('عنوان سئو', max_length=200, blank=True)
    meta_description = models.TextField('توضیحات سئو', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'دسته‌بندی'
        verbose_name_plural = 'دسته‌بندی‌ها'
        ordering = ['created_at']

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
    name_en = models.CharField('نام انگلیسی', max_length=300, blank=True)
    slug = models.SlugField('اسلاگ', max_length=300, unique=True, allow_unicode=True, db_index=True)
    description = models.TextField('توضیحات')
    short_description = models.CharField('توضیح کوتاه', max_length=500, blank=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products', verbose_name='دسته')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name='products', verbose_name='برند')
    price = models.PositiveBigIntegerField('قیمت (تومان)', db_index=True)
    compare_at_price = models.PositiveBigIntegerField('قیمت قبل از تخفیف', null=True, blank=True)
    stock = models.PositiveIntegerField('موجودی', default=0)
    stock_unit_label = models.CharField('واحد شمارش', max_length=20, default='عدد')
    pack_label = models.CharField('برچسب بسته', max_length=20, default='شل')
    stock_pack_sizes = models.JSONField(
        'اندازه بسته‌ها',
        default=list,
        blank=True,
        help_text='لیست اعداد — مثلاً [1, 6, 12] یعنی هر شل ۱۲ عدد',
    )
    low_stock_threshold = models.PositiveSmallIntegerField(
        'آستانه موجودی کم',
        null=True,
        blank=True,
        help_text='خالی = استفاده از پیش‌فرض فروشگاه',
    )
    sku = models.CharField('کد محصول', max_length=100, unique=True, blank=True)
    is_active = models.BooleanField('فعال', default=True, db_index=True)
    is_featured = models.BooleanField('ویژه/پرفروش', default=False)
    sales_count = models.PositiveIntegerField('تعداد فروش', default=0)
    meta_title = models.CharField('عنوان سئو', max_length=200, blank=True)
    meta_description = models.TextField('توضیحات سئو', blank=True)
    license_holder = models.CharField('صادرکننده مجوز', max_length=200, blank=True)
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

    def get_effective_pack_sizes(self):
        sizes = self.stock_pack_sizes or []
        if not sizes:
            settings = StoreSettings.get_settings()
            sizes = settings.default_stock_pack_sizes or [1, 6, 12, 24]
        normalized = sorted({int(s) for s in sizes if int(s) > 0})
        if 1 not in normalized:
            normalized.insert(0, 1)
        return normalized

    def get_effective_low_stock_threshold(self):
        if self.low_stock_threshold is not None:
            return self.low_stock_threshold
        return StoreSettings.get_settings().default_low_stock_threshold


class StockMovement(models.Model):
    REASON_MANUAL = 'manual'
    REASON_PURCHASE = 'purchase'
    REASON_COUNT = 'inventory_count'
    REASON_CORRECTION = 'correction'

    REASON_CHOICES = [
        (REASON_MANUAL, 'تعدیل دستی'),
        (REASON_PURCHASE, 'ورودی خرید'),
        (REASON_COUNT, 'انبارگردانی'),
        (REASON_CORRECTION, 'اصلاح'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='stock_movements', verbose_name='محصول',
    )
    delta = models.IntegerField('تغییر')
    stock_before = models.PositiveIntegerField('موجودی قبل')
    stock_after = models.PositiveIntegerField('موجودی بعد')
    pack_size = models.PositiveIntegerField('اندازه بسته', null=True, blank=True)
    pack_count = models.IntegerField('تعداد بسته', null=True, blank=True)
    reason = models.CharField('دلیل', max_length=30, choices=REASON_CHOICES, default=REASON_MANUAL)
    note = models.CharField('یادداشت', max_length=300, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='stock_movements',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'حرکت انبار'
        verbose_name_plural = 'حرکات انبار'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.product.name}: {self.delta:+d}'


class ProductImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name='محصول')
    image = models.ImageField('تصویر', upload_to=product_image_path)
    alt_text = models.CharField('متن جایگزین', max_length=200, blank=True)
    is_primary = models.BooleanField('تصویر اصلی', default=False)
    sort_order = models.PositiveIntegerField('ترتیب', default=0, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'تصویر محصول'
        verbose_name_plural = 'تصاویر محصول'
        ordering = ['created_at']

    def __str__(self):
        return f'{self.product.name} - تصویر {self.sort_order}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image:
            try:
                img = Image.open(self.image.path)
                ext = self.image.name.rsplit('.', 1)[-1].lower()
                if ext == 'webp' and img.width <= 1200:
                    return
                if img.width > 1200:
                    ratio = 1200 / img.width
                    new_size = (1200, int(img.height * ratio))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                save_kwargs = {'optimize': True}
                if ext in ('jpg', 'jpeg', 'webp'):
                    save_kwargs['quality'] = 85
                img.save(self.image.path, **save_kwargs)
            except Exception:
                pass


class ProductAttribute(models.Model):
    ATTR_SCENT = 'scent'
    ATTR_SKIN_TYPE = 'skin_type'
    ATTR_VOLUME = 'volume'
    ATTR_TYPE = 'product_type'
    ATTR_NOTE_TOP = 'note_top'
    ATTR_NOTE_MIDDLE = 'note_middle'
    ATTR_NOTE_BASE = 'note_base'
    ATTR_LICENSE = 'license'

    ATTR_CHOICES = [
        (ATTR_SCENT, 'رایحه'),
        (ATTR_SKIN_TYPE, 'نوع پوست'),
        (ATTR_VOLUME, 'حجم'),
        (ATTR_TYPE, 'نوع محصول'),
        (ATTR_NOTE_TOP, 'نت اولیه'),
        (ATTR_NOTE_MIDDLE, 'نت میانی'),
        (ATTR_NOTE_BASE, 'نت پایانی'),
        (ATTR_LICENSE, 'مجوز/اصالت'),
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
    sort_order = models.PositiveIntegerField('ترتیب', default=0, editable=False)
    is_active = models.BooleanField('فعال', default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'پست اینستاگرام'
        verbose_name_plural = 'پست‌های اینستاگرام'
        ordering = ['created_at']

    def __str__(self):
        return self.caption or self.post_url[:50]


class StoreSettings(models.Model):
    zarinpal_merchant_id = models.CharField('کد مرچنت زرین‌پال', max_length=100, blank=True)
    shipping_cost = models.PositiveIntegerField('هزینه ارسال بسته (تومان)', default=150000)
    free_shipping_threshold = models.PositiveIntegerField(
        'حداقل خرید برای ارسال رایگان (تومان)',
        default=0,
    )
    contact_person_name = models.CharField(
        'نام مسئول فروش', max_length=100, blank=True,
        help_text='نامی که به مشتری نمایش داده می‌شود — مثلاً خانم قراچه',
    )
    contact_sms_phone = models.CharField(
        'شماره تماس/پیامک', max_length=20, blank=True,
        help_text='مثلاً 09123456789 — از طریق پیامک SMS',
    )
    contact_telegram = models.CharField(
        'شناسه تلگرام', max_length=100, blank=True,
        help_text='بدون @ — مثلاً lumia_beauty',
    )
    contact_whatsapp = models.CharField(
        'شماره واتساپ', max_length=20, blank=True,
        help_text='فرمت بین‌المللی بدون + — مثلاً 989123456789',
    )
    contact_bale = models.CharField(
        'شناسه بله', max_length=100, blank=True,
        help_text='مثلاً lumia_beauty',
    )
    default_low_stock_threshold = models.PositiveSmallIntegerField(
        'آستانه پیش‌فرض موجودی کم',
        default=5,
    )
    default_stock_pack_sizes = models.JSONField(
        'اندازه پیش‌فرض بسته‌ها',
        default=list,
        blank=True,
    )

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
        if created or not obj.default_stock_pack_sizes:
            obj.default_stock_pack_sizes = [1, 6, 12, 24]
            obj.save(update_fields=['default_stock_pack_sizes'])
        return obj

