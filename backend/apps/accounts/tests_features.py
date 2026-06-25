from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import WishlistItem
from apps.catalog.models import Brand, Category, Product
from apps.orders.models import Order, OrderItem

User = get_user_model()


class FeaturePackAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone='09123456789')
        self.staff = User.objects.create_user(phone='09111111111', is_staff=True)
        self.category = Category.objects.create(name='Cat', slug='cat')
        self.brand = Brand.objects.create(name='Brand', slug='brand')
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            sku='SKU-TEST-1',
            category=self.category,
            brand=self.brand,
            price=100000,
            stock=3,
            is_active=True,
        )
        self.product2 = Product.objects.create(
            name='Other Product',
            slug='other-product',
            sku='SKU-TEST-2',
            category=self.category,
            brand=self.brand,
            price=200000,
            stock=10,
            is_active=True,
        )
        self.order = Order.objects.create(
            user=self.user,
            order_number='LB12345678',
            status=Order.STATUS_SHIPPED,
            subtotal=100000,
            total=150000,
            shipping_cost=50000,
            shipping_name='Test',
            shipping_phone='09123456789',
            shipping_province='تهران',
            shipping_city='تهران',
            shipping_address='خیابان تست',
            tracking_number='123456789012345678901234',
        )
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            product_name=self.product.name,
            product_price=self.product.price,
            quantity=1,
            subtotal=self.product.price,
        )

    def _auth(self, user):
        self.client.force_authenticate(user=user)

    def test_order_serializer_includes_tracking(self):
        self._auth(self.user)
        response = self.client.get(reverse('order-detail', kwargs={'order_number': self.order.order_number}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['tracking_number'], '123456789012345678901234')

    def test_wishlist_add_list_remove(self):
        self._auth(self.user)
        add = self.client.post('/api/user/wishlist/', {'product_id': str(self.product.id)}, format='json')
        self.assertEqual(add.status_code, status.HTTP_201_CREATED)
        self.assertTrue(WishlistItem.objects.filter(user=self.user, product=self.product).exists())

        listing = self.client.get('/api/user/wishlist/')
        self.assertEqual(listing.status_code, status.HTTP_200_OK)
        self.assertEqual(len(listing.data), 1)

        ids = self.client.get('/api/user/wishlist/ids/')
        self.assertIn(str(self.product.id), ids.data)

        delete = self.client.delete(f'/api/user/wishlist/{self.product.id}/')
        self.assertEqual(delete.status_code, status.HTTP_204_NO_CONTENT)

    def test_related_products(self):
        response = self.client.get('/api/products/test-product/related/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any(p['slug'] == 'other-product' for p in response.data))

    def test_low_stock_admin(self):
        self._auth(self.staff)
        response = self.client.get('/api/admin/inventory/low-stock/', {'threshold': 5})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data['count'], 1)
        slugs = [p['slug'] for p in response.data['results']]
        self.assertIn('test-product', slugs)

    def test_notifications_summary(self):
        self._auth(self.staff)
        response = self.client.get('/api/admin/notifications/summary/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('pending_orders', response.data)
        self.assertIn('low_stock_count', response.data)
