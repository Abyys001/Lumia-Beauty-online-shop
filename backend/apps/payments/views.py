from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import redirect
from django.conf import settings

from apps.orders.models import Order

from .models import Payment
from .serializers import PaymentRequestSerializer
from .services import create_payment_request, verify_payment_callback


class ZarinpalRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = PaymentRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order_number = serializer.validated_data['order_number']

        try:
            order = Order.objects.get(order_number=order_number, user=request.user)
        except Order.DoesNotExist:
            return Response({'detail': 'سفارش یافت نشد'}, status=status.HTTP_404_NOT_FOUND)

        if order.status != Order.STATUS_PENDING:
            return Response({'detail': 'این سفارش قبلاً پرداخت شده است'}, status=status.HTTP_400_BAD_REQUEST)

        redirect_url, error = create_payment_request(order)
        if error:
            return Response({'detail': error}, status=status.HTTP_502_BAD_GATEWAY)

        return Response({'redirect_url': redirect_url})


class ZarinpalVerifyView(APIView):
    def get(self, request):
        authority = request.query_params.get('Authority', '')
        status_param = request.query_params.get('Status', '')

        order, result, message = verify_payment_callback(authority, status_param)

        site_url = getattr(settings, 'FRONTEND_URL', 'http://localhost')
        if result == 'success':
            return redirect(f'{site_url}/checkout/success?order={order.order_number}&ref={message}')
        return redirect(f'{site_url}/checkout/failed?order={order.order_number if order else ""}&message={message}')
