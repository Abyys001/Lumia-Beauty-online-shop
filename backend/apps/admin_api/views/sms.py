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

from apps.accounts.services.sms_sync import sync_default_template_for_mode, sync_iranpayamak_default_template

from apps.accounts.sms import get_sms_provider

from apps.accounts.sms.iranpayamak import IranPayamakProvider, get_iranpayamak_client, validate_iranpayamak_api_key

from apps.accounts.sms.iranpayamak_utils import map_iranpayamak_error

from apps.accounts.sms.smsir import SmsIrProvider, validate_sms_ir_api_key

from apps.accounts.utils.encryption import API_KEY_MASK

from apps.admin_api.permissions import IsStaff

from apps.admin_api.serializers import (

    AdminAuthAuditLogSerializer,

    AdminAuthSettingsSerializer,

    AdminOtpSettingsSerializer,

    AdminOtpTemplateSerializer,

    AdminSmsLogSerializer,

    AdminSmsProviderSettingsSerializer,

)





def _is_masked_key(value: str) -> bool:

    cleaned = str(value).strip()

    return not cleaned or cleaned == API_KEY_MASK or cleaned.startswith('*')





def _provider_response_data(obj: SmsProviderSettings) -> dict:

    data = AdminSmsProviderSettingsSerializer(obj).data

    data['api_key'] = SmsConfigService.mask_api_key(obj.api_key_encrypted)

    data['sandbox_api_key'] = SmsConfigService.mask_api_key(obj.sandbox_api_key_encrypted)

    data['panel_password'] = SmsConfigService.mask_panel_password(obj.panel_password_encrypted)

    data['has_bearer_token'] = bool(SmsConfigService.resolve_bearer_token())

    return data





def _default_base_url(provider_mode: str) -> str:

    if provider_mode == SmsProviderSettings.PROVIDER_IRANPAYAMAK:

        return 'https://api.iranpayamak.com'

    return 'https://api.sms.ir/v1'





def _apply_provider_settings(request, *, validate_keys: bool = True) -> Response | None:

    """Persist provider settings from request body. Returns error Response or None."""

    obj = SmsConfigService.get_provider_settings()

    data = dict(request.data)

    api_key = data.pop('api_key', None)

    sandbox_api_key = data.pop('sandbox_api_key', None)

    panel_password = data.pop('panel_password', None)

    was_sandbox = obj.is_sandbox

    new_mode = data.get('provider_mode', obj.provider_mode)



    serializer = AdminSmsProviderSettingsSerializer(obj, data=data, partial=True)

    serializer.is_valid(raise_exception=True)

    serializer.save()



    if new_mode == SmsProviderSettings.PROVIDER_IRANPAYAMAK:

        obj.base_url = _default_base_url(SmsProviderSettings.PROVIDER_IRANPAYAMAK)

        obj.save(update_fields=['base_url', 'updated_at'])
        sync_iranpayamak_default_template()

    elif new_mode == SmsProviderSettings.PROVIDER_SMSIR and (

        not obj.base_url or 'iranpayamak' in obj.base_url

    ):

        obj.base_url = _default_base_url(SmsProviderSettings.PROVIDER_SMSIR)

        obj.save(update_fields=['base_url', 'updated_at'])



    base_url = obj.base_url or _default_base_url(obj.provider_mode)



    if api_key is not None and not _is_masked_key(str(api_key)):

        cleaned = str(api_key).strip()

        if validate_keys:

            if obj.provider_mode == SmsProviderSettings.PROVIDER_IRANPAYAMAK:

                _, error = validate_iranpayamak_api_key(cleaned, base_url)

            else:

                _, error = validate_sms_ir_api_key(cleaned, base_url)

            if error:

                return Response({'message': error, 'field': 'api_key'}, status=status.HTTP_400_BAD_REQUEST)

        SmsConfigService.set_api_key(cleaned, sandbox=False)



    if sandbox_api_key is not None and not _is_masked_key(str(sandbox_api_key)):

        cleaned = str(sandbox_api_key).strip()

        if validate_keys and obj.provider_mode == SmsProviderSettings.PROVIDER_SMSIR:

            _, error = validate_sms_ir_api_key(cleaned, base_url)

            if error:

                return Response(

                    {'message': error, 'field': 'sandbox_api_key'},

                    status=status.HTTP_400_BAD_REQUEST,

                )

        if obj.provider_mode == SmsProviderSettings.PROVIDER_SMSIR:

            SmsConfigService.set_api_key(cleaned, sandbox=True)



    if panel_password is not None and not _is_masked_key(str(panel_password)):

        SmsConfigService.set_panel_password(str(panel_password).strip())



    obj.refresh_from_db()



    if obj.provider_mode == SmsProviderSettings.PROVIDER_IRANPAYAMAK and obj.is_active:
        if not (obj.line_number or '').strip():
            return Response(
                {'message': 'شماره خط IranPayamak الزامی است', 'field': 'line_number'},
                status=status.HTTP_400_BAD_REQUEST,
            )

    if obj.is_sandbox != was_sandbox and obj.provider_mode == SmsProviderSettings.PROVIDER_SMSIR:

        sync_default_template_for_mode(obj.is_sandbox)



    return None





def _runtime_provider_name(provider) -> str:

    if isinstance(provider, SmsIrProvider):

        return 'smsir'

    if isinstance(provider, IranPayamakProvider):

        return 'iranpayamak'

    return 'mock'





class AdminSmsProviderView(APIView):

    permission_classes = [IsStaff]



    def get(self, request):

        SmsConfigService.bootstrap_from_env()

        obj = SmsConfigService.get_provider_settings()

        return Response(_provider_response_data(obj))



    def patch(self, request):

        error_response = _apply_provider_settings(request, validate_keys=True)

        if error_response:

            return error_response

        return self.get(request)





class AdminSmsProviderTestView(APIView):

    permission_classes = [IsStaff]



    def post(self, request):

        error_response = _apply_provider_settings(request, validate_keys=False)

        if error_response:

            return error_response



        provider = get_sms_provider()

        if isinstance(provider, (SmsIrProvider, IranPayamakProvider)):

            result = provider.test_connection()

            obj = SmsConfigService.get_provider_settings()

            obj.last_test_at = timezone.now()

            if result.success:

                obj.last_test_status = SmsProviderSettings.TEST_OK

                credit = result.provider_response.get('credit', 'N/A')

                obj.last_test_message = f'Credit: {credit}'

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

        balance_count = None

        balance_details = None

        if isinstance(provider, SmsIrProvider):

            credit, _ = provider.get_credit()

        elif isinstance(provider, IranPayamakProvider):

            credit, _ = provider.get_credit()

            details, _ = provider.get_balance_details()

            if details:

                balance_count = details.get('balanceCount')

                balance_details = details.get('details')



        has_api_key = bool(

            SmsConfigService.resolve_api_key()

            if obj.provider_mode == SmsProviderSettings.PROVIDER_SMSIR

            else SmsConfigService.resolve_iranpayamak_api_key()

        )



        return Response({

            'provider_mode': obj.provider_mode,

            'is_active': obj.is_active,

            'is_sandbox': obj.is_sandbox,

            'has_api_key': has_api_key,

            'has_production_api_key': bool(SmsConfigService.resolve_api_key(sandbox=False)),

            'has_sandbox_api_key': bool(SmsConfigService.resolve_api_key(sandbox=True)),

            'has_bearer_token': bool(SmsConfigService.resolve_bearer_token()),

            'line_number': obj.line_number,

            'number_format': obj.number_format,

            'panel_username': obj.panel_username,

            'last_test_at': obj.last_test_at,

            'last_test_status': obj.last_test_status,

            'last_test_message': obj.last_test_message,

            'credit': credit,

            'balance_count': balance_count,

            'balance_details': balance_details,

            'runtime_provider': _runtime_provider_name(provider),

        })





class AdminSmsProviderLoginView(APIView):

    permission_classes = [IsStaff]



    def post(self, request):

        obj = SmsConfigService.get_provider_settings()

        if obj.provider_mode != SmsProviderSettings.PROVIDER_IRANPAYAMAK:

            return Response({'message': 'ورود پنل فقط برای IranPayamak است'}, status=status.HTTP_400_BAD_REQUEST)



        username = (request.data.get('username') or obj.panel_username or '').strip()

        password = (request.data.get('password') or '').strip()

        if not password:

            password = SmsConfigService.resolve_panel_password()

        if not username or not password:

            return Response({'message': 'نام کاربری و رمز عبور الزامی است'}, status=status.HTTP_400_BAD_REQUEST)



        client, err = _iranpayamak_login_client()

        if err:

            return err



        method = request.data.get('method')

        result = client.login(username, password, method=method)

        if not result.success:

            return Response({

                'success': False,

                'message': map_iranpayamak_error(result.message, result.http_status),

                'requires_2fa': result.http_status == 200 and bool(result.data),

            }, status=status.HTTP_400_BAD_REQUEST)



        data = result.data if isinstance(result.data, dict) else {}

        token = data.get('token') or data.get('access_token') or data.get('bearer_token')

        if token:

            SmsConfigService.cache_bearer_token(str(token))

            obj.panel_username = username

            if request.data.get('password'):

                SmsConfigService.set_panel_password(password)

            obj.save(update_fields=['panel_username', 'updated_at'])

            return Response({'success': True, 'message': 'ورود موفق — توکن Bearer ذخیره شد'})



        return Response({

            'success': True,

            'requires_2fa': True,

            'token': data.get('token') or result.raw.get('token'),

            'message': 'کد 2FA ارسال شد — verify-2fa را فراخوانی کنید',

            'data': data,

        })





class AdminSmsProviderVerify2faView(APIView):

    permission_classes = [IsStaff]



    def post(self, request):

        obj = SmsConfigService.get_provider_settings()

        if obj.provider_mode != SmsProviderSettings.PROVIDER_IRANPAYAMAK:

            return Response({'message': '2FA فقط برای IranPayamak است'}, status=status.HTTP_400_BAD_REQUEST)



        token = (request.data.get('token') or '').strip()

        code = (request.data.get('code') or '').strip()

        method = (request.data.get('method') or 'sms').strip()

        if not token or not code:

            return Response({'message': 'token و code الزامی است'}, status=status.HTTP_400_BAD_REQUEST)



        client, err = _iranpayamak_login_client()

        if err:

            return err



        result = client.verify_2fa(token, code, method=method)

        if not result.success:

            return Response({

                'success': False,

                'message': map_iranpayamak_error(result.message, result.http_status),

            }, status=status.HTTP_400_BAD_REQUEST)



        data = result.data if isinstance(result.data, dict) else {}

        bearer = data.get('token') or data.get('access_token') or data.get('bearer_token') or token

        SmsConfigService.cache_bearer_token(str(bearer))

        return Response({'success': True, 'message': '2FA تأیید شد — توکن Bearer ذخیره شد'})





def _iranpayamak_login_client():

    client = get_iranpayamak_client()

    if not client:

        return None, Response(

            {'message': 'کلید Api-Key IranPayamak تنظیم نشده است'},

            status=status.HTTP_400_BAD_REQUEST,

        )

    return client, None





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


