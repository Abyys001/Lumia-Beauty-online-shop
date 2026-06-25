import secrets

import string



from rest_framework import status

from rest_framework.response import Response

from rest_framework.views import APIView



from apps.accounts.models import SmsProviderSettings

from apps.accounts.services.sms_config import SmsConfigService

from apps.accounts.sms.iranpayamak import get_iranpayamak_client

from apps.accounts.sms.iranpayamak_utils import map_iranpayamak_error, to_ascii_digits

from apps.accounts.sms.smsir import get_sms_ir_client

from apps.accounts.sms.smsir_utils import map_delivery_state

from apps.admin_api.permissions import IsStaff





def _api_response(result, *, extra: dict | None = None) -> Response:

    body = {

        'success': result.success,

        'status': result.status,

        'message': result.message,

        'data': result.data,

        'error_hint': result.error_hint,

        'http_status': result.http_status,

        'raw': result.raw,

    }

    if extra:

        body.update(extra)

    code = status.HTTP_200_OK if result.success else status.HTTP_400_BAD_REQUEST

    return Response(body, status=code)





def _provider_mode() -> str:

    settings = SmsConfigService.get_provider_settings()

    return settings.provider_mode or SmsConfigService.resolve_provider_mode()





def _smsir_only_response() -> Response:

    return Response({

        'success': False,

        'message': 'این گزارش فقط برای SMS.ir در دسترس است',

        'error_hint': 'ارائه‌دهنده فعال را به SMS.ir تغییر دهید',

    }, status=status.HTTP_400_BAD_REQUEST)





def _smsir_client_or_error():

    client = get_sms_ir_client()

    if not client:

        return None, Response(

            {'success': False, 'message': 'کلید API تنظیم نشده است', 'error_hint': 'کلید API تنظیم نشده است'},

            status=status.HTTP_400_BAD_REQUEST,

        )

    return client, None





def _iranpayamak_client_or_error(*, with_bearer: bool = False):

    client = get_iranpayamak_client(with_bearer=with_bearer)

    if not client:

        return None, Response(

            {'success': False, 'message': 'کلید Api-Key IranPayamak تنظیم نشده است'},

            status=status.HTTP_400_BAD_REQUEST,

        )

    return client, None





class AdminSmsCreditView(APIView):

    permission_classes = [IsStaff]



    def get(self, request):

        settings = SmsConfigService.get_provider_settings()

        mode = _provider_mode()



        if mode == SmsProviderSettings.PROVIDER_IRANPAYAMAK:

            client, err = _iranpayamak_client_or_error()

            if err:

                return err

            result = client.get_balance()

            credit = None

            balance_count = None

            if result.success and isinstance(result.data, dict):

                credit = float(result.data.get('balanceAmount', 0))

                balance_count = result.data.get('balanceCount')

            return _api_response(result, extra={

                'credit': credit,

                'balance_count': balance_count,

                'balance_details': result.data if isinstance(result.data, dict) else None,

                'provider': 'iranpayamak',

            })



        client, err = _smsir_client_or_error()

        if err:

            return err

        result = client.get_credit()

        return _api_response(result, extra={

            'is_sandbox': settings.is_sandbox,

            'credit': float(result.data) if result.success and result.data is not None else None,

            'provider': 'smsir',

        })





class AdminSmsLinesView(APIView):

    permission_classes = [IsStaff]



    def get(self, request):

        settings = SmsConfigService.get_provider_settings()

        mode = _provider_mode()



        if mode == SmsProviderSettings.PROVIDER_IRANPAYAMAK:

            client, err = _iranpayamak_client_or_error(with_bearer=True)

            if err:

                return err

            if not SmsConfigService.resolve_bearer_token():

                return Response({

                    'success': False,

                    'message': 'برای دریافت خطوط ابتدا از پنل ادمین وارد شوید (Login + 2FA)',

                    'error_hint': 'Bearer token موجود نیست',

                }, status=status.HTTP_400_BAD_REQUEST)

            search = request.query_params.get('search', '')

            is_dedicated = request.query_params.get('is_dedicated')

            dedicated = None

            if is_dedicated is not None:

                dedicated = str(is_dedicated).lower() in ('1', 'true', 'yes')

            return _api_response(client.get_lines(search=search, is_dedicated=dedicated))



        if settings.is_sandbox:

            return Response({

                'success': False,

                'message': 'در محیط Sandbox گزارش خطوط ثبت نمی‌شود',

                'error_hint': 'Sandbox را خاموش کنید یا از محیط Production استفاده کنید',

            }, status=status.HTTP_400_BAD_REQUEST)

        client, err = _smsir_client_or_error()

        if err:

            return err

        return _api_response(client.get_line_numbers())





class AdminSmsTestVerifyView(APIView):

    permission_classes = [IsStaff]



    def post(self, request):

        settings = SmsConfigService.get_provider_settings()

        mode = _provider_mode()

        phone = request.data.get('phone', '')

        code = to_ascii_digits(str(request.data.get('code') or ''))

        if not code:

            code = ''.join(secrets.choice(string.digits) for _ in range(6))



        template = SmsConfigService.get_default_template()

        if not template:

            return Response({'success': False, 'message': 'قالب OTP فعال یافت نشد'}, status=status.HTTP_400_BAD_REQUEST)



        if mode == SmsProviderSettings.PROVIDER_IRANPAYAMAK:

            client, err = _iranpayamak_client_or_error()

            if err:

                return err

            pattern_code = (template.pattern_code or '').strip()

            line_number = (settings.line_number or '').strip()

            if not pattern_code:

                return Response({'success': False, 'message': 'کد Pattern در قالب تنظیم نشده'}, status=status.HTTP_400_BAD_REQUEST)

            if not line_number:

                return Response({'success': False, 'message': 'شماره خط IranPayamak تنظیم نشده'}, status=status.HTTP_400_BAD_REQUEST)

            param_name = (template.parameter_name or 'CODE').strip()

            result, payload = client.send_pattern(

                pattern_code,

                phone,

                line_number,

                {param_name: code},

                settings.number_format,

            )

            return Response({

                'success': result.success,

                'status': result.status,

                'message': result.message,

                'data': result.data,

                'error_hint': result.error_hint,

                'payload': payload,

                'pattern_code': pattern_code,

                'code_used': code,

                'provider': 'iranpayamak',

            }, status=status.HTTP_200_OK if result.success else status.HTTP_400_BAD_REQUEST)



        if settings.is_sandbox and template.sms_ir_template_id != 123456:

            return Response({

                'success': False,

                'message': 'در Sandbox فقط قالب 123456 مجاز است',

            }, status=status.HTTP_400_BAD_REQUEST)



        client, err = _smsir_client_or_error()

        if err:

            return err



        param_name = (template.parameter_name or 'Code').strip('#')

        result, payload = client.send_verify(

            phone,

            int(template.sms_ir_template_id),

            [{'name': param_name, 'value': code}],

        )

        return Response({

            'success': result.success,

            'status': result.status,

            'message': result.message,

            'data': result.data,

            'error_hint': result.error_hint,

            'payload': payload,

            'is_sandbox': settings.is_sandbox,

            'template_id': template.sms_ir_template_id,

            'code_used': code,

            'provider': 'smsir',

        }, status=status.HTTP_200_OK if result.success else status.HTTP_400_BAD_REQUEST)





class AdminSmsMessageReportView(APIView):

    permission_classes = [IsStaff]



    def get(self, request, message_id):

        settings = SmsConfigService.get_provider_settings()

        if _provider_mode() != SmsProviderSettings.PROVIDER_SMSIR:

            return _smsir_only_response()

        if settings.is_sandbox:

            return Response({

                'success': False,

                'message': 'در Sandbox گزارش پیامک ثبت نمی‌شود',

                'error_hint': 'گزارش فقط در Production در دسترس است',

            }, status=status.HTTP_400_BAD_REQUEST)

        client, err = _smsir_client_or_error()

        if err:

            return err

        result = client.get_message_report(message_id)

        extra = {}

        if result.success and isinstance(result.data, dict):

            ds = result.data.get('deliveryState')

            extra['delivery_state_label'] = map_delivery_state(ds)

        return _api_response(result, extra=extra)





class AdminSmsSendPacksView(APIView):

    permission_classes = [IsStaff]



    def get(self, request):

        if _provider_mode() != SmsProviderSettings.PROVIDER_SMSIR:

            return _smsir_only_response()

        settings = SmsConfigService.get_provider_settings()

        if settings.is_sandbox:

            return Response({

                'success': False,

                'message': 'در Sandbox گزارش بسته‌ها ثبت نمی‌شود',

            }, status=status.HTTP_400_BAD_REQUEST)

        client, err = _smsir_client_or_error()

        if err:

            return err

        page = int(request.query_params.get('page', 1))

        size = int(request.query_params.get('page_size', 100))

        return _api_response(client.get_send_packs(page, size))





class AdminSmsPackDetailView(APIView):

    permission_classes = [IsStaff]



    def get(self, request, pack_id):

        if _provider_mode() != SmsProviderSettings.PROVIDER_SMSIR:

            return _smsir_only_response()

        settings = SmsConfigService.get_provider_settings()

        if settings.is_sandbox:

            return Response({

                'success': False,

                'message': 'در Sandbox گزارش بسته‌ها ثبت نمی‌شود',

            }, status=status.HTTP_400_BAD_REQUEST)

        client, err = _smsir_client_or_error()

        if err:

            return err

        return _api_response(client.get_pack_detail(pack_id))





class AdminSmsLiveReportView(APIView):

    permission_classes = [IsStaff]



    def get(self, request):

        if _provider_mode() != SmsProviderSettings.PROVIDER_SMSIR:

            return _smsir_only_response()

        settings = SmsConfigService.get_provider_settings()

        if settings.is_sandbox:

            return Response({

                'success': False,

                'message': 'در Sandbox گزارش live ثبت نمی‌شود',

            }, status=status.HTTP_400_BAD_REQUEST)

        client, err = _smsir_client_or_error()

        if err:

            return err

        page = int(request.query_params.get('page', 1))

        size = int(request.query_params.get('page_size', 100))

        return _api_response(client.get_live_sends(page, size))





class AdminSmsReceiveLatestView(APIView):

    permission_classes = [IsStaff]



    def get(self, request):

        if _provider_mode() != SmsProviderSettings.PROVIDER_SMSIR:

            return _smsir_only_response()

        settings = SmsConfigService.get_provider_settings()

        if settings.is_sandbox:

            return Response({

                'success': False,

                'message': 'در Sandbox پیامک دریافتی ثبت نمی‌شود',

            }, status=status.HTTP_400_BAD_REQUEST)

        client, err = _smsir_client_or_error()

        if err:

            return err

        count = int(request.query_params.get('count', 50))

        return _api_response(client.get_latest_received(count))





class AdminSmsErrorCodesView(APIView):

    permission_classes = [IsStaff]



    def get(self, request):

        from apps.accounts.sms.smsir_utils import DELIVERY_STATE_MESSAGES, SMSIR_STATUS_MESSAGES

        return Response({

            'status_codes': [{'code': k, 'message': v} for k, v in sorted(SMSIR_STATUS_MESSAGES.items())],

            'delivery_states': [{'code': k, 'message': v} for k, v in sorted(DELIVERY_STATE_MESSAGES.items())],

            'provider': _provider_mode(),

        })


