from django.db import transaction
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import Address
from apps.cart.services import get_or_create_cart
from apps.catalog.models import Product
from apps.catalog.shipping import calculate_shipping_cost, qualifies_for_free_shipping
from apps.coupons.services import apply_coupon, validate_coupon

from .models import Order, OrderItem
from .serializers import CreateOrderSerializer, OrderSerializer
from .services import maybe_expire_stale_orders


class CreateOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        cart = get_or_create_cart(request)
        cart_items = list(cart.items.select_for_update().select_related('product'))
        if not cart_items:
            return Response({'detail': 'سبد خرید خالی است'}, status=status.HTTP_400_BAD_REQUEST)

        product_ids = [item.product_id for item in cart_items]
        locked_products = {
            product.id: product
            for product in Product.objects.select_for_update().filter(id__in=product_ids)
        }

        for item in cart_items:
            product = locked_products[item.product_id]
            if product.stock < item.quantity:
                return Response(
                    {'detail': f'موجودی {product.name} کافی نیست'},
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

        shipping_cost = calculate_shipping_cost(subtotal, free_shipping=free_shipping)
        order_free_shipping = qualifies_for_free_shipping(subtotal, free_shipping=free_shipping)
        total = max(subtotal - discount_amount + shipping_cost, 0)

        order = Order.objects.create(
            user=request.user,
            subtotal=subtotal,
            discount_amount=discount_amount,
            shipping_cost=shipping_cost,
            total=total,
            coupon_code=coupon_code,
            free_shipping=order_free_shipping,
            **shipping,
            note=data.get('note', ''),
        )

        for item in cart_items:
            product = locked_products[item.product_id]
            OrderItem.objects.create(
                order=order,
                product=product,
                product_name=product.name,
                product_price=product.price,
                quantity=item.quantity,
                subtotal=product.price * item.quantity,
            )

        # Payment is card-to-card and confirmed manually by the seller, possibly hours
        # later. The order is the record from here on, so free the cart immediately
        # instead of leaving stale items around until confirmation.
        cart.items.all().delete()

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
                    'shipping_plate_number': data.get('shipping_plate_number', ''),
                }
            except Address.DoesNotExist:
                return None

        required = ['shipping_phone', 'shipping_province', 'shipping_city', 'shipping_address']
        if not all(data.get(f) for f in required):
            return None

        user_name = user.full_name if user else ''
        return {
            'shipping_name': data.get('shipping_name') or user_name or 'مشتری',
            'shipping_phone': data['shipping_phone'],
            'shipping_province': data['shipping_province'],
            'shipping_city': data['shipping_city'],
            'shipping_address': data['shipping_address'],
            'shipping_postal_code': data.get('shipping_postal_code', ''),
            'shipping_plate_number': data.get('shipping_plate_number', ''),
        }


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'order_number'

    def get_queryset(self):
        maybe_expire_stale_orders()
        return Order.objects.filter(user=self.request.user).select_related('payment').prefetch_related('items')


class UserOrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        maybe_expire_stale_orders()
        return Order.objects.filter(user=self.request.user).select_related('payment').prefetch_related('items')
