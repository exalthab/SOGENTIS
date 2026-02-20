from __future__ import annotations

from decimal import Decimal

from django.db import models


class Tax(models.Model):
    """
    TVA / Taxe simple et stable.
    Ex: code="VAT18", rate=18.00
    """
    code = models.CharField(max_length=32, unique=True, db_index=True)
    name = models.CharField(max_length=255, db_index=True)

    rate = models.DecimalField(max_digits=7, decimal_places=4, default=Decimal("0.0000"))  # 18.0000
    is_inclusive = models.BooleanField(default=False, db_index=True)  # taxe incluse dans prix
    is_active = models.BooleanField(default=True, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        ordering = ["code"]
        indexes = [models.Index(fields=["is_active", "is_inclusive"])]

    def __str__(self) -> str:
        return f"{self.code} ({self.rate}%)"


__all__ = ["Tax"]
