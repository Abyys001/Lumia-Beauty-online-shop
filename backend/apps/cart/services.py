from django.conf import settings
from django.db import transaction

from .models import Cart


def _lock_cart(cart):
    return Cart.objects.select_for_update().get(pk=cart.pk)


@transaction.atomic
def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart = _lock_cart(cart)
        if not request.session.session_key:
            request.session.create()
        session_cart = Cart.objects.select_for_update().filter(
            session_key=request.session.session_key,
            user__isnull=True,
        ).first()
        if session_cart and session_cart.items.exists():
            for item in session_cart.items.select_related('product').select_for_update():
                existing = cart.items.select_for_update().filter(product=item.product).first()
                if existing:
                    existing.quantity = min(
                        existing.quantity + item.quantity,
                        item.product.stock,
                        settings.MAX_CART_ITEM_QUANTITY,
                    )
                    existing.save()
                elif item.product.stock > 0:
                    item.quantity = min(item.quantity, item.product.stock, settings.MAX_CART_ITEM_QUANTITY)
                    item.cart = cart
                    item.save(update_fields=['cart', 'quantity'])
            session_cart.delete()
        return cart

    if not request.session.session_key:
        request.session.create()
    cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key, user=None)
    return _lock_cart(cart)
