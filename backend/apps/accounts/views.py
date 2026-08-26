import logging

from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AuthAuditLog, AuthSettings, TrustedDevice
from .serializers import (
    ChangePasswordSerializer,
    DeviceLoginSerializer,
    LoginSerializer,
    RegisterSerializer,
    TrustedDeviceSerializer,
    UserSerializer,
)
from .services.audit import AuthAuditService
from .services.devices import resolve_device, rotate_device, trust_device
from .services.tokens import issue_tokens

logger = logging.getLogger('accounts.auth')


def _client_ip(request) -> str | None:
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def _user_agent(request) -> str:
    return request.META.get('HTTP_USER_AGENT', '')


def _device_payload(device, raw_token: str) -> dict:
    return {
        'id': str(device.id),
        'token': raw_token,
        'name': device.name,
        'expires_at': device.expires_at,
    }


def _auth_response(request, user, *, created: bool = False, method: str = 'password',
                   remember: bool = False, device_name: str = '') -> Response:
    tokens = issue_tokens(user)
    data = {
        'access': tokens['access'],
        'refresh': tokens['refresh'],
        'user': UserSerializer(user).data,
        'device': None,
    }
    if remember:
        issued = trust_device(
            user,
            name=device_name,
            user_agent=_user_agent(request),
            ip_address=_client_ip(request),
        )
        data['device'] = _device_payload(issued['device'], issued['token'])

    AuthAuditService.log(
        AuthAuditLog.ACTION_LOGIN_SUCCESS,
        phone=user.phone,
        user=user,
        ip_address=_client_ip(request),
        metadata={'method': method, 'new_user': created, 'remembered': remember},
    )
    return Response(data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return _auth_response(
            request, user, created=True,
            remember=serializer.validated_data.get('remember_device', True),
            device_name=serializer.validated_data.get('device_name', ''),
        )


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        return _auth_response(
            request, user,
            remember=serializer.validated_data.get('remember_device', True),
            device_name=serializer.validated_data.get('device_name', ''),
        )


class DeviceLoginView(APIView):
    """Silent sign-in from a remembered browser — no password, no prompt.

    The secret is single-use: every success hands back a replacement that the
    client must store, so a copied token stops working the moment the real
    device comes back (see `resolve_device`).
    """

    permission_classes = [permissions.AllowAny]
    throttle_scope = 'device_login'

    def post(self, request):
        serializer = DeviceLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ip = _client_ip(request)
        device = resolve_device(
            serializer.validated_data['device_id'],
            serializer.validated_data['device_token'],
            ip_address=ip,
        )
        if device is None:
            AuthAuditService.log(
                AuthAuditLog.ACTION_LOGIN_BLOCKED,
                ip_address=ip,
                metadata={'method': 'device', 'device_id': str(serializer.validated_data['device_id'])},
            )
            return Response(
                {'detail': 'این دستگاه دیگر معتبر نیست. لطفاً دوباره وارد شوید.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        raw_token = rotate_device(device, user_agent=_user_agent(request), ip_address=ip)
        tokens = issue_tokens(device.user)
        AuthAuditService.log(
            AuthAuditLog.ACTION_DEVICE_LOGIN,
            phone=device.user.phone, user=device.user, ip_address=ip,
            metadata={'device_id': str(device.id)},
        )
        return Response({
            'access': tokens['access'],
            'refresh': tokens['refresh'],
            'user': UserSerializer(device.user).data,
            'device': _device_payload(device, raw_token),
        })


class RememberDevicePolicyView(APIView):
    """Lets the sign-in form show the checkbox pre-ticked the way the store wants."""

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        auth = AuthSettings.get_settings()
        return Response({
            'remember_device_default': auth.remember_device_default,
            'trusted_device_lifetime_days': auth.trusted_device_lifetime_days,
        })


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        device_id = request.data.get('device_id')
        everywhere = bool(request.data.get('everywhere'))
        if everywhere:
            request.user.revoke_sessions()
        elif device_id:
            TrustedDevice.objects.filter(user=request.user, id=device_id, revoked_at__isnull=True).update(
                revoked_at=timezone.now(),
            )
        AuthAuditService.log(
            AuthAuditLog.ACTION_LOGOUT,
            phone=request.user.phone, user=request.user, ip_address=_client_ip(request),
            metadata={'everywhere': everywhere},
        )
        return Response({'detail': 'خارج شدید'})


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save(update_fields=['password'])
        # Everything issued under the old password dies; this browser is handed a
        # fresh pair (and a fresh device secret if it was a remembered one).
        user.revoke_sessions()
        AuthAuditService.log(
            AuthAuditLog.ACTION_PASSWORD_CHANGED,
            phone=user.phone,
            user=user,
            ip_address=_client_ip(request),
            metadata={'method': 'self_change'},
        )
        remember = bool(request.data.get('remember_device'))
        tokens = issue_tokens(user)
        payload = {'detail': 'رمز عبور با موفقیت تغییر کرد', **tokens, 'device': None}
        if remember:
            issued = trust_device(user, user_agent=_user_agent(request), ip_address=_client_ip(request))
            payload['device'] = _device_payload(issued['device'], issued['token'])
        return Response(payload)


class TrustedDeviceListView(generics.ListAPIView):
    serializer_class = TrustedDeviceSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return self.request.user.trusted_devices.filter(revoked_at__isnull=True)

    def get_serializer_context(self):
        return {**super().get_serializer_context(),
                'current_device_id': self.request.query_params.get('current')}


class TrustedDeviceDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        device = TrustedDevice.objects.filter(user=request.user, id=pk).first()
        if device is None:
            return Response({'detail': 'دستگاه یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
        device.revoke()
        AuthAuditService.log(
            AuthAuditLog.ACTION_DEVICE_REVOKED,
            phone=request.user.phone, user=request.user, ip_address=_client_ip(request),
            metadata={'device_id': str(device.id), 'by': 'self'},
        )
        return Response(status=status.HTTP_204_NO_CONTENT)
