from rest_framework import filters, generics
from django_filters.rest_framework import DjangoFilterBackend

from apps.coupons.models import Coupon

from ..permissions import IsStaff
from ..serializers import AdminCouponSerializer


class AdminCouponListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsStaff]
    serializer_class = AdminCouponSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['coupon_type', 'is_active']
    search_fields = ['code']

    def get_queryset(self):
        return Coupon.objects.prefetch_related('usage__user', 'usage__order').order_by('-created_at')


class AdminCouponDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsStaff]
    serializer_class = AdminCouponSerializer
    lookup_field = 'id'

    def get_queryset(self):
        return Coupon.objects.prefetch_related('usage__user', 'usage__order')
