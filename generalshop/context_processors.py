from .cart import get_cart


def cart_count(request):
    """Number of items in the visitor's cart, for the header badge."""
    cart = get_cart(request)
    return {"cart_count": cart.item_count if cart else 0}
