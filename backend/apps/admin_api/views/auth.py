from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import AuthAuditLog, AuthSettings
from apps.admin_api.permissions import IsStaff
from apps.admin_api.serializers import AdminAuthAuditLogSerializer, AdminAuthSettingsSerializer


class AdminAuthSettingsView(APIView):
    permission_classes = [IsStaff]

    def get(self, request):
        obj = AuthSettings.get_settings()
        return Response(AdminAuthSettingsSerializer(obj).data)

    def patch(self, request):
        obj = AuthSettings.get_settings()
        serializer = AdminAuthSettingsSerializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class AdminAuthAuditLogListView(generics.ListAPIView):
    permission_classes = [IsStaff]
    serializer_class = AdminAuthAuditLogSerializer

    def get_queryset(self):
        qs = AuthAuditLog.objects.select_related('user').all()
        phone = self.request.query_params.get('phone')
        action = self.request.query_params.get('action')
        if phone:
            qs = qs.filter(phone__contains=phone)
        if action:
            qs = qs.filter(action=action)
        return qs
