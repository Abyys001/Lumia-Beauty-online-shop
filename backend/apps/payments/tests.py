from unittest.mock import MagicMock, patch

from django.test import TestCase, override_settings
from django.utils import timezone

from apps.accounts.models import User
from apps.catalog.models import Category, Product
from apps.coupons.models import Coupon, CouponUsage
from apps.orders.models import Order, OrderItem
from apps.payments.models import Payment, Refund, ZarinpalSettings
from apps.payments.services import (
    create_payment_request,
    process_unverified_payments,
    refund_payment,
    reverse_payment,
    verify_payment_callback,
)
from apps.payments.zarinpal.config import ZarinpalConfigService
from apps.payments.zarinpal.errors import get_error_message, parse_api_response


class PaymentCorrectnessTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone='09123456789')
        self.category = Category.objects.create(name='پوست', slug='skin')
        self.product = Product.objects.create(
            name='کرم تست',
            slug='test-cream',
            description='توضیح تست',
            category=self.category,
            price=100000,
            stock=5,
            sku='TEST-CREAM',
        )

    def create_order(self, quantity=2, coupon_code=''):
        subtotal = self.product.price * quantity
        order = Order.objects.create(
            user=self.user,
            subtotal=subtotal,
            discount_amount=0,
            shipping_cost=0,
            total=subtotal,
            coupon_code=coupon_code,
            shipping_name='کاربر تست',
            shipping_phone='09123456789',
            shipping_province='تهران',
            shipping_city='تهران',
            shipping_address='آدرس تست',
            shipping_postal_code='1234567890',
        )
        OrderItem.objects.create(
            order=order,
            product=self.product,
            product_name=self.product.name,
            product_price=self.product.price,
            quantity=quantity,
            subtotal=subtotal,
        )
        return order

    def create_payment(self, order, authority=None):
        return Payment.objects.create(
            order=order,
            amount=order.total,
            authority=authority or f'MOCK_{order.order_number}',
            status=Payment.STATUS_PENDING,
        )

    def test_successful_payment_callback_is_idempotent(self):
        order = self.create_order(quantity=2)
        payment = self.create_payment(order)

        first_order, first_result, _ = verify_payment_callback(payment.authority, 'OK')
        second_order, second_result, _ = verify_payment_callback(payment.authority, 'OK')

        self.product.refresh_from_db()
        payment.refresh_from_db()
        self.assertEqual(first_result, 'success')
        self.assertEqual(second_result, 'success')
        self.assertEqual(self.product.stock, 3)
        self.assertEqual(payment.status, Payment.STATUS_SUCCESS)

    def test_successful_gateway_with_insufficient_stock_needs_review(self):
        order = self.create_order(quantity=4)
        payment = self.create_payment(order)
        self.product.stock = 1
        self.product.save(update_fields=['stock'])

        result_order, result, message = verify_payment_callback(payment.authority, 'OK')

        payment.refresh_from_db()
        self.assertEqual(result, 'failed')
        self.assertIn('موجودی', message)
        self.assertEqual(payment.status, Payment.STATUS_NEEDS_REVIEW)
        self.assertEqual(result_order.status, Order.STATUS_PENDING)

    def test_coupon_max_uses_is_rechecked_during_payment(self):
        coupon = Coupon.objects.create(
            code='LIMITED',
            coupon_type=Coupon.TYPE_FIXED,
            value=10000,
            max_uses=1,
            used_count=1,
        )
        order = self.create_order(quantity=1, coupon_code=coupon.code)
        payment = self.create_payment(order)

        _, result, message = verify_payment_callback(payment.authority, 'OK')

        payment.refresh_from_db()
        self.assertEqual(result, 'failed')
        self.assertIn('کد تخفیف', message)
        self.assertEqual(payment.status, Payment.STATUS_NEEDS_REVIEW)


class ZarinpalErrorMappingTests(TestCase):
    def test_known_error_codes(self):
        self.assertIn('ناموفق', get_error_message(-51))
        self.assertIn('نامعتبر', get_error_message(-54))

    def test_parse_success_response(self):
        success, data, msg, code = parse_api_response({
            'data': {'code': 100, 'authority': 'A123', 'message': 'Success'},
            'errors': [],
        })
        self.assertTrue(success)
        self.assertEqual(code, 100)

    def test_parse_error_array(self):
        success, data, msg, code = parse_api_response({
            'data': None,
            'errors': [{'code': -54, 'message': 'Invalid authority'}],
        })
        self.assertFalse(success)
        self.assertEqual(code, -54)


class Code101RecoveryTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone='09111111111')
        self.category = Category.objects.create(name='cat', slug='cat')
        self.product = Product.objects.create(
            name='P', slug='p', description='d', category=self.category,
            price=50000, stock=10, sku='P1',
        )
        self.order = Order.objects.create(
            user=self.user, subtotal=50000, discount_amount=0,
            shipping_cost=0, total=50000,
            shipping_name='N', shipping_phone='09111111111',
            shipping_province='تهران', shipping_city='تهران',
            shipping_address='آدرس', shipping_postal_code='1234567890',
        )
        OrderItem.objects.create(
            order=self.order, product=self.product,
            product_name='P', product_price=50000, quantity=1, subtotal=50000,
        )
        self.payment = Payment.objects.create(
            order=self.order, amount=50000,
            authority='REAL_AUTH_123', status=Payment.STATUS_PENDING,
        )

    @patch('apps.payments.services.ZarinpalRestClient.verify_payment')
    def test_code_101_does_not_double_decrement_stock(self, mock_verify):
        mock_verify.return_value = (True, {'code': 101, 'ref_id': '999'}, 'Verified', 101)

        _, result, _ = verify_payment_callback('REAL_AUTH_123', 'OK')
        self.product.refresh_from_db()
        self.order.refresh_from_db()
        self.assertEqual(result, 'success')
        self.assertEqual(self.order.status, Order.STATUS_PAID)
        self.assertEqual(self.product.stock, 9)

        _, result2, _ = verify_payment_callback('REAL_AUTH_123', 'OK')
        self.product.refresh_from_db()
        self.assertEqual(result2, 'success')
        self.assertEqual(self.product.stock, 9)


class ConfigResolutionTests(TestCase):
    @override_settings(ZARINPAL_MERCHANT_ID='env-merchant', ZARINPAL_MOCK=True)
    def test_db_merchant_overrides_env(self):
        settings = ZarinpalSettings.get_settings()
        settings.merchant_id = 'db-merchant'
        settings.is_mock = True
        settings.save()
        self.assertEqual(ZarinpalConfigService.resolve_merchant_id(), 'db-merchant')

    @override_settings(ZARINPAL_MERCHANT_ID='env-only', ZARINPAL_MOCK=True)
    def test_env_fallback_when_db_empty(self):
        self.assertEqual(ZarinpalConfigService.resolve_merchant_id(), 'env-only')


@override_settings(ZARINPAL_MOCK=True)
class MockPaymentRequestTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone='09222222222')
        self.order = Order.objects.create(
            user=self.user, subtotal=10000, discount_amount=0,
            shipping_cost=0, total=10000,
            shipping_name='N', shipping_phone='09222222222',
            shipping_province='تهران', shipping_city='تهران',
            shipping_address='آدرس', shipping_postal_code='1234567890',
        )

    def test_mock_creates_redirect_to_callback(self):
        url, error, authority = create_payment_request(self.order)
        self.assertIsNone(error)
        self.assertIn('MOCK_', authority)
        self.assertIn('Authority=', url)


class RefundTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone='09333333333')
        self.staff = User.objects.create_user(phone='09444444444', is_staff=True)
        self.category = Category.objects.create(name='c', slug='c')
        self.product = Product.objects.create(
            name='X', slug='x', description='d', category=self.category,
            price=20000, stock=5, sku='X1',
        )
        self.order = Order.objects.create(
            user=self.user, subtotal=20000, discount_amount=0,
            shipping_cost=0, total=20000, status=Order.STATUS_PAID,
            shipping_name='N', shipping_phone='09333333333',
            shipping_province='تهران', shipping_city='تهران',
            shipping_address='آدرس', shipping_postal_code='1234567890',
        )
        OrderItem.objects.create(
            order=self.order, product=self.product,
            product_name='X', product_price=20000, quantity=1, subtotal=20000,
        )
        self.payment = Payment.objects.create(
            order=self.order, amount=20000,
            authority='MOCK_LB001', status=Payment.STATUS_SUCCESS,
            ref_id='12345', paid_at=timezone.now(),
        )

    def test_mock_reverse_refunds_order(self):
        refund, error = reverse_payment(self.payment, initiated_by=self.staff)
        self.assertIsNone(error)
        self.assertEqual(refund.status, Refund.STATUS_COMPLETED)
        self.payment.refresh_from_db()
        self.order.refresh_from_db()
        self.assertEqual(self.payment.status, Payment.STATUS_REFUNDED)
        self.assertEqual(self.order.status, Order.STATUS_REFUNDED)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 6)


class UnverifiedProcessingTests(TestCase):
    @override_settings(ZARINPAL_MOCK=True)
    def test_skipped_in_mock_mode(self):
        result = process_unverified_payments()
        self.assertEqual(result['processed'], 0)

    @patch('apps.payments.services.ZarinpalConfigService.resolve_is_mock', return_value=False)
    @patch('apps.payments.services.ZarinpalRestClient.unverified')
    def test_processes_matching_pending(self, mock_unverified, _mock):
        user = User.objects.create_user(phone='09555555555')
        order = Order.objects.create(
            user=user, subtotal=10000, discount_amount=0,
            shipping_cost=0, total=10000,
            shipping_name='N', shipping_phone='09555555555',
            shipping_province='تهران', shipping_city='تهران',
            shipping_address='آدرس', shipping_postal_code='1234567890',
        )
        Payment.objects.create(
            order=order, amount=10000,
            authority='MOCK_PENDING', status=Payment.STATUS_PENDING,
        )
        mock_unverified.return_value = (
            True,
            {'authorities': [{'authority': 'MOCK_PENDING', 'amount': 10000}]},
            'ok',
            100,
        )
        with patch('apps.payments.services.verify_payment_callback') as mock_verify:
            mock_verify.return_value = (order, 'success', 'ref')
            result = process_unverified_payments()
        self.assertEqual(result['processed'], 1)
