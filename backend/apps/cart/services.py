from .models import Cart


def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        if not request.session.session_key:
            request.session.create()
        session_cart = Cart.objects.filter(session_key=request.session.session_key, user__isnull=True).first()
        if session_cart and session_cart.items.exists():
            for item in session_cart.items.all():
                existing = cart.items.filter(product=item.product).first()
                if existing:
                    existing.quantity += item.quantity
                    existing.save()
                else:
                    item.cart = cart
                    item.save()
            session_cart.delete()
        return cart

    if not request.session.session_key:
        request.session.create()
    cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key, user=None)
    return cart
