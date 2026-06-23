from django.test import TestCase

from apps.accounts.models import User
from apps.catalog.models import Category, Product
from apps.coupons.models import Coupon, CouponUsage
from apps.orders.models import Order, OrderItem

from .models import Payment
from .services import verify_payment_callback


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

    def create_payment(self, order):
        return Payment.objects.create(
            order=order,
            amount=order.total,
            authority=f'MOCK_{order.order_number}',
            status=Payment.STATUS_PENDING,
        )

    def test_successful_payment_callback_is_idempotent(self):
        order = self.create_order(quantity=2)
        payment = self.create_payment(order)

        first_order, first_result, _ = verify_payment_callback(payment.authority, 'OK')
        second_order, second_result, _ = verify_payment_callback(payment.authority, 'OK')

        self.product.refresh_from_db()
        first_order.refresh_from_db()
        second_order.refresh_from_db()
        payment.refresh_from_db()
        self.assertEqual(first_result, 'success')
        self.assertEqual(second_result, 'success')
        self.assertEqual(self.product.stock, 3)
        self.assertEqual(self.product.sales_count, 2)
        self.assertEqual(payment.status, Payment.STATUS_SUCCESS)
        self.assertEqual(first_order.status, Order.STATUS_PAID)
        self.assertEqual(second_order.status, Order.STATUS_PAID)

    def test_successful_gateway_with_insufficient_stock_needs_review(self):
        order = self.create_order(quantity=4)
        payment = self.create_payment(order)
        self.product.stock = 1
        self.product.save(update_fields=['stock'])

        result_order, result, message = verify_payment_callback(payment.authority, 'OK')

        self.product.refresh_from_db()
        payment.refresh_from_db()
        result_order.refresh_from_db()
        self.assertEqual(result, 'failed')
        self.assertIn('موجودی', message)
        self.assertEqual(self.product.stock, 1)
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

        self.product.refresh_from_db()
        payment.refresh_from_db()
        self.assertEqual(result, 'failed')
        self.assertIn('کد تخفیف', message)
        self.assertEqual(self.product.stock, 5)
        self.assertEqual(payment.status, Payment.STATUS_NEEDS_REVIEW)
        self.assertFalse(CouponUsage.objects.filter(coupon=coupon, order=order).exists())
