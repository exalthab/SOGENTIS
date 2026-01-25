# economic/ecommerce/models/sku_sequence.py
from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _


class SkuSequence(models.Model):
    """
    Séquence SKU par (vendor_code, category_code).
    Anti-collision en prod via select_for_update() côté Product.
    """
    vendor_code = models.CharField(max_length=8, verbose_name=_("Code vendeur"))
    category_code = models.CharField(max_length=8, verbose_name=_("Code catégorie"))
    last_number = models.PositiveIntegerField(default=0, verbose_name=_("Dernier numéro"))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Créé le"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Mis à jour le"))

    class Meta:
        verbose_name = _("Séquence SKU")
        verbose_name_plural = _("Séquences SKU")
        constraints = [
            models.UniqueConstraint(
                fields=["vendor_code", "category_code"],
                name="uniq_sku_sequence_vendor_category",
            )
        ]
        indexes = [
            models.Index(fields=["vendor_code", "category_code"]),
        ]

    def __str__(self) -> str:
        return f"{self.vendor_code}-{self.category_code}-{self.last_number:04d}"
