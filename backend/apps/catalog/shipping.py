"""Shipping cost helpers backed by the StoreSettings singleton.

Both numbers are edited by the seller at /admin/settings/shipping — nothing here
is hardcoded. A `free_shipping_threshold` of 0 disables the threshold entirely,
which is the flat-fee behaviour the shop started with.
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


def qualifies_for_free_shipping(subtotal: int, *, free_shipping: bool = False) -> bool:
    """`free_shipping` comes from a free-shipping coupon and always wins."""
    if free_shipping:
        return True
    threshold = get_shipping_settings()['free_shipping_threshold']
    return bool(threshold) and subtotal >= threshold


def calculate_shipping_cost(subtotal: int, *, free_shipping: bool = False) -> int:
    if qualifies_for_free_shipping(subtotal, free_shipping=free_shipping):
        return 0
    return get_shipping_settings()['shipping_cost']
