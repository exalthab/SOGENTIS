# economic/ecommerce/models/product_image.py

from django.db import models
from django.utils.translation import gettext_lazy as _

from .product import Product


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name=_("Produit"),
    )

    image = models.ImageField(
        upload_to="products/",
        verbose_name=_("Image"),
    )

    alt_text = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Texte alternatif"),
    )

    is_main = models.BooleanField(
        default=False,
        verbose_name=_("Image principale"),
    )

    class Meta:
        verbose_name = _("Image du produit")
        verbose_name_plural = _("Images du produit")
        ordering = ["-is_main", "id"]

    def __str__(self):
        return f"Image – {self.product}"
