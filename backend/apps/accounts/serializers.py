from rest_framework import serializers

from apps.accounts.sms.smsir_utils import to_ascii_digits

from .models import Address, User, normalize_phone


class OTPRequestSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)

    def validate_phone(self, value):
        phone = normalize_phone(value)
        if not phone.startswith('09') or len(phone) != 11:
            raise serializers.ValidationError('شماره موبایل معتبر نیست')
        return phone


class OTPVerifySerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)
    code = serializers.CharField(max_length=6, min_length=6)

    def validate_phone(self, value):
        phone = normalize_phone(value)
        if not phone.startswith('09') or len(phone) != 11:
            raise serializers.ValidationError('شماره موبایل معتبر نیست')
        return phone

    def validate_code(self, value):
        code = to_ascii_digits(str(value).strip())
        if not code.isdigit() or len(code) != 6:
            raise serializers.ValidationError('کد تأیید باید ۶ رقم باشد')
        return code


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'phone', 'first_name', 'last_name', 'full_name', 'email', 'date_joined', 'is_staff']
        read_only_fields = ['id', 'phone', 'date_joined', 'is_staff']


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            'id', 'title', 'province', 'city', 'address_line',
            'postal_code', 'receiver_name', 'receiver_phone', 'is_default', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
