# economic/ecommerce/models/product_image.py

from django.db import models
from django.utils.translation import gettext_lazy as _
from .product import Product
from django.utils import timezone


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="economic/products/gallery/")
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)  # <- ajouté


    class Meta:
        verbose_name = _("Image produit")
        verbose_name_plural = _("Images produits")
        ordering = ["-is_primary"]

    def __str__(self):
        return f"{self.product} — image"
