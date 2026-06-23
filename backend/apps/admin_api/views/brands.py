from rest_framework import filters, generics

from apps.catalog.models import Brand

from ..permissions import IsStaff
from ..serializers import AdminBrandSerializer


class AdminBrandListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsStaff]
    queryset = Brand.objects.all().order_by('name')
    serializer_class = AdminBrandSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class AdminBrandDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsStaff]
    queryset = Brand.objects.all()
    serializer_class = AdminBrandSerializer
    lookup_field = 'id'
