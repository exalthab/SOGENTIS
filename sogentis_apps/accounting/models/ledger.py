# accounting/models/ledger.py
from __future__ import annotations

from decimal import Decimal

from django.db import models
from django.utils.translation import gettext_lazy as _

from .account import Account
from .period import AccountingPeriod


class LedgerBalance(models.Model):
    """
    Snapshot (cache) des soldes par compte pour une période (utile au close).
    - opening: solde au début
    - movement: mouvements dans la période
    - closing: solde fin période
    """

    period = models.ForeignKey(AccountingPeriod, on_delete=models.CASCADE, related_name="ledger_balances")
    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name="ledger_balances")

    currency = models.CharField(max_length=8, blank=True, default="")

    opening_debit = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    opening_credit = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))

    movement_debit = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    movement_credit = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))

    closing_debit = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    closing_credit = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["period_id", "account_id"]
        constraints = [
            models.UniqueConstraint(fields=["period", "account"], name="uniq_ledger_balance_period_account"),
        ]
        indexes = [
            models.Index(fields=["period", "account"]),
            models.Index(fields=["account", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.period} • {self.account.code}"

    @property
    def opening_net(self) -> Decimal:
        return Decimal(self.opening_debit or 0) - Decimal(self.opening_credit or 0)

    @property
    def movement_net(self) -> Decimal:
        return Decimal(self.movement_debit or 0) - Decimal(self.movement_credit or 0)

    @property
    def closing_net(self) -> Decimal:
        return Decimal(self.closing_debit or 0) - Decimal(self.closing_credit or 0)

    @property
    def closing_balance_for_report(self) -> Decimal:
        """
        Pour les reports: actif/charges = débit-nature, passif/capitaux/produits = crédit-nature.
        """
        net = self.closing_net
        if self.account.is_debit_nature:
            return net
        return -net
