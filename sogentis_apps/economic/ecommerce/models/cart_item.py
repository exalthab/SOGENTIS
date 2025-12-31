# economic/ecommerce/models/cart_item.py

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from .cart import Cart
from .product import Product


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name=_("Panier"),
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="cart_items",
        verbose_name=_("Produit"),
    )

    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name=_("Quantité"),
    )

    unit_price = models.DecimalField(
        _("Prix unitaire"),
        max_digits=10,
        decimal_places=2,
        default=0.00,
    )

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = _("Article du panier")
        verbose_name_plural = _("Articles du panier")
        constraints = [
            models.UniqueConstraint(
                fields=["cart", "product"],
                name="unique_product_per_cart",
            )
        ]

    def __str__(self):
        return f"{self.product} × {self.quantity}"

    @property
    def total_price(self):
        return self.unit_price * self.quantity





# # /economic/ecommerce/models/cart_item.py

# from django.db import models
# from django.utils.translation import gettext_lazy as _

# from .cart import Cart
# from .product import Product


# class CartItem(models.Model):
#     cart = models.ForeignKey(
#         Cart,
#         on_delete=models.CASCADE,
#         related_name="items",
#         verbose_name=_("Panier"),
#     )

#     product = models.ForeignKey(
#         Product,
#         on_delete=models.CASCADE,
#         related_name="cart_items",
#         verbose_name=_("Produit"),
#     )

#     quantity = models.PositiveIntegerField(
#         default=1,
#         verbose_name=_("Quantité"),
#     )

#     class Meta:
#         verbose_name = _("Article du panier")
#         verbose_name_plural = _("Articles du panier")
#         constraints = [
#             models.UniqueConstraint(
#                 fields=["cart", "product"],
#                 name="unique_product_per_cart",
#             )
#         ]

#     def __str__(self):
#         return f"{self.product} × {self.quantity}"
