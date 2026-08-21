from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import Address, User
from apps.catalog.models import Category, Product
from apps.payments.models import Payment

from .models import Order
from .services import expire_stale_pending_orders, expiry_days


class ManualCheckoutFlowTests(TestCase):
    """End-to-end card-to-card flow: purchase code → seller confirms → tracking."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(phone='09123456789')
        self.staff = User.objects.create_user(phone='09120000000', is_staff=True)
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

    def place_order(self, quantity=2):
        self.client.force_authenticate(self.user)
        self.client.post(
            '/api/cart/',
            {'product_id': str(self.product.id), 'quantity': quantity},
            format='json',
        )
        response = self.client.post(
            '/api/orders/',
            {
                'shipping_name': 'کاربر تست',
                'shipping_phone': '09123456789',
                'shipping_province': 'تهران',
                'shipping_city': 'تهران',
                'shipping_address': 'خیابان ولیعصر، کوچه دوم، ساختمان تست',
                'shipping_postal_code': '1234567890',
                'shipping_plate_number': '12/3',
            },
            format='json',
        )
        self.assertEqual(response.status_code, 201)
        return response.data

    def test_checkout_returns_purchase_code_and_frees_the_cart(self):
        data = self.place_order()

        self.assertEqual(len(data['purchase_code']), 6)
        self.assertTrue(data['purchase_code'].isdigit())
        self.assertEqual(data['status'], Order.STATUS_PENDING)

        cart = self.client.get('/api/cart/')
        self.assertEqual(cart.data['item_count'], 0)

        # Stock is untouched until the seller confirms the transfer.
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 5)

    def test_staff_lookup_by_purchase_code_and_order_number(self):
        data = self.place_order()
        self.client.force_authenticate(self.staff)

        by_code = self.client.get(f'/api/admin/orders/lookup/?code={data["purchase_code"]}')
        self.assertEqual(by_code.status_code, 200)
        self.assertEqual(by_code.data['order_number'], data['order_number'])
        self.assertEqual(by_code.data['shipping_plate_number'], '12/3')

        by_number = self.client.get(f'/api/admin/orders/lookup/?code={data["order_number"].lower()}')
        self.assertEqual(by_number.status_code, 200)

        missing = self.client.get('/api/admin/orders/lookup/?code=000000')
        self.assertEqual(missing.status_code, 404)

    def test_lookup_is_staff_only(self):
        data = self.place_order()
        self.client.force_authenticate(self.user)
        response = self.client.get(f'/api/admin/orders/lookup/?code={data["purchase_code"]}')
        self.assertEqual(response.status_code, 403)

    def test_mark_paid_fulfills_order_and_is_idempotent(self):
        data = self.place_order()
        self.client.force_authenticate(self.staff)

        first = self.client.post(f'/api/admin/orders/{data["id"]}/mark-paid/')
        self.assertEqual(first.status_code, 200)
        self.assertEqual(first.data['status'], Order.STATUS_PAID)
        self.assertEqual(first.data['payment_status'], 'success')

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 3)
        self.assertEqual(self.product.sales_count, 2)

        second = self.client.post(f'/api/admin/orders/{data["id"]}/mark-paid/')
        self.assertEqual(second.status_code, 200)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 3)

    def test_mark_paid_rejected_for_cancelled_order(self):
        data = self.place_order()
        Order.objects.filter(pk=data['id']).update(status=Order.STATUS_CANCELLED)

        self.client.force_authenticate(self.staff)
        response = self.client.post(f'/api/admin/orders/{data["id"]}/mark-paid/')
        self.assertEqual(response.status_code, 400)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 5)

    def test_shipping_requires_a_24_digit_tracking_number(self):
        data = self.place_order()
        self.client.force_authenticate(self.staff)
        self.client.post(f'/api/admin/orders/{data["id"]}/mark-paid/')

        short = self.client.patch(
            f'/api/admin/orders/{data["id"]}/',
            {'status': Order.STATUS_SHIPPED, 'tracking_number': '123'},
            format='json',
        )
        self.assertEqual(short.status_code, 400)
        self.assertIn('tracking_number', short.data)

        persian = '۱۲۳۴۵۶۷۸۹۰۱۲۳۴۵۶۷۸۹۰۱۲۳۴'
        ok = self.client.patch(
            f'/api/admin/orders/{data["id"]}/',
            {'status': Order.STATUS_SHIPPED, 'tracking_number': persian},
            format='json',
        )
        self.assertEqual(ok.status_code, 200)
        self.assertEqual(ok.data['tracking_number'], '123456789012345678901234')

        # Status changes afterwards must not re-demand the tracking number.
        delivered = self.client.patch(
            f'/api/admin/orders/{data["id"]}/',
            {'status': Order.STATUS_DELIVERED},
            format='json',
        )
        self.assertEqual(delivered.status_code, 200)

    def test_customer_sees_tracking_number_on_their_order(self):
        data = self.place_order()
        self.client.force_authenticate(self.staff)
        self.client.post(f'/api/admin/orders/{data["id"]}/mark-paid/')
        self.client.patch(
            f'/api/admin/orders/{data["id"]}/',
            {'status': Order.STATUS_SHIPPED, 'tracking_number': '1' * 24},
            format='json',
        )

        self.client.force_authenticate(self.user)
        response = self.client.get(f'/api/orders/{data["order_number"]}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['tracking_number'], '1' * 24)
        self.assertEqual(response.data['status'], Order.STATUS_SHIPPED)

    def test_customer_cannot_read_another_customers_order(self):
        data = self.place_order()
        other = User.objects.create_user(phone='09121111111')
        self.client.force_authenticate(other)
        response = self.client.get(f'/api/orders/{data["order_number"]}/')
        self.assertEqual(response.status_code, 404)


class PendingOrderExpiryTests(TestCase):
    def setUp(self):
        self.client = APIClient()
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

    def make_order(self, *, age_days=0, status=Order.STATUS_PENDING):
        order = Order.objects.create(
            user=self.user,
            subtotal=100000,
            shipping_cost=0,
            total=100000,
            status=status,
            shipping_name='کاربر تست',
            shipping_phone='09123456789',
            shipping_province='تهران',
            shipping_city='تهران',
            shipping_address='آدرس تست',
        )
        if age_days:
            Order.objects.filter(pk=order.pk).update(
                created_at=timezone.now() - timedelta(days=age_days),
            )
        return order

    def test_only_pending_orders_past_the_window_are_cancelled(self):
        stale = self.make_order(age_days=8)
        fresh = self.make_order(age_days=6)
        paid = self.make_order(age_days=30, status=Order.STATUS_PAID)
        Payment.objects.create(order=stale, amount=stale.total, status=Payment.STATUS_PENDING)

        self.assertEqual(expire_stale_pending_orders(), 1)

        stale.refresh_from_db()
        fresh.refresh_from_db()
        paid.refresh_from_db()
        self.assertEqual(stale.status, Order.STATUS_CANCELLED)
        self.assertEqual(fresh.status, Order.STATUS_PENDING)
        self.assertEqual(paid.status, Order.STATUS_PAID)
        self.assertEqual(stale.payment.status, Payment.STATUS_FAILED)

        # Nothing was reserved, so stock stays where it was.
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 5)

    def test_expired_order_can_no_longer_be_confirmed(self):
        stale = self.make_order(age_days=8)
        expire_stale_pending_orders()

        staff = User.objects.create_user(phone='09120000000', is_staff=True)
        self.client.force_authenticate(staff)
        response = self.client.post(f'/api/admin/orders/{stale.id}/mark-paid/')
        self.assertEqual(response.status_code, 400)

    def test_order_payload_carries_the_payment_deadline(self):
        order = self.make_order()
        self.client.force_authenticate(self.user)

        response = self.client.get(f'/api/orders/{order.order_number}/')
        self.assertEqual(response.status_code, 200)
        deadline = response.data['expires_at']
        self.assertIsNotNone(deadline)
        self.assertEqual((deadline - order.created_at).days, expiry_days())

        Order.objects.filter(pk=order.pk).update(status=Order.STATUS_PAID)
        response = self.client.get(f'/api/orders/{order.order_number}/')
        self.assertIsNone(response.data['expires_at'])


class CheckoutValidationTests(TestCase):
    """Every rejected checkout must name the offending field, not just fail."""

    VALID = {
        'shipping_name': 'مریم رضایی',
        'shipping_phone': '09123456789',
        'shipping_province': 'تهران',
        'shipping_city': 'تهران',
        'shipping_address': 'خیابان ولیعصر، کوچه دوم، پلاک ۱۲',
        'shipping_postal_code': '1234567890',
    }

    def setUp(self):
        self.client = APIClient()
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
        self.client.force_authenticate(self.user)
        self.client.post(
            '/api/cart/',
            {'product_id': str(self.product.id), 'quantity': 1},
            format='json',
        )

    def post(self, **overrides):
        return self.client.post('/api/orders/', {**self.VALID, **overrides}, format='json')

    def test_blank_optional_looking_fields_are_reported_per_field(self):
        """The old serializer rejected blanks with DRF's generic message and no
        `detail` key, so the UI could only say "خطا در ثبت سفارش"."""
        response = self.client.post(
            '/api/orders/',
            {key: '' for key in self.VALID},
            format='json',
        )
        self.assertEqual(response.status_code, 400)
        for field in self.VALID:
            self.assertIn(field, response.data, f'{field} was not reported')
            self.assertIn('الزامی', str(response.data[field][0]))

    def test_name_and_postal_code_are_required(self):
        for field in ('shipping_name', 'shipping_postal_code'):
            with self.subTest(field=field):
                response = self.post(**{field: ''})
                self.assertEqual(response.status_code, 400)
                self.assertIn(field, response.data)

    def test_phone_must_be_an_iranian_mobile_number(self):
        for bad in ('12345', '02112345678', '0912345678'):
            with self.subTest(phone=bad):
                response = self.post(shipping_phone=bad)
                self.assertEqual(response.status_code, 400)
                self.assertIn('shipping_phone', response.data)

    def test_postal_code_must_be_ten_digits(self):
        response = self.post(shipping_postal_code='12345')
        self.assertEqual(response.status_code, 400)
        self.assertIn('shipping_postal_code', response.data)

    def test_persian_digits_are_accepted_and_normalized(self):
        response = self.post(shipping_phone='۰۹۱۲۳۴۵۶۷۸۹', shipping_postal_code='۱۲۳۴۵۶۷۸۹۰')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['shipping_phone'], '09123456789')
        self.assertEqual(response.data['shipping_postal_code'], '1234567890')

    def test_too_short_address_is_rejected(self):
        response = self.post(shipping_address='تهران')
        self.assertEqual(response.status_code, 400)
        self.assertIn('shipping_address', response.data)

    def test_address_belonging_to_another_user_is_reported_on_the_field(self):
        other = User.objects.create_user(phone='09120000001')
        address = Address.objects.create(
            user=other,
            province='تهران',
            city='تهران',
            address_line='خیابان آزادی، پلاک ۵',
            postal_code='1234567890',
            receiver_name='کاربر دیگر',
            receiver_phone='09120000001',
        )
        response = self.client.post('/api/orders/', {'address_id': str(address.id)}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('address_id', response.data)

    def test_saved_address_supplies_every_shipping_field(self):
        address = Address.objects.create(
            user=self.user,
            province='فارس',
            city='شیراز',
            address_line='بلوار زند، پلاک ۹',
            postal_code='7134567890',
            receiver_name='مریم رضایی',
            receiver_phone='09123456789',
        )
        response = self.client.post(
            '/api/orders/',
            {'address_id': str(address.id), 'shipping_plate_number': '9'},
            format='json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['shipping_city'], 'شیراز')
        self.assertEqual(response.data['shipping_postal_code'], '7134567890')
        self.assertEqual(response.data['shipping_plate_number'], '9')

    def test_insufficient_stock_names_the_product_and_the_remaining_count(self):
        self.product.stock = 0
        self.product.save(update_fields=['stock'])
        response = self.post()
        self.assertEqual(response.status_code, 400)
        self.assertIn('کرم تست', response.data['detail'])
