import logging

from django.conf import settings
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import OTPRequestSerializer, OTPVerifySerializer, UserSerializer
from .services.otp_service import OtpService

logger = logging.getLogger('accounts.otp')


def _client_ip(request) -> str | None:
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


class OTPRequestView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_scope = 'otp'

    def post(self, request):
        serializer = OTPRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone']
        ip = _client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        result = OtpService.request_otp(phone, ip_address=ip, user_agent=user_agent)

        if result.bypass_tokens and result.user:
            return Response({
                'access': result.bypass_tokens['access'],
                'refresh': result.bypass_tokens['refresh'],
                'user': UserSerializer(result.user).data,
            })

        if not result.success:
            return Response({'detail': result.detail}, status=result.status_code)

        response_data = {'detail': result.detail}
        if result.debug_code:
            response_data['debug_code'] = result.debug_code

        return Response(response_data)


class OTPVerifyView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_scope = 'otp'

    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone']
        code = serializer.validated_data['code']
        ip = _client_ip(request)

        result = OtpService.verify_otp(phone, code, ip_address=ip)

        if not result.success:
            return Response({'detail': result.detail}, status=result.status_code)

        return Response({
            'access': result.tokens['access'],
            'refresh': result.tokens['refresh'],
            'user': UserSerializer(result.user).data,
        })


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
