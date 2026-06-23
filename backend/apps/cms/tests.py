from django.test import TestCase
from rest_framework.test import APIClient

from .models import HomeHero, TrustBadge


class HomeCMSAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_home_cms_is_public(self):
        response = self.client.get('/api/cms/home/')

        self.assertEqual(response.status_code, 200)
        self.assertIn('hero', response.data)
        self.assertIn('trust_badges', response.data)

    def test_home_cms_returns_active_content(self):
        HomeHero.objects.create(
            headline='تیتر تست',
            subheadline='زیرتیتر',
            is_active=True,
        )
        TrustBadge.objects.create(icon='shield', title='تضمین اصالت', sort_order=1)

        response = self.client.get('/api/cms/home/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['hero']['headline'], 'تیتر تست')
        self.assertEqual(len(response.data['trust_badges']), 1)
