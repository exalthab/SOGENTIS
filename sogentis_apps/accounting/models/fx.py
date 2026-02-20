from __future__ import annotations

from decimal import Decimal

from django.db import models


class FxRate(models.Model):
    """
    Taux de change par date (base -> quote).
    Ex: base=XOF quote=EUR date=2026-02-16 rate=0.00152
    """
    base_currency = models.CharField(max_length=3, db_index=True)   # XOF
    quote_currency = models.CharField(max_length=3, db_index=True)  # EUR
    rate_date = models.DateField(db_index=True)

    rate = models.DecimalField(max_digits=18, decimal_places=8, default=Decimal("1.00000000"))
    source = models.CharField(max_length=64, blank=True, default="")  # ECB, manual, etc.

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        unique_together = (("base_currency", "quote_currency", "rate_date"),)
        ordering = ["-rate_date", "base_currency", "quote_currency"]
        indexes = [
            models.Index(fields=["base_currency", "quote_currency", "rate_date"]),
        ]

    def __str__(self) -> str:
        return f"{self.base_currency}/{self.quote_currency} {self.rate_date} = {self.rate}"


__all__ = ["FxRate"]
