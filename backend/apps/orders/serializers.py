from rest_framework import serializers

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product_name', 'product_price', 'quantity', 'subtotal', 'product']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'status', 'status_display', 'subtotal',
            'discount_amount', 'shipping_cost', 'total', 'coupon_code',
            'free_shipping', 'shipping_name', 'shipping_phone',
            'shipping_province', 'shipping_city', 'shipping_address',
            'shipping_postal_code', 'note', 'items', 'created_at',
        ]


class CreateOrderSerializer(serializers.Serializer):
    address_id = serializers.UUIDField(required=False)
    shipping_name = serializers.CharField(max_length=200, required=False)
    shipping_phone = serializers.CharField(max_length=11, required=False)
    shipping_province = serializers.CharField(max_length=100, required=False)
    shipping_city = serializers.CharField(max_length=100, required=False)
    shipping_address = serializers.CharField(required=False)
    shipping_postal_code = serializers.CharField(max_length=10, required=False)
    coupon_code = serializers.CharField(max_length=50, required=False, allow_blank=True)
    note = serializers.CharField(required=False, allow_blank=True)
