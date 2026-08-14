import logging

from django.db import transaction
from django.db.models import F
from django.db.models.functions import Greatest
from django.utils import timezone

from apps.catalog.models import Product
from apps.catalog.signals import invalidate_product_cache
from apps.coupons.services import record_coupon_usage, validate_coupon
from apps.orders.models import Order

from .models import Payment, PaymentLog, Refund
from .zarinpal.config import ZarinpalConfigService
from .zarinpal.graphql import ZarinpalGraphQLClient
from .zarinpal.rest import ZarinpalRestClient

logger = logging.getLogger(__name__)


def _log_payment(payment, action, request_data, response_data):
    if not ZarinpalConfigService.resolve_enable_logging():
        return
    PaymentLog.objects.create(
        payment=payment,
        action=action,
        request_data=request_data,
        response_data=response_data if isinstance(response_data, dict) else {'raw': str(response_data)},
    )


def _build_metadata(order):
    metadata = {'order_number': order.order_number}
    user = order.user
    if user.phone:
        metadata['mobile'] = user.phone
    if getattr(user, 'email', None):
        metadata['email'] = user.email
    return metadata


def create_payment_request(order):
    payment, _ = Payment.objects.get_or_create(
        order=order,
        defaults={'amount': order.total, 'status': Payment.STATUS_PENDING},
    )

    if payment.amount != order.total:
        payment.amount = order.total
        payment.save(update_fields=['amount'])

    if ZarinpalConfigService.resolve_is_mock():
        authority = f'MOCK_{order.order_number}'
        payment.authority = authority
        payment.save(update_fields=['authority'])
        callback_url = ZarinpalConfigService.resolve_callback_url()
        sep = '&' if '?' in callback_url else '?'
        redirect_url = f'{callback_url}{sep}Authority={authority}&Status=OK'
        _log_payment(payment, 'request_mock', {'order': order.order_number}, {'authority': authority})
        return redirect_url, None, authority

    try:
        success, data, message, error_code = ZarinpalRestClient.request_payment(
            amount=order.total,
            description=f'سفارش {order.order_number} - Lumia Beauty',
            metadata=_build_metadata(order),
        )
    except Exception as exc:
        logger.exception('Zarinpal request failed: %s', exc)
        return None, 'خطا در اتصال به درگاه پرداخت', None

    _log_payment(
        payment, 'request',
        {'amount': order.total, 'order': order.order_number},
        {'success': success, 'data': data, 'error_code': error_code},
    )

    if success and data.get('authority'):
        authority = data['authority']
        payment.authority = authority
        payment.save(update_fields=['authority'])
        return ZarinpalRestClient.get_redirect_url(authority), None, authority

    payment.error_code = error_code
    payment.save(update_fields=['error_code'])
    return None, message or 'خطا در اتصال به درگاه پرداخت', None


def _fulfill_order(payment, order, result_data):
    """Decrement stock, record coupon, clear cart — called only on first verify (code 100)."""
    items = list(order.items.select_related('product'))
    locked_products = {
        product.id: product
        for product in Product.objects.select_for_update().filter(
            id__in=[item.product_id for item in items]
        )
    }

    for item in items:
        product = locked_products[item.product_id]
        if product.stock < item.quantity:
            payment.status = Payment.STATUS_NEEDS_REVIEW
            payment.gateway_response = result_data
            payment.save(update_fields=['status', 'gateway_response'])
            return order, 'failed', 'موجودی سفارش پس از پرداخت کافی نیست و نیازمند بررسی است'

    coupon = None
    if order.coupon_code:
        coupon, error = validate_coupon(order.coupon_code, order.user, order.subtotal, lock=True)
        if error:
            payment.status = Payment.STATUS_NEEDS_REVIEW
            payment.gateway_response = result_data
            payment.save(update_fields=['status', 'gateway_response'])
            return order, 'failed', error

    if coupon:
        error = record_coupon_usage(coupon, order.user, order)
        if error:
            payment.status = Payment.STATUS_NEEDS_REVIEW
            payment.gateway_response = result_data
            payment.save(update_fields=['status', 'gateway_response'])
            return order, 'failed', error

    for item in items:
        Product.objects.filter(pk=item.product_id, stock__gte=item.quantity).update(
            stock=F('stock') - item.quantity,
            sales_count=F('sales_count') + item.quantity,
        )

    for item in items:
        invalidate_product_cache(product_id=item.product_id, slug=item.product.slug)

    cart = order.user.carts.first()
    if cart:
        cart.items.all().delete()

    return None, None, None


def _mark_payment_success(payment, order, data, result_data, fulfill=True):
    ref_id = str(data.get('ref_id', ''))
    payment.status = Payment.STATUS_SUCCESS
    payment.ref_id = ref_id
    payment.session_id = ref_id or payment.session_id
    payment.card_pan = data.get('card_pan', '') or payment.card_pan
    payment.fee = data.get('fee') if data.get('fee') is not None else payment.fee
    payment.fee_type = data.get('fee_type', '') or payment.fee_type
    payment.paid_at = timezone.now()
    payment.gateway_response = result_data
    payment.error_code = None
    payment.save(update_fields=[
        'status', 'ref_id', 'session_id', 'card_pan', 'fee', 'fee_type',
        'paid_at', 'gateway_response', 'error_code',
    ])

    if fulfill:
        err_order, err_result, err_msg = _fulfill_order(payment, order, result_data)
        if err_order:
            return err_order, err_result, err_msg

    order.status = Order.STATUS_PAID
    order.save(update_fields=['status'])
    return order, 'success', ref_id


@transaction.atomic
def confirm_manual_payment(order, initiated_by=None):
    """Mark an order as paid manually (card-to-card, no gateway).

    Decrements stock, records coupon usage and clears the customer's cart
    exactly like a successful gateway payment.
    """
    order = Order.objects.select_for_update().get(pk=order.pk)
    payment, _ = Payment.objects.select_for_update().get_or_create(
        order=order,
        defaults={'amount': order.total, 'status': Payment.STATUS_PENDING},
    )

    if payment.amount != order.total:
        payment.amount = order.total
        payment.save(update_fields=['amount'])

    if payment.status == Payment.STATUS_SUCCESS:
        return order, 'success', payment.ref_id

    ref_id = f'MANUAL-{order.purchase_code}'
    result_data = {
        'manual': True,
        'initiated_by': str(initiated_by) if initiated_by else None,
        'purchase_code': order.purchase_code,
    }
    PaymentLog.objects.create(
        payment=payment,
        action='manual_confirm',
        request_data={'order': order.order_number, 'purchase_code': order.purchase_code},
        response_data=result_data,
    )

    result_order, result, msg = _mark_payment_success(
        payment, order, {'ref_id': ref_id}, result_data, fulfill=True,
    )
    if result == 'failed':
        return result_order, 'failed', msg or 'تکمیل سفارش ناموفق بود'

    result_order.refresh_from_db()
    return result_order, 'success', ref_id


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
        success, data, message, error_code = True, {'code': 100, 'ref_id': '12345678'}, 'موفق', 100
        result_data = {'data': data}
    else:
        try:
            success, data, message, error_code = ZarinpalRestClient.verify_payment(order.total, authority)
            result_data = {'data': data}
        except Exception as exc:
            logger.exception('Zarinpal verify failed: %s', exc)
            return order, 'failed', 'خطا در ارتباط با درگاه پرداخت'

    _log_payment(
        payment, 'verify',
        {'authority': authority, 'amount': order.total},
        result_data,
    )

    code = data.get('code') if isinstance(data, dict) else error_code
    try:
        code = int(code) if code is not None else None
    except (TypeError, ValueError):
        pass

    if code == 100:
        return _mark_payment_success(payment, order, data, result_data, fulfill=True)

    if code == 101:
        # Gateway already verified — fulfill only if order still pending (recovery after timeout)
        needs_fulfill = order.status == Order.STATUS_PENDING
        return _mark_payment_success(payment, order, data, result_data, fulfill=needs_fulfill)

    payment.status = Payment.STATUS_FAILED
    payment.error_code = error_code
    payment.gateway_response = result_data
    payment.save(update_fields=['status', 'error_code', 'gateway_response'])
    order.status = Order.STATUS_CANCELLED
    order.save(update_fields=['status'])
    return order, 'failed', message or 'تأیید پرداخت ناموفق بود'


def inquiry_payment(payment):
    if not payment.authority or payment.authority.startswith('MOCK_'):
        return False, {}, 'تراکنش Mock قابل استعلام نیست', None
    try:
        success, data, message, error_code = ZarinpalRestClient.inquiry(payment.authority)
    except Exception as exc:
        logger.exception('Zarinpal inquiry failed: %s', exc)
        return False, {}, 'خطا در ارتباط با درگاه پرداخت', None
    _log_payment(payment, 'inquiry', {'authority': payment.authority}, {'data': data, 'success': success})
    return success, data, message, error_code


def _restore_stock(order):
    for item in order.items.select_related('product'):
        Product.objects.filter(pk=item.product_id).update(
            stock=F('stock') + item.quantity,
            sales_count=Greatest(F('sales_count') - item.quantity, 0),
        )
        invalidate_product_cache(product_id=item.product_id, slug=item.product.slug)


@transaction.atomic
def reverse_payment(payment, initiated_by=None):
    if payment.status != Payment.STATUS_SUCCESS:
        return None, 'فقط پرداخت‌های موفق قابل برگشت هستند'
    if not payment.is_recent:
        return None, 'مهلت برگشت فوری (۳۰ دقیقه) به پایان رسیده — از مرجوعی GraphQL استفاده کنید'

    existing = payment.refunds.filter(status=Refund.STATUS_COMPLETED).exists()
    if existing:
        return None, 'این پرداخت قبلاً مرجوع شده است'

    if payment.authority.startswith('MOCK_'):
        refund = Refund.objects.create(
            payment=payment,
            amount=payment.amount,
            method=Refund.METHOD_REVERSE,
            reason='CUSTOMER_REQUEST',
            status=Refund.STATUS_COMPLETED,
            initiated_by=initiated_by,
            gateway_response={'mock': True},
        )
        payment.status = Payment.STATUS_REFUNDED
        payment.save(update_fields=['status'])
        order = payment.order
        order.status = Order.STATUS_REFUNDED
        order.save(update_fields=['status'])
        _restore_stock(order)
        return refund, None

    try:
        success, data, message, error_code = ZarinpalRestClient.reverse_payment(payment.authority)
    except Exception as exc:
        logger.exception('Zarinpal reverse failed: %s', exc)
        return None, 'خطا در ارتباط با درگاه پرداخت'

    _log_payment(payment, 'reverse', {'authority': payment.authority}, {'data': data, 'success': success})

    refund = Refund.objects.create(
        payment=payment,
        amount=payment.amount,
        method=Refund.METHOD_REVERSE,
        reason='CUSTOMER_REQUEST',
        status=Refund.STATUS_COMPLETED if success else Refund.STATUS_FAILED,
        initiated_by=initiated_by,
        gateway_response={'data': data, 'error_code': error_code},
    )

    if not success:
        return refund, message or 'برگشت تراکنش ناموفق بود'

    payment.status = Payment.STATUS_REFUNDED
    payment.save(update_fields=['status'])
    order = payment.order
    order.status = Order.STATUS_REFUNDED
    order.save(update_fields=['status'])
    _restore_stock(order)
    return refund, None


@transaction.atomic
def refund_payment(payment, amount, method='card', reason='CUSTOMER_REQUEST', initiated_by=None):
    if payment.status != Payment.STATUS_SUCCESS:
        return None, 'فقط پرداخت‌های موفق قابل مرجوع هستند'

    existing = payment.refunds.filter(status=Refund.STATUS_COMPLETED).exists()
    if existing:
        return None, 'این پرداخت قبلاً مرجوع شده است'

    if amount > payment.amount:
        return None, 'مبلغ مرجوعی بیشتر از مبلغ پرداخت است'

    if payment.is_recent and method in ('instant', 'reverse', Refund.METHOD_REVERSE):
        return reverse_payment(payment, initiated_by=initiated_by)

    session_id = payment.session_id or payment.ref_id
    if not session_id:
        return None, 'شناسه Session برای مرجوعی GraphQL موجود نیست'

    gql_method = 'CARD' if method in ('instant', 'card', Refund.METHOD_CARD) else 'PAYA'
    try:
        result = ZarinpalGraphQLClient.add_refund(
            session_id=session_id,
            amount=amount,
            description=reason,
            method=gql_method,
            reason=reason,
        )
    except Exception as exc:
        logger.exception('Zarinpal GraphQL refund failed: %s', exc)
        return None, 'خطا در ارتباط با درگاه پرداخت'

    _log_payment(payment, 'refund_graphql', {'session_id': session_id, 'amount': amount}, result)

    resource = (result.get('data') or {}).get('resource')
    if not resource and result.get('errors'):
        err_msg = result['errors'][0].get('message', 'مرجوعی ناموفق بود')
        refund = Refund.objects.create(
            payment=payment,
            amount=amount,
            method=Refund.METHOD_CARD if gql_method == 'CARD' else Refund.METHOD_PAYA,
            reason=reason,
            status=Refund.STATUS_FAILED,
            initiated_by=initiated_by,
            gateway_response=result,
        )
        return refund, err_msg

    refund_status = Refund.STATUS_PENDING
    timeline = (resource or {}).get('timeline') or []
    if timeline and timeline[0].get('refund_status') == 'COMPLETED':
        refund_status = Refund.STATUS_COMPLETED

    refund = Refund.objects.create(
        payment=payment,
        amount=amount,
        method=Refund.METHOD_CARD if gql_method == 'CARD' else Refund.METHOD_PAYA,
        reason=reason,
        status=refund_status,
        gateway_refund_id=str((resource or {}).get('id', '')),
        initiated_by=initiated_by,
        gateway_response=result,
    )

    if refund_status == Refund.STATUS_COMPLETED:
        payment.status = Payment.STATUS_REFUNDED
        payment.save(update_fields=['status'])
        order = payment.order
        order.status = Order.STATUS_REFUNDED
        order.save(update_fields=['status'])
        if amount >= payment.amount:
            _restore_stock(order)

    return refund, None


def process_unverified_payments():
    """Fetch unverified authorities from Zarinpal and verify matching pending payments."""
    if ZarinpalConfigService.resolve_is_mock():
        return {'processed': 0, 'message': 'Mock mode — skipped'}

    try:
        success, data, message, _ = ZarinpalRestClient.unverified()
    except Exception as exc:
        logger.exception('Zarinpal unverified failed: %s', exc)
        return {'processed': 0, 'error': str(exc)}

    if not success:
        return {'processed': 0, 'error': message}

    authorities = data.get('authorities') or []
    processed = 0
    for entry in authorities:
        authority = entry.get('authority') if isinstance(entry, dict) else entry
        if not authority:
            continue
        try:
            payment = Payment.objects.get(authority=authority, status=Payment.STATUS_PENDING)
        except Payment.DoesNotExist:
            continue
        order, result, _ = verify_payment_callback(authority, 'OK')
        if result == 'success':
            processed += 1
            logger.info('Unverified payment verified: %s order=%s', authority, order.order_number if order else '')

    return {'processed': processed, 'total_unverified': len(authorities)}


def run_reconciliation():
    """Fetch reconciliation data from GraphQL if auto_reconcile enabled."""
    if not ZarinpalConfigService.resolve_auto_reconcile():
        return {'skipped': True}
    terminal_id = ZarinpalConfigService.resolve_terminal_id()
    if not terminal_id:
        return {'error': 'Terminal ID not configured'}
    result = ZarinpalGraphQLClient.list_reconciliations(terminal_id, 'PAID')
    items = ((result.get('data') or {}).get('resource')) or []
    return {'count': len(items), 'items': items}
