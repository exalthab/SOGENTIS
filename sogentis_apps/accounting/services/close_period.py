# accounting/services/close_period.py
from __future__ import annotations

from datetime import date
from typing import Optional

from django.db import transaction
from django.utils import timezone

from accounting.models import Account, JournalEntry, JournalLine
from accounting.models.audit import AccountingAudit
from accounting.models.ledger import LedgerBalance
from accounting.models.period import AccountingPeriod
from accounting.selectors.report_queries import compute_trial_balance


def _posted_entry_filter_kwargs() -> dict:
    return {"status": getattr(JournalEntry.Status, "POSTED", "POSTED")}


@transaction.atomic
def close_period(
    *,
    period: AccountingPeriod,
    actor=None,
    force: bool = False,
) -> AccountingPeriod:
    if period.is_closed and not force:
        return period

    posted_kwargs = _posted_entry_filter_kwargs()
    field_names = {f.name for f in JournalEntry._meta.fields}

    entries = JournalEntry.objects.filter(date__gte=period.start_date, date__lte=period.end_date)
    if period.pole:
        if "pole" in field_names:
            entries = entries.filter(pole=period.pole)
    if period.company_code:
        if "company_code" in field_names:
            entries = entries.filter(company_code=period.company_code)

    if "status" in field_names:
        unposted_exists = entries.exclude(**posted_kwargs).exists()
        if unposted_exists and not force:
            raise ValueError("Unposted journal entries exist in this period.")

    # Snapshot trial-balance movements for the period
    tb = compute_trial_balance(pole=period.pole, company_code=period.company_code, start=period.start_date, end=period.end_date)
    rows = tb["rows"]

    # On calcule aussi l'opening depuis avant start_date
    opening_tb = compute_trial_balance(pole=period.pole, company_code=period.company_code, start=None, end=period.start_date.replace(day=period.start_date.day) )
    # NOTE: opening_tb ci-dessus inclut start_date; on corrige en prenant < start_date via lignes directes
    # (service simple: recalcul opening propre)
    opening_lines = JournalLine.objects.select_related("account", "entry").filter(entry__date__lt=period.start_date)
    # posted filter
    if "status" in field_names:
        opening_lines = opening_lines.filter(entry__status=posted_kwargs["status"])
    if period.pole:
        opening_lines = opening_lines.filter(account__pole=period.pole)
    if period.company_code:
        opening_lines = opening_lines.filter(account__company_code=period.company_code)

    # build opening by account
    opening_map = {}
    for l in opening_lines.iterator():
        aid = l.account_id
        o = opening_map.setdefault(aid, {"debit": 0, "credit": 0})
        o["debit"] += float(l.debit or 0)
        o["credit"] += float(l.credit or 0)

    # upsert ledger snapshot
    for r in rows:
        acc = r["account"]
        mov_net = r["net"]  # debit-credit
        # movement debit/credit from net is not enough; we store aggregated by querying again for accuracy
        # but lightweight: infer from tb debit/credit columns
        # Here, we re-use net and store movement on the side it lands.
        mov_debit = r["debit"]
        mov_credit = r["credit"]

        o = opening_map.get(acc.id, {"debit": 0, "credit": 0})
        opening_debit = o["debit"]
        opening_credit = o["credit"]

        # closing = opening + movements (net)
        opening_net = (opening_debit - opening_credit)
        closing_net = opening_net + float(mov_net)

        if closing_net >= 0:
            closing_debit = closing_net
            closing_credit = 0.0
        else:
            closing_debit = 0.0
            closing_credit = -closing_net

        LedgerBalance.objects.update_or_create(
            period=period,
            account=acc,
            defaults={
                "currency": (acc.currency or ""),
                "opening_debit": opening_debit,
                "opening_credit": opening_credit,
                "movement_debit": float(mov_debit or 0),
                "movement_credit": float(mov_credit or 0),
                "closing_debit": closing_debit,
                "closing_credit": closing_credit,
            },
        )

    period.status = AccountingPeriod.Status.CLOSED
    period.closed_at = timezone.now()
    period.closed_by = getattr(actor, "username", "") or getattr(actor, "email", "") or "system"
    period.save()

    AccountingAudit.log(
        action=AccountingAudit.Action.CLOSE_PERIOD,
        actor=actor,
        pole=period.pole,
        company_code=period.company_code,
        obj=period,
        message="Period closed",
        metadata={"period_id": period.id, "start": str(period.start_date), "end": str(period.end_date)},
    )

    return period


@transaction.atomic
def open_period(*, period: AccountingPeriod, actor=None) -> AccountingPeriod:
    period.status = AccountingPeriod.Status.OPEN
    period.closed_at = None
    period.closed_by = ""
    period.save()

    AccountingAudit.log(
        action=AccountingAudit.Action.OPEN_PERIOD,
        actor=actor,
        pole=period.pole,
        company_code=period.company_code,
        obj=period,
        message="Period re-opened",
        metadata={"period_id": period.id},
    )
    return period
