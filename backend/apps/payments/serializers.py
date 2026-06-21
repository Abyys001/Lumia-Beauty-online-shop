from rest_framework import serializers


class PaymentRequestSerializer(serializers.Serializer):
    order_number = serializers.CharField(max_length=20)
