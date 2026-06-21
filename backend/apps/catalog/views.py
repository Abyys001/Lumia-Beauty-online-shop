import hashlib

from django.core.cache import cache
from django_filters import rest_framework as filters
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Category, InstagramPost, Product, Review
from .serializers import (
    CategorySerializer,
    InstagramPostSerializer,
    ProductDetailSerializer,
    ProductListSerializer,
    ReviewCreateSerializer,
)


class ProductFilter(filters.FilterSet):
    brand = filters.CharFilter(field_name='brand__slug')
    category = filters.CharFilter(field_name='category__slug')
    min_price = filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = filters.NumberFilter(field_name='price', lookup_expr='lte')
    scent = filters.CharFilter(field_name='attributes__value', method='filter_attribute')
    skin_type = filters.CharFilter(field_name='attributes__value', method='filter_attribute')
    in_stock = filters.BooleanFilter(method='filter_in_stock')

    class Meta:
        model = Product
        fields = ['brand', 'category', 'min_price', 'max_price', 'is_featured']

    def filter_attribute(self, queryset, name, value):
        key_map = {'scent': 'scent', 'skin_type': 'skin_type'}
        key = key_map.get(name, name)
        return queryset.filter(attributes__key=key, attributes__value__icontains=value).distinct()

    def filter_in_stock(self, queryset, name, value):
        if value:
            return queryset.filter(stock__gt=0)
        return queryset.filter(stock=0)


class ProductListView(generics.ListAPIView):
    serializer_class = ProductListSerializer
    filterset_class = ProductFilter
    search_fields = ['name', 'description', 'short_description']
    ordering_fields = ['price', 'created_at', 'sales_count', 'name']
    ordering = ['-created_at']

    def get_queryset(self):
        return Product.objects.filter(is_active=True).select_related('brand', 'category').prefetch_related('images')


class ProductDetailView(generics.RetrieveAPIView):
    serializer_class = ProductDetailSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        return Product.objects.filter(is_active=True).select_related('brand', 'category').prefetch_related(
            'images', 'attributes', 'reviews__user',
        )

    def retrieve(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        cache_key = f'product_detail_slug:{slug}'
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        cache.set(cache_key, data, timeout=600)
        return Response(data)


class ProductSearchView(APIView):
    def get(self, request):
        q = request.query_params.get('q', '').strip()
        if len(q) < 2:
            return Response([])

        cache_key = f'search:{hashlib.md5(q.encode()).hexdigest()}'
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

        products = Product.objects.filter(
            is_active=True, name__icontains=q,
        ).select_related('brand').prefetch_related('images')[:8]

        serializer = ProductListSerializer(products, many=True, context={'request': request})
        data = serializer.data
        cache.set(cache_key, data, timeout=60)
        return Response(data)


class FeaturedProductsView(APIView):
    def get(self, request):
        cached = cache.get('products_featured')
        if cached:
            return Response(cached)

        products = Product.objects.filter(is_active=True, is_featured=True).select_related(
            'brand', 'category',
        ).prefetch_related('images')[:12]

        serializer = ProductListSerializer(products, many=True, context={'request': request})
        data = serializer.data
        cache.set('products_featured', data, timeout=300)
        return Response(data)


class CategoryListView(generics.ListAPIView):
    serializer_class = CategorySerializer

    def get_queryset(self):
        return Category.objects.filter(is_active=True, parent__isnull=True).prefetch_related('children')


class ProductReviewCreateView(generics.CreateAPIView):
    serializer_class = ReviewCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_product(self):
        return Product.objects.get(slug=self.kwargs['slug'], is_active=True)

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['product'] = self.get_product()
        return ctx

    def create(self, request, *args, **kwargs):
        product = self.get_product()
        if Review.objects.filter(product=product, user=request.user).exists():
            return Response({'detail': 'شما قبلاً برای این محصول نظر ثبت کرده‌اید'}, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)


class InstagramPostListView(generics.ListAPIView):
    serializer_class = InstagramPostSerializer

    def get_queryset(self):
        return InstagramPost.objects.filter(is_active=True)
