"""
URL configuration for Lumia Beauty project.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.accounts.urls')),
    path('api/', include('apps.catalog.urls')),
    path('api/cart/', include('apps.cart.urls')),
    path('api/orders/', include('apps.orders.urls')),
    path('api/payments/', include('apps.payments.urls')),
    path('api/coupons/', include('apps.coupons.urls')),
    path('api/blog/', include('apps.blog.urls')),
    path('api/user/', include('apps.accounts.user_urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = 'لومیا بیوتی — پنل مدیریت'
admin.site.site_title = 'Lumia Beauty Admin'
admin.site.index_title = 'مدیریت فروشگاه'

from django.utils import timezone
from django.db.models import Sum
from apps.orders.models import Order
from apps.catalog.models import Product

original_get_app_list = admin.site.get_app_list
original_index = admin.site.index

def custom_get_app_list(request, app_label=None):
    raw_app_list = original_get_app_list(request, app_label)
    
    model_dicts = {}
    for app in raw_app_list:
        for model in app.get('models', []):
            key = f"{app['app_label']}.{model['object_name']}"
            model_dicts[key] = model
            
    shop_models = []
    for k in ['catalog.Product', 'catalog.Category', 'catalog.Brand', 'orders.Order', 'catalog.Review']:
        if k in model_dicts:
            shop_models.append(model_dicts[k])
            
    content_models = []
    for k in ['blog.Post', 'catalog.InstagramPost']:
        if k in model_dicts:
            content_models.append(model_dicts[k])
            
    settings_models = []
    for k in ['catalog.StoreSettings']:
        if k in model_dicts:
            settings_models.append(model_dicts[k])
            
    new_app_list = []
    if shop_models:
        new_app_list.append({
            'name': '۱. فروشگاه (محصولات و سفارشات)',
            'app_label': 'store_group',
            'app_url': '/admin/catalog/product/',
            'has_module_perms': True,
            'models': shop_models,
        })
    if content_models:
        new_app_list.append({
            'name': '۲. محتوا (وبلاگ و اینستاگرام)',
            'app_label': 'content_group',
            'app_url': '/admin/blog/post/',
            'has_module_perms': True,
            'models': content_models,
        })
    if settings_models:
        new_app_list.append({
            'name': '۳. تنظیمات فنی',
            'app_label': 'settings_group',
            'app_url': '/admin/catalog/storesettings/',
            'has_module_perms': True,
            'models': settings_models,
        })
        
    return new_app_list

def custom_index(request, extra_context=None):
    # Calculate status stats
    new_orders_count = Order.objects.filter(status=Order.STATUS_PAID).count()
    low_stock_count = Product.objects.filter(stock__lt=5, is_active=True).count()
    
    # Today's income (for paid orders created today)
    today = timezone.localtime(timezone.now()).date()
    today_income = Order.objects.filter(
        status=Order.STATUS_PAID,
        created_at__date=today
    ).aggregate(total_sum=Sum('total'))['total_sum'] or 0

    today_income_formatted = f"{today_income:,} تومان"
    
    extra_context = extra_context or {}
    extra_context.update({
        'new_orders_count': new_orders_count,
        'low_stock_count': low_stock_count,
        'today_income_formatted': today_income_formatted,
    })
    return original_index(request, extra_context)

admin.site.get_app_list = custom_get_app_list
admin.site.index = custom_index

