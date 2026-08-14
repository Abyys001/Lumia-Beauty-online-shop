from rest_framework import serializers

from .media_utils import relative_media_url
from .models import Brand, Category, InstagramPost, Product, ProductAttribute, ProductImage, Review, StoreSettings


class RelativeURLField(serializers.ImageField):
    """Always return the relative /media/... URL so SSR-generated image paths
    resolve correctly in the browser (Nginx already serves /media/)."""
    def to_representation(self, value):
        return relative_media_url(value)


class ProductImageSerializer(serializers.ModelSerializer):
    image = RelativeURLField()

    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'is_primary']


class ProductAttributeSerializer(serializers.ModelSerializer):
    key_display = serializers.CharField(source='get_key_display', read_only=True)

    class Meta:
        model = ProductAttribute
        fields = ['key', 'key_display', 'value']


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ['id', 'user_name', 'rating', 'comment', 'created_at']

    def get_user_name(self, obj):
        return obj.user.full_name or 'کاربر'


class BrandSerializer(serializers.ModelSerializer):
    logo = RelativeURLField()

    class Meta:
        model = Brand
        fields = ['id', 'name', 'slug', 'logo']


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    image = RelativeURLField()

    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'description', 'image', 'mood',
            'parent', 'children', 'meta_title', 'meta_description',
        ]

    def get_children(self, obj):
        if self.context.get('include_children', True):
            children = obj.children.filter(is_active=True).order_by('created_at')
            return CategorySerializer(children, many=True, context={'include_children': False}).data
        return []


class ProductListSerializer(serializers.ModelSerializer):
    primary_image = serializers.SerializerMethodField()
    brand_name = serializers.CharField(source='brand.name', read_only=True, default='')
    category_name = serializers.CharField(source='category.name', read_only=True)
    discount_percent = serializers.IntegerField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'short_description', 'price', 'compare_at_price',
            'discount_percent', 'stock', 'is_in_stock', 'is_featured', 'primary_image',
            'brand_name', 'category_name', 'sales_count',
        ]

    def get_primary_image(self, obj):
        img = obj.images.filter(is_primary=True).first() or obj.images.first()
        return relative_media_url(img.image) if img else None


class ProductDetailSerializer(ProductListSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    attributes = ProductAttributeSerializer(many=True, read_only=True)
    reviews = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    brand = BrandSerializer(read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta(ProductListSerializer.Meta):
        fields = ProductListSerializer.Meta.fields + [
            'name_en', 'description', 'sku', 'license_holder',
            'images', 'attributes', 'reviews',
            'average_rating', 'brand', 'category', 'meta_title', 'meta_description',
            'created_at', 'updated_at',
        ]

    def get_reviews(self, obj):
        reviews = obj.reviews.filter(is_approved=True)[:10]
        return ReviewSerializer(reviews, many=True).data

    def get_average_rating(self, obj):
        reviews = obj.reviews.filter(is_approved=True)
        if not reviews.exists():
            return None
        return round(sum(r.rating for r in reviews) / reviews.count(), 1)


class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['rating', 'comment']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        validated_data['product'] = self.context['product']
        return super().create(validated_data)


class InstagramPostSerializer(serializers.ModelSerializer):
    image = RelativeURLField()

    class Meta:
        model = InstagramPost
        fields = ['id', 'image', 'post_url', 'caption']


class ShippingSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreSettings
        fields = ['shipping_cost', 'free_shipping_threshold']


class StoreContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreSettings
        fields = ['contact_sms_phone', 'contact_telegram', 'contact_whatsapp', 'contact_bale']
