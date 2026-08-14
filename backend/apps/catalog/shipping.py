"""Shipping cost helpers backed by StoreSettings singleton.

Shipping is a flat fee applied to every order (no free-shipping threshold).
"""

DEFAULT_SHIPPING_COST = 150000
DEFAULT_FREE_SHIPPING_THRESHOLD = 0


def get_shipping_settings() -> dict[str, int]:
    from .models import StoreSettings

    settings = StoreSettings.get_settings()
    return {
        'shipping_cost': settings.shipping_cost,
        'free_shipping_threshold': settings.free_shipping_threshold,
    }


def calculate_shipping_cost(subtotal: int, *, free_shipping: bool = False) -> int:
    return get_shipping_settings()['shipping_cost']


def qualifies_for_free_shipping(subtotal: int, *, free_shipping: bool = False) -> bool:
    return False
