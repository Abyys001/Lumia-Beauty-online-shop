from django.contrib import admin

from .models import Coupon, CouponUsage


class CouponUsageInline(admin.TabularInline):
    model = CouponUsage
    extra = 0
    readonly_fields = ['user', 'order', 'used_at']


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'coupon_type', 'value', 'min_order_amount', 'used_count', 'is_active']
    list_filter = ['coupon_type', 'is_active']
    search_fields = ['code']
    inlines = [CouponUsageInline]
