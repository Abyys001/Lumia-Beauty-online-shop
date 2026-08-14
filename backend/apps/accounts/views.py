import logging

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AuthAuditLog
from .serializers import LoginSerializer, RegisterSerializer, UserSerializer
from .services.audit import AuthAuditService
from .services.tokens import issue_tokens

logger = logging.getLogger('accounts.auth')


def _client_ip(request) -> str | None:
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def _auth_response(request, user, created: bool = False) -> Response:
    tokens = issue_tokens(user)
    data = {
        'access': tokens['access'],
        'refresh': tokens['refresh'],
        'user': UserSerializer(user).data,
    }
    AuthAuditService.log(
        AuthAuditLog.ACTION_LOGIN_SUCCESS,
        phone=user.phone,
        user=user,
        ip_address=_client_ip(request),
        metadata={'method': 'password', 'new_user': created},
    )
    return Response(data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return _auth_response(request, user, created=True)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        return _auth_response(request, user)


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
