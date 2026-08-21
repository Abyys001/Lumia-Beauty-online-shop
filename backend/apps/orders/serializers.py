import re

from rest_framework import serializers

from apps.accounts.models import Address, normalize_phone, to_en_digits

from .models import Order, OrderItem
from .services import expires_at


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product_name', 'product_price', 'quantity', 'subtotal', 'product']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_status = serializers.SerializerMethodField()
    payment_status_display = serializers.SerializerMethodField()
    expires_at = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'purchase_code', 'status', 'status_display', 'subtotal',
            'discount_amount', 'shipping_cost', 'total', 'coupon_code',
            'free_shipping', 'shipping_name', 'shipping_phone',
            'shipping_province', 'shipping_city', 'shipping_address',
            'shipping_postal_code', 'shipping_plate_number', 'tracking_number', 'note', 'items',
            'payment_status', 'payment_status_display', 'expires_at',
            'created_at', 'updated_at',
        ]

    def get_expires_at(self, obj):
        return expires_at(obj)

    def get_payment_status(self, obj):
        payment = getattr(obj, 'payment', None)
        return payment.status if payment else None

    def get_payment_status_display(self, obj):
        payment = getattr(obj, 'payment', None)
        return payment.get_status_display() if payment else ''


class CreateOrderSerializer(serializers.Serializer):
    """Validates one checkout submission.

    Every field is declared optional and blank-tolerant so that a missing value
    is reported by ``validate()`` with a message the customer can act on, rather
    than by DRF's generic "may not be blank". Which fields are actually required
    depends on ``address_id``: picking a saved address supplies all of them.
    """

    address_id = serializers.UUIDField(required=False, allow_null=True)
    shipping_name = serializers.CharField(max_length=200, required=False, allow_blank=True)
    shipping_phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    shipping_province = serializers.CharField(max_length=100, required=False, allow_blank=True)
    shipping_city = serializers.CharField(max_length=100, required=False, allow_blank=True)
    shipping_address = serializers.CharField(required=False, allow_blank=True)
    shipping_postal_code = serializers.CharField(max_length=20, required=False, allow_blank=True)
    shipping_plate_number = serializers.CharField(max_length=20, required=False, allow_blank=True)
    coupon_code = serializers.CharField(max_length=50, required=False, allow_blank=True)
    note = serializers.CharField(max_length=1000, required=False, allow_blank=True)

    REQUIRED_LABELS = {
        'shipping_name': 'نام و نام خانوادگی گیرنده',
        'shipping_phone': 'شماره موبایل گیرنده',
        'shipping_province': 'استان',
        'shipping_city': 'شهر',
        'shipping_address': 'آدرس دقیق پستی',
        'shipping_postal_code': 'کد پستی',
    }

    def validate_address_id(self, value):
        if value is None:
            return value
        user = self.context['request'].user
        if not Address.objects.filter(id=value, user=user).exists():
            raise serializers.ValidationError('این آدرس در دفترچه آدرس‌های شما پیدا نشد.')
        return value

    def validate_shipping_phone(self, value):
        value = normalize_phone(value) if value else ''
        if value and (len(value) != 11 or not value.startswith('09')):
            raise serializers.ValidationError('شماره موبایل باید ۱۱ رقم باشد و با ۰۹ شروع شود. مثال: ۰۹۱۲۳۴۵۶۷۸۹')
        return value

    def validate_shipping_postal_code(self, value):
        value = to_en_digits(value).strip().replace('-', '').replace(' ', '') if value else ''
        if value and not re.fullmatch(r'\d{10}', value):
            raise serializers.ValidationError('کد پستی باید دقیقاً ۱۰ رقم باشد (بدون خط تیره).')
        return value

    def validate_shipping_name(self, value):
        value = value.strip()
        if value and len(value) < 3:
            raise serializers.ValidationError('نام گیرنده باید حداقل ۳ حرف باشد.')
        return value

    def validate_shipping_address(self, value):
        value = value.strip()
        if value and len(value) < 10:
            raise serializers.ValidationError('آدرس را کامل‌تر بنویسید (حداقل ۱۰ حرف) تا بسته درست به دستتان برسد.')
        return value

    def validate(self, attrs):
        # A saved address already carries every shipping field; only the manual
        # form has to be checked, and then all of its fields are mandatory.
        if attrs.get('address_id'):
            return attrs

        errors = {
            field: f'{label} الزامی است.'
            for field, label in self.REQUIRED_LABELS.items()
            if not attrs.get(field)
        }
        if errors:
            raise serializers.ValidationError(errors)
        return attrs

    def shipping_info(self):
        """Flatten validated input into ``Order.shipping_*`` kwargs."""
        data = self.validated_data
        plate_number = data.get('shipping_plate_number', '').strip()

        if data.get('address_id'):
            addr = Address.objects.get(id=data['address_id'], user=self.context['request'].user)
            return {
                'shipping_name': addr.receiver_name,
                'shipping_phone': addr.receiver_phone,
                'shipping_province': addr.province,
                'shipping_city': addr.city,
                'shipping_address': addr.address_line,
                'shipping_postal_code': addr.postal_code,
                'shipping_plate_number': plate_number,
            }

        return {
            'shipping_name': data['shipping_name'],
            'shipping_phone': data['shipping_phone'],
            'shipping_province': data['shipping_province'],
            'shipping_city': data['shipping_city'],
            'shipping_address': data['shipping_address'],
            'shipping_postal_code': data['shipping_postal_code'],
            'shipping_plate_number': plate_number,
        }
