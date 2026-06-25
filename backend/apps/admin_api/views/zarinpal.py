from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.admin_api.permissions import IsStaff
from apps.payments.models import Payment, ZarinpalSettings
from apps.payments.serializers import (
    AdminPaymentSerializer,
    AdminRefundRequestSerializer,
)
from apps.payments.services import inquiry_payment, refund_payment, reverse_payment
from apps.payments.zarinpal.config import ZarinpalConfigService
from apps.payments.zarinpal.rest import ZarinpalRestClient


class AdminPaymentListView(APIView):
    permission_classes = [IsStaff]

    def get(self, request):
        qs = Payment.objects.select_related('order').order_by('-created_at')
        status_filter = request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
        limit = min(int(request.query_params.get('limit', 50)), 100)
        payments = qs[:limit]
        return Response(AdminPaymentSerializer(payments, many=True).data)


class AdminPaymentDetailView(APIView):
    permission_classes = [IsStaff]

    def get(self, request, payment_id):
        try:
            payment = Payment.objects.select_related('order').prefetch_related(
                'logs', 'refunds'
            ).get(pk=payment_id)
        except Payment.DoesNotExist:
            return Response({'detail': 'پرداخت یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
        return Response(AdminPaymentSerializer(payment).data)


class AdminPaymentInquiryView(APIView):
    permission_classes = [IsStaff]

    def post(self, request, payment_id):
        try:
            payment = Payment.objects.get(pk=payment_id)
        except Payment.DoesNotExist:
            return Response({'detail': 'پرداخت یافت نشد'}, status=status.HTTP_404_NOT_FOUND)

        success, data, message, error_code = inquiry_payment(payment)
        return Response({
            'success': success,
            'data': data,
            'message': message,
            'error_code': error_code,
        })


class AdminPaymentReverseView(APIView):
    permission_classes = [IsStaff]

    def post(self, request, payment_id):
        try:
            payment = Payment.objects.get(pk=payment_id)
        except Payment.DoesNotExist:
            return Response({'detail': 'پرداخت یافت نشد'}, status=status.HTTP_404_NOT_FOUND)

        refund, error = reverse_payment(payment, initiated_by=request.user)
        if error:
            return Response({'detail': error}, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            'success': True,
            'refund_id': str(refund.id),
            'status': refund.status,
        })


class AdminPaymentRefundView(APIView):
    permission_classes = [IsStaff]

    def post(self, request, payment_id):
        try:
            payment = Payment.objects.get(pk=payment_id)
        except Payment.DoesNotExist:
            return Response({'detail': 'پرداخت یافت نشد'}, status=status.HTTP_404_NOT_FOUND)

        serializer = AdminRefundRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        amount = serializer.validated_data.get('amount') or payment.amount

        refund, error = refund_payment(
            payment,
            amount=amount,
            method=serializer.validated_data['method'],
            reason=serializer.validated_data['reason'],
            initiated_by=request.user,
        )
        if error:
            return Response({'detail': error}, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            'success': True,
            'refund_id': str(refund.id),
            'status': refund.status,
        })


class AdminZarinpalSettingsView(APIView):
    permission_classes = [IsStaff]

    def get(self, request):
        from apps.payments.serializers import AdminZarinpalSettingsSerializer
        instance = ZarinpalSettings.get_settings()
        return Response(AdminZarinpalSettingsSerializer(instance).data)

    def patch(self, request):
        from apps.payments.serializers import AdminZarinpalSettingsSerializer
        instance = ZarinpalSettings.get_settings()
        serializer = AdminZarinpalSettingsSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class AdminZarinpalTestView(APIView):
    permission_classes = [IsStaff]

    def post(self, request):
        if ZarinpalConfigService.resolve_is_mock():
            return Response({
                'success': True,
                'message': 'حالت Mock فعال است — اتصال واقعی تست نشد',
                'mock': True,
            })

        try:
            success, data, message, error_code = ZarinpalRestClient.fee_calculation(100000)
        except Exception as exc:
            return Response({
                'success': False,
                'message': f'خطا در اتصال: {exc}',
            }, status=status.HTTP_502_BAD_GATEWAY)

        return Response({
            'success': success,
            'data': data,
            'message': message,
            'error_code': error_code,
        })


class AdminZarinpalSessionsView(APIView):
    permission_classes = [IsStaff]

    def get(self, request):
        from apps.payments.zarinpal.graphql import ZarinpalGraphQLClient
        terminal_id = request.query_params.get('terminal_id')
        result = ZarinpalGraphQLClient.list_sessions(terminal_id)
        if result.get('errors'):
            return Response({'errors': result['errors']}, status=status.HTTP_502_BAD_GATEWAY)
        sessions = (result.get('data') or {}).get('Session') or []
        return Response({'sessions': sessions})


class AdminZarinpalReconciliationsView(APIView):
    permission_classes = [IsStaff]

    def get(self, request):
        from apps.payments.zarinpal.graphql import ZarinpalGraphQLClient
        terminal_id = request.query_params.get('terminal_id')
        status_filter = request.query_params.get('status')
        result = ZarinpalGraphQLClient.list_reconciliations(terminal_id, status_filter)
        if result.get('errors'):
            return Response({'errors': result['errors']}, status=status.HTTP_502_BAD_GATEWAY)
        items = (result.get('data') or {}).get('resource') or []
        return Response({'reconciliations': items})
