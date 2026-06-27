import hashlib

from django.core.cache import cache
from django.db.models import Q
from django_filters import rest_framework as filters
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .cache_utils import (
    CACHE_TTL_BRANDS,
    CACHE_TTL_CATEGORIES,
    CACHE_TTL_PRODUCT_DETAIL,
    CACHE_TTL_PRODUCT_RELATED,
    CACHE_TTL_PRODUCTS_FEATURED,
    CACHE_TTL_PRODUCTS_LIST,
    CACHE_TTL_SEARCH,
    products_list_cache_key,
)
from .models import Brand, Category, InstagramPost, Product, ProductAttribute, Review, StoreSettings
from .serializers import (
    BrandSerializer,
    CategorySerializer,
    InstagramPostSerializer,
    ProductDetailSerializer,
    ProductListSerializer,
    ReviewCreateSerializer,
    ShippingSettingsSerializer,
)


class ProductFilter(filters.FilterSet):
    brand = filters.CharFilter(field_name='brand__slug')
    category = filters.CharFilter(field_name='category__slug')
    mood = filters.CharFilter(field_name='category__mood', lookup_expr='icontains')
    min_price = filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = filters.NumberFilter(field_name='price', lookup_expr='lte')
    scent = filters.CharFilter(method='filter_scent')
    skin_type = filters.CharFilter(method='filter_skin_type')
    note_top = filters.CharFilter(method='filter_note')
    note_middle = filters.CharFilter(method='filter_note')
    note_base = filters.CharFilter(method='filter_note')
    in_stock = filters.BooleanFilter(method='filter_in_stock')

    class Meta:
        model = Product
        fields = ['brand', 'category', 'mood', 'min_price', 'max_price', 'is_featured']

    def filter_scent(self, queryset, name, value):
        return queryset.filter(
            attributes__key__in=['scent', ProductAttribute.ATTR_NOTE_TOP,
                                 ProductAttribute.ATTR_NOTE_MIDDLE, ProductAttribute.ATTR_NOTE_BASE],
            attributes__value__icontains=value,
        ).distinct()

    def filter_skin_type(self, queryset, name, value):
        return queryset.filter(attributes__key='skin_type', attributes__value__icontains=value).distinct()

    def filter_note(self, queryset, name, value):
        key_map = {'note_top': 'note_top', 'note_middle': 'note_middle', 'note_base': 'note_base'}
        key = key_map.get(name, name)
        return queryset.filter(attributes__key=key, attributes__value__icontains=value).distinct()

    def filter_in_stock(self, queryset, name, value):
        if value:
            return queryset.filter(stock__gt=0)
        return queryset.filter(stock=0)


class ProductListView(generics.ListAPIView):
    serializer_class = ProductListSerializer
    filterset_class = ProductFilter
    permission_classes = [permissions.AllowAny]
    search_fields = ['name', 'description', 'short_description']
    ordering_fields = ['price', 'created_at', 'sales_count', 'name']
    ordering = ['-created_at']

    def get_queryset(self):
        return Product.objects.filter(is_active=True).select_related('brand', 'category').prefetch_related('images')

    def list(self, request, *args, **kwargs):
        cache_key = products_list_cache_key(request)
        cached = cache.get(cache_key)
        if cached is not None:
            return Response(cached)

        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=CACHE_TTL_PRODUCTS_LIST)
        return response


class ProductDetailView(generics.RetrieveAPIView):
    serializer_class = ProductDetailSerializer
    lookup_field = 'slug'
    permission_classes = [permissions.AllowAny]

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
        cache.set(cache_key, data, timeout=CACHE_TTL_PRODUCT_DETAIL)
        return Response(data)


class RelatedProductsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, slug):
        cache_key = f'product_related:{slug}'
        cached = cache.get(cache_key)
        if cached is not None:
            return Response(cached)

        try:
            product = Product.objects.select_related('category', 'brand').get(slug=slug, is_active=True)
        except Product.DoesNotExist:
            return Response({'detail': 'محصول یافت نشد'}, status=status.HTTP_404_NOT_FOUND)

        related = (
            Product.objects.filter(is_active=True, stock__gt=0)
            .exclude(id=product.id)
            .filter(
                Q(category=product.category) | Q(brand=product.brand),
            )
            .select_related('brand', 'category')
            .prefetch_related('images')
            .distinct()[:8]
        )
        if related.count() < 4:
            extra = (
                Product.objects.filter(is_active=True, stock__gt=0)
                .exclude(id=product.id)
                .exclude(id__in=related.values_list('id', flat=True))
                .select_related('brand', 'category')
                .prefetch_related('images')
                .order_by('-sales_count')[:8 - related.count()]
            )
            related = list(related) + list(extra)

        serializer = ProductListSerializer(related, many=True, context={'request': request})
        data = serializer.data
        cache.set(cache_key, data, timeout=CACHE_TTL_PRODUCT_RELATED)
        return Response(data)


class ProductSearchView(APIView):
    permission_classes = [permissions.AllowAny]

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
        cache.set(cache_key, data, timeout=CACHE_TTL_SEARCH)
        return Response(data)


class FeaturedProductsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        cached = cache.get('products_featured')
        if cached:
            return Response(cached)

        products = Product.objects.filter(is_active=True, is_featured=True).select_related(
            'brand', 'category',
        ).prefetch_related('images')[:12]

        serializer = ProductListSerializer(products, many=True, context={'request': request})
        data = serializer.data
        cache.set('products_featured', data, timeout=CACHE_TTL_PRODUCTS_FEATURED)
        return Response(data)


class CategoryListView(generics.ListAPIView):
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        return Category.objects.filter(is_active=True, parent__isnull=True).prefetch_related('children').order_by('created_at')

    def list(self, request, *args, **kwargs):
        cached = cache.get('categories_list')
        if cached is not None:
            return Response(cached)

        response = super().list(request, *args, **kwargs)
        cache.set('categories_list', response.data, timeout=CACHE_TTL_CATEGORIES)
        return response


class BrandListView(generics.ListAPIView):
    serializer_class = BrandSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        return Brand.objects.filter(is_active=True).order_by('name')

    def list(self, request, *args, **kwargs):
        cached = cache.get('brands_list')
        if cached is not None:
            return Response(cached)

        response = super().list(request, *args, **kwargs)
        cache.set('brands_list', response.data, timeout=CACHE_TTL_BRANDS)
        return response


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
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return InstagramPost.objects.filter(is_active=True).order_by('created_at')


class ShippingSettingsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        settings, _ = StoreSettings.objects.get_or_create(pk=1)
        return Response(ShippingSettingsSerializer(settings).data)
