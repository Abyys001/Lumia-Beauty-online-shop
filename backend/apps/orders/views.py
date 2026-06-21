from django.db import transaction
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import Address
from apps.cart.services import get_or_create_cart
from apps.coupons.services import apply_coupon, validate_coupon

from .models import Order, OrderItem
from .serializers import CreateOrderSerializer, OrderSerializer

SHIPPING_COST = 50000
FREE_SHIPPING_THRESHOLD = 500000


class CreateOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        cart = get_or_create_cart(request)
        if not cart.items.exists():
            return Response({'detail': 'سبد خرید خالی است'}, status=status.HTTP_400_BAD_REQUEST)

        for item in cart.items.select_related('product'):
            if item.product.stock < item.quantity:
                return Response(
                    {'detail': f'موجودی {item.product.name} کافی نیست'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        shipping = self._get_shipping_info(request.user, data)
        if not shipping:
            return Response({'detail': 'اطلاعات آدرس الزامی است'}, status=status.HTTP_400_BAD_REQUEST)

        subtotal = cart.total
        discount_amount = 0
        free_shipping = False
        coupon_code = data.get('coupon_code', '')

        if coupon_code:
            coupon, error = validate_coupon(coupon_code, request.user, subtotal)
            if error:
                return Response({'detail': error}, status=status.HTTP_400_BAD_REQUEST)
            discount_amount, free_shipping = apply_coupon(coupon, subtotal)

        shipping_cost = 0 if free_shipping or subtotal >= FREE_SHIPPING_THRESHOLD else SHIPPING_COST
        total = max(subtotal - discount_amount + shipping_cost, 0)

        order = Order.objects.create(
            user=request.user,
            subtotal=subtotal,
            discount_amount=discount_amount,
            shipping_cost=shipping_cost,
            total=total,
            coupon_code=coupon_code,
            free_shipping=free_shipping or subtotal >= FREE_SHIPPING_THRESHOLD,
            **shipping,
            note=data.get('note', ''),
        )

        for item in cart.items.select_related('product'):
            OrderItem.objects.create(
                order=order,
                product=item.product,
                product_name=item.product.name,
                product_price=item.product.price,
                quantity=item.quantity,
                subtotal=item.subtotal,
            )

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    def _get_shipping_info(self, user, data):
        if data.get('address_id'):
            try:
                addr = Address.objects.get(id=data['address_id'], user=user)
                return {
                    'shipping_name': addr.receiver_name,
                    'shipping_phone': addr.receiver_phone,
                    'shipping_province': addr.province,
                    'shipping_city': addr.city,
                    'shipping_address': addr.address_line,
                    'shipping_postal_code': addr.postal_code,
                }
            except Address.DoesNotExist:
                return None

        required = [
            'shipping_name', 'shipping_phone', 'shipping_province',
            'shipping_city', 'shipping_address', 'shipping_postal_code',
        ]
        if all(data.get(f) for f in required):
            return {field: data[field] for field in required}
        return None


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'order_number'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items')


class UserOrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items')
