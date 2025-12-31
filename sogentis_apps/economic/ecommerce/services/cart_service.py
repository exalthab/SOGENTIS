# economic/ecommerce/services/cart_service.py
from django.shortcuts import get_object_or_404
from ..models.cart import Cart
from ..models.cart_item import CartItem
from ..models.product import Product


def get_or_create_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


def add_product_to_cart(user, product_id, quantity=1):
    cart = get_or_create_cart(user)
    product = get_object_or_404(Product, id=product_id, is_active=True)

    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={"quantity": quantity},
    )

    if not created:
        item.quantity += quantity
        item.save()

    return item


def remove_cart_item(item_id, user):
    cart = get_or_create_cart(user)
    CartItem.objects.filter(id=item_id, cart=cart).delete()


def clear_cart(cart):
    cart.items.all().delete()


def cart_total(cart):
    return sum(item.product.price * item.quantity for item in cart.items.all())
