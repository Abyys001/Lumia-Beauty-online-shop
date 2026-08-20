from django.test import TestCase
from rest_framework.test import APIClient


class APIPermissionTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_products_are_public(self):
        response = self.client.get('/api/products/')

        self.assertEqual(response.status_code, 200)

    def test_cart_is_public(self):
        response = self.client.get('/api/cart/')

        self.assertEqual(response.status_code, 200)
