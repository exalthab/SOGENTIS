# economic/ecommerce/models/order_item.py

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class OrderItem(models.Model):
    order = models.ForeignKey(
        "Order",
        on_delete=models.CASCADE,
        related_name="items"
    )
    product = models.ForeignKey(
        "Product",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ordered_items"
    )

    product_name = models.CharField(max_length=255, default="N/A")
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = _("Article de commande")
        verbose_name_plural = _("Articles de commande")

    def __str__(self):
        return f"{self.product_name} × {self.quantity}"

    @property
    def subtotal(self):
        return self.unit_price * self.quantity

    @property
    def formatted_unit_price(self):
        return f"{self.unit_price:,.0f} FCFA"

    @property
    def formatted_subtotal(self):
        return f"{self.subtotal:,.0f} FCFA"

    def save(self, *args, **kwargs):
        if self.product and not self.product_name:
            self.product_name = self.product.safe_translation_getter("name", any_language=True)
        super().save(*args, **kwargs)





# # economic/ecommerce/models/order_item.py
# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from django.utils import timezone  # ✅ needed for default

# class OrderItem(models.Model):

#     order = models.ForeignKey(
#         "Order",
#         on_delete=models.CASCADE,
#         related_name="items"
#     )

#     # Produit lié (optionnel)
#     product = models.ForeignKey(
#         "Product",
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name="ordered_items"
#     )

#     # Nom figé au moment de l'achat
#     product_name = models.CharField(max_length=255)

#     quantity = models.PositiveIntegerField(default=1)
#     unit_price = models.DecimalField(max_digits=12, decimal_places=2)

#     # ✅ new field
#     created_at = models.DateTimeField(default=timezone.now)

#     class Meta:
#         verbose_name = _("Article de commande")
#         verbose_name_plural = _("Articles de commande")

#     def __str__(self):
#         return f"{self.product_name} × {self.quantity}"

#     @property
#     def subtotal(self):
#         return self.unit_price * self.quantity

#     @property
#     def formatted_unit_price(self):
#         return f"{self.unit_price:,.0f} FCFA"

#     @property
#     def formatted_subtotal(self):
#         return f"{self.subtotal:,.0f} FCFA"






# class OrderItem(models.Model):
#     order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
#     product = models.ForeignKey('Product', on_delete=models.PROTECT)
#     quantity = models.PositiveIntegerField()
#     price = models.PositiveIntegerField()  # copie prix à la commande

#     def __str__(self):
#         return f"{self.product.name} x{self.quantity}"