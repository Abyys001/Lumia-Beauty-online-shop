from django.conf import settings
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .otp import check_otp_rate_limit, generate_otp_code, store_otp, verify_otp
from .serializers import OTPRequestSerializer, OTPVerifySerializer, UserSerializer
from .services import KavenegarService


class OTPRequestView(APIView):
    def post(self, request):
        serializer = OTPRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone']

        if not check_otp_rate_limit(phone):
            return Response(
                {'detail': 'تعداد درخواست‌ها بیش از حد مجاز است. لطفاً چند دقیقه صبر کنید.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        code = generate_otp_code()
        store_otp(phone, code)
        sent = KavenegarService.send_otp(phone, code)

        response_data = {'detail': 'کد تأیید ارسال شد'}
        if settings.DEBUG:
            response_data['debug_code'] = code

        if not sent and not settings.DEBUG:
            return Response({'detail': 'خطا در ارسال پیامک'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        return Response(response_data)


class OTPVerifyView(APIView):
    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone']
        code = serializer.validated_data['code']

        if not verify_otp(phone, code):
            return Response({'detail': 'کد تأیید نامعتبر یا منقضی شده است'}, status=status.HTTP_400_BAD_REQUEST)

        user, _ = User.objects.get_or_create(phone=phone)
        refresh = RefreshToken.for_user(user)

        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data,
        })


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
