from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.orders.models import Order
from apps.payments.services import confirm_manual_payment

from ..permissions import IsStaff
from ..serializers import AdminOrderListSerializer, AdminOrderSerializer


class AdminOrderListView(generics.ListAPIView):
    permission_classes = [IsStaff]
    serializer_class = AdminOrderListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['order_number', 'purchase_code', 'shipping_phone', 'shipping_name', 'user__phone']
    ordering_fields = ['created_at', 'total']
    ordering = ['-created_at']

    def get_queryset(self):
        qs = Order.objects.select_related('user').order_by('-created_at')
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            qs = qs.filter(created_at__date__gte=date_from)
        if date_to:
            qs = qs.filter(created_at__date__lte=date_to)
        return qs


class AdminOrderLookupView(APIView):
    """Find an order by its 6-digit purchase code or LB order number."""
    permission_classes = [IsStaff]

    def get(self, request):
        code = (request.query_params.get('code') or '').strip().upper()
        if not code:
            return Response({'detail': 'کد خرید را وارد کنید'}, status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.select_related('user').prefetch_related('items__product').filter(
            purchase_code=code
        ).first()
        if not order and code.startswith('LB'):
            order = Order.objects.select_related('user').prefetch_related('items__product').filter(
                order_number=code
            ).first()
        if not order:
            return Response({'detail': 'سفارشی با این کد پیدا نشد'}, status=status.HTTP_404_NOT_FOUND)

        return Response(AdminOrderSerializer(order).data)


class AdminOrderMarkPaidView(APIView):
    """Confirm a card-to-card payment manually and mark the order paid."""
    permission_classes = [IsStaff]

    def post(self, request, id):
        try:
            order = Order.objects.get(pk=id)
        except Order.DoesNotExist:
            return Response({'detail': 'سفارش یافت نشد'}, status=status.HTTP_404_NOT_FOUND)

        result_order, result, msg = confirm_manual_payment(order, initiated_by=request.user)
        if result == 'failed':
            return Response({'detail': msg}, status=status.HTTP_400_BAD_REQUEST)

        return Response(AdminOrderSerializer(result_order).data)


class AdminOrderDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsStaff]
    serializer_class = AdminOrderSerializer
    lookup_field = 'id'

    def get_queryset(self):
        return Order.objects.select_related('user').prefetch_related('items__product')

    def partial_update(self, request, *args, **kwargs):
        order = self.get_object()
        serializer = self.get_serializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
