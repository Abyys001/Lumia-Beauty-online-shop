from django.db.models import ProtectedError
from django.utils import timezone
from rest_framework import filters, generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import AuthAuditLog, TrustedDevice, User
from ..permissions import IsStaff, IsSuperUser
from ..serializers import (
    AdminSetPasswordSerializer,
    AdminTrustedDeviceSerializer,
    AdminUserCreateSerializer,
    AdminUserListSerializer,
    AdminUserRoleSerializer,
    AdminUserSerializer,
)
from ..services import audit_actor
from ..services.users import (
    assert_can_manage,
    assert_not_self,
    assert_role_change_sticks,
    assert_superuser_remains,
)


def _client_ip(request) -> str | None:
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def _base_queryset():
    return User.objects.prefetch_related('addresses', 'trusted_devices')


class AdminUserListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsStaff]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['phone', 'first_name', 'last_name', 'email']
    ordering_fields = ['date_joined', 'phone', 'last_login']
    ordering = ['-date_joined']

    def get_serializer_class(self):
        return AdminUserCreateSerializer if self.request.method == 'POST' else AdminUserListSerializer

    def get_queryset(self):
        qs = _base_queryset().order_by('-date_joined')
        role = self.request.query_params.get('role')
        if role == 'staff':
            qs = qs.filter(is_staff=True)
        elif role == 'customer':
            qs = qs.filter(is_staff=False)
        is_active = self.request.query_params.get('is_active')
        if is_active in ('true', 'false'):
            qs = qs.filter(is_active=(is_active == 'true'))
        return qs

    def perform_create(self, serializer):
        wants_admin = serializer.validated_data.get('is_staff') or serializer.validated_data.get('is_superuser')
        if wants_admin and not self.request.user.is_superuser:
            raise ValidationError({'detail': 'فقط مدیر ارشد می‌تواند کاربر ادمین بسازد.'})
        user = serializer.save()
        audit_actor(
            AuthAuditLog.ACTION_ROLE_CHANGED, self.request.user, user, _client_ip(self.request),
            extra={'created': True, 'is_staff': user.is_staff, 'is_superuser': user.is_superuser},
        )


class AdminUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsStaff]
    serializer_class = AdminUserSerializer
    lookup_field = 'id'

    def get_queryset(self):
        return _base_queryset()

    def perform_update(self, serializer):
        target = serializer.instance
        assert_can_manage(self.request.user, target)
        if serializer.validated_data.get('is_active') is False:
            assert_not_self(self.request.user, target, 'نمی‌توانید حساب خودتان را غیرفعال کنید.')
            assert_superuser_remains(target, losing_superuser=True)
        user = serializer.save()
        if user.is_active is False:
            # A deactivated account must stop working immediately, not at token expiry.
            user.revoke_sessions()

    def perform_destroy(self, instance):
        if not self.request.user.is_superuser:
            raise ValidationError({'detail': 'فقط مدیر ارشد می‌تواند کاربر را حذف کند.'})
        assert_not_self(self.request.user, instance, 'نمی‌توانید حساب خودتان را حذف کنید.')
        assert_superuser_remains(instance, losing_superuser=True)
        # Logged before the row goes, so the audit trail survives the delete.
        audit_actor(
            AuthAuditLog.ACTION_ROLE_CHANGED, self.request.user, instance, _client_ip(self.request),
            extra={'deleted': True},
        )
        try:
            instance.delete()
        except ProtectedError:
            raise ValidationError({'detail': (
                'این کاربر سفارش ثبت‌شده دارد و برای حفظ سوابق مالی حذف نمی‌شود. '
                'به‌جای آن حسابش را غیرفعال کنید.'
            )})


class AdminUserSetPasswordView(APIView):
    """Reset a customer's password when they call the shop — no old password needed."""

    permission_classes = [IsStaff]

    def post(self, request, id):
        target = generics.get_object_or_404(User, id=id)
        assert_can_manage(request.user, target)
        serializer = AdminSetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        target.set_password(serializer.validated_data['password'])
        target.save(update_fields=['password'])
        if serializer.validated_data['revoke_sessions']:
            target.revoke_sessions()

        audit_actor(
            AuthAuditLog.ACTION_ADMIN_PASSWORD_SET, request.user, target, _client_ip(request),
            extra={'revoked_sessions': serializer.validated_data['revoke_sessions']},
        )
        return Response({'detail': f'رمز عبور {target.full_name} تغییر کرد.'})


class AdminUserRolesView(APIView):
    """Grant or take away dashboard access. Superuser-only, by design."""

    permission_classes = [IsSuperUser]

    def post(self, request, id):
        target = generics.get_object_or_404(User, id=id)
        serializer = AdminUserRoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        before = {'is_staff': target.is_staff, 'is_superuser': target.is_superuser}
        is_staff = serializer.validated_data.get('is_staff', target.is_staff)
        is_superuser = serializer.validated_data.get('is_superuser', target.is_superuser)
        # Superuser without staff cannot reach the dashboard at all — keep them paired.
        if is_superuser:
            is_staff = True

        if before == {'is_staff': is_staff, 'is_superuser': is_superuser}:
            return Response(AdminUserSerializer(target).data)

        if not is_staff or not is_superuser:
            assert_not_self(request.user, target, 'نمی‌توانید دسترسی خودتان را کم کنید.')
        assert_superuser_remains(target, losing_superuser=not is_superuser)
        assert_role_change_sticks(target, is_staff=is_staff, is_superuser=is_superuser)

        target.is_staff = is_staff
        target.is_superuser = is_superuser
        target.save(update_fields=['is_staff', 'is_superuser'])
        # Permissions live in the token's user lookup, but a demoted admin should
        # lose the dashboard on their next request, not whenever they log out.
        target.revoke_sessions(keep_devices=True)

        audit_actor(
            AuthAuditLog.ACTION_ROLE_CHANGED, request.user, target, _client_ip(request),
            extra={'before': before, 'after': {'is_staff': is_staff, 'is_superuser': is_superuser}},
        )
        return Response(AdminUserSerializer(target).data)


class AdminUserRevokeSessionsView(APIView):
    """Sign a user out of every browser — tokens and remembered devices alike."""

    permission_classes = [IsStaff]

    def post(self, request, id):
        target = generics.get_object_or_404(User, id=id)
        assert_can_manage(request.user, target)
        keep_devices = bool(request.data.get('keep_devices'))
        target.revoke_sessions(keep_devices=keep_devices)
        audit_actor(
            AuthAuditLog.ACTION_SESSIONS_REVOKED, request.user, target, _client_ip(request),
            extra={'keep_devices': keep_devices},
        )
        return Response({'detail': f'همه‌ی نشست‌های {target.full_name} باطل شد.'})


class AdminUserDeviceView(APIView):
    """The remembered browsers behind a user's auto-login, and a way to drop them."""

    permission_classes = [IsStaff]

    def get(self, request, id):
        target = generics.get_object_or_404(User, id=id)
        assert_can_manage(request.user, target)
        devices = target.trusted_devices.filter(revoked_at__isnull=True)
        return Response(AdminTrustedDeviceSerializer(devices, many=True).data)

    def delete(self, request, id, device_id=None):
        target = generics.get_object_or_404(User, id=id)
        assert_can_manage(request.user, target)
        devices = TrustedDevice.objects.filter(user=target, revoked_at__isnull=True)
        if device_id is not None:
            devices = devices.filter(id=device_id)
        count = devices.update(revoked_at=timezone.now())
        audit_actor(
            AuthAuditLog.ACTION_DEVICE_REVOKED, request.user, target, _client_ip(request),
            extra={'device_id': str(device_id) if device_id else 'all', 'count': count},
        )
        return Response(status=status.HTTP_204_NO_CONTENT)
