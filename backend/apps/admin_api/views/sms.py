from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import (
    AuthAuditLog,
    AuthSettings,
    OtpSettings,
    OtpTemplate,
    SmsLog,
    SmsProviderSettings,
)
from apps.accounts.services.sms_config import SmsConfigService
from apps.accounts.sms import get_sms_provider
from apps.accounts.sms.smsir import SmsIrProvider
from apps.accounts.utils.encryption import API_KEY_MASK, decrypt_value, mask_secret
from apps.admin_api.permissions import IsStaff
from apps.admin_api.serializers import (
    AdminAuthAuditLogSerializer,
    AdminAuthSettingsSerializer,
    AdminOtpSettingsSerializer,
    AdminOtpTemplateSerializer,
    AdminSmsLogSerializer,
    AdminSmsProviderSettingsSerializer,
)


class AdminSmsProviderView(APIView):
    permission_classes = [IsStaff]

    def get(self, request):
        SmsConfigService.bootstrap_from_env()
        obj = SmsConfigService.get_provider_settings()
        data = AdminSmsProviderSettingsSerializer(obj).data
        if obj.api_key_encrypted:
            raw = decrypt_value(obj.api_key_encrypted)
            data['api_key'] = mask_secret(raw) if raw else ''
        else:
            data['api_key'] = ''
        return Response(data)

    def patch(self, request):
        obj = SmsConfigService.get_provider_settings()
        api_key = request.data.pop('api_key', None)
        serializer = AdminSmsProviderSettingsSerializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        if api_key is not None and api_key and api_key != API_KEY_MASK and not api_key.startswith('*'):
            SmsConfigService.set_api_key(api_key)
        return self.get(request)


class AdminSmsProviderTestView(APIView):
    permission_classes = [IsStaff]

    def post(self, request):
        provider = get_sms_provider()
        if isinstance(provider, SmsIrProvider):
            result = provider.test_connection()
            obj = SmsConfigService.get_provider_settings()
            obj.last_test_at = timezone.now()
            if result.success:
                obj.last_test_status = SmsProviderSettings.TEST_OK
                obj.last_test_message = f"Credit: {result.provider_response.get('credit', 'N/A')}"
            else:
                obj.last_test_status = SmsProviderSettings.TEST_FAILED
                obj.last_test_message = result.error or 'Connection failed'
            obj.save(update_fields=['last_test_at', 'last_test_status', 'last_test_message', 'updated_at'])
            return Response({
                'success': result.success,
                'message': obj.last_test_message,
                'response': result.provider_response,
            }, status=status.HTTP_200_OK if result.success else status.HTTP_400_BAD_REQUEST)
        return Response({'success': True, 'message': 'Mock provider active — no external connection needed'})


class AdminSmsProviderStatusView(APIView):
    permission_classes = [IsStaff]

    def get(self, request):
        SmsConfigService.bootstrap_from_env()
        obj = SmsConfigService.get_provider_settings()
        provider = get_sms_provider()
        credit = None
        if isinstance(provider, SmsIrProvider):
            credit = provider.get_credit()
        return Response({
            'provider_mode': obj.provider_mode,
            'is_active': obj.is_active,
            'is_sandbox': obj.is_sandbox,
            'has_api_key': bool(SmsConfigService.resolve_api_key()),
            'last_test_at': obj.last_test_at,
            'last_test_status': obj.last_test_status,
            'last_test_message': obj.last_test_message,
            'credit': credit,
            'runtime_provider': 'smsir' if isinstance(provider, SmsIrProvider) else 'mock',
        })


class AdminOtpTemplateListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsStaff]
    serializer_class = AdminOtpTemplateSerializer
    queryset = OtpTemplate.objects.all()


class AdminOtpTemplateDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsStaff]
    serializer_class = AdminOtpTemplateSerializer
    queryset = OtpTemplate.objects.all()
    lookup_field = 'id'


class AdminOtpTemplateActivateView(APIView):
    permission_classes = [IsStaff]

    def post(self, request, id):
        template = OtpTemplate.objects.get(id=id)
        template.is_active = True
        template.save(update_fields=['is_active', 'updated_at'])
        return Response(AdminOtpTemplateSerializer(template).data)


class AdminOtpTemplateSetDefaultView(APIView):
    permission_classes = [IsStaff]

    def post(self, request, id):
        template = OtpTemplate.objects.get(id=id)
        template.is_default = True
        template.is_active = True
        template.save()
        return Response(AdminOtpTemplateSerializer(template).data)


class AdminOtpTemplatePreviewView(APIView):
    permission_classes = [IsStaff]

    def post(self, request):
        body = request.data.get('body_preview', '')
        param = request.data.get('parameter_name', 'Code')
        sample = request.data.get('sample_code', '123456')
        preview = body.replace(f'{{{param}}}', sample).replace('{Code}', sample).replace('{CODE}', sample)
        return Response({'preview': preview, 'sample_code': sample})


class AdminOtpSettingsView(APIView):
    permission_classes = [IsStaff]

    def get(self, request):
        obj = OtpSettings.get_settings()
        return Response(AdminOtpSettingsSerializer(obj).data)

    def patch(self, request):
        obj = OtpSettings.get_settings()
        serializer = AdminOtpSettingsSerializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


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


class AdminSmsLogListView(generics.ListAPIView):
    permission_classes = [IsStaff]
    serializer_class = AdminSmsLogSerializer

    def get_queryset(self):
        qs = SmsLog.objects.select_related('template').all()
        phone = self.request.query_params.get('phone')
        status_param = self.request.query_params.get('status')
        provider = self.request.query_params.get('provider')
        if phone:
            qs = qs.filter(phone__contains=phone)
        if status_param:
            qs = qs.filter(status=status_param)
        if provider:
            qs = qs.filter(provider=provider)
        return qs


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
