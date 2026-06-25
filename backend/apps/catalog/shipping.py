"""Shipping cost helpers backed by StoreSettings singleton."""

DEFAULT_SHIPPING_COST = 50000
DEFAULT_FREE_SHIPPING_THRESHOLD = 500000


def get_shipping_settings() -> dict[str, int]:
    from .models import StoreSettings

    settings = StoreSettings.get_settings()
    return {
        'shipping_cost': settings.shipping_cost,
        'free_shipping_threshold': settings.free_shipping_threshold,
    }


def calculate_shipping_cost(subtotal: int, *, free_shipping: bool = False) -> int:
    cfg = get_shipping_settings()
    if free_shipping or subtotal >= cfg['free_shipping_threshold']:
        return 0
    return cfg['shipping_cost']


def qualifies_for_free_shipping(subtotal: int, *, free_shipping: bool = False) -> bool:
    if free_shipping:
        return True
    return subtotal >= get_shipping_settings()['free_shipping_threshold']
