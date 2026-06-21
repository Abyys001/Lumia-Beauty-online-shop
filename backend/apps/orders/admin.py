from django.contrib import admin
from django.urls import path
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
import json

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'product_name', 'product_price', 'quantity', 'subtotal']



@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'shipping_name', 'shipping_phone', 'status', 'total', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order_number', 'shipping_phone', 'shipping_name']
    readonly_fields = ['order_number', 'subtotal', 'total', 'created_at', 'updated_at']
    inlines = [OrderItemInline]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<str:order_id>/ship/', self.admin_site.admin_view(self.ship_order_view), name='order-ship'),
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
        from apps.catalog.models import StoreSettings
        settings_obj = StoreSettings.get_settings()
        api_key = settings_obj.kavenegar_api_key

        print("\n" + "="*80)
        print("SIMULATING KAVENEGAR SMS TRANSMISSION:")
        print(f"API Key: {api_key or 'NOT SET (DEVELOPMENT FALLBACK)'}")
        print(f"Recipient Phone: {order.shipping_phone}")
        print("Message content:")
        print(f"سلام {order.shipping_name} عزیز، سفارش شما با شماره {order.order_number} تحویل پست شد.")
        print(f"کد رهگیری ۲۴ رقمی پست شما: {order.tracking_number}")
        print("="*80 + "\n")

