import json

import requests
from django.conf import settings
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from apps.catalog.models import Product
from apps.coupons.services import record_coupon_usage, validate_coupon
from apps.orders.models import Order

from .models import Payment, PaymentLog


class ZarinpalService:
    SANDBOX_URL = 'https://sandbox.zarinpal.com/pg/v4/payment'
    PRODUCTION_URL = 'https://api.zarinpal.com/pg/v4/payment'
    SANDBOX_GATEWAY = 'https://sandbox.zarinpal.com/pg/StartPay/'
    PRODUCTION_GATEWAY = 'https://www.zarinpal.com/pg/StartPay/'

    @classmethod
    def _base_url(cls):
        return cls.SANDBOX_URL if settings.ZARINPAL_SANDBOX else cls.PRODUCTION_URL

    @classmethod
    def _gateway_url(cls):
        return cls.SANDBOX_GATEWAY if settings.ZARINPAL_SANDBOX else cls.PRODUCTION_GATEWAY

    @classmethod
    def request_payment(cls, amount, description, order_number):
        url = f'{cls._base_url()}/request.json'
        payload = {
            'merchant_id': settings.ZARINPAL_MERCHANT_ID,
            'amount': amount,
            'description': description,
            'callback_url': settings.ZARINPAL_CALLBACK_URL,
            'metadata': {'order_number': order_number},
        }
        response = requests.post(url, json=payload, timeout=15)
        return response.json()

    @classmethod
    def verify_payment(cls, amount, authority):
        url = f'{cls._base_url()}/verify.json'
        payload = {
            'merchant_id': settings.ZARINPAL_MERCHANT_ID,
            'amount': amount,
            'authority': authority,
        }
        response = requests.post(url, json=payload, timeout=15)
        return response.json()

    @classmethod
    def get_redirect_url(cls, authority):
        return f'{cls._gateway_url()}{authority}'


def create_payment_request(order):
    payment, _ = Payment.objects.get_or_create(
        order=order,
        defaults={'amount': order.total, 'status': Payment.STATUS_PENDING},
    )

    if settings.ZARINPAL_SANDBOX:
        # Mock payment request for sandbox to be 100% offline and smooth
        authority = f"MOCK_{order.order_number}"
        payment.authority = authority
        payment.save(update_fields=['authority'])
        # Use callback URL as the redirect
        callback_url = settings.ZARINPAL_CALLBACK_URL
        if '?' in callback_url:
            redirect_url = f"{callback_url}&Authority={authority}&Status=OK"
        else:
            redirect_url = f"{callback_url}?Authority={authority}&Status=OK"
        return redirect_url, None

    try:
        result = ZarinpalService.request_payment(
            amount=order.total,
            description=f'سفارش {order.order_number} - Lumia Beauty',
            order_number=order.order_number,
        )
    except Exception:
        return None, 'خطا در اتصال به درگاه پرداخت'

    PaymentLog.objects.create(
        payment=payment,
        action='request',
        request_data={'amount': order.total, 'order': order.order_number},
        response_data=result,
    )

    data = result.get('data', {})
    if data.get('code') == 100:
        authority = data['authority']
        payment.authority = authority
        payment.save(update_fields=['authority'])
        return ZarinpalService.get_redirect_url(authority), None

    return None, 'خطا در اتصال به درگاه پرداخت'


@transaction.atomic
def verify_payment_callback(authority, status_param):
    try:
        payment = Payment.objects.select_for_update().get(authority=authority)
    except Payment.DoesNotExist:
        return None, 'failed', 'تراکنش یافت نشد'

    order = Order.objects.select_for_update().get(pk=payment.order_id)

    if payment.status == Payment.STATUS_SUCCESS:
        return order, 'success', payment.ref_id

    if status_param != 'OK':
        payment.status = Payment.STATUS_FAILED
        payment.save(update_fields=['status'])
        order.status = Order.STATUS_CANCELLED
        order.save(update_fields=['status'])
        return order, 'failed', 'پرداخت لغو شد'

    if payment.amount != order.total:
        payment.status = Payment.STATUS_FAILED
        payment.save(update_fields=['status'])
        return order, 'failed', 'مبلغ تراکنش نامعتبر است'

    if authority.startswith('MOCK_'):
        result = {'data': {'code': 100, 'ref_id': '12345678'}}
    else:
        try:
            result = ZarinpalService.verify_payment(order.total, authority)
        except Exception:
            return order, 'failed', 'خطا در ارتباط با درگاه پرداخت'

    PaymentLog.objects.create(
        payment=payment,
        action='verify',
        request_data={'authority': authority, 'amount': order.total},
        response_data=result,
    )

    data = result.get('data', {})
    if data.get('code') in (100, 101):
        items = list(order.items.select_related('product'))
        locked_products = {
            product.id: product
            for product in Product.objects.select_for_update().filter(id__in=[item.product_id for item in items])
        }

        for item in items:
            product = locked_products[item.product_id]
            if product.stock < item.quantity:
                payment.status = Payment.STATUS_NEEDS_REVIEW
                payment.gateway_response = result
                payment.save(update_fields=['status', 'gateway_response'])
                return order, 'failed', 'موجودی سفارش پس از پرداخت کافی نیست و نیازمند بررسی است'

        coupon = None
        if order.coupon_code:
            coupon, error = validate_coupon(order.coupon_code, order.user, order.subtotal, lock=True)
            if error:
                payment.status = Payment.STATUS_NEEDS_REVIEW
                payment.gateway_response = result
                payment.save(update_fields=['status', 'gateway_response'])
                return order, 'failed', error

        if coupon:
            error = record_coupon_usage(coupon, order.user, order)
            if error:
                payment.status = Payment.STATUS_NEEDS_REVIEW
                payment.gateway_response = result
                payment.save(update_fields=['status', 'gateway_response'])
                return order, 'failed', error

        ref_id = str(data.get('ref_id', ''))
        payment.status = Payment.STATUS_SUCCESS
        payment.ref_id = ref_id
        payment.paid_at = timezone.now()
        payment.gateway_response = result
        payment.save(update_fields=['status', 'ref_id', 'paid_at', 'gateway_response'])

        order.status = Order.STATUS_PAID
        order.save(update_fields=['status'])

        for item in items:
            Product.objects.filter(pk=item.product_id, stock__gte=item.quantity).update(
                stock=F('stock') - item.quantity,
                sales_count=F('sales_count') + item.quantity,
            )

        cart = order.user.carts.first()
        if cart:
            cart.items.all().delete()

        return order, 'success', ref_id

    payment.status = Payment.STATUS_FAILED
    payment.gateway_response = result
    payment.save(update_fields=['status', 'gateway_response'])
    order.status = Order.STATUS_CANCELLED
    order.save(update_fields=['status'])
    return order, 'failed', 'تأیید پرداخت ناموفق بود'
