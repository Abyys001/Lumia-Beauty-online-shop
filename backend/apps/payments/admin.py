from django.contrib import admin

from .models import Payment, PaymentLog


class PaymentLogInline(admin.TabularInline):
    model = PaymentLog
    extra = 0
    readonly_fields = ['action', 'request_data', 'response_data', 'created_at']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['order', 'amount', 'status', 'ref_id', 'authority', 'created_at', 'paid_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order__order_number', 'authority', 'ref_id']
    readonly_fields = ['authority', 'ref_id', 'gateway_response', 'created_at', 'paid_at']
    inlines = [PaymentLogInline]
