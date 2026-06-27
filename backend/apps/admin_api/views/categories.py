from rest_framework import filters, generics

from apps.catalog.models import Category

from ..permissions import IsStaff
from ..serializers import AdminCategorySerializer


class AdminCategoryListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsStaff]
    queryset = Category.objects.prefetch_related('children').order_by('created_at')
    serializer_class = AdminCategorySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'slug']


class AdminCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsStaff]
    queryset = Category.objects.prefetch_related('children')
    serializer_class = AdminCategorySerializer
    lookup_field = 'id'
