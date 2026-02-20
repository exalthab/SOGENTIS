# accounting/models/period.py
from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _


class AccountingPeriod(models.Model):
    """
    Période comptable (ex: mois, trimestre, année) pour close/re-open.
    Scope: pole + company_code.
    """

    class Status(models.TextChoices):
        OPEN = "OPEN", _("Open")
        CLOSED = "CLOSED", _("Closed")

    pole = models.CharField(max_length=16, blank=True, default="", db_index=True)
    company_code = models.CharField(max_length=32, blank=True, default="", db_index=True)

    name = models.CharField(max_length=80, blank=True, default="")  # ex: "2026-01"
    start_date = models.DateField(db_index=True)
    end_date = models.DateField(db_index=True)

    status = models.CharField(max_length=16, choices=Status.choices, default=Status.OPEN, db_index=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    closed_by = models.CharField(max_length=64, blank=True, default="")

    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-start_date", "-id"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(end_date__gte=models.F("start_date")),
                name="acct_period_end_gte_start",
            ),
            models.UniqueConstraint(
                fields=["pole", "company_code", "start_date", "end_date"],
                name="uniq_acct_period_scope_range",
            ),
        ]
        indexes = [
            models.Index(fields=["pole", "company_code", "status"]),
            models.Index(fields=["pole", "company_code", "start_date"]),
        ]

    def __str__(self) -> str:
        scope = "/".join([p for p in [self.pole, self.company_code] if p]) or "GLOBAL"
        nm = self.name or f"{self.start_date}→{self.end_date}"
        return f"{scope} • {nm} ({self.status})"

    def save(self, *args, **kwargs):
        self.pole = (self.pole or "").strip().upper()
        self.company_code = (self.company_code or "").strip().upper()
        self.name = (self.name or "").strip()
        super().save(*args, **kwargs)

    def contains(self, d) -> bool:
        return bool(d and self.start_date <= d <= self.end_date)

    @property
    def is_closed(self) -> bool:
        return self.status == self.Status.CLOSED
