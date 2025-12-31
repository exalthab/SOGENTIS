# economic/ecommerce/models/cart.py

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .product import Product


class Cart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="ecom_carts",
    )
    session_key = models.CharField(max_length=64, blank=True, null=True, db_index=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = _("Panier")
        verbose_name_plural = _("Paniers")

    def __str__(self):
        return f"Cart({self.user_id or self.session_key})"

    @property
    def items_count(self) -> int:
        return sum(i.quantity for i in self.items.all())

    @property
    def subtotal(self):
        return sum(i.subtotal for i in self.items.all())

    def clear(self):
        self.items.all().delete()


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="cart_items")
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = _("Article de panier")
        verbose_name_plural = _("Articles de panier")
        unique_together = ("cart", "product")

    def __str__(self):
        return f"{self.product} x{self.quantity}"

    @property
    def subtotal(self):
        return self.unit_price * self.quantity

    def save(self, *args, **kwargs):
        if not self.unit_price:
            self.unit_price = self.product.discounted_price
        super().save(*args, **kwargs)
