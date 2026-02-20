# accounting/models/sequence.py
from __future__ import annotations

from django.db import models, transaction
from django.utils import timezone


class AccountingSequence(models.Model):
    """
    Séquence atomique (pour refs type JE-YYYYMM-00001).
    """
    key = models.CharField(max_length=120, unique=True, db_index=True)
    value = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["key", "id"]

    def __str__(self) -> str:
        return f"{self.key}={self.value}"

    @classmethod
    @transaction.atomic
    def next_value(cls, key: str) -> int:
        key = (key or "").strip()
        obj, _ = cls.objects.select_for_update().get_or_create(key=key, defaults={"value": 0})
        obj.value += 1
        obj.updated_at = timezone.now()
        obj.save(update_fields=["value", "updated_at"])
        return obj.value
