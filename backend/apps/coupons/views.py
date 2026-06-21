from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status

from .models import Coupon
from .services import apply_coupon, validate_coupon


class ValidateCouponSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=50)
    subtotal = serializers.IntegerField(min_value=0)


class ValidateCouponView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ValidateCouponSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data['code']
        subtotal = serializer.validated_data['subtotal']

        coupon, error = validate_coupon(code, request.user, subtotal)
        if error:
            return Response({'detail': error, 'valid': False}, status=status.HTTP_400_BAD_REQUEST)

        discount_amount, free_shipping = apply_coupon(coupon, subtotal)
        return Response({
            'valid': True,
            'code': coupon.code,
            'coupon_type': coupon.coupon_type,
            'discount_amount': discount_amount,
            'free_shipping': free_shipping,
        })
