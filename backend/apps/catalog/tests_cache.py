"""Guards for the catalog cache invalidation contract.

Product detail responses are cached for two hours under their slug. Anything that
survives an edit — a stale entry under the pre-rename slug, a detail payload that
still carries the replaced photo — shows a customer one product's picture next to
another product's details, which is exactly what the cache is not allowed to do.
"""

from io import BytesIO

from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from PIL import Image
from rest_framework.test import APIClient

from apps.catalog.models import Category, Product, ProductImage


def image_file(name='test.png'):
    buffer = BytesIO()
    Image.new('RGB', (10, 10), 'white').save(buffer, format='PNG')
    return SimpleUploadedFile(name, buffer.getvalue(), content_type='image/png')


class ProductCacheInvalidationTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()
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
        ProductImage.objects.create(product=self.product, image=image_file(), is_primary=True)

    def test_renaming_a_product_drops_the_cache_entry_of_the_old_slug(self):
        self.assertEqual(self.client.get('/api/products/test-cream/').status_code, 200)

        product = Product.objects.get(pk=self.product.pk)
        product.slug = 'test-cream-2'
        product.save()

        self.assertEqual(self.client.get('/api/products/test-cream/').status_code, 404)
        self.assertEqual(self.client.get('/api/products/test-cream-2/').status_code, 200)

    def test_a_new_photo_replaces_the_cached_one(self):
        first = self.client.get('/api/products/test-cream/').data['primary_image']

        ProductImage.objects.filter(product=self.product).delete()
        ProductImage.objects.create(product=self.product, image=image_file('other.png'), is_primary=True)

        second = self.client.get('/api/products/test-cream/').data['primary_image']
        self.assertNotEqual(first, second)
        self.assertIn(str(self.product.id), second)
