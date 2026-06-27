from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.catalog.models import Product, ProductImage

from ..permissions import IsStaff
from ..serializers import (
    AdminProductImageSerializer,
    AdminProductSerializer,
    AdminProductWriteSerializer,
)


class AdminProductListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsStaff]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category', 'brand', 'is_active', 'is_featured']
    search_fields = ['name', 'sku', 'slug']
    ordering = ['-created_at']

    def get_queryset(self):
        return Product.objects.select_related('category', 'brand').prefetch_related('images', 'attributes')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AdminProductWriteSerializer
        return AdminProductSerializer


class AdminProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsStaff]
    lookup_field = 'id'

    def get_queryset(self):
        return Product.objects.select_related('category', 'brand').prefetch_related('images', 'attributes')

    def get_serializer_class(self):
        if self.request.method in ('PATCH', 'PUT'):
            return AdminProductWriteSerializer
        return AdminProductSerializer


class AdminProductImageUploadView(APIView):
    permission_classes = [IsStaff]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, id):
        product = generics.get_object_or_404(Product, id=id)
        images = request.FILES.getlist('images')
        if not images:
            return Response({'detail': 'هیچ تصویری ارسال نشد'}, status=status.HTTP_400_BAD_REQUEST)
        created = []
        for image in images:
            obj = ProductImage.objects.create(
                product=product,
                image=image,
                alt_text=request.data.get('alt_text', ''),
                is_primary=not product.images.exists(),
            )
            created.append(AdminProductImageSerializer(obj, context={'request': request}).data)
        return Response(created, status=status.HTTP_201_CREATED)

    def delete(self, request, id, img_id):
        img = generics.get_object_or_404(ProductImage, id=img_id, product_id=id)
        img.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
