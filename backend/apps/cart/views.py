from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.catalog.models import Product

from .models import Cart, CartItem
from .serializers import AddToCartSerializer, CartSerializer, UpdateCartItemSerializer
from .services import get_or_create_cart


class CartView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        cart = get_or_create_cart(request)
        return Response(CartSerializer(cart).data)

    @transaction.atomic
    def post(self, request):
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cart = get_or_create_cart(request)
        product = get_object_or_404(
            Product.objects.select_for_update(),
            id=serializer.validated_data['product_id'],
            is_active=True,
        )
        quantity = serializer.validated_data['quantity']

        if product.stock < quantity:
            return Response({'detail': 'موجودی کافی نیست'}, status=status.HTTP_400_BAD_REQUEST)

        item, created = CartItem.objects.select_for_update().get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity},
        )
        if not created:
            new_qty = item.quantity + quantity
            if product.stock < new_qty:
                return Response({'detail': 'موجودی کافی نیست'}, status=status.HTTP_400_BAD_REQUEST)
            item.quantity = new_qty
            item.save()

        return Response(CartSerializer(cart).data, status=status.HTTP_201_CREATED)

    @transaction.atomic
    def delete(self, request):
        cart = get_or_create_cart(request)
        cart.items.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CartItemView(APIView):
    permission_classes = [permissions.AllowAny]

    @transaction.atomic
    def patch(self, request, item_id):
        cart = get_or_create_cart(request)
        item = get_object_or_404(CartItem.objects.select_for_update().select_related('product'), id=item_id, cart=cart)
        serializer = UpdateCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        quantity = serializer.validated_data['quantity']

        if quantity == 0:
            item.delete()
        else:
            if item.product.stock < quantity:
                return Response({'detail': 'موجودی کافی نیست'}, status=status.HTTP_400_BAD_REQUEST)
            item.quantity = quantity
            item.save()

        cart.refresh_from_db()
        return Response(CartSerializer(cart).data)

    @transaction.atomic
    def delete(self, request, item_id):
        cart = get_or_create_cart(request)
        item = get_object_or_404(CartItem.objects.select_for_update(), id=item_id, cart=cart)
        item.delete()
        return Response(CartSerializer(cart).data)
