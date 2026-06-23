from rest_framework import serializers

from apps.accounts.models import (
    Address, AuthAuditLog, AuthSettings, OtpSettings, OtpTemplate,
    SmsLog, SmsProviderSettings, User,
)
from apps.blog.models import Post, PostCategory, Tag
from apps.catalog.models import (
    Brand, Category, InstagramPost, Product,
    ProductAttribute, ProductImage, Review, StoreSettings,
)
from apps.coupons.models import Coupon, CouponUsage
from apps.orders.models import Order, OrderItem
from apps.payments.models import Payment


# ── Accounts ──────────────────────────────────────────────────────────────────

class AdminAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'title', 'province', 'city', 'address_line',
                  'postal_code', 'receiver_name', 'receiver_phone', 'is_default', 'created_at']


class AdminUserSerializer(serializers.ModelSerializer):
    address_count = serializers.SerializerMethodField()
    addresses = AdminAddressSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'phone', 'first_name', 'last_name', 'email',
                  'is_active', 'is_staff', 'date_joined', 'address_count', 'addresses']
        read_only_fields = ['id', 'phone', 'date_joined']

    def get_address_count(self, obj):
        return obj.addresses.count()


class AdminUserListSerializer(serializers.ModelSerializer):
    address_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'phone', 'first_name', 'last_name', 'email',
                  'is_active', 'is_staff', 'date_joined', 'address_count']
        read_only_fields = ['id', 'phone', 'date_joined', 'is_staff']

    def get_address_count(self, obj):
        return obj.addresses.count()


# ── Catalog ───────────────────────────────────────────────────────────────────

class AdminCategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'image', 'parent',
                  'mood', 'is_active', 'sort_order', 'meta_title', 'meta_description',
                  'created_at', 'children']
        read_only_fields = ['id', 'created_at']

    def get_children(self, obj):
        return [{'id': c.id, 'name': c.name, 'slug': c.slug} for c in obj.children.all()]


class AdminBrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name', 'slug', 'logo', 'is_active']
        read_only_fields = ['id']


class AdminProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'is_primary', 'sort_order']
        read_only_fields = ['id']


class AdminProductAttributeSerializer(serializers.ModelSerializer):
    key_display = serializers.CharField(source='get_key_display', read_only=True)

    class Meta:
        model = ProductAttribute
        fields = ['id', 'key', 'key_display', 'value']
        read_only_fields = ['id']


class AdminProductSerializer(serializers.ModelSerializer):
    images = AdminProductImageSerializer(many=True, read_only=True)
    attributes = AdminProductAttributeSerializer(many=True, read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True, default='')
    category_name = serializers.CharField(source='category.name', read_only=True)
    discount_percent = serializers.SerializerMethodField()
    primary_image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'short_description',
            'category', 'category_name', 'brand', 'brand_name',
            'price', 'compare_at_price', 'stock', 'sku',
            'is_active', 'is_featured', 'sales_count',
            'meta_title', 'meta_description',
            'created_at', 'updated_at',
            'images', 'attributes', 'primary_image', 'discount_percent',
        ]
        read_only_fields = ['id', 'sales_count', 'created_at', 'updated_at']

    def get_primary_image(self, obj):
        img = obj.images.filter(is_primary=True).first() or obj.images.first()
        return img.image.url if img else None

    def get_discount_percent(self, obj):
        return obj.discount_percent


class AdminProductWriteSerializer(serializers.ModelSerializer):
    original_price = serializers.IntegerField(write_only=True, min_value=0)
    discounted_price = serializers.IntegerField(write_only=True, min_value=0)
    attributes = AdminProductAttributeSerializer(many=True, required=False)

    class Meta:
        model = Product
        fields = [
            'name', 'slug', 'description', 'short_description',
            'category', 'brand', 'original_price', 'discounted_price',
            'stock', 'sku', 'is_active', 'is_featured',
            'meta_title', 'meta_description', 'attributes',
        ]

    def validate(self, data):
        dp = data.get('discounted_price')
        op = data.get('original_price')
        if dp is not None and op is not None and dp >= op:
            raise serializers.ValidationError('قیمت فروش باید کمتر از قیمت اصلی باشد')
        return data

    def _set_prices(self, validated_data):
        if 'original_price' in validated_data:
            validated_data['compare_at_price'] = validated_data.pop('original_price')
        if 'discounted_price' in validated_data:
            validated_data['price'] = validated_data.pop('discounted_price')
        return validated_data

    def create(self, validated_data):
        attributes_data = validated_data.pop('attributes', [])
        validated_data = self._set_prices(validated_data)
        product = super().create(validated_data)
        for attr in attributes_data:
            ProductAttribute.objects.create(product=product, **attr)
        return product

    def update(self, instance, validated_data):
        attributes_data = validated_data.pop('attributes', None)
        validated_data = self._set_prices(validated_data)
        product = super().update(instance, validated_data)
        if attributes_data is not None:
            product.attributes.all().delete()
            for attr in attributes_data:
                ProductAttribute.objects.create(product=product, **attr)
        return product


class AdminReviewSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    user_phone = serializers.CharField(source='user.phone', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'product', 'product_name', 'user', 'user_phone',
                  'rating', 'comment', 'is_approved', 'created_at']
        read_only_fields = ['id', 'product', 'user', 'rating', 'comment', 'created_at']


class AdminInstagramPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstagramPost
        fields = ['id', 'image', 'post_url', 'caption', 'sort_order', 'is_active']
        read_only_fields = ['id']


class AdminStoreSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreSettings
        fields = ['zarinpal_merchant_id']


# ── Orders ────────────────────────────────────────────────────────────────────

class AdminOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'product_price', 'quantity', 'subtotal']
        read_only_fields = ['id', 'product', 'product_name', 'product_price', 'quantity', 'subtotal']


class AdminOrderSerializer(serializers.ModelSerializer):
    items = AdminOrderItemSerializer(many=True, read_only=True)
    user_phone = serializers.CharField(source='user.phone', read_only=True)
    payment_status = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user', 'user_phone', 'status',
            'subtotal', 'discount_amount', 'shipping_cost', 'total',
            'coupon_code', 'free_shipping',
            'shipping_name', 'shipping_phone', 'shipping_province',
            'shipping_city', 'shipping_address', 'shipping_postal_code',
            'tracking_number', 'note', 'created_at', 'updated_at',
            'items', 'payment_status',
        ]
        read_only_fields = [
            'id', 'order_number', 'user', 'user_phone',
            'subtotal', 'discount_amount', 'shipping_cost', 'total',
            'coupon_code', 'free_shipping',
            'shipping_name', 'shipping_phone', 'shipping_province',
            'shipping_city', 'shipping_address', 'shipping_postal_code',
            'created_at', 'updated_at', 'items', 'payment_status',
        ]

    def get_payment_status(self, obj):
        try:
            return obj.payment.status
        except Exception:
            return None

    def validate(self, data):
        status = data.get('status')
        tracking = data.get('tracking_number', '')
        if status == Order.STATUS_SHIPPED:
            if not tracking or len(tracking) != 24 or not tracking.isdigit():
                raise serializers.ValidationError(
                    {'tracking_number': 'کد رهگیری باید دقیقاً ۲۴ رقم باشد'}
                )
        return data


class AdminOrderListSerializer(serializers.ModelSerializer):
    user_phone = serializers.CharField(source='user.phone', read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'order_number', 'user_phone', 'status', 'total', 'created_at']
        read_only_fields = fields


# ── Coupons ───────────────────────────────────────────────────────────────────

class AdminCouponUsageSerializer(serializers.ModelSerializer):
    user_phone = serializers.CharField(source='user.phone', read_only=True)
    order_number = serializers.CharField(source='order.order_number', read_only=True, default='')

    class Meta:
        model = CouponUsage
        fields = ['id', 'user_phone', 'order_number', 'used_at']
        read_only_fields = fields


class AdminCouponSerializer(serializers.ModelSerializer):
    usage = AdminCouponUsageSerializer(many=True, read_only=True)

    class Meta:
        model = Coupon
        fields = [
            'id', 'code', 'coupon_type', 'value', 'min_order_amount',
            'max_uses', 'used_count', 'per_user_limit',
            'is_active', 'valid_from', 'valid_until', 'created_at', 'usage',
        ]
        read_only_fields = ['id', 'used_count', 'created_at']


# ── Blog ──────────────────────────────────────────────────────────────────────

class AdminTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']
        read_only_fields = ['id']


class AdminPostCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PostCategory
        fields = ['id', 'name', 'slug']
        read_only_fields = ['id']


class AdminPostSerializer(serializers.ModelSerializer):
    tags = AdminTagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(), write_only=True, source='tags', required=False
    )
    category_name = serializers.CharField(source='category.name', read_only=True, default='')
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'excerpt', 'content', 'cover_image',
            'category', 'category_name', 'tags', 'tag_ids',
            'author', 'author_name', 'is_published',
            'meta_title', 'meta_description',
            'published_at', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_author_name(self, obj):
        if obj.author:
            return obj.author.get_full_name() or obj.author.phone
        return ''


# ── SMS / OTP Settings ────────────────────────────────────────────────────────

class AdminSmsProviderSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SmsProviderSettings
        fields = [
            'provider_mode', 'base_url', 'is_sandbox', 'is_active',
            'last_test_at', 'last_test_status', 'last_test_message', 'updated_at',
        ]
        read_only_fields = ['last_test_at', 'last_test_status', 'last_test_message', 'updated_at']


class AdminOtpTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OtpTemplate
        fields = [
            'id', 'name', 'sms_ir_template_id', 'parameter_name', 'body_preview',
            'is_active', 'is_default', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AdminOtpSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OtpSettings
        fields = [
            'otp_length', 'expiry_seconds', 'max_verify_attempts', 'verify_window_seconds',
            'rate_limit_count', 'rate_limit_window_seconds', 'resend_delay_seconds',
            'ip_rate_limit_count', 'ip_rate_limit_window_seconds', 'updated_at',
        ]
        read_only_fields = ['updated_at']

    def validate_otp_length(self, value):
        if value < 4 or value > 8:
            raise serializers.ValidationError('طول OTP باید بین ۴ تا ۸ باشد')
        return value


class AdminAuthSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthSettings
        fields = [
            'otp_login_enabled', 'access_token_lifetime_minutes',
            'refresh_token_lifetime_days', 'rotate_refresh_tokens',
            'admin_bypass_phone', 'updated_at',
        ]
        read_only_fields = ['updated_at']


class AdminSmsLogSerializer(serializers.ModelSerializer):
    template_name = serializers.CharField(source='template.name', read_only=True, default='')

    class Meta:
        model = SmsLog
        fields = [
            'id', 'phone', 'message_type', 'template', 'template_name', 'provider',
            'status', 'request_data', 'response_data', 'provider_message_id',
            'error_message', 'ip_address', 'created_at',
        ]


class AdminAuthAuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthAuditLog
        fields = ['id', 'action', 'phone', 'user', 'ip_address', 'metadata', 'created_at']

