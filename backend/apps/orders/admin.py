from django.contrib import admin
from django.urls import path
from django.http import JsonResponse
from django.utils.html import format_html
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
import json

from .models import Order, OrderItem
from apps.payments.services import confirm_manual_payment

_ORDER_STATUS_COLORS = {
    'pending':    '#6c757d',
    'paid':       '#28a745',
    'processing': '#17a2b8',
    'shipped':    '#007bff',
    'delivered':  '#6f42c1',
    'cancelled':  '#dc3545',
    'refunded':   '#fd7e14',
}


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'product_name', 'product_price', 'quantity', 'subtotal']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'shipping_name', 'shipping_phone', 'colored_status', 'total', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order_number', 'purchase_code', 'shipping_phone', 'shipping_name']
    readonly_fields = ['order_number', 'subtotal', 'total', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    list_per_page = 20

    def colored_status(self, obj):
        color = _ORDER_STATUS_COLORS.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 10px;border-radius:12px;font-size:0.82em;white-space:nowrap;">{}</span>',
            color, obj.get_status_display()
        )
    colored_status.short_description = 'وضعیت'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<str:order_id>/ship/', self.admin_site.admin_view(self.ship_order_view), name='order-ship'),
            path('<str:order_id>/confirm-payment/', self.admin_site.admin_view(self.confirm_payment_view), name='order-confirm-payment'),
        ]
        return custom_urls + urls

    @method_decorator(csrf_protect)
    def ship_order_view(self, request, order_id):
        if request.method == 'POST':
            try:
                data = json.loads(request.body)
            except Exception:
                return JsonResponse({'success': False, 'error': 'فرمت درخواست نامعتبر است.'}, status=400)

            tracking_number = data.get('tracking_number', '').strip()
            if not tracking_number or len(tracking_number) != 24 or not tracking_number.isdigit():
                return JsonResponse({'success': False, 'error': 'کد رهگیری پست باید دقیقاً ۲۴ رقم باشد.'}, status=400)

            try:
                order = Order.objects.get(pk=order_id)
                order.status = Order.STATUS_SHIPPED
                order.tracking_number = tracking_number
                order.save()

                # Simulate SMS sending
                self.send_shipment_sms(order)

                return JsonResponse({'success': True})
            except Order.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'سفارش یافت نشد.'}, status=404)
        return JsonResponse({'success': False, 'error': 'درخواست نامعتبر است.'}, status=405)

    def send_shipment_sms(self, order):
        print("\n" + "=" * 80)
        print("SIMULATING SHIPMENT SMS:")
        print(f"Recipient Phone: {order.shipping_phone}")
        print("Message content:")
        print(f"سلام {order.shipping_name} عزیز، سفارش شما با شماره {order.order_number} تحویل پست شد.")
        print(f"کد رهگیری ۲۴ رقمی پست شما: {order.tracking_number}")
        print("=" * 80 + "\n")

    @method_decorator(csrf_protect)
    def confirm_payment_view(self, request, order_id):
        if request.method == 'POST':
            try:
                order = Order.objects.get(pk=order_id)
            except Order.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'سفارش یافت نشد.'}, status=404)

            if order.status != Order.STATUS_PENDING:
                return JsonResponse({'success': False, 'error': 'فقط سفارشات در انتظار پرداخت قابل تأیید هستند.'}, status=400)

            result_order, result, msg = confirm_manual_payment(order, initiated_by=request.user)
            if result == 'success':
                return JsonResponse({'success': True, 'ref_id': msg})
            return JsonResponse({'success': False, 'error': msg or 'تأیید پرداخت ناموفق بود.'}, status=400)
        return JsonResponse({'success': False, 'error': 'درخواست نامعتبر است.'}, status=405)

