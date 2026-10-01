"""The visitor's shopping cart: an incomplete Order remembered in their session."""

from django.db import transaction
from django.db.models import F

from .models import Order, OrderedProduct

CART_SESSION_KEY = "cart_order_id"


def get_cart(request):
    """The visitor's open cart with its lines and products loaded, or None."""
    order_id = request.session.get(CART_SESSION_KEY)
    if order_id is None:
        return None
    return (
        Order.objects.filter(pk=order_id, complete=False)
        .prefetch_related("ordered_products__product")
        .first()
    )


def get_or_create_cart(request):
    cart = get_cart(request)
    if cart is None:
        cart = Order.objects.create()
        request.session[CART_SESSION_KEY] = cart.pk
    return cart


@transaction.atomic
def add_product(cart, product):
    line, created = OrderedProduct.objects.get_or_create(order=cart, product=product)
    if not created:
        OrderedProduct.objects.filter(pk=line.pk).update(quantity=F("quantity") + 1)


@transaction.atomic
def remove_one(cart, product):
    """Take one unit out of the cart, dropping the line when none are left."""
    line = OrderedProduct.objects.select_for_update().filter(order=cart, product=product).first()
    if line is None:
        return
    if line.quantity > 1:
        line.quantity = F("quantity") - 1
        line.save(update_fields=["quantity"])
    else:
        line.delete()


def remove_product(cart, product):
    OrderedProduct.objects.filter(order=cart, product=product).delete()


CART_ACTIONS = {"add": add_product, "subtract": remove_one, "remove": remove_product}
