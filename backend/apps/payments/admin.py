from django.contrib import admin
from django.utils.html import format_html

from .models import Payment, PaymentLog

_PAYMENT_STATUS_COLORS = {
    'pending':      '#6c757d',
    'success':      '#28a745',
    'failed':       '#dc3545',
    'needs_review': '#fd7e14',
    'refunded':     '#17a2b8',
}


class PaymentLogInline(admin.TabularInline):
    model = PaymentLog
    extra = 0
    readonly_fields = ['action', 'request_data', 'response_data', 'created_at']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['order', 'amount', 'colored_status', 'ref_id', 'authority', 'created_at', 'paid_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order__order_number', 'authority', 'ref_id']
    readonly_fields = ['authority', 'ref_id', 'gateway_response', 'created_at', 'paid_at']
    inlines = [PaymentLogInline]

    def colored_status(self, obj):
        color = _PAYMENT_STATUS_COLORS.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 10px;border-radius:12px;font-size:0.82em;">{}</span>',
            color, obj.get_status_display()
        )
    colored_status.short_description = 'وضعیت'
