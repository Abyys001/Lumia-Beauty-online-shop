from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from apps.catalog.models import Category, Product, StockMovement, StoreSettings
from apps.admin_api.services.inventory import adjust_product_stock, is_low_stock, InventoryAdjustmentError

User = get_user_model()


class InventoryServiceTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='پوست', slug='skin')
        self.product = Product.objects.create(
            name='کرم تست',
            slug='cream-test',
            description='test',
            category=self.category,
            price=100000,
            stock=10,
            stock_pack_sizes=[1, 6, 12],
            sku='INV-001',
        )

    def test_adjust_by_pack_increases_stock(self):
        product, movement = adjust_product_stock(
            self.product.id,
            mode='pack',
            pack_size=12,
            pack_count=2,
        )
        self.assertEqual(product.stock, 34)
        self.assertEqual(movement.delta, 24)
        self.assertEqual(movement.pack_size, 12)
        self.assertEqual(movement.pack_count, 2)

    def test_invalid_pack_size_raises(self):
        with self.assertRaises(InventoryAdjustmentError):
            adjust_product_stock(
                self.product.id,
                mode='pack',
                pack_size=10,
                pack_count=1,
            )

    def test_set_absolute_stock(self):
        product, movement = adjust_product_stock(
            self.product.id,
            mode='set',
            absolute_stock=100,
        )
        self.assertEqual(product.stock, 100)
        self.assertEqual(movement.delta, 90)

    def test_stock_movement_logged(self):
        _, movement = adjust_product_stock(self.product.id, mode='delta', delta=5)
        self.assertTrue(StockMovement.objects.filter(id=movement.id).exists())

    def test_per_product_threshold(self):
        self.product.low_stock_threshold = 3
        self.product.stock = 4
        self.product.save()
        self.assertFalse(is_low_stock(self.product))
        self.product.stock = 2
        self.assertTrue(is_low_stock(self.product))


class InventoryApiTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(phone='09120000000', is_staff=True)
        self.client = APIClient()
        self.client.force_authenticate(user=self.staff)
        self.category = Category.objects.create(name='cat', slug='cat')
        self.product = Product.objects.create(
            name='P1',
            slug='p1',
            description='d',
            category=self.category,
            price=50000,
            stock=5,
            stock_pack_sizes=[1, 12],
            sku='P1SKU',
        )
        settings = StoreSettings.get_settings()
        settings.default_low_stock_threshold = 5
        settings.save()

    def test_adjust_api_pack(self):
        response = self.client.post('/api/admin/inventory/adjust/', {
            'product_id': str(self.product.id),
            'mode': 'pack',
            'pack_size': 12,
            'pack_count': 1,
            'note': 'ورودی تست',
        }, format='json')
        self.assertEqual(response.status_code, 200)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 17)

    def test_summary_endpoint(self):
        response = self.client.get('/api/admin/inventory/summary/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('low_stock', response.data)

    def test_list_with_status_filter(self):
        response = self.client.get('/api/admin/inventory/', {'status': 'low', 'threshold': 10})
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
