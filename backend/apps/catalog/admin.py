from django import forms
from django.contrib import admin
from django.utils.html import format_html

from .models import Brand, Category, InstagramPost, Product, ProductAttribute, ProductImage, Review, StoreSettings


class ProductAdminForm(forms.ModelForm):
    original_price = forms.IntegerField(
        label='قیمت اصلی (تومان)',
        min_value=0,
        required=True,
        help_text='قیمت پایه و بدون تخفیف محصول'
    )
    discounted_price = forms.IntegerField(
        label='قیمت با تخفیف (تومان)',
        min_value=0,
        required=False,
        help_text='در صورت تمایل به اعمال تخفیف، این فیلد را پر کنید. در غیر این صورت خالی بگذارید.'
    )

    class Meta:
        model = Product
        exclude = ['price', 'compare_at_price']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            if self.instance.compare_at_price:
                self.initial['original_price'] = self.instance.compare_at_price
                self.initial['discounted_price'] = self.instance.price
            else:
                self.initial['original_price'] = self.instance.price
                self.initial['discounted_price'] = None

    def clean(self):
        cleaned_data = super().clean()
        original_price = cleaned_data.get('original_price')
        discounted_price = cleaned_data.get('discounted_price')

        if discounted_price and discounted_price >= original_price:
            raise forms.ValidationError(
                {'discounted_price': 'قیمت با تخفیف باید از قیمت اصلی کمتر باشد.'}
            )
        return cleaned_data

    def save(self, commit=True):
        product = super().save(commit=False)
        original_price = self.cleaned_data.get('original_price')
        discounted_price = self.cleaned_data.get('discounted_price')

        if discounted_price:
            product.price = discounted_price
            product.compare_at_price = original_price
        else:
            product.price = original_price
            product.compare_at_price = None

        if commit:
            product.save()
        return product


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    verbose_name = 'تصویر'
    verbose_name_plural = 'ویترین بصری (تصاویر محصول - عکس گرفته شده با گوشی را به این کادر بکشید)'


class ProductAttributeInline(admin.TabularInline):
    model = ProductAttribute
    extra = 1
    verbose_name = 'ویژگی'
    verbose_name_plural = 'ویژگی‌های محصول'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'parent', 'mood', 'is_active', 'sort_order']
    list_filter = ['is_active', 'mood']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = ['thumbnail', 'name', 'category', 'brand', 'price', 'stock', 'is_active', 'is_featured', 'sales_count']
    list_filter = ['is_active', 'is_featured', 'category', 'brand']
    search_fields = ['name', 'sku', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ProductAttributeInline]
    list_editable = ['is_active', 'is_featured', 'stock']
    list_per_page = 20
    save_on_top = True

    def thumbnail(self, obj):
        img = obj.images.first()
        if img:
            return format_html(
                '<img src="{}" style="height:40px;width:40px;object-fit:cover;border-radius:6px;box-shadow:0 1px 4px rgba(0,0,0,0.15);" />',
                img.image.url
            )
        return '—'
    thumbnail.short_description = 'تصویر'

    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('name', 'slug', 'brand', 'category', 'description', 'short_description', 'is_active', 'is_featured')
        }),
        ('قیمت و انبار', {
            'fields': ('original_price', 'discounted_price', 'stock', 'sku')
        }),
        ('سئو و موتورهای جستجو', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',),
        }),
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'rating']
    list_editable = ['is_approved']
    search_fields = ['product__name', 'user__phone', 'comment']


@admin.register(InstagramPost)
class InstagramPostAdmin(admin.ModelAdmin):
    list_display = ['caption_preview', 'sort_order', 'is_active', 'post_url']
    list_editable = ['sort_order', 'is_active']
    verbose_name = 'پست اینستاگرام'
    verbose_name_plural = 'ویترین اینستاگرام (جدول دو ستونه آپلود عکس و لینک مستقیم)'

    def caption_preview(self, obj):
        return obj.caption[:50] if obj.caption else format_html('<a href="{}">لینک</a>', obj.post_url)
    caption_preview.short_description = 'توضیح'


@admin.register(StoreSettings)
class StoreSettingsAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'shipping_cost', 'free_shipping_threshold', 'zarinpal_merchant_id']

    def has_add_permission(self, request):
        # Allow only 1 instance
        return not StoreSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

