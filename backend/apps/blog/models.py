import uuid

from django.conf import settings
from django.db import models


class PostCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('نام', max_length=200)
    slug = models.SlugField('اسلاگ', max_length=200, unique=True, allow_unicode=True)

    class Meta:
        verbose_name = 'دسته مقاله'
        verbose_name_plural = 'دسته‌های مقاله'

    def __str__(self):
        return self.name


class Tag(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('نام', max_length=100)
    slug = models.SlugField('اسلاگ', max_length=100, unique=True, allow_unicode=True)

    class Meta:
        verbose_name = 'برچسب'
        verbose_name_plural = 'برچسب‌ها'

    def __str__(self):
        return self.name


class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField('عنوان', max_length=300)
    slug = models.SlugField('اسلاگ', max_length=300, unique=True, allow_unicode=True, db_index=True)
    excerpt = models.TextField('خلاصه', max_length=500)
    content = models.TextField('محتوا')
    cover_image = models.ImageField('تصویر شاخص', upload_to='blog/', blank=True, null=True)
    category = models.ForeignKey(PostCategory, on_delete=models.SET_NULL, null=True, related_name='posts')
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    is_published = models.BooleanField('منتشر شده', default=False, db_index=True)
    meta_title = models.CharField('عنوان سئو', max_length=200, blank=True)
    meta_description = models.TextField('توضیحات سئو', blank=True)
    published_at = models.DateTimeField('تاریخ انتشار', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'مقاله'
        verbose_name_plural = 'مقالات'
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return self.title
