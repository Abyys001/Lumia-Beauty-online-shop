from rest_framework import serializers

from .models import Address, AuthSettings, User, normalize_phone


class PhoneLoginSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)

    def validate_phone(self, value):
        phone = normalize_phone(value)
        if not phone.startswith('09') or len(phone) != 11:
            raise serializers.ValidationError('شماره موبایل معتبر نیست')
        return phone


class PasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)

    def validate_password(self, value):
        if len(value) < 4:
            raise serializers.ValidationError('رمز عبور باید حداقل ۴ کاراکتر باشد')
        return value


class RegisterSerializer(PhoneLoginSerializer, PasswordSerializer):
    first_name = serializers.CharField(required=False, allow_blank=True, default='', max_length=100)
    last_name = serializers.CharField(required=False, allow_blank=True, default='', max_length=100)

    def create(self, validated_data):
        phone = validated_data['phone']
        password = validated_data['password']
        first_name = validated_data.get('first_name', '')
        last_name = validated_data.get('last_name', '')

        user = User.objects.filter(phone=phone).first()
        if user is not None and user.has_usable_password():
            raise serializers.ValidationError({'phone': 'این شماره قبلاً ثبت شده است. لطفاً وارد شوید.'})

        if user is None:
            user = User(phone=phone)
        user.set_password(password)
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        return user


class LoginSerializer(PhoneLoginSerializer, PasswordSerializer):
    def validate(self, attrs):
        from django.conf import settings as django_settings
        from django.contrib.auth import authenticate

        phone = attrs['phone']
        user = authenticate(phone=phone, password=attrs['password'])

        auth = AuthSettings.get_settings()
        bypass_phone = normalize_phone(auth.admin_bypass_phone) if auth.admin_bypass_phone else ''
        if not bypass_phone:
            env_phone = getattr(django_settings, 'ADMIN_BYPASS_PHONE', '') or ''
            bypass_phone = normalize_phone(env_phone) if env_phone else ''
        if user is None and phone == bypass_phone:
            user = User.objects.filter(phone=phone).first()
            if user is None:
                user = User.objects.create_user(phone=phone)
            if not user.is_staff or not user.is_superuser:
                user.is_staff = True
                user.is_superuser = True
                user.save(update_fields=['is_staff', 'is_superuser'])

        if user is None or not user.is_active:
            raise serializers.ValidationError({'detail': 'شماره موبایل یا رمز عبور اشتباه است'})

        attrs['user'] = user
        return attrs


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
