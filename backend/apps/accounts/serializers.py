from rest_framework import serializers
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from .authentication import SESSION_EPOCH_CLAIM

from .models import (
    Address,
    AuthSettings,
    TrustedDevice,
    User,
    is_admin_phone,
    normalize_phone,
    promote_to_admin,
)


class RememberDeviceMixin(serializers.Serializer):
    # Offered on login *and* sign-up: the customer should never have to type the
    # password again on a phone they own.
    remember_device = serializers.BooleanField(required=False, default=True)
    device_name = serializers.CharField(required=False, allow_blank=True, max_length=120)


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


class RegisterSerializer(PhoneLoginSerializer, PasswordSerializer, RememberDeviceMixin):
    # The name goes on the parcel, so it is collected once at sign-up rather
    # than chased down at checkout.
    first_name = serializers.CharField(max_length=100, error_messages={
        'blank': 'نام الزامی است.', 'required': 'نام الزامی است.',
    })
    last_name = serializers.CharField(max_length=100, error_messages={
        'blank': 'نام خانوادگی الزامی است.', 'required': 'نام خانوادگی الزامی است.',
    })

    def validate_first_name(self, value):
        return value.strip()

    def validate_last_name(self, value):
        return value.strip()

    def create(self, validated_data):
        phone = validated_data['phone']
        password = validated_data['password']
        first_name = validated_data.get('first_name', '')
        last_name = validated_data.get('last_name', '')

        user = User.objects.filter(phone=phone).first()
        # An empty password hash is a placeholder row (admin phones seeded on boot),
        # which Django still reports as "usable" — such a row may finish registering.
        if user is not None and user.password and user.has_usable_password():
            raise serializers.ValidationError({'phone': 'این شماره قبلاً ثبت شده است. لطفاً وارد شوید.'})

        if user is None:
            user = User(phone=phone)
        user.set_password(password)
        user.first_name = first_name
        user.last_name = last_name
        if is_admin_phone(phone):
            user.is_staff = True
            user.is_superuser = True
        user.save()
        return user


class ChangePasswordSerializer(serializers.Serializer):
    # Deliberately no current-password field: the store asked for a
    # low-friction form (new + confirm) for an already-signed-in device.
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        if len(value) < 4:
            raise serializers.ValidationError('رمز عبور باید حداقل ۴ کاراکتر باشد')
        return value

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({'confirm_password': 'رمزها یکسان نیستند'})
        return attrs


class LoginSerializer(PhoneLoginSerializer, PasswordSerializer, RememberDeviceMixin):
    def validate(self, attrs):
        from django.conf import settings as django_settings
        from django.contrib.auth import authenticate

        phone = attrs['phone']
        user = authenticate(phone=phone, password=attrs['password'])

        # Password bypass stays limited to the single configured bypass phone.
        auth = AuthSettings.get_settings()
        bypass_phone = normalize_phone(auth.admin_bypass_phone) if auth.admin_bypass_phone else ''
        if not bypass_phone:
            env_phone = getattr(django_settings, 'ADMIN_BYPASS_PHONE', '') or ''
            bypass_phone = normalize_phone(env_phone) if env_phone else ''
        if user is None and phone == bypass_phone:
            user = User.objects.filter(phone=phone).first()
            if user is None:
                user = User.objects.create_user(phone=phone)

        if user is not None and is_admin_phone(phone):
            promote_to_admin(user)

        if user is None or not user.is_active:
            raise serializers.ValidationError({'detail': 'شماره موبایل یا رمز عبور اشتباه است'})

        attrs['user'] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'phone', 'first_name', 'last_name', 'full_name', 'email',
                  'date_joined', 'is_staff', 'is_superuser']
        read_only_fields = ['id', 'phone', 'date_joined', 'is_staff', 'is_superuser']


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


class DeviceLoginSerializer(serializers.Serializer):
    device_id = serializers.UUIDField()
    device_token = serializers.CharField(max_length=200, trim_whitespace=False)


class TrustedDeviceSerializer(serializers.ModelSerializer):
    is_current = serializers.SerializerMethodField()

    class Meta:
        model = TrustedDevice
        fields = ['id', 'name', 'ip_address', 'created_at', 'last_used_at', 'expires_at', 'is_current']

    def get_is_current(self, obj):
        return str(obj.id) == str(self.context.get('current_device_id') or '')


class EpochTokenRefreshSerializer(TokenRefreshSerializer):
    """Refuses a refresh token that predates the user's last session revocation.

    Without this the endpoint would happily mint an access token that every
    view then rejects, so the client would burn a retry before falling back to
    its remembered device.
    """

    def validate(self, attrs):
        token = RefreshToken(attrs['refresh'])
        user = User.objects.filter(pk=token.get('user_id')).only('session_epoch', 'is_active').first()
        epoch = token.get(SESSION_EPOCH_CLAIM)
        if user is None or not user.is_active or epoch is None or int(epoch) != user.session_epoch:
            raise InvalidToken('نشست شما باطل شده است. دوباره وارد شوید.')
        return super().validate(attrs)
