# accounting/models/journal.py
from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _


class Journal(models.Model):
    class Pole(models.TextChoices):
        ECONOMIC = "ECONOMIC", _("Économique")
        SOCIAL = "SOCIAL", _("Social")
        INSTITUTION = "INSTITUTION", _("Institution")
        CORE = "CORE", _("Core")

    code = models.CharField(max_length=24, unique=True, db_index=True)
    name = models.CharField(max_length=160)
    pole = models.CharField(max_length=16, choices=Pole.choices, blank=True, default="", db_index=True)

    default_currency = models.CharField(max_length=8, default="XOF")
    is_active = models.BooleanField(default=True)
    is_system = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["code", "id"]

    def __str__(self) -> str:
        return f"{self.code} — {self.name}"
