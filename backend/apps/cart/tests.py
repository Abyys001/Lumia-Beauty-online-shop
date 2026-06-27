from django.conf import settings
from django.test import TestCase
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.catalog.models import Category, Product

from .models import Cart, CartItem


class CartConsistencyTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(phone='09123456789')
        self.category = Category.objects.create(name='عطر', slug='perfume')
        self.product = Product.objects.create(
            name='محصول تست',
            slug='test-product',
            description='توضیح تست',
            category=self.category,
            price=100000,
            stock=5,
            sku='TEST-1',
        )

    def test_guest_can_add_and_view_cart(self):
        response = self.client.post(
            '/api/cart/',
            {'product_id': str(self.product.id), 'quantity': 1},
            format='json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['item_count'], 1)

        response = self.client.get('/api/cart/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['item_count'], 1)

    def test_add_to_cart_rejects_quantity_above_limit(self):
        self.client.force_authenticate(self.user)

        response = self.client.post(
            '/api/cart/',
            {'product_id': str(self.product.id), 'quantity': settings.MAX_CART_ITEM_QUANTITY + 1},
            format='json',
        )

        self.assertEqual(response.status_code, 400)

    def test_session_cart_merge_caps_quantity_to_stock(self):
        self.product.stock = 2
        self.product.save(update_fields=['stock'])
        session = self.client.session
        session.save()
        session_cart = Cart.objects.create(session_key=session.session_key)
        CartItem.objects.create(cart=session_cart, product=self.product, quantity=4)
        self.client.force_authenticate(self.user)

        response = self.client.get('/api/cart/')

        self.assertEqual(response.status_code, 200)
        user_cart = Cart.objects.get(user=self.user)
        item = user_cart.items.get(product=self.product)
        self.assertEqual(item.quantity, 2)
