"""Shipping is money, and every number comes from StoreSettings — not from code.

`free_shipping_threshold = 0` keeps the original flat-fee behaviour; anything
above it waives the fee for baskets that reach it. A free-shipping coupon wins
regardless of the threshold.
"""

from django.test import TestCase

from apps.catalog.models import StoreSettings
from apps.catalog.shipping import calculate_shipping_cost, qualifies_for_free_shipping


class ShippingCostTests(TestCase):
    def set_settings(self, cost, threshold):
        settings = StoreSettings.get_settings()
        settings.shipping_cost = cost
        settings.free_shipping_threshold = threshold
        settings.save(update_fields=['shipping_cost', 'free_shipping_threshold'])

    def test_flat_fee_when_no_threshold_is_configured(self):
        self.set_settings(cost=180000, threshold=0)
        self.assertEqual(calculate_shipping_cost(50_000), 180000)
        self.assertEqual(calculate_shipping_cost(900_000_000), 180000)
        self.assertFalse(qualifies_for_free_shipping(900_000_000))

    def test_seller_can_change_the_fee(self):
        self.set_settings(cost=250000, threshold=0)
        self.assertEqual(calculate_shipping_cost(50_000), 250000)

    def test_threshold_waives_the_fee(self):
        self.set_settings(cost=150000, threshold=5_000_000)
        self.assertEqual(calculate_shipping_cost(4_999_999), 150000)
        self.assertEqual(calculate_shipping_cost(5_000_000), 0)
        self.assertTrue(qualifies_for_free_shipping(5_000_000))

    def test_free_shipping_coupon_beats_the_threshold(self):
        self.set_settings(cost=150000, threshold=5_000_000)
        self.assertEqual(calculate_shipping_cost(10_000, free_shipping=True), 0)
        self.assertTrue(qualifies_for_free_shipping(10_000, free_shipping=True))
