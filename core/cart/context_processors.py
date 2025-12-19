from .cart import CartSession


def cart_processor(request):
    """Add the cart object to the template context."""
    cart = CartSession(request.session)
    return {"cart": cart}
