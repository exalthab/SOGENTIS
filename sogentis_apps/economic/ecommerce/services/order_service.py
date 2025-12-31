# economic/ecommerce/services/order_service.py
from decimal import Decimal
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from ..models.order import Order
from ..models.order_item import OrderItem
from ..models.product import Product
from .cart_service import cart_total, clear_cart


@transaction.atomic
def create_order_from_cart(user, cart):
    if not cart.items.exists():
        raise ValueError(_("Le panier est vide"))

    # lock produits pour éviter survente
    items = list(cart.items.select_related("product"))
    product_ids = [i.product_id for i in items]

    products_locked = (
        Product.objects.select_for_update()
        .filter(id__in=product_ids)
        .in_bulk(field_name="id")
    )

    # vérifier stock
    for item in items:
        p = products_locked[item.product_id]
        if not p.is_active:
            raise ValueError(_("Produit indisponible"))
        if p.stock < item.quantity:
            raise ValueError(_(f"Stock insuffisant pour {p}"))

    total = Decimal(cart_total(cart))

    order = Order.objects.create(
        user=user,
        total_amount=total,
        status="pending",
    )

    # créer lignes + décrément stock
    for item in items:
        p = products_locked[item.product_id]

        OrderItem.objects.create(
            order=order,
            product=p,
            quantity=item.quantity,
            unit_price=p.price,
        )

        p.stock -= item.quantity
        p.save(update_fields=["stock"])

    clear_cart(cart)
    return order
