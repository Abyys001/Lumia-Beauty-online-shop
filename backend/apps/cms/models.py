import uuid

from django.db import models


class HomeHero(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    headline = models.CharField('تیتر اصلی', max_length=300)
    subheadline = models.CharField('تیتر فرعی', max_length=300, blank=True)
    description = models.TextField('توضیح', blank=True)
    cta_text = models.CharField('متن دکمه', max_length=100, default='کشف رایحه تو')
    cta_url = models.CharField('لینک دکمه', max_length=200, default='/shop')
    cta_secondary_text = models.CharField('متن دکمه دوم', max_length=100, blank=True)
    cta_secondary_url = models.CharField('لینک دکمه دوم', max_length=200, blank=True)
    badge_text = models.CharField('برچسب بالای تیتر', max_length=100, blank=True)
    video_webm = models.FileField('ویدیو WebM', upload_to='cms/hero/', blank=True, null=True)
    video_poster = models.ImageField('پوستر ویدیو', upload_to='cms/hero/', blank=True, null=True)
    fallback_image = models.ImageField('تصویر جایگزین', upload_to='cms/hero/', blank=True, null=True)
    is_active = models.BooleanField('فعال', default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'بنر صفحه اصلی'
        verbose_name_plural = 'بنر صفحه اصلی'

    def __str__(self):
        return self.headline[:50]

    @classmethod
    def get_active(cls):
        return cls.objects.filter(is_active=True).order_by('-updated_at').first()


class TrustBadge(models.Model):
    ICON_CHOICES = [
        ('shield', 'تضمین اصالت'),
        ('shipping', 'ارسال سریع'),
        ('consult', 'مشاوره'),
        ('payment', 'پرداخت امن'),
        ('custom', 'سفارشی'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    icon = models.CharField('آیکون', max_length=20, choices=ICON_CHOICES, default='shield')
    title = models.CharField('عنوان', max_length=100)
    description = models.CharField('توضیح', max_length=200, blank=True)
    sort_order = models.PositiveIntegerField('ترتیب', default=0)
    is_active = models.BooleanField('فعال', default=True)

    class Meta:
        verbose_name = 'نشان اعتماد'
        verbose_name_plural = 'نشان‌های اعتماد'
        ordering = ['sort_order']

    def __str__(self):
        return self.title
