from rest_framework import serializers

from apps.accounts.utils.encryption import API_KEY_MASK, encrypt_value, mask_secret
from apps.payments.models import Payment, PaymentLog, Refund, ZarinpalSettings
from apps.payments.zarinpal.config import ZarinpalConfigService


class PaymentRequestSerializer(serializers.Serializer):
    order_number = serializers.CharField(max_length=20)


class AdminPaymentLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentLog
        fields = ['id', 'action', 'request_data', 'response_data', 'created_at']


class AdminRefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Refund
        fields = [
            'id', 'amount', 'method', 'reason', 'status',
            'gateway_refund_id', 'created_at', 'updated_at',
        ]


class AdminPaymentSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    logs = AdminPaymentLogSerializer(many=True, read_only=True)
    refunds = AdminRefundSerializer(many=True, read_only=True)
    is_recent = serializers.BooleanField(read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'order_number', 'amount', 'authority', 'ref_id', 'session_id',
            'card_pan', 'fee', 'fee_type', 'error_code', 'status',
            'created_at', 'paid_at', 'is_recent', 'logs', 'refunds',
        ]


class AdminRefundRequestSerializer(serializers.Serializer):
    amount = serializers.IntegerField(min_value=10000, required=False)
    method = serializers.ChoiceField(
        choices=['instant', 'reverse', 'card', 'paya'],
        default='instant',
    )
    reason = serializers.CharField(max_length=100, default='CUSTOMER_REQUEST')


class AdminZarinpalSettingsSerializer(serializers.ModelSerializer):
    client_secret = serializers.CharField(write_only=True, required=False, allow_blank=True)
    client_secret_masked = serializers.SerializerMethodField()
    callback_url_resolved = serializers.SerializerMethodField()
    token_valid = serializers.SerializerMethodField()

    class Meta:
        model = ZarinpalSettings
        fields = [
            'merchant_id', 'is_sandbox', 'is_mock', 'callback_url', 'callback_url_resolved',
            'currency', 'client_id', 'client_secret', 'client_secret_masked',
            'terminal_id', 'auto_reconcile', 'max_retry_attempts', 'enable_api_logging',
            'token_valid', 'token_expires_at', 'updated_at',
        ]
        read_only_fields = ['token_expires_at', 'updated_at']

    def get_client_secret_masked(self, obj):
        if obj.client_secret_encrypted:
            return API_KEY_MASK
        env = ZarinpalConfigService.resolve_client_secret()
        return mask_secret(env) if env else ''

    def get_callback_url_resolved(self, obj):
        return ZarinpalConfigService.resolve_callback_url()

    def get_token_valid(self, obj):
        from django.utils import timezone
        if not obj.token_expires_at:
            return False
        return obj.token_expires_at > timezone.now()

    def update(self, instance, validated_data):
        secret = validated_data.pop('client_secret', None)
        if secret:
            instance.client_secret_encrypted = encrypt_value(secret)
        return super().update(instance, validated_data)
