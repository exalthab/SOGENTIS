# accounting/services/posting.py
from __future__ import annotations

from decimal import Decimal
from typing import Optional

from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.utils import timezone

from accounting.models import Account, Journal, JournalEntry, JournalLine


# ----------------------------
# System defaults (QB-like)
# ----------------------------
DEFAULT_JOURNALS = {
    "RECEIPTS": ("RECEIPTS", "Encaissements"),
}

# key -> (code, name, type, subtype, reconcilable)
DEFAULT_ACCOUNTS = {
    # Assets (trésorerie)
    "CASH": ("1010", "Caisse", Account.Type.ASSET, Account.Subtype.CASH, True),
    "BANK": ("1020", "Banque", Account.Type.ASSET, Account.Subtype.BANK, True),
    "MOBILE": ("1030", "Mobile Money", Account.Type.ASSET, Account.Subtype.BANK, True),
    "PAYPAL": ("1040", "PayPal", Account.Type.ASSET, Account.Subtype.BANK, True),

    # Expense (fees)
    "FEES": ("6100", "Frais paiement / banque", Account.Type.EXPENSE, Account.Subtype.FEES, False),

    # Income
    "REV_ECOM": ("7010", "Ventes e-commerce", Account.Type.INCOME, Account.Subtype.SALES, False),
    "REV_FORM": ("7020", "Formations", Account.Type.INCOME, Account.Subtype.TRAINING_REVENUE, False),
    "REV_PREST": ("7030", "Prestations & packs", Account.Type.INCOME, Account.Subtype.SERVICE_REVENUE, False),
    "REV_DON": ("7040", "Dons", Account.Type.INCOME, Account.Subtype.DONATION_INCOME, False),
    "REV_OTHER": ("7090", "Autres produits", Account.Type.OTHER_INCOME, Account.Subtype.SALES, False),
}


def _company_from_pole(pole: str) -> str:
    pole = (pole or Account.Pole.ECONOMIC).strip().upper()
    return pole


def _ensure_journal(code: str, name: str, *, pole: str, currency: str = "XOF") -> Journal:
    pole = (pole or Account.Pole.ECONOMIC).strip().upper()
    defaults = {
        "name": name,
        "pole": pole,
        "default_currency": (currency or "XOF").upper(),
        "is_active": True,
        "is_system": True,
    }
    j, created = Journal.objects.get_or_create(code=code, defaults=defaults)
    if not created:
        changed = False
        for f, v in defaults.items():
            if hasattr(j, f) and getattr(j, f) != v:
                setattr(j, f, v)
                changed = True
        if changed:
            j.save()
    return j


def _ensure_account(key: str, *, pole: str, company_code: str, currency: str = "XOF") -> Account:
    code, name, typ, subtype, reconcilable = DEFAULT_ACCOUNTS[key]
    return Account.ensure(
        pole=pole,
        company_code=company_code,
        code=code,
        name=name,
        type=typ,
        subtype=subtype,
        currency=currency,
        is_system=True,
        is_active=True,
        is_reconcilable=reconcilable,
        order=int(code) * 10 if str(code).isdigit() else 1000,
    )


def _ensure_system_defaults(*, pole: str, company_code: str, currency: str) -> None:
    # Journaux
    for _, (j_code, j_name) in DEFAULT_JOURNALS.items():
        _ensure_journal(j_code, j_name, pole=pole, currency=currency)

    # Comptes système
    for key in DEFAULT_ACCOUNTS.keys():
        _ensure_account(key, pole=pole, company_code=company_code, currency=currency)


def _cash_account_key_by_provider(provider: str) -> str:
    p = (provider or "").lower().strip()
    if p in ("wave", "orange_money", "orange"):
        return "MOBILE"
    if p == "paypal":
        return "PAYPAL"
    if p in ("stripe", "visa"):
        return "BANK"
    return "CASH"


def _revenue_account_key_by_purpose(purpose: str) -> str:
    pu = (purpose or "").upper().strip()
    if pu == "DONATION":
        return "REV_DON"
    if pu == "ECOM_ORDER":
        return "REV_ECOM"
    if pu == "FORMATION":
        return "REV_FORM"
    if pu in ("PRESTATION", "PACK"):
        return "REV_PREST"
    if pu in ("PUBLICATION",):
        return "REV_OTHER"
    return "REV_OTHER"


def _intent_object_id(intent) -> str:
    if getattr(intent, "pk", None):
        return str(intent.pk)
    if getattr(intent, "id", None):
        return str(intent.id)
    if getattr(intent, "uuid", None):
        return str(intent.uuid)
    return ""


@transaction.atomic
def post_payment_intent(intent) -> Optional[JournalEntry]:
    """
    Posting double-écriture depuis payments.PaymentIntent (appelé depuis intent.mark_paid()).

    - Débit: trésorerie (selon provider) => montant net
    - Débit: frais (si fee>0)
    - Crédit: produit => montant brut
    Idempotent: (content_type, object_id, kind=PAYMENT)
    """
    amount = Decimal(getattr(intent, "amount", 0) or 0)
    if amount <= 0:
        return None

    if (getattr(intent, "status", "") or "").upper() != "PAID":
        return None

    pole = (getattr(intent, "pole", "") or Account.Pole.ECONOMIC).strip().upper()
    currency = (getattr(intent, "currency", None) or "XOF").upper()
    provider = (getattr(intent, "provider", "") or "").strip()
    purpose = (getattr(intent, "purpose", "") or "").strip()
    desc = (getattr(intent, "description", "") or "").strip()
    ref = (getattr(intent, "reference", "") or "").strip()

    metadata = getattr(intent, "metadata", None) or {}
    company_code = (metadata.get("company_code") or _company_from_pole(pole) or "").strip().upper()

    # Fee (optionnel)
    fee = Decimal(metadata.get("fee") or metadata.get("provider_fee") or 0)
    if fee < 0:
        fee = Decimal("0.00")
    if fee > amount:
        fee = amount

    _ensure_system_defaults(pole=pole, company_code=company_code, currency=currency)

    ct = ContentType.objects.get_for_model(intent.__class__)
    obj_id = _intent_object_id(intent)
    if not obj_id:
        return None

    # Idempotent
    existing = JournalEntry.objects.filter(
        content_type=ct,
        object_id=obj_id,
        kind=JournalEntry.Kind.PAYMENT,
    ).first()
    if existing:
        if getattr(existing, "status", None) != JournalEntry.Status.POSTED:
            existing.post()
        return existing

    # Journal
    j_code, j_name = DEFAULT_JOURNALS["RECEIPTS"]
    journal = _ensure_journal(j_code, j_name, pole=pole, currency=currency)

    # Accounts
    cash_key = _cash_account_key_by_provider(provider)
    rev_key = _revenue_account_key_by_purpose(purpose)

    acc_cash = _ensure_account(cash_key, pole=pole, company_code=company_code, currency=currency)
    acc_rev = _ensure_account(rev_key, pole=pole, company_code=company_code, currency=currency)
    acc_fee = _ensure_account("FEES", pole=pole, company_code=company_code, currency=currency) if fee > 0 else None

    memo = (desc or f"Payment {ref}".strip())[:240]

    entry = JournalEntry.objects.create(
        journal=journal,
        date=timezone.localdate(),
        memo=memo,
        kind=JournalEntry.Kind.PAYMENT,
        status=JournalEntry.Status.DRAFT,
        content_type=ct,
        object_id=obj_id,
        metadata={
            "intent_uuid": str(getattr(intent, "uuid", "") or ""),
            "payment_reference": ref,
            "provider": provider,
            "provider_ref": (getattr(intent, "provider_ref", "") or "").strip(),
            "purpose": purpose,
            "pole": pole,
            "company_code": company_code,
            "amount": str(amount),
            "fee": str(fee),
            "currency": currency,
        },
    )

    net = amount - fee

    # 1) Débit trésorerie (net)
    JournalLine.objects.create(
        entry=entry,
        account=acc_cash,
        label=(desc or ref or "Encaissement").strip()[:240],
        debit=net,
        credit=Decimal("0.00"),
        currency=currency,
        amount_fx=net,
    )

    # 2) Débit frais (si applicable)
    if fee > 0 and acc_fee is not None:
        JournalLine.objects.create(
            entry=entry,
            account=acc_fee,
            label="Frais provider"[:240],
            debit=fee,
            credit=Decimal("0.00"),
            currency=currency,
            amount_fx=fee,
        )

    # 3) Crédit produit (brut)
    JournalLine.objects.create(
        entry=entry,
        account=acc_rev,
        label=(desc or ref or "Produit").strip()[:240],
        debit=Decimal("0.00"),
        credit=amount,
        currency=currency,
        amount_fx=amount,
    )

    entry.post()
    return entry
