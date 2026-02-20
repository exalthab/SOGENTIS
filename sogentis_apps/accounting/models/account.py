# accounting/models/account.py
from __future__ import annotations

from decimal import Decimal
from typing import Optional

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _


class Account(models.Model):
    """
    Chart of Accounts style QuickBooks (entreprise).
    - Scope: pole + company_code (multi-pôles / multi-entités)
    - Hiérarchie parent/enfant (sub-account)
    - Type/Subtype (QB-like) (valeurs uniques -> pas d'erreur enum)
    - Opening balance + helpers + seed idempotent (ensure)
    """

    # ----------------------------
    # Multi-pôles / entités
    # ----------------------------
    class Pole(models.TextChoices):
        ECONOMIC = "ECONOMIC", _("Économique")
        SOCIAL = "SOCIAL", _("Social")
        INSTITUTION = "INSTITUTION", _("Institution")
        CORE = "CORE", _("Core")

    # ----------------------------
    # QuickBooks-ish classification
    # ----------------------------
    class Type(models.TextChoices):
        ASSET = "ASSET", _("Actif")
        LIABILITY = "LIABILITY", _("Passif")
        EQUITY = "EQUITY", _("Capitaux propres")
        INCOME = "INCOME", _("Produit")
        COGS = "COGS", _("Coût des ventes (COGS)")
        EXPENSE = "EXPENSE", _("Charge")
        OTHER_INCOME = "OTHER_INCOME", _("Autres produits")
        OTHER_EXPENSE = "OTHER_EXPENSE", _("Autres charges")

    class Subtype(models.TextChoices):
        # --------------------
        # ASSET
        # --------------------
        CASH = "CASH", _("Caisse / Cash")
        BANK = "BANK", _("Compte bancaire")
        ACCOUNTS_RECEIVABLE = "AR", _("Clients (Accounts Receivable)")
        INVENTORY = "INVENTORY", _("Stock / Inventaire")
        FIXED_ASSET = "FIXED_ASSET", _("Immobilisations")
        OTHER_CURRENT_ASSET = "OCA", _("Autres actifs courants")

        # --------------------
        # LIABILITY
        # --------------------
        ACCOUNTS_PAYABLE = "AP", _("Fournisseurs (Accounts Payable)")
        TAX_PAYABLE = "TAX_PAYABLE", _("Taxes à payer")
        PAYROLL_LIABILITY = "PAYROLL_LIABILITY", _("Charges sociales à payer")  # ✅ unique
        OTHER_CURRENT_LIABILITY = "OCL", _("Autres passifs courants")
        LONG_TERM_LIABILITY = "LTL", _("Dettes long terme")

        # Legacy (compat données anciennes)
        PAYROLL_LIABILITY_LEGACY = "PAYROLL", _("Charges sociales à payer (legacy)")

        # --------------------
        # EQUITY
        # --------------------
        OWNER_EQUITY = "OWNER_EQUITY", _("Capital / Apports")
        RETAINED_EARNINGS = "RETAINED_EARNINGS", _("Résultats reportés")

        # Legacy
        RETAINED_EARNINGS_LEGACY = "RETAINED", _("Résultats reportés (legacy)")

        # --------------------
        # INCOME / OTHER_INCOME
        # --------------------
        SALES = "SALES", _("Ventes / Chiffre d'affaires")
        SERVICE_REVENUE = "SERVICE_REVENUE", _("Prestations / Services")
        DONATION_INCOME = "DONATION_INCOME", _("Produits de dons")
        TRAINING_REVENUE = "TRAINING_REVENUE", _("Produits formations")
        DIGITAL_GOODS = "DIGITAL_GOODS", _("Produits numériques")
        SHIPPING_INCOME = "SHIPPING_INCOME", _("Produits livraison")
        DISCOUNT = "DISCOUNT", _("Remises / Discounts")

        # --------------------
        # COGS
        # --------------------
        COGS_DEFAULT = "COGS_DEFAULT", _("COGS")
        PURCHASES = "PURCHASES", _("Achats")

        # --------------------
        # EXPENSE / OTHER_EXPENSE
        # --------------------
        OPERATING_EXPENSE = "OPERATING_EXPENSE", _("Charges d'exploitation")
        FEES = "FEES", _("Frais (paiement, banque)")
        MARKETING = "MARKETING", _("Marketing")
        SOFTWARE = "SOFTWARE", _("Logiciels / SaaS")
        PAYROLL_EXPENSE = "PAYROLL_EXPENSE", _("Salaires")  # ✅ unique (pas PAYROLL)
        RENT = "RENT", _("Loyer")
        UTILITIES = "UTILITIES", _("Eau / Électricité / Télécom")
        TRAVEL = "TRAVEL", _("Déplacements")
        OTHER_EXP = "OTHER_EXP", _("Autres charges")

    # ----------------------------
    # Fields
    # ----------------------------
    pole = models.CharField(
        max_length=16,
        choices=Pole.choices,
        default=Pole.ECONOMIC,
        db_index=True,
        help_text=_("Pôle : ECONOMIC / SOCIAL / INSTITUTION / CORE."),
    )

    company_code = models.CharField(
        max_length=32,
        blank=True,
        default="",
        db_index=True,
        help_text=_("Entité (optionnel) : ex ECONOMIC-SN / SOCIAL-RW / ..."),
    )

    account_number = models.CharField(
        max_length=32,
        blank=True,
        default="",
        db_index=True,
        help_text=_("Numéro de compte (optionnel)."),
    )

    code = models.CharField(max_length=32, db_index=True)
    name = models.CharField(max_length=160)

    type = models.CharField(max_length=16, choices=Type.choices, db_index=True)
    subtype = models.CharField(max_length=32, choices=Subtype.choices, blank=True, default="", db_index=True)

    currency = models.CharField(max_length=8, default="XOF", help_text=_("Devise de reporting."))

    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="children",
        help_text=_("Compte parent (sub-account)."),
    )

    opening_balance = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    opening_balance_date = models.DateField(null=True, blank=True)

    is_active = models.BooleanField(default=True, db_index=True)
    is_system = models.BooleanField(default=False, db_index=True)

    is_reconcilable = models.BooleanField(
        default=False,
        db_index=True,
        help_text=_("Reconciliable (banque/caisse) si activé."),
    )

    description = models.CharField(max_length=240, blank=True, default="")
    order = models.PositiveIntegerField(default=1000, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["pole", "company_code", "order", "code", "id"]
        constraints = [
            models.UniqueConstraint(fields=["pole", "company_code", "code"], name="uniq_account_scope_code"),
            models.CheckConstraint(check=~Q(parent=models.F("id")), name="account_parent_not_self"),
            models.UniqueConstraint(
                fields=["pole", "company_code", "account_number"],
                name="uniq_account_scope_number",
                condition=~Q(account_number=""),
            ),
        ]
        indexes = [
            models.Index(fields=["pole", "company_code", "type", "subtype"]),
            models.Index(fields=["pole", "company_code", "is_active"]),
            models.Index(fields=["pole", "company_code", "is_system"]),
        ]

    def __str__(self) -> str:
        scope = [self.pole] if self.pole else []
        if self.company_code:
            scope.append(self.company_code)
        s = f"{'/'.join(scope)}:" if scope else ""
        num = f"[{self.account_number}] " if self.account_number else ""
        return f"{s}{num}{self.code} — {self.name}"

    def save(self, *args, **kwargs):
        self.code = (self.code or "").strip()
        self.name = (self.name or "").strip()
        self.currency = (self.currency or "XOF").upper()
        self.pole = (self.pole or self.Pole.ECONOMIC).strip().upper()
        self.company_code = (self.company_code or "").strip().upper()
        self.account_number = (self.account_number or "").strip()
        self.subtype = (self.subtype or "").strip()
        super().save(*args, **kwargs)

    def clean(self):
        self.validate_parent_rules()
        if self.parent_id:
            if (self.pole or "") != (self.parent.pole or ""):
                raise ValidationError({"parent": _("Le compte parent doit être dans le même pôle.")})
            if (self.company_code or "") != (self.parent.company_code or ""):
                raise ValidationError({"parent": _("Le compte parent doit être dans la même entité (company_code).")})

    # ----------------------------
    # QuickBooks-like helpers
    # ----------------------------
    @property
    def is_debit_nature(self) -> bool:
        return self.type in {self.Type.ASSET, self.Type.EXPENSE, self.Type.COGS}

    @property
    def is_credit_nature(self) -> bool:
        return self.type in {self.Type.LIABILITY, self.Type.EQUITY, self.Type.INCOME, self.Type.OTHER_INCOME}

    @property
    def fully_qualified_name(self) -> str:
        parts = [self.name]
        node = self.parent
        seen: set[int] = set()
        while node:
            if node.pk and node.pk in seen:
                break
            if node.pk:
                seen.add(node.pk)
            parts.append(node.name)
            node = node.parent
        return ":".join(reversed(parts))

    def full_code(self) -> str:
        scope = [self.pole] if self.pole else []
        if self.company_code:
            scope.append(self.company_code)
        prefix = "/".join(scope)
        return f"{prefix}:{self.code}" if prefix else self.code

    def validate_parent_rules(self) -> None:
        seen: set[int] = set()
        node: Optional["Account"] = self.parent
        while node:
            if node.pk and node.pk in seen:
                raise ValidationError(_("Cycle détecté dans la hiérarchie des comptes."))
            if node.pk:
                seen.add(node.pk)
            node = node.parent

    # ----------------------------
    # Query helpers
    # ----------------------------
    @classmethod
    def active(cls, *, pole: str = "", company_code: str = "") -> models.QuerySet["Account"]:
        qs = cls.objects.filter(is_active=True)
        if pole:
            qs = qs.filter(pole=(pole or "").strip().upper())
        if company_code:
            qs = qs.filter(company_code=(company_code or "").strip().upper())
        return qs

    @classmethod
    def by_code(cls, *, code: str, pole: str = "", company_code: str = "") -> Optional["Account"]:
        code = (code or "").strip()
        if not code:
            return None
        qs = cls.objects.filter(code=code)
        if pole:
            qs = qs.filter(pole=(pole or "").strip().upper())
        if company_code:
            qs = qs.filter(company_code=(company_code or "").strip().upper())
        return qs.first()

    @classmethod
    def ensure(
        cls,
        *,
        code: str,
        name: str,
        type: str,
        subtype: str = "",
        pole: str = "",
        company_code: str = "",
        currency: str = "XOF",
        parent: Optional["Account"] = None,
        is_system: bool = False,
        is_active: bool = True,
        is_reconcilable: bool = False,
        order: int = 1000,
        description: str = "",
        account_number: str = "",
        opening_balance: Decimal = Decimal("0.00"),
        opening_balance_date=None,
    ) -> "Account":
        pole_n = (pole or cls.Pole.ECONOMIC).strip().upper()
        cc_n = (company_code or "").strip().upper()
        code_n = (code or "").strip()

        obj, created = cls.objects.get_or_create(
            pole=pole_n,
            company_code=cc_n,
            code=code_n,
            defaults={
                "name": name,
                "type": type,
                "subtype": subtype or "",
                "currency": (currency or "XOF").upper(),
                "parent": parent,
                "is_system": is_system,
                "is_active": is_active,
                "is_reconcilable": is_reconcilable,
                "order": order,
                "description": description or "",
                "account_number": (account_number or "").strip(),
                "opening_balance": opening_balance or Decimal("0.00"),
                "opening_balance_date": opening_balance_date,
            },
        )

        if not created:
            updates = {
                "name": name,
                "type": type,
                "subtype": subtype or "",
                "currency": (currency or "XOF").upper(),
                "parent": parent,
                "is_system": is_system,
                "is_active": is_active,
                "is_reconcilable": is_reconcilable,
                "order": order,
                "description": description or "",
                "account_number": (account_number or "").strip(),
                "opening_balance": opening_balance or Decimal("0.00"),
                "opening_balance_date": opening_balance_date,
            }
            changed = False
            for f, v in updates.items():
                if getattr(obj, f) != v:
                    setattr(obj, f, v)
                    changed = True
            if changed:
                obj.save()

        return obj






# # accounting/models/account.py
# from __future__ import annotations

# from decimal import Decimal
# from typing import Optional

# from django.core.exceptions import ValidationError
# from django.db import models
# from django.db.models import Q
# from django.utils.translation import gettext_lazy as _


# class Account(models.Model):
#     """
#     Chart of Accounts style QuickBooks (entreprise).
#     - Scope: pole + company_code (multi-pôles / multi-entités)
#     - Hiérarchie parent/enfant (sub-account)
#     - Type/Subtype (QB-like)
#     - Opening balance + helpers + seed idempotent (ensure)
#     """

#     # ----------------------------
#     # Multi-pôles / entités
#     # ----------------------------
#     class Pole(models.TextChoices):
#         ECONOMIC = "ECONOMIC", _("Économique")
#         SOCIAL = "SOCIAL", _("Social")
#         INSTITUTION = "INSTITUTION", _("Institution")
#         CORE = "CORE", _("Core")

#     # ----------------------------
#     # QuickBooks-ish classification
#     # ----------------------------
#     class Type(models.TextChoices):
#         ASSET = "ASSET", _("Actif")
#         LIABILITY = "LIABILITY", _("Passif")
#         EQUITY = "EQUITY", _("Capitaux propres")
#         INCOME = "INCOME", _("Produit")
#         COGS = "COGS", _("Coût des ventes (COGS)")
#         EXPENSE = "EXPENSE", _("Charge")
#         OTHER_INCOME = "OTHER_INCOME", _("Autres produits")
#         OTHER_EXPENSE = "OTHER_EXPENSE", _("Autres charges")

#     class Subtype(models.TextChoices):
#         # --------------------
#         # ASSET
#         # --------------------
#         CASH = "CASH", _("Caisse / Cash")
#         BANK = "BANK", _("Compte bancaire")
#         ACCOUNTS_RECEIVABLE = "AR", _("Clients (Accounts Receivable)")
#         INVENTORY = "INVENTORY", _("Stock / Inventaire")
#         FIXED_ASSET = "FIXED_ASSET", _("Immobilisations")
#         OTHER_CURRENT_ASSET = "OCA", _("Autres actifs courants")

#         # --------------------
#         # LIABILITY
#         # --------------------
#         ACCOUNTS_PAYABLE = "AP", _("Fournisseurs (Accounts Payable)")
#         TAX_PAYABLE = "TAX_PAYABLE", _("Taxes à payer")
#         PAYROLL_LIABILITY = "PAYROLL_LIABILITY", _("Charges sociales à payer")  # ✅ unique
#         OTHER_CURRENT_LIABILITY = "OCL", _("Autres passifs courants")
#         LONG_TERM_LIABILITY = "LTL", _("Dettes long terme")

#         # Legacy (compat données anciennes)
#         PAYROLL_LIABILITY_LEGACY = "PAYROLL", _("Charges sociales à payer (legacy)")

#         # --------------------
#         # EQUITY
#         # --------------------
#         OWNER_EQUITY = "OWNER_EQUITY", _("Capital / Apports")
#         RETAINED_EARNINGS = "RETAINED_EARNINGS", _("Résultats reportés")

#         # Legacy
#         RETAINED_EARNINGS_LEGACY = "RETAINED", _("Résultats reportés (legacy)")

#         # --------------------
#         # INCOME / OTHER_INCOME
#         # --------------------
#         SALES = "SALES", _("Ventes / Chiffre d'affaires")
#         SERVICE_REVENUE = "SERVICE_REVENUE", _("Prestations / Services")
#         DONATION_INCOME = "DONATION_INCOME", _("Produits de dons")
#         TRAINING_REVENUE = "TRAINING_REVENUE", _("Produits formations")
#         DIGITAL_GOODS = "DIGITAL_GOODS", _("Produits numériques")
#         SHIPPING_INCOME = "SHIPPING_INCOME", _("Produits livraison")
#         DISCOUNT = "DISCOUNT", _("Remises / Discounts")

#         # --------------------
#         # COGS
#         # --------------------
#         COGS_DEFAULT = "COGS_DEFAULT", _("COGS")
#         PURCHASES = "PURCHASES", _("Achats")

#         # --------------------
#         # EXPENSE / OTHER_EXPENSE
#         # --------------------
#         OPERATING_EXPENSE = "OPERATING_EXPENSE", _("Charges d'exploitation")
#         FEES = "FEES", _("Frais (paiement, banque)")
#         MARKETING = "MARKETING", _("Marketing")
#         SOFTWARE = "SOFTWARE", _("Logiciels / SaaS")
#         PAYROLL_EXPENSE = "PAYROLL_EXPENSE", _("Salaires")  # ✅ unique (pas PAYROLL)
#         RENT = "RENT", _("Loyer")
#         UTILITIES = "UTILITIES", _("Eau / Électricité / Télécom")
#         TRAVEL = "TRAVEL", _("Déplacements")
#         OTHER_EXP = "OTHER_EXP", _("Autres charges")

#     # ----------------------------
#     # Fields
#     # ----------------------------
#     pole = models.CharField(
#         max_length=16,
#         choices=Pole.choices,
#         blank=True,
#         default="",
#         db_index=True,
#         help_text=_("Pôle (optionnel) : ECONOMIC / SOCIAL / INSTITUTION / CORE."),
#     )

#     company_code = models.CharField(
#         max_length=32,
#         blank=True,
#         default="",
#         db_index=True,
#         help_text=_("Entité (optionnel) : ex ECONOMIC-SN / SOCIAL-RW / ..."),
#     )

#     account_number = models.CharField(
#         max_length=32,
#         blank=True,
#         default="",
#         db_index=True,
#         help_text=_("Numéro de compte (optionnel)."),
#     )

#     code = models.CharField(max_length=32, db_index=True)
#     name = models.CharField(max_length=160)

#     type = models.CharField(max_length=16, choices=Type.choices, db_index=True)
#     subtype = models.CharField(max_length=32, choices=Subtype.choices, blank=True, default="", db_index=True)

#     currency = models.CharField(max_length=8, default="XOF", help_text=_("Devise de reporting."))

#     parent = models.ForeignKey(
#         "self",
#         null=True,
#         blank=True,
#         on_delete=models.PROTECT,
#         related_name="children",
#         help_text=_("Compte parent (sub-account)."),
#     )

#     opening_balance = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
#     opening_balance_date = models.DateField(null=True, blank=True)

#     is_active = models.BooleanField(default=True, db_index=True)
#     is_system = models.BooleanField(default=False, db_index=True)

#     # QB-like flags utiles
#     is_reconcilable = models.BooleanField(
#         default=False,
#         db_index=True,
#         help_text=_("Reconciliable (banque/caisse) si activé."),
#     )

#     description = models.CharField(max_length=240, blank=True, default="")
#     order = models.PositiveIntegerField(default=1000, db_index=True)

#     created_at = models.DateTimeField(auto_now_add=True, db_index=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         ordering = ["pole", "company_code", "order", "code", "id"]
#         constraints = [
#             # ✅ Scope entreprise: pole + company_code + code
#             models.UniqueConstraint(fields=["pole", "company_code", "code"], name="uniq_account_scope_code"),
#             models.CheckConstraint(check=~Q(parent=models.F("id")), name="account_parent_not_self"),
#             # account_number unique par scope si renseigné
#             models.UniqueConstraint(
#                 fields=["pole", "company_code", "account_number"],
#                 name="uniq_account_scope_number",
#                 condition=~Q(account_number=""),
#             ),
#         ]
#         indexes = [
#             models.Index(fields=["pole", "company_code", "type", "subtype"]),
#             models.Index(fields=["pole", "company_code", "is_active"]),
#             models.Index(fields=["pole", "company_code", "is_system"]),
#         ]

#     def __str__(self) -> str:
#         scope = []
#         if self.pole:
#             scope.append(self.pole)
#         if self.company_code:
#             scope.append(self.company_code)
#         s = f"{'/'.join(scope)}:" if scope else ""
#         num = f"[{self.account_number}] " if self.account_number else ""
#         return f"{s}{num}{self.code} — {self.name}"

#     def save(self, *args, **kwargs):
#         self.code = (self.code or "").strip()
#         self.name = (self.name or "").strip()
#         self.currency = (self.currency or "XOF").upper()
#         self.pole = (self.pole or "").strip().upper()
#         self.company_code = (self.company_code or "").strip().upper()
#         self.account_number = (self.account_number or "").strip()
#         self.subtype = (self.subtype or "").strip()
#         super().save(*args, **kwargs)

#     def clean(self):
#         self.validate_parent_rules()
#         if self.parent_id:
#             if (self.pole or "") != (self.parent.pole or ""):
#                 raise ValidationError({"parent": _("Le compte parent doit être dans le même pôle.")})
#             if (self.company_code or "") != (self.parent.company_code or ""):
#                 raise ValidationError({"parent": _("Le compte parent doit être dans la même entité (company_code).")})

#     # ----------------------------
#     # QuickBooks-like helpers
#     # ----------------------------
#     @property
#     def is_debit_nature(self) -> bool:
#         return self.type in {self.Type.ASSET, self.Type.EXPENSE, self.Type.COGS}

#     @property
#     def is_credit_nature(self) -> bool:
#         return self.type in {self.Type.LIABILITY, self.Type.EQUITY, self.Type.INCOME, self.Type.OTHER_INCOME}

#     @property
#     def fully_qualified_name(self) -> str:
#         parts = [self.name]
#         node = self.parent
#         seen: set[int] = set()
#         while node:
#             if node.pk and node.pk in seen:
#                 break
#             if node.pk:
#                 seen.add(node.pk)
#             parts.append(node.name)
#             node = node.parent
#         return ":".join(reversed(parts))

#     def full_code(self) -> str:
#         # Scope clair
#         scope = []
#         if self.pole:
#             scope.append(self.pole)
#         if self.company_code:
#             scope.append(self.company_code)
#         prefix = "/".join(scope)
#         return f"{prefix}:{self.code}" if prefix else self.code

#     def validate_parent_rules(self) -> None:
#         seen: set[int] = set()
#         node: Optional["Account"] = self.parent
#         while node:
#             if node.pk and node.pk in seen:
#                 raise ValidationError(_("Cycle détecté dans la hiérarchie des comptes."))
#             if node.pk:
#                 seen.add(node.pk)
#             node = node.parent

#     # ----------------------------
#     # Query helpers
#     # ----------------------------
#     @classmethod
#     def active(cls, *, pole: str = "", company_code: str = "") -> models.QuerySet["Account"]:
#         qs = cls.objects.filter(is_active=True)
#         if pole:
#             qs = qs.filter(pole=(pole or "").strip().upper())
#         if company_code:
#             qs = qs.filter(company_code=(company_code or "").strip().upper())
#         return qs

#     @classmethod
#     def by_code(cls, *, code: str, pole: str = "", company_code: str = "") -> Optional["Account"]:
#         code = (code or "").strip()
#         if not code:
#             return None
#         qs = cls.objects.filter(code=code)
#         if pole:
#             qs = qs.filter(pole=(pole or "").strip().upper())
#         if company_code:
#             qs = qs.filter(company_code=(company_code or "").strip().upper())
#         return qs.first()

#     @classmethod
#     def ensure(
#         cls,
#         *,
#         code: str,
#         name: str,
#         type: str,
#         subtype: str = "",
#         pole: str = "",
#         company_code: str = "",
#         currency: str = "XOF",
#         parent: Optional["Account"] = None,
#         is_system: bool = False,
#         is_active: bool = True,
#         is_reconcilable: bool = False,
#         order: int = 1000,
#         description: str = "",
#         account_number: str = "",
#         opening_balance: Decimal = Decimal("0.00"),
#         opening_balance_date=None,
#     ) -> "Account":
#         pole_n = (pole or "").strip().upper()
#         cc_n = (company_code or "").strip().upper()
#         code_n = (code or "").strip()

#         obj, created = cls.objects.get_or_create(
#             pole=pole_n,
#             company_code=cc_n,
#             code=code_n,
#             defaults={
#                 "name": name,
#                 "type": type,
#                 "subtype": subtype or "",
#                 "currency": (currency or "XOF").upper(),
#                 "parent": parent,
#                 "is_system": is_system,
#                 "is_active": is_active,
#                 "is_reconcilable": is_reconcilable,
#                 "order": order,
#                 "description": description or "",
#                 "account_number": (account_number or "").strip(),
#                 "opening_balance": opening_balance or Decimal("0.00"),
#                 "opening_balance_date": opening_balance_date,
#             },
#         )

#         if not created:
#             updates = {
#                 "name": name,
#                 "type": type,
#                 "subtype": subtype or "",
#                 "currency": (currency or "XOF").upper(),
#                 "parent": parent,
#                 "is_system": is_system,
#                 "is_active": is_active,
#                 "is_reconcilable": is_reconcilable,
#                 "order": order,
#                 "description": description or "",
#                 "account_number": (account_number or "").strip(),
#                 "opening_balance": opening_balance or Decimal("0.00"),
#                 "opening_balance_date": opening_balance_date,
#             }
#             changed = False
#             for f, v in updates.items():
#                 if getattr(obj, f) != v:
#                     setattr(obj, f, v)
#                     changed = True
#             if changed:
#                 obj.save()

#         return obj






# # accounting/models/account.py
# from __future__ import annotations

# from decimal import Decimal
# from typing import Iterable, Optional

# from django.db import models
# from django.db.models import Q
# from django.utils.translation import gettext_lazy as _


# class Account(models.Model):
#     """
#     Plan comptable (Chart of Accounts) style QuickBooks.
#     - code unique par entité (company) si multi-entités
#     - support comptes parents/enfants (hiérarchie)
#     - classification: Asset/Liability/Equity/Income/COGS/Expense/Other
#     """

#     class Type(models.TextChoices):
#         ASSET = "ASSET", _("Actif")
#         LIABILITY = "LIABILITY", _("Passif")
#         EQUITY = "EQUITY", _("Capitaux propres")
#         INCOME = "INCOME", _("Produit")
#         COGS = "COGS", _("Coût des ventes (COGS)")
#         EXPENSE = "EXPENSE", _("Charge")
#         OTHER_INCOME = "OTHER_INCOME", _("Autres produits")
#         OTHER_EXPENSE = "OTHER_EXPENSE", _("Autres charges")

#     class Subtype(models.TextChoices):
#         # Assets
#         CASH = "CASH", _("Caisse / Banque (Cash)")
#         BANK = "BANK", _("Compte bancaire")
#         ACCOUNTS_RECEIVABLE = "AR", _("Clients (Accounts Receivable)")
#         INVENTORY = "INVENTORY", _("Stock / Inventaire")
#         FIXED_ASSET = "FIXED_ASSET", _("Immobilisations")
#         OTHER_CURRENT_ASSET = "OCA", _("Autres actifs courants")

#         # Liabilities
#         ACCOUNTS_PAYABLE = "AP", _("Fournisseurs (Accounts Payable)")
#         TAX_PAYABLE = "TAX_PAYABLE", _("Taxes à payer")
#         PAYROLL_LIABILITY = "PAYROLL", _("Charges sociales à payer")
#         OTHER_CURRENT_LIABILITY = "OCL", _("Autres passifs courants")
#         LONG_TERM_LIABILITY = "LTL", _("Dettes long terme")

#         # Equity
#         OWNER_EQUITY = "OWNER_EQUITY", _("Capital / Apports")
#         RETAINED_EARNINGS = "RETAINED", _("Résultats reportés")

#         # Income/Expense
#         SALES = "SALES", _("Ventes / Chiffre d'affaires")
#         SERVICE_REVENUE = "SERVICE_REVENUE", _("Prestations / Services")
#         DONATION_INCOME = "DONATION_INCOME", _("Produits de dons")
#         TRAINING_REVENUE = "TRAINING_REVENUE", _("Produits formations")
#         DIGITAL_GOODS = "DIGITAL_GOODS", _("Produits numériques")
#         SHIPPING_INCOME = "SHIPPING_INCOME", _("Produits livraison")
#         DISCOUNT = "DISCOUNT", _("Remises / Discounts")

#         COGS_DEFAULT = "COGS_DEFAULT", _("COGS")
#         PURCHASES = "PURCHASES", _("Achats")

#         OPERATING_EXPENSE = "OPERATING_EXPENSE", _("Charges d'exploitation")
#         FEES = "FEES", _("Frais (paiement, banque)")
#         MARKETING = "MARKETING", _("Marketing")
#         SOFTWARE = "SOFTWARE", _("Logiciels / SaaS")
#         PAYROLL = "PAYROLL", _("Salaires")
#         RENT = "RENT", _("Loyer")
#         UTILITIES = "UTILITIES", _("Eau / Électricité / Télécom")
#         TRAVEL = "TRAVEL", _("Déplacements")
#         OTHER_EXP = "OTHER_EXP", _("Autres charges")

#     # Si tu as une app "company" ou modèle "AccountingCompany", remplace par FK.
#     # On garde un champ léger pour ne pas casser ton projet si multi-entité pas encore là.
#     company_code = models.CharField(
#         max_length=32,
#         blank=True,
#         default="",
#         db_index=True,
#         help_text=_("Code entité (optionnel) : ECONOMIC / SOCIAL / INSTITUTION / ..."),
#     )

#     code = models.CharField(max_length=32, db_index=True)
#     name = models.CharField(max_length=160)

#     type = models.CharField(max_length=16, choices=Type.choices, db_index=True)
#     subtype = models.CharField(max_length=32, choices=Subtype.choices, blank=True, default="", db_index=True)

#     currency = models.CharField(max_length=8, default="XOF", help_text=_("Devise de reporting (si applicable)."))

#     parent = models.ForeignKey(
#         "self",
#         null=True,
#         blank=True,
#         on_delete=models.PROTECT,
#         related_name="children",
#         help_text=_("Compte parent (hiérarchie)."),
#     )

#     is_active = models.BooleanField(default=True, db_index=True)
#     is_system = models.BooleanField(
#         default=False,
#         db_index=True,
#         help_text=_("Compte système (protégé) utilisé par les règles d'imputation."),
#     )

#     description = models.CharField(max_length=240, blank=True, default="")

#     order = models.PositiveIntegerField(default=1000, db_index=True)

#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         ordering = ["company_code", "order", "code", "id"]
#         constraints = [
#             models.UniqueConstraint(fields=["company_code", "code"], name="uniq_account_company_code"),
#             models.CheckConstraint(
#                 check=~Q(parent=models.F("id")),
#                 name="account_parent_not_self",
#             ),
#         ]
#         indexes = [
#             models.Index(fields=["company_code", "type", "subtype"]),
#             models.Index(fields=["company_code", "is_active"]),
#         ]

#     def __str__(self) -> str:
#         cc = f"{self.company_code}:" if self.company_code else ""
#         return f"{cc}{self.code} — {self.name}"

#     def save(self, *args, **kwargs):
#         self.code = (self.code or "").strip()
#         self.name = (self.name or "").strip()
#         self.currency = (self.currency or "XOF").upper()
#         self.company_code = (self.company_code or "").strip().upper()

#         # Normalisation subtype
#         self.subtype = (self.subtype or "").strip()

#         super().save(*args, **kwargs)

#     # ----------------------------
#     # Helpers QuickBooks-like
#     # ----------------------------
#     @property
#     def is_debit_nature(self) -> bool:
#         """
#         Nature débit (Asset/Expense/COGS) => solde normal débiteur.
#         """
#         return self.type in {self.Type.ASSET, self.Type.EXPENSE, self.Type.COGS}

#     @property
#     def is_credit_nature(self) -> bool:
#         """
#         Nature crédit (Liability/Equity/Income/OtherIncome) => solde normal créditeur.
#         """
#         return self.type in {
#             self.Type.LIABILITY,
#             self.Type.EQUITY,
#             self.Type.INCOME,
#             self.Type.OTHER_INCOME,
#         }

#     def full_code(self) -> str:
#         return f"{self.company_code}:{self.code}" if self.company_code else self.code

#     def validate_parent_rules(self) -> None:
#         """
#         Règles simples :
#         - pas de boucle (Django constraint empêche parent=self; pas l'arbre complet)
#         - idéalement, le parent doit avoir même type (optionnel) => on ne force pas ici.
#         """
#         # Boucle profonde (rare), garde-fou simple:
#         seen: set[int] = set()
#         node: Optional["Account"] = self.parent
#         while node:
#             if node.pk and node.pk in seen:
#                 raise ValueError("Cycle détecté dans la hiérarchie des comptes.")
#             if node.pk:
#                 seen.add(node.pk)
#             node = node.parent

#     # ----------------------------
#     # Classmethods utilitaires
#     # ----------------------------
#     @classmethod
#     def active(cls, company_code: str = "") -> models.QuerySet["Account"]:
#         cc = (company_code or "").strip().upper()
#         qs = cls.objects.filter(is_active=True)
#         return qs.filter(company_code=cc) if cc else qs

#     @classmethod
#     def by_code(cls, code: str, company_code: str = "") -> Optional["Account"]:
#         code = (code or "").strip()
#         if not code:
#             return None
#         cc = (company_code or "").strip().upper()
#         qs = cls.objects.filter(code=code)
#         if cc:
#             qs = qs.filter(company_code=cc)
#         return qs.first()

#     @classmethod
#     def ensure(
#         cls,
#         *,
#         code: str,
#         name: str,
#         type: str,
#         subtype: str = "",
#         company_code: str = "",
#         currency: str = "XOF",
#         parent: Optional["Account"] = None,
#         is_system: bool = False,
#         order: int = 1000,
#         description: str = "",
#         is_active: bool = True,
#     ) -> "Account":
#         """
#         Crée ou met à jour un compte (idempotent) — utile pour seed/migrations.
#         """
#         cc = (company_code or "").strip().upper()
#         code = (code or "").strip()

#         obj, created = cls.objects.get_or_create(
#             company_code=cc,
#             code=code,
#             defaults={
#                 "name": name,
#                 "type": type,
#                 "subtype": subtype or "",
#                 "currency": (currency or "XOF").upper(),
#                 "parent": parent,
#                 "is_system": is_system,
#                 "order": order,
#                 "description": description or "",
#                 "is_active": is_active,
#             },
#         )

#         if not created:
#             changed = False
#             for field, value in {
#                 "name": name,
#                 "type": type,
#                 "subtype": subtype or "",
#                 "currency": (currency or "XOF").upper(),
#                 "parent": parent,
#                 "is_system": is_system,
#                 "order": order,
#                 "description": description or "",
#                 "is_active": is_active,
#             }.items():
#                 if getattr(obj, field) != value:
#                     setattr(obj, field, value)
#                     changed = True
#             if changed:
#                 obj.save()

#         return obj






# # accounting/models/account.py
# from __future__ import annotations

# from django.db import models
# from django.utils.translation import gettext_lazy as _


# class Account(models.Model):
#     class Type(models.TextChoices):
#         ASSET = "ASSET", _("Actif")
#         LIABILITY = "LIABILITY", _("Passif")
#         EQUITY = "EQUITY", _("Capitaux propres")
#         INCOME = "INCOME", _("Produit")
#         EXPENSE = "EXPENSE", _("Charge")

#     class Pole(models.TextChoices):
#         ECONOMIC = "ECONOMIC", _("Économique")
#         SOCIAL = "SOCIAL", _("Social")
#         INSTITUTION = "INSTITUTION", _("Institution")
#         CORE = "CORE", _("Core")

#     code = models.CharField(max_length=32, unique=True, db_index=True)
#     name = models.CharField(max_length=180)
#     type = models.CharField(max_length=16, choices=Type.choices, db_index=True)

#     pole = models.CharField(max_length=16, choices=Pole.choices, blank=True, default="", db_index=True)

#     parent = models.ForeignKey(
#         "self",
#         null=True,
#         blank=True,
#         on_delete=models.PROTECT,
#         related_name="children",
#     )

#     description = models.CharField(max_length=240, blank=True, default="")
#     is_active = models.BooleanField(default=True)
#     is_system = models.BooleanField(default=False)

#     created_at = models.DateTimeField(auto_now_add=True, db_index=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         ordering = ["code", "id"]
#         indexes = [
#             models.Index(fields=["type", "code"]),
#             models.Index(fields=["pole", "code"]),
#             models.Index(fields=["is_active", "code"]),
#         ]

#     def __str__(self) -> str:
#         return f"{self.code} — {self.name}"
