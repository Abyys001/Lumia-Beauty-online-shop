from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, status
from rest_framework.response import Response

from apps.orders.models import Order

from ..permissions import IsStaff
from ..serializers import AdminOrderListSerializer, AdminOrderSerializer


class AdminOrderListView(generics.ListAPIView):
    permission_classes = [IsStaff]
    serializer_class = AdminOrderListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['order_number', 'shipping_phone', 'shipping_name', 'user__phone']
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
