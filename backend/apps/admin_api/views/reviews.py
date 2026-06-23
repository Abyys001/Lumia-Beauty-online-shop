from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics

from apps.catalog.models import Review

from ..permissions import IsStaff
from ..serializers import AdminReviewSerializer


class AdminReviewListView(generics.ListAPIView):
    permission_classes = [IsStaff]
    serializer_class = AdminReviewSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_approved', 'rating']
    search_fields = ['product__name', 'user__phone', 'comment']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return Review.objects.select_related('product', 'user')


class AdminReviewDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsStaff]
    serializer_class = AdminReviewSerializer
    lookup_field = 'id'

    def get_queryset(self):
        return Review.objects.select_related('product', 'user')
