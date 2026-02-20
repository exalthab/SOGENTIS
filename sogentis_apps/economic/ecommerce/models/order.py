 # economic/ecommerce/models/order.py
from __future__ import annotations

import uuid
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

D0 = Decimal("0.00")
Q = models.Q


class Order(models.Model):
    """
    Order (prod-ready)
    - Panier session -> Order + OrderItem
    - Proforma AVANT paiement (pending)
    - Facture APRÈS paiement (paid/shipped/completed)
    """

    # ==========================
    # STATUTS COMMANDE
    # ==========================
    STATUS_PENDING = "pending"
    STATUS_PAID = "paid"
    STATUS_SHIPPED = "shipped"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_PENDING, _("En attente")),
        (STATUS_PAID, _("Payée")),
        (STATUS_SHIPPED, _("Expédiée")),
        (STATUS_COMPLETED, _("Terminée")),
        (STATUS_CANCELLED, _("Annulée")),
    ]

    FINAL_STATUSES = {STATUS_PAID, STATUS_SHIPPED, STATUS_COMPLETED, STATUS_CANCELLED}

    # ==========================
    # IDENTIFIANTS
    # ==========================
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        verbose_name=_("UUID"),
    )

    # ⚠️ IMPORTANT:
    # - pas de unique=True (évite clash si anciennes lignes ont reference="")
    # - unicité via UniqueConstraint conditionnel (Postgres)
    reference = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        db_index=True,
        editable=False,
        verbose_name=_("Référence"),
        help_text=_("Auto-générée. Ex: ORD-20260124-0001"),
    )

    # ==========================
    # UTILISATEUR
    # ==========================
    # ✅ Commande invité: user peut être NULL
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders",
        verbose_name=_("Utilisateur"),
        null=True,
        blank=True,
    )

    customer_email = models.EmailField(
        _("Email client"),
        blank=True,
        db_index=True,
        help_text=_("Copie de l'email au moment de la commande (facture / export)."),
    )

    # ==========================
    # FACTURATION / LIVRAISON
    # ==========================
    billing_name = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name=_("Nom (facturation)"),
    )
    billing_phone = models.CharField(
        max_length=40,
        blank=True,
        db_index=True,
        verbose_name=_("Téléphone (facturation)"),
    )
    billing_address = models.TextField(
        blank=True,
        verbose_name=_("Adresse (facturation)"),
    )
    billing_zip = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_("Code postal"),
    )
    billing_city = models.CharField(
        max_length=120,
        blank=True,
        verbose_name=_("Ville"),
    )
    billing_country = models.CharField(
        max_length=120,
        blank=True,
        verbose_name=_("Pays"),
    )
    customer_note = models.TextField(
        blank=True,
        verbose_name=_("Note client"),
    )

    # ==========================
    # STATUT & MONTANTS
    # ==========================
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        verbose_name=_("Statut"),
        db_index=True,
    )

    currency = models.CharField(
        max_length=10,
        default="XOF",
        db_index=True,
        verbose_name=_("Devise"),
    )

    subtotal_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=D0,
        verbose_name=_("Sous-total"),
        help_text=_("Somme des lignes (items)."),
    )

    shipping_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=D0,
        verbose_name=_("Livraison"),
    )

    tax_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=D0,
        verbose_name=_("Taxes"),
    )

    discount_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=D0,
        verbose_name=_("Remise"),
        help_text=_("Montant à soustraire du total."),
    )

    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=D0,
        verbose_name=_("Montant total"),
    )

    # ==========================
    # TIMESTAMPS
    # ==========================
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Créée le"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Mise à jour le"))

    paid_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Payée le"))
    shipped_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Expédiée le"))
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Terminée le"))
    cancelled_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Annulée le"))

    class Meta:
        db_table = "ecommerce_order"
        verbose_name = _("Commande")
        verbose_name_plural = _("Commandes")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["user"]),
            models.Index(fields=["customer_email"]),
            models.Index(fields=["reference"]),
            models.Index(fields=["user", "created_at"]),
        ]
        constraints = [
            # ✅ Unicité "utile" : unique seulement si reference non NULL et non vide
            models.UniqueConstraint(
                fields=["reference"],
                condition=Q(reference__isnull=False) & ~Q(reference=""),
                name="uniq_order_reference_not_empty",
            ),
        ]

    def __str__(self):
        return self.reference or f"Commande {self.uuid}"

    # ==========================
    # DECIMAL HELPERS
    # ==========================
    @staticmethod
    def _to_dec(val) -> Decimal:
        try:
            return Decimal(str(val))
        except Exception:
            return D0

    @staticmethod
    def _q2(val: Decimal) -> Decimal:
        try:
            return Decimal(val).quantize(Decimal("0.01"))
        except Exception:
            return D0

    @staticmethod
    def _normalize_str(s: str | None) -> str | None:
        if s is None:
            return None
        s = str(s).strip()
        return s if s else None

    @staticmethod
    def _norm_spaces(s: str | None) -> str:
        return " ".join((s or "").strip().split())

    def _normalize_money_fields(self):
        self.subtotal_amount = self._q2(max(D0, self._to_dec(self.subtotal_amount)))
        self.shipping_amount = self._q2(max(D0, self._to_dec(self.shipping_amount)))
        self.tax_amount = self._q2(max(D0, self._to_dec(self.tax_amount)))
        self.discount_amount = self._q2(max(D0, self._to_dec(self.discount_amount)))
        self.total_amount = self._q2(max(D0, self._to_dec(self.total_amount)))

    def _expected_total(self, subtotal: Decimal | None = None) -> Decimal:
        sub = self._to_dec(subtotal if subtotal is not None else self.subtotal_amount)
        ship = self._to_dec(self.shipping_amount)
        tax = self._to_dec(self.tax_amount)
        disc = self._to_dec(self.discount_amount)
        total = sub + ship + tax - disc
        if total < 0:
            total = D0
        return self._q2(total)

    # ==========================
    # VALIDATIONS (remplace CheckConstraint)
    # ==========================
    def clean(self):
        super().clean()

        # reference: éviter "" en DB
        self.reference = self._normalize_str(self.reference)

        # currency normalize
        self.currency = (self.currency or "").strip().upper() or "XOF"

        # email normalize
        self.customer_email = (self.customer_email or "").strip()

        # champs texte: nettoyage
        self.billing_name = self._norm_spaces(self.billing_name)
        self.billing_phone = self._norm_spaces(self.billing_phone)
        self.billing_address = (self.billing_address or "").strip()
        self.billing_zip = (self.billing_zip or "").strip()
        self.billing_city = self._norm_spaces(self.billing_city)
        self.billing_country = self._norm_spaces(self.billing_country)
        self.customer_note = (self.customer_note or "").strip()

        # money normalize
        self._normalize_money_fields()

        # règles >= 0
        money_errors = {}
        if self.total_amount < 0:
            money_errors["total_amount"] = _("Le total ne peut pas être négatif.")
        if self.subtotal_amount < 0:
            money_errors["subtotal_amount"] = _("Le sous-total ne peut pas être négatif.")
        if self.shipping_amount < 0:
            money_errors["shipping_amount"] = _("La livraison ne peut pas être négative.")
        if self.tax_amount < 0:
            money_errors["tax_amount"] = _("Les taxes ne peuvent pas être négatives.")
        if self.discount_amount < 0:
            money_errors["discount_amount"] = _("La remise ne peut pas être négative.")
        if money_errors:
            raise ValidationError(money_errors)

        # ✅ commande invitée: exiger un email (sinon impossible facture/proforma)
        if not self.user_id and not self.customer_email:
            raise ValidationError({"customer_email": _("Email requis pour une commande invitée.")})

        # ✅ pour une commande "pro" : si on veut l'adresse, on peut exiger ces champs
        # (tu as dit: "Oui il faut l'adresse")
        addr_errors = {}
        if not self.billing_name:
            addr_errors["billing_name"] = _("Nom / Prénom requis.")
        if not self.billing_address:
            addr_errors["billing_address"] = _("Adresse requise.")
        if not self.billing_city:
            addr_errors["billing_city"] = _("Ville requise.")
        if not self.billing_country:
            addr_errors["billing_country"] = _("Pays requis.")
        if addr_errors:
            raise ValidationError(addr_errors)

    # ==========================
    # CALCULS
    # ==========================
    def calculate_subtotal(self) -> Decimal:
        total = D0
        for it in self.items.all():
            try:
                total += (self._to_dec(it.unit_price) * self._to_dec(it.quantity))
            except Exception:
                continue
        return self._q2(total)

    def recalc_totals(self, save: bool = True):
        new_sub = self.calculate_subtotal()
        new_total = self._expected_total(subtotal=new_sub)
        self.subtotal_amount = new_sub
        self.total_amount = new_total

        if save and self.pk:
            type(self).objects.filter(pk=self.pk).update(
                subtotal_amount=new_sub,
                total_amount=new_total,
                updated_at=timezone.now(),
            )

    # ==========================
    # REFERENCE AUTO (atomic)
    # ==========================
    @staticmethod
    def _reference_prefix() -> str:
        today = timezone.now().strftime("%Y%m%d")
        return f"ORD-{today}-"

    @classmethod
    def _next_reference(cls) -> str:
        prefix = cls._reference_prefix()
        last = (
            cls.objects.select_for_update()
            .filter(reference__startswith=prefix)
            .order_by("-reference")
            .values_list("reference", flat=True)
            .first()
        )
        last_n = 0
        if last:
            try:
                last_n = int(last.split("-")[-1])
            except Exception:
                last_n = 0
        return f"{prefix}{(last_n + 1):04d}"

    # ==========================
    # SAVE (prod safe)
    # ==========================
    def save(self, *args, **kwargs):
        # currency normalize
        self.currency = (self.currency or "").strip().upper() or "XOF"

        # Email snapshot depuis user si disponible
        if self.user_id and not self.customer_email:
            try:
                self.customer_email = (getattr(self.user, "email", "") or "").strip()
            except Exception:
                self.customer_email = (self.customer_email or "").strip()

        # éviter "" en DB
        self.reference = self._normalize_str(self.reference)

        # money normalize (pré)
        self._normalize_money_fields()

        with transaction.atomic():
            previous_status = None
            if self.pk:
                previous_status = (
                    type(self).objects.select_for_update()
                    .filter(pk=self.pk)
                    .values_list("status", flat=True)
                    .first()
                )

            # Référence auto si absente
            if not self.reference:
                self.reference = self._next_reference()

            # total cohérent
            self.total_amount = self._expected_total()

            # timestamps transitions
            now_ts = timezone.now()
            if previous_status != self.status:
                if self.status == self.STATUS_PAID and self.paid_at is None:
                    self.paid_at = now_ts
                if self.status == self.STATUS_SHIPPED and self.shipped_at is None:
                    self.shipped_at = now_ts
                if self.status == self.STATUS_COMPLETED and self.completed_at is None:
                    self.completed_at = now_ts
                if self.status == self.STATUS_CANCELLED and self.cancelled_at is None:
                    self.cancelled_at = now_ts

            # ✅ clean() remplace CheckConstraint
            self.full_clean()
            super().save(*args, **kwargs)

        # Recalc non récursif (update SQL)
        try:
            if self.pk and self.items.exists():
                self.recalc_totals(save=True)
        except Exception:
            pass

    # ==========================
    # HELPERS MÉTIER (prod)
    # ==========================
    @property
    def is_paid(self) -> bool:
        return self.status in {self.STATUS_PAID, self.STATUS_SHIPPED, self.STATUS_COMPLETED}

    @property
    def is_cancelled(self) -> bool:
        return self.status == self.STATUS_CANCELLED

    @property
    def is_final(self) -> bool:
        return self.status in self.FINAL_STATUSES

    @property
    def is_editable(self) -> bool:
        return self.status == self.STATUS_PENDING

    @property
    def can_pay(self) -> bool:
        # Paiement autorisé uniquement si pending
        return self.status == self.STATUS_PENDING

    def get_customer_email(self) -> str:
        if self.customer_email:
            return self.customer_email
        if self.user_id:
            return (getattr(self.user, "email", "") or "").strip()
        return ""

    def get_customer_display_name(self) -> str:
        if self.billing_name:
            return self.billing_name
        if self.user_id:
            try:
                fn = getattr(self.user, "get_full_name", lambda: "")() or ""
            except Exception:
                fn = ""
            return fn.strip() or (getattr(self.user, "username", "") or "").strip() or _("Client")
        return _("Client")

    # --------------------------
    # Transitions
    # --------------------------
    def mark_paid(self):
        if self.status != self.STATUS_PAID:
            self.status = self.STATUS_PAID
        if self.paid_at is None:
            self.paid_at = timezone.now()
        self.save(update_fields=["status", "paid_at", "updated_at"])

    def mark_shipped(self):
        if self.status != self.STATUS_SHIPPED:
            self.status = self.STATUS_SHIPPED
        if self.shipped_at is None:
            self.shipped_at = timezone.now()
        self.save(update_fields=["status", "shipped_at", "updated_at"])

    def mark_completed(self):
        if self.status != self.STATUS_COMPLETED:
            self.status = self.STATUS_COMPLETED
        if self.completed_at is None:
            self.completed_at = timezone.now()
        self.save(update_fields=["status", "completed_at", "updated_at"])

    def mark_cancelled(self):
        if self.status != self.STATUS_CANCELLED:
            self.status = self.STATUS_CANCELLED
        if self.cancelled_at is None:
            self.cancelled_at = timezone.now()
        self.save(update_fields=["status", "cancelled_at", "updated_at"])








# # economic/ecommerce/models/order.py
# from __future__ import annotations

# import uuid
# from decimal import Decimal

# from django.conf import settings
# from django.core.exceptions import ValidationError
# from django.db import models, transaction
# from django.utils import timezone
# from django.utils.translation import gettext_lazy as _

# D0 = Decimal("0.00")
# Q = models.Q


# class Order(models.Model):
#     # ==========================
#     # STATUTS COMMANDE
#     # ==========================
#     STATUS_PENDING = "pending"
#     STATUS_PAID = "paid"
#     STATUS_SHIPPED = "shipped"
#     STATUS_COMPLETED = "completed"
#     STATUS_CANCELLED = "cancelled"

#     STATUS_CHOICES = [
#         (STATUS_PENDING, _("En attente")),
#         (STATUS_PAID, _("Payée")),
#         (STATUS_SHIPPED, _("Expédiée")),
#         (STATUS_COMPLETED, _("Terminée")),
#         (STATUS_CANCELLED, _("Annulée")),
#     ]

#     # ==========================
#     # IDENTIFIANTS
#     # ==========================
#     uuid = models.UUIDField(
#         default=uuid.uuid4,
#         editable=False,
#         unique=True,
#         verbose_name=_("UUID"),
#     )

#     # ⚠️ IMPORTANT:
#     # - pas de unique=True pour éviter clash si anciennes lignes ont reference=""
#     # - unicité via UniqueConstraint conditionnel (Postgres)
#     reference = models.CharField(
#         max_length=20,
#         null=True,
#         blank=True,
#         db_index=True,
#         editable=False,
#         verbose_name=_("Référence"),
#         help_text=_("Auto-générée. Ex: ORD-20260124-0001"),
#     )

#     # ==========================
#     # UTILISATEUR
#     # ==========================
#     # ⚠️ Avec ton checkout tu veux "user=None si anonyme".
#     # Ici on met null=True/blank=True pour accepter les commandes invité.
#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.PROTECT,
#         related_name="orders",
#         verbose_name=_("Utilisateur"),
#         null=True,
#         blank=True,
#     )

#     customer_email = models.EmailField(
#         _("Email client"),
#         blank=True,
#         db_index=True,
#         help_text=_("Copie de l'email au moment de la commande (facture / export)."),
#     )

#     # ==========================
#     # FACTURATION / LIVRAISON
#     # ==========================
#     billing_name = models.CharField(
#         max_length=255,
#         blank=True,
#         db_index=True,
#         verbose_name=_("Nom (facturation)"),
#     )
#     billing_phone = models.CharField(
#         max_length=40,
#         blank=True,
#         db_index=True,
#         verbose_name=_("Téléphone (facturation)"),
#     )
#     billing_address = models.TextField(
#         blank=True,
#         verbose_name=_("Adresse (facturation)"),
#     )
#     billing_zip = models.CharField(
#         max_length=20,
#         blank=True,
#         verbose_name=_("Code postal"),
#     )
#     billing_city = models.CharField(
#         max_length=120,
#         blank=True,
#         verbose_name=_("Ville"),
#     )
#     billing_country = models.CharField(
#         max_length=120,
#         blank=True,
#         verbose_name=_("Pays"),
#     )
#     customer_note = models.TextField(
#         blank=True,
#         verbose_name=_("Note client"),
#     )

#     # ==========================
#     # STATUT & MONTANTS
#     # ==========================
#     status = models.CharField(
#         max_length=20,
#         choices=STATUS_CHOICES,
#         default=STATUS_PENDING,
#         verbose_name=_("Statut"),
#         db_index=True,
#     )

#     currency = models.CharField(
#         max_length=10,
#         default="XOF",
#         db_index=True,
#         verbose_name=_("Devise"),
#     )

#     subtotal_amount = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         default=D0,
#         verbose_name=_("Sous-total"),
#         help_text=_("Somme des lignes (items)."),
#     )

#     shipping_amount = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         default=D0,
#         verbose_name=_("Livraison"),
#     )

#     tax_amount = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         default=D0,
#         verbose_name=_("Taxes"),
#     )

#     discount_amount = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         default=D0,
#         verbose_name=_("Remise"),
#         help_text=_("Montant à soustraire du total."),
#     )

#     total_amount = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         default=D0,
#         verbose_name=_("Montant total"),
#     )

#     # ==========================
#     # TIMESTAMPS
#     # ==========================
#     created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Créée le"))
#     updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Mise à jour le"))

#     paid_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Payée le"))
#     shipped_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Expédiée le"))
#     completed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Terminée le"))
#     cancelled_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Annulée le"))

#     class Meta:
#         verbose_name = _("Commande")
#         verbose_name_plural = _("Commandes")
#         ordering = ["-created_at"]
#         indexes = [
#             models.Index(fields=["status"]),
#             models.Index(fields=["created_at"]),
#             models.Index(fields=["user"]),
#             models.Index(fields=["customer_email"]),
#             models.Index(fields=["reference"]),
#             models.Index(fields=["user", "created_at"]),
#         ]
#         constraints = [
#             # ✅ Unicité "utile" : unique seulement si reference non NULL et non vide
#             models.UniqueConstraint(
#                 fields=["reference"],
#                 condition=Q(reference__isnull=False) & ~Q(reference=""),
#                 name="uniq_order_reference_not_empty",
#             ),
#         ]

#     def __str__(self):
#         return self.reference or f"Commande {self.uuid}"

#     # ==========================
#     # DECIMAL HELPERS
#     # ==========================
#     @staticmethod
#     def _to_dec(val) -> Decimal:
#         try:
#             return Decimal(val)
#         except Exception:
#             return D0

#     @staticmethod
#     def _q2(val: Decimal) -> Decimal:
#         try:
#             return Decimal(val).quantize(Decimal("0.01"))
#         except Exception:
#             return D0

#     @staticmethod
#     def _normalize_str(s: str | None) -> str | None:
#         if s is None:
#             return None
#         s = str(s).strip()
#         return s if s else None

#     def _normalize_money_fields(self):
#         self.subtotal_amount = self._q2(max(D0, self._to_dec(self.subtotal_amount)))
#         self.shipping_amount = self._q2(max(D0, self._to_dec(self.shipping_amount)))
#         self.tax_amount = self._q2(max(D0, self._to_dec(self.tax_amount)))
#         self.discount_amount = self._q2(max(D0, self._to_dec(self.discount_amount)))
#         self.total_amount = self._q2(max(D0, self._to_dec(self.total_amount)))

#     def _expected_total(self, subtotal: Decimal | None = None) -> Decimal:
#         sub = self._to_dec(subtotal if subtotal is not None else self.subtotal_amount)
#         ship = self._to_dec(self.shipping_amount)
#         tax = self._to_dec(self.tax_amount)
#         disc = self._to_dec(self.discount_amount)
#         total = sub + ship + tax - disc
#         if total < 0:
#             total = D0
#         return self._q2(total)

#     # ==========================
#     # VALIDATIONS (remplace CheckConstraint)
#     # ==========================
#     def clean(self):
#         super().clean()

#         # normalisations
#         self.reference = self._normalize_str(self.reference)

#         if self.currency:
#             self.currency = (self.currency or "").strip().upper() or "XOF"
#         else:
#             self.currency = "XOF"

#         # money fields
#         self._normalize_money_fields()

#         # règles ">= 0" (au lieu de CheckConstraint)
#         money_errors = {}
#         if self.total_amount < 0:
#             money_errors["total_amount"] = _("Le total ne peut pas être négatif.")
#         if self.subtotal_amount < 0:
#             money_errors["subtotal_amount"] = _("Le sous-total ne peut pas être négatif.")
#         if self.shipping_amount < 0:
#             money_errors["shipping_amount"] = _("La livraison ne peut pas être négative.")
#         if self.tax_amount < 0:
#             money_errors["tax_amount"] = _("Les taxes ne peuvent pas être négatives.")
#         if self.discount_amount < 0:
#             money_errors["discount_amount"] = _("La remise ne peut pas être négative.")
#         if money_errors:
#             raise ValidationError(money_errors)

#         # email snapshot minimal (si non user)
#         self.customer_email = (self.customer_email or "").strip()

#         # champs texte : nettoyage léger
#         self.billing_name = " ".join((self.billing_name or "").split())
#         self.billing_phone = " ".join((self.billing_phone or "").split())
#         self.billing_zip = (self.billing_zip or "").strip()
#         self.billing_city = " ".join((self.billing_city or "").split())
#         self.billing_country = " ".join((self.billing_country or "").split())

#     # ==========================
#     # CALCULS
#     # ==========================
#     def calculate_subtotal(self) -> Decimal:
#         total = D0
#         for it in self.items.all():
#             try:
#                 total += (Decimal(it.unit_price) * Decimal(it.quantity))
#             except Exception:
#                 continue
#         return self._q2(total)

#     def recalc_totals(self, save: bool = True):
#         new_sub = self.calculate_subtotal()
#         new_total = self._expected_total(subtotal=new_sub)

#         self.subtotal_amount = new_sub
#         self.total_amount = new_total

#         if save and self.pk:
#             type(self).objects.filter(pk=self.pk).update(
#                 subtotal_amount=new_sub,
#                 total_amount=new_total,
#                 updated_at=timezone.now(),
#             )

#     # ==========================
#     # REFERENCE AUTO (atomic)
#     # ==========================
#     @staticmethod
#     def _reference_prefix() -> str:
#         today = timezone.now().strftime("%Y%m%d")
#         return f"ORD-{today}-"

#     @classmethod
#     def _next_reference(cls) -> str:
#         prefix = cls._reference_prefix()
#         last = (
#             cls.objects.select_for_update()
#             .filter(reference__startswith=prefix)
#             .order_by("-reference")
#             .values_list("reference", flat=True)
#             .first()
#         )
#         last_n = 0
#         if last:
#             try:
#                 last_n = int(last.split("-")[-1])
#             except Exception:
#                 last_n = 0
#         return f"{prefix}{(last_n + 1):04d}"

#     # ==========================
#     # SAVE (prod safe)
#     # ==========================
#     def save(self, *args, **kwargs):
#         # currency normalize
#         if self.currency:
#             self.currency = (self.currency or "").strip().upper() or "XOF"
#         else:
#             self.currency = "XOF"

#         # Email snapshot
#         if self.user_id and not self.customer_email:
#             self.customer_email = getattr(self.user, "email", "") or ""

#         # IMPORTANT: éviter "" en DB
#         self.reference = self._normalize_str(self.reference)

#         # normalise money
#         self._normalize_money_fields()

#         with transaction.atomic():
#             previous_status = None
#             if self.pk:
#                 previous_status = (
#                     type(self).objects.select_for_update()
#                     .filter(pk=self.pk)
#                     .values_list("status", flat=True)
#                     .first()
#                 )

#             # Référence auto si absente
#             if not self.reference:
#                 self.reference = self._next_reference()

#             # Timestamps de transition
#             now_ts = timezone.now()
#             if previous_status != self.status:
#                 if self.status == self.STATUS_PAID and self.paid_at is None:
#                     self.paid_at = now_ts
#                 if self.status == self.STATUS_SHIPPED and self.shipped_at is None:
#                     self.shipped_at = now_ts
#                 if self.status == self.STATUS_COMPLETED and self.completed_at is None:
#                     self.completed_at = now_ts
#                 if self.status == self.STATUS_CANCELLED and self.cancelled_at is None:
#                     self.cancelled_at = now_ts

#             # total cohérent
#             self.total_amount = self._expected_total()

#             # ✅ clean() remplace tes CheckConstraint
#             self.full_clean()
#             super().save(*args, **kwargs)

#         # Recalc non récursif (update SQL)
#         try:
#             if self.pk and self.items.exists():
#                 self.recalc_totals(save=True)
#         except Exception:
#             pass

#     # ==========================
#     # HELPERS MÉTIER
#     # ==========================
#     @property
#     def is_paid(self):
#         return self.status in {self.STATUS_PAID, self.STATUS_SHIPPED, self.STATUS_COMPLETED}

#     @property
#     def is_editable(self):
#         return self.status == self.STATUS_PENDING

#     @property
#     def can_pay(self) -> bool:
#         return self.status == self.STATUS_PENDING

#     def mark_paid(self):
#         if self.status != self.STATUS_PAID:
#             self.status = self.STATUS_PAID
#         if self.paid_at is None:
#             self.paid_at = timezone.now()
#         self.save(update_fields=["status", "paid_at", "updated_at"])

#     def mark_shipped(self):
#         if self.status != self.STATUS_SHIPPED:
#             self.status = self.STATUS_SHIPPED
#         if self.shipped_at is None:
#             self.shipped_at = timezone.now()
#         self.save(update_fields=["status", "shipped_at", "updated_at"])

#     def mark_completed(self):
#         if self.status != self.STATUS_COMPLETED:
#             self.status = self.STATUS_COMPLETED
#         if self.completed_at is None:
#             self.completed_at = timezone.now()
#         self.save(update_fields=["status", "completed_at", "updated_at"])

#     def mark_cancelled(self):
#         if self.status != self.STATUS_CANCELLED:
#             self.status = self.STATUS_CANCELLED
#         if self.cancelled_at is None:
#             self.cancelled_at = timezone.now()
#         self.save(update_fields=["status", "cancelled_at", "updated_at"])





# # economic/ecommerce/models/order.py
# from __future__ import annotations

# import uuid
# from decimal import Decimal

# from django.conf import settings
# from django.db import models, transaction
# from django.utils import timezone
# from django.utils.translation import gettext_lazy as _

# D0 = Decimal("0.00")
# Q = models.Q


# class Order(models.Model):
#     # ==========================
#     # STATUTS COMMANDE
#     # ==========================
#     STATUS_PENDING = "pending"
#     STATUS_PAID = "paid"
#     STATUS_SHIPPED = "shipped"
#     STATUS_COMPLETED = "completed"
#     STATUS_CANCELLED = "cancelled"

#     STATUS_CHOICES = [
#         (STATUS_PENDING, _("En attente")),
#         (STATUS_PAID, _("Payée")),
#         (STATUS_SHIPPED, _("Expédiée")),
#         (STATUS_COMPLETED, _("Terminée")),
#         (STATUS_CANCELLED, _("Annulée")),
#     ]

#     # ==========================
#     # IDENTIFIANTS
#     # ==========================
#     uuid = models.UUIDField(
#         default=uuid.uuid4,
#         editable=False,
#         unique=True,
#         verbose_name=_("UUID"),
#     )

#     reference = models.CharField(
#         max_length=20,
#         null=True,
#         blank=True,
#         db_index=True,
#         editable=False,
#         verbose_name=_("Référence"),
#         help_text=_("Auto-générée. Ex: ORD-20260124-0001"),
#     )

#     # ==========================
#     # UTILISATEUR
#     # ==========================
#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.PROTECT,
#         related_name="orders",
#         verbose_name=_("Utilisateur"),
#     )

#     customer_email = models.EmailField(
#         _("Email client"),
#         blank=True,
#         db_index=True,
#         help_text=_("Copie de l'email au moment de la commande (facture / export)."),
#     )

#     # ==========================
#     # FACTURATION / LIVRAISON (✅ AJOUT)
#     # ==========================
#     billing_name = models.CharField(
#         max_length=255,
#         blank=True,
#         db_index=True,
#         verbose_name=_("Nom (facturation)"),
#     )
#     billing_phone = models.CharField(
#         max_length=40,
#         blank=True,
#         db_index=True,
#         verbose_name=_("Téléphone (facturation)"),
#     )
#     billing_address = models.TextField(
#         blank=True,
#         verbose_name=_("Adresse (facturation)"),
#     )
#     billing_zip = models.CharField(
#         max_length=20,
#         blank=True,
#         verbose_name=_("Code postal"),
#     )
#     billing_city = models.CharField(
#         max_length=120,
#         blank=True,
#         verbose_name=_("Ville"),
#     )
#     billing_country = models.CharField(
#         max_length=120,
#         blank=True,
#         verbose_name=_("Pays"),
#     )
#     customer_note = models.TextField(
#         blank=True,
#         verbose_name=_("Note client"),
#     )

#     # ==========================
#     # STATUT & MONTANTS
#     # ==========================
#     status = models.CharField(
#         max_length=20,
#         choices=STATUS_CHOICES,
#         default=STATUS_PENDING,
#         verbose_name=_("Statut"),
#         db_index=True,
#     )

#     currency = models.CharField(
#         max_length=10,
#         default="XOF",
#         db_index=True,
#         verbose_name=_("Devise"),
#     )

#     subtotal_amount = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         default=D0,
#         verbose_name=_("Sous-total"),
#         help_text=_("Somme des lignes (items)."),
#     )

#     shipping_amount = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         default=D0,
#         verbose_name=_("Livraison"),
#     )

#     tax_amount = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         default=D0,
#         verbose_name=_("Taxes"),
#     )

#     discount_amount = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         default=D0,
#         verbose_name=_("Remise"),
#         help_text=_("Montant à soustraire du total."),
#     )

#     total_amount = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         default=D0,
#         verbose_name=_("Montant total"),
#     )

#     # ==========================
#     # TIMESTAMPS
#     # ==========================
#     created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Créée le"))
#     updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Mise à jour le"))

#     paid_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Payée le"))
#     shipped_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Expédiée le"))
#     completed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Terminée le"))
#     cancelled_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Annulée le"))

#     class Meta:
#         verbose_name = _("Commande")
#         verbose_name_plural = _("Commandes")
#         ordering = ["-created_at"]
#         indexes = [
#             models.Index(fields=["status"]),
#             models.Index(fields=["created_at"]),
#             models.Index(fields=["user"]),
#             models.Index(fields=["customer_email"]),
#             models.Index(fields=["reference"]),
#             models.Index(fields=["user", "created_at"]),
#         ]
#         constraints = [
#             models.CheckConstraint(check=Q(total_amount__gte=0), name="chk_order_total_gte_0"),
#             models.CheckConstraint(check=Q(subtotal_amount__gte=0), name="chk_order_subtotal_gte_0"),
#             models.CheckConstraint(check=Q(shipping_amount__gte=0), name="chk_order_shipping_gte_0"),
#             models.CheckConstraint(check=Q(tax_amount__gte=0), name="chk_order_tax_gte_0"),
#             models.CheckConstraint(check=Q(discount_amount__gte=0), name="chk_order_discount_gte_0"),
#             models.UniqueConstraint(
#                 fields=["reference"],
#                 condition=Q(reference__isnull=False) & ~Q(reference=""),
#                 name="uniq_order_reference_not_empty",
#             ),
#         ]

#     def __str__(self):
#         return self.reference or f"Commande {self.uuid}"

#     # ==========================
#     # DECIMAL HELPERS
#     # ==========================
#     @staticmethod
#     def _to_dec(val) -> Decimal:
#         try:
#             return Decimal(val)
#         except Exception:
#             return D0

#     @staticmethod
#     def _q2(val: Decimal) -> Decimal:
#         try:
#             return Decimal(val).quantize(Decimal("0.01"))
#         except Exception:
#             return D0

#     def _normalize_money_fields(self):
#         self.subtotal_amount = self._q2(max(D0, self._to_dec(self.subtotal_amount)))
#         self.shipping_amount = self._q2(max(D0, self._to_dec(self.shipping_amount)))
#         self.tax_amount = self._q2(max(D0, self._to_dec(self.tax_amount)))
#         self.discount_amount = self._q2(max(D0, self._to_dec(self.discount_amount)))
#         self.total_amount = self._q2(max(D0, self._to_dec(self.total_amount)))

#     def _expected_total(self, subtotal: Decimal | None = None) -> Decimal:
#         sub = self._to_dec(subtotal if subtotal is not None else self.subtotal_amount)
#         ship = self._to_dec(self.shipping_amount)
#         tax = self._to_dec(self.tax_amount)
#         disc = self._to_dec(self.discount_amount)
#         total = sub + ship + tax - disc
#         if total < 0:
#             total = D0
#         return self._q2(total)

#     @staticmethod
#     def _normalize_str(s: str | None) -> str | None:
#         if s is None:
#             return None
#         s = str(s).strip()
#         return s if s else None

#     # ==========================
#     # CALCULS
#     # ==========================
#     def calculate_subtotal(self) -> Decimal:
#         total = D0
#         for it in self.items.all():
#             try:
#                 total += (Decimal(it.unit_price) * Decimal(it.quantity))
#             except Exception:
#                 continue
#         return self._q2(total)

#     def recalc_totals(self, save: bool = True):
#         new_sub = self.calculate_subtotal()
#         new_total = self._expected_total(subtotal=new_sub)
#         self.subtotal_amount = new_sub
#         self.total_amount = new_total

#         if save and self.pk:
#             type(self).objects.filter(pk=self.pk).update(
#                 subtotal_amount=new_sub,
#                 total_amount=new_total,
#                 updated_at=timezone.now(),
#             )

#     # ==========================
#     # REFERENCE AUTO (atomic)
#     # ==========================
#     @staticmethod
#     def _reference_prefix() -> str:
#         today = timezone.now().strftime("%Y%m%d")
#         return f"ORD-{today}-"

#     @classmethod
#     def _next_reference(cls) -> str:
#         prefix = cls._reference_prefix()
#         last = (
#             cls.objects.select_for_update()
#             .filter(reference__startswith=prefix)
#             .order_by("-reference")
#             .values_list("reference", flat=True)
#             .first()
#         )
#         last_n = 0
#         if last:
#             try:
#                 last_n = int(last.split("-")[-1])
#             except Exception:
#                 last_n = 0
#         return f"{prefix}{(last_n + 1):04d}"

#     # ==========================
#     # SAVE (prod safe)
#     # ==========================
#     def save(self, *args, **kwargs):
#         if self.currency:
#             self.currency = (self.currency or "").strip().upper() or "XOF"

#         # Email snapshot
#         if self.user_id and not self.customer_email:
#             self.customer_email = getattr(self.user, "email", "") or ""

#         # éviter "" en DB
#         self.reference = self._normalize_str(self.reference)
#         self._normalize_money_fields()

#         with transaction.atomic():
#             previous_status = None
#             if self.pk:
#                 previous_status = (
#                     type(self).objects.select_for_update()
#                     .filter(pk=self.pk)
#                     .values_list("status", flat=True)
#                     .first()
#                 )

#             if not self.reference:
#                 self.reference = self._next_reference()

#             now_ts = timezone.now()
#             if previous_status != self.status:
#                 if self.status == self.STATUS_PAID and self.paid_at is None:
#                     self.paid_at = now_ts
#                 if self.status == self.STATUS_SHIPPED and self.shipped_at is None:
#                     self.shipped_at = now_ts
#                 if self.status == self.STATUS_COMPLETED and self.completed_at is None:
#                     self.completed_at = now_ts
#                 if self.status == self.STATUS_CANCELLED and self.cancelled_at is None:
#                     self.cancelled_at = now_ts

#             self.total_amount = self._expected_total()

#             self.full_clean()
#             super().save(*args, **kwargs)

#         try:
#             if self.pk and self.items.exists():
#                 self.recalc_totals(save=True)
#         except Exception:
#             pass

#     # ==========================
#     # HELPERS MÉTIER
#     # ==========================
#     @property
#     def is_paid(self):
#         return self.status in {self.STATUS_PAID, self.STATUS_SHIPPED, self.STATUS_COMPLETED}

#     @property
#     def is_editable(self):
#         return self.status == self.STATUS_PENDING

#     def mark_paid(self):
#         if self.status != self.STATUS_PAID:
#             self.status = self.STATUS_PAID
#         if self.paid_at is None:
#             self.paid_at = timezone.now()
#         self.save(update_fields=["status", "paid_at", "updated_at"])

#     def mark_shipped(self):
#         if self.status != self.STATUS_SHIPPED:
#             self.status = self.STATUS_SHIPPED
#         if self.shipped_at is None:
#             self.shipped_at = timezone.now()
#         self.save(update_fields=["status", "shipped_at", "updated_at"])

#     def mark_completed(self):
#         if self.status != self.STATUS_COMPLETED:
#             self.status = self.STATUS_COMPLETED
#         if self.completed_at is None:
#             self.completed_at = timezone.now()
#         self.save(update_fields=["status", "completed_at", "updated_at"])

#     def mark_cancelled(self):
#         if self.status != self.STATUS_CANCELLED:
#             self.status = self.STATUS_CANCELLED
#         if self.cancelled_at is None:
#             self.cancelled_at = timezone.now()
#         self.save(update_fields=["status", "cancelled_at", "updated_at"])






# # /economic/ecommerce/models/order.py
# from __future__ import annotations

# import uuid
# from decimal import Decimal

# from django.conf import settings
# from django.db import models, transaction
# from django.utils import timezone
# from django.utils.translation import gettext_lazy as _

# D0 = Decimal("0.00")
# Q = models.Q


# class Order(models.Model):
#     # ==========================
#     # STATUTS COMMANDE
#     # ==========================
#     STATUS_PENDING = "pending"
#     STATUS_PAID = "paid"
#     STATUS_SHIPPED = "shipped"
#     STATUS_COMPLETED = "completed"
#     STATUS_CANCELLED = "cancelled"

#     STATUS_CHOICES = [
#         (STATUS_PENDING, _("En attente")),
#         (STATUS_PAID, _("Payée")),
#         (STATUS_SHIPPED, _("Expédiée")),
#         (STATUS_COMPLETED, _("Terminée")),
#         (STATUS_CANCELLED, _("Annulée")),
#     ]

#     # ==========================
#     # IDENTIFIANTS
#     # ==========================
#     uuid = models.UUIDField(
#         default=uuid.uuid4,
#         editable=False,
#         unique=True,
#         verbose_name=_("UUID"),
#     )

#     reference = models.CharField(
#         max_length=20,
#         null=True,
#         blank=True,
#         db_index=True,
#         editable=False,
#         verbose_name=_("Référence"),
#         help_text=_("Auto-générée. Ex: ORD-20260124-0001"),
#     )

#     # ==========================
#     # UTILISATEUR
#     # ==========================
#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.PROTECT,
#         related_name="orders",
#         verbose_name=_("Utilisateur"),
#     )

#     customer_email = models.EmailField(
#         _("Email client"),
#         blank=True,
#         db_index=True,
#         help_text=_("Copie de l'email au moment de la commande (facture / export)."),
#     )

#     # ==========================
#     # FACTURATION / BILLING
#     # ==========================
#     billing_name = models.CharField(
#         max_length=255,
#         blank=True,
#         default="",
#         verbose_name=_("Nom facturation"),
#     )
#     billing_address = models.CharField(
#         max_length=255,
#         blank=True,
#         default="",
#         verbose_name=_("Adresse"),
#     )
#     billing_zip = models.CharField(
#         max_length=32,
#         blank=True,
#         default="",
#         verbose_name=_("Code postal"),
#     )
#     billing_city = models.CharField(
#         max_length=120,
#         blank=True,
#         default="",
#         verbose_name=_("Ville"),
#     )
#     billing_country = models.CharField(
#         max_length=80,
#         blank=True,
#         default="",
#         verbose_name=_("Pays"),
#     )

#     # ==========================
#     # STATUT & MONTANTS
#     # ==========================
#     status = models.CharField(
#         max_length=20,
#         choices=STATUS_CHOICES,
#         default=STATUS_PENDING,
#         verbose_name=_("Statut"),
#         db_index=True,
#     )

#     currency = models.CharField(
#         max_length=10,
#         default="XOF",
#         db_index=True,
#         verbose_name=_("Devise"),
#     )

#     subtotal_amount = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         default=D0,
#         verbose_name=_("Sous-total"),
#         help_text=_("Somme des lignes (items)."),
#     )

#     shipping_amount = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         default=D0,
#         verbose_name=_("Livraison"),
#     )

#     tax_amount = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         default=D0,
#         verbose_name=_("Taxes"),
#     )

#     discount_amount = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         default=D0,
#         verbose_name=_("Remise"),
#         help_text=_("Montant à soustraire du total."),
#     )

#     total_amount = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         default=D0,
#         verbose_name=_("Montant total"),
#     )

#     # ==========================
#     # TIMESTAMPS
#     # ==========================
#     created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Créée le"))
#     updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Mise à jour le"))

#     paid_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Payée le"))
#     shipped_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Expédiée le"))
#     completed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Terminée le"))
#     cancelled_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Annulée le"))

#     # ==========================
#     # MÉTA
#     # ==========================
#     class Meta:
#         verbose_name = _("Commande")
#         verbose_name_plural = _("Commandes")
#         ordering = ["-created_at"]
#         indexes = [
#             models.Index(fields=["status"]),
#             models.Index(fields=["created_at"]),
#             models.Index(fields=["user"]),
#             models.Index(fields=["customer_email"]),
#             models.Index(fields=["reference"]),
#             models.Index(fields=["user", "created_at"]),
#         ]
#         constraints = [
#             models.CheckConstraint(check=Q(total_amount__gte=0), name="chk_order_total_gte_0"),
#             models.CheckConstraint(check=Q(subtotal_amount__gte=0), name="chk_order_subtotal_gte_0"),
#             models.CheckConstraint(check=Q(shipping_amount__gte=0), name="chk_order_shipping_gte_0"),
#             models.CheckConstraint(check=Q(tax_amount__gte=0), name="chk_order_tax_gte_0"),
#             models.CheckConstraint(check=Q(discount_amount__gte=0), name="chk_order_discount_gte_0"),
#             models.UniqueConstraint(
#                 fields=["reference"],
#                 condition=Q(reference__isnull=False) & ~Q(reference=""),
#                 name="uniq_order_reference_not_empty",
#             ),
#         ]

#     # ==========================
#     # STR
#     # ==========================
#     def __str__(self):
#         return self.reference or f"Commande {self.uuid}"

#     # ==========================
#     # HELPERS TEMPLATE
#     # ==========================
#     @property
#     def status_display(self) -> str:
#         try:
#             return self.get_status_display()
#         except Exception:
#             return str(self.status)

#     @property
#     def can_pay(self) -> bool:
#         return self.status == self.STATUS_PENDING

#     # ==========================
#     # HELPERS DÉCIMAL
#     # ==========================
#     @staticmethod
#     def _to_dec(val) -> Decimal:
#         try:
#             return Decimal(val)
#         except Exception:
#             return D0

#     @staticmethod
#     def _q2(val: Decimal) -> Decimal:
#         try:
#             return Decimal(val).quantize(Decimal("0.01"))
#         except Exception:
#             return D0

#     def _normalize_money_fields(self):
#         self.subtotal_amount = self._q2(max(D0, self._to_dec(self.subtotal_amount)))
#         self.shipping_amount = self._q2(max(D0, self._to_dec(self.shipping_amount)))
#         self.tax_amount = self._q2(max(D0, self._to_dec(self.tax_amount)))
#         self.discount_amount = self._q2(max(D0, self._to_dec(self.discount_amount)))
#         self.total_amount = self._q2(max(D0, self._to_dec(self.total_amount)))

#     def _expected_total(self, subtotal: Decimal | None = None) -> Decimal:
#         sub = self._to_dec(subtotal if subtotal is not None else self.subtotal_amount)
#         ship = self._to_dec(self.shipping_amount)
#         tax = self._to_dec(self.tax_amount)
#         disc = self._to_dec(self.discount_amount)
#         total = sub + ship + tax - disc
#         if total < 0:
#             total = D0
#         return self._q2(total)

#     @staticmethod
#     def _normalize_str(s: str | None) -> str | None:
#         if s is None:
#             return None
#         s = str(s).strip()
#         return s if s else None

#     # ==========================
#     # CALCULS
#     # ==========================
#     def calculate_subtotal(self) -> Decimal:
#         total = D0
#         for it in self.items.all():
#             try:
#                 total += Decimal(it.unit_price) * Decimal(it.quantity)
#             except Exception:
#                 continue
#         return self._q2(total)

#     def recalc_totals(self, save: bool = True):
#         new_sub = self.calculate_subtotal()
#         new_total = self._expected_total(subtotal=new_sub)
#         self.subtotal_amount = new_sub
#         self.total_amount = new_total

#         if save and self.pk:
#             type(self).objects.filter(pk=self.pk).update(
#                 subtotal_amount=new_sub,
#                 total_amount=new_total,
#                 updated_at=timezone.now(),
#             )

#     # ==========================
#     # RÉFÉRENCE AUTO (ATOMIC)
#     # ==========================
#     @staticmethod
#     def _reference_prefix() -> str:
#         today = timezone.now().strftime("%Y%m%d")
#         return f"ORD-{today}-"

#     @classmethod
#     def _next_reference(cls) -> str:
#         prefix = cls._reference_prefix()
#         last = (
#             cls.objects.select_for_update()
#             .filter(reference__startswith=prefix)
#             .order_by("-reference")
#             .values_list("reference", flat=True)
#             .first()
#         )
#         last_n = 0
#         if last:
#             try:
#                 last_n = int(last.split("-")[-1])
#             except Exception:
#                 last_n = 0
#         return f"{prefix}{(last_n + 1):04d}"

#     # ==========================
#     # HELPERS MÉTIER
#     # ==========================
#     @property
#     def is_paid(self):
#         return self.status in {self.STATUS_PAID, self.STATUS_SHIPPED, self.STATUS_COMPLETED}

#     @property
#     def is_editable(self):
#         return self.status == self.STATUS_PENDING

#     def mark_paid(self):
#         if self.status != self.STATUS_PAID:
#             self.status = self.STATUS_PAID
#         if self.paid_at is None:
#             self.paid_at = timezone.now()
#         self.save(update_fields=["status", "paid_at", "updated_at"])

#     def mark_shipped(self):
#         if self.status != self.STATUS_SHIPPED:
#             self.status = self.STATUS_SHIPPED
#         if self.shipped_at is None:
#             self.shipped_at = timezone.now()
#         self.save(update_fields=["status", "shipped_at", "updated_at"])

#     def mark_completed(self):
#         if self.status != self.STATUS_COMPLETED:
#             self.status = self.STATUS_COMPLETED
#         if self.completed_at is None:
#             self.completed_at = timezone.now()
#         self.save(update_fields=["status", "completed_at", "updated_at"])

#     def mark_cancelled(self):
#         if self.status != self.STATUS_CANCELLED:
#             self.status = self.STATUS_CANCELLED
#         if self.cancelled_at is None:
#             self.cancelled_at = timezone.now()
#         self.save(update_fields=["status", "cancelled_at", "updated_at"])

#     # ==========================
#     # SAVE
#     # ==========================
#     def save(self, *args, **kwargs):
#         # Normalisations
#         if self.currency:
#             self.currency = (self.currency or "").strip().upper() or "XOF"

#         # Email snapshot
#         if self.user_id and not self.customer_email:
#             self.customer_email = getattr(self.user, "email", "") or ""

#         # Billing defaults
#         self.billing_name = (self.billing_name or "").strip()
#         self.billing_address = (self.billing_address or "").strip()
#         self.billing_zip = (self.billing_zip or "").strip()
#         self.billing_city = (self.billing_city or "").strip()
#         self.billing_country = (self.billing_country or "").strip()

#         self.reference = self._normalize_str(self.reference)
#         self._normalize_money_fields()

#         with transaction.atomic():
#             previous_status = None
#             if self.pk:
#                 previous_status = (
#                     type(self).objects.select_for_update()
#                     .filter(pk=self.pk)
#                     .values_list("status", flat=True)
#                     .first()
#                 )

#             if not self.reference:
#                 self.reference = self._next_reference()

#             now_ts = timezone.now()
#             if previous_status != self.status:
#                 if self.status == self.STATUS_PAID and self.paid_at is None:
#                     self.paid_at = now_ts
#                 if self.status == self.STATUS_SHIPPED and self.shipped_at is None:
#                     self.shipped_at = now_ts
#                 if self.status == self.STATUS_COMPLETED and self.completed_at is None:
#                     self.completed_at = now_ts
#                 if self.status == self.STATUS_CANCELLED and self.cancelled_at is None:
#                     self.cancelled_at = now_ts

#             self.total_amount = self._expected_total()

#             self.full_clean()
#             super().save(*args, **kwargs)

#         try:
#             if self.pk and self.items.exists():
#                 self.recalc_totals(save=True)
#         except Exception:
#             pass







# # /economic/ecommerce/models/order.py
# from __future__ import annotations

# import uuid
# from decimal import Decimal

# from django.conf import settings
# from django.db import models, transaction
# from django.utils import timezone
# from django.utils.translation import gettext_lazy as _

# D0 = Decimal("0.00")
# Q = models.Q


# class Order(models.Model):
#     # ==========================
#     # STATUTS COMMANDE
#     # ==========================
#     STATUS_PENDING = "pending"
#     STATUS_PAID = "paid"
#     STATUS_SHIPPED = "shipped"
#     STATUS_COMPLETED = "completed"
#     STATUS_CANCELLED = "cancelled"

#     STATUS_CHOICES = [
#         (STATUS_PENDING, _("En attente")),
#         (STATUS_PAID, _("Payée")),
#         (STATUS_SHIPPED, _("Expédiée")),
#         (STATUS_COMPLETED, _("Terminée")),
#         (STATUS_CANCELLED, _("Annulée")),
#     ]

#     # ==========================
#     # IDENTIFIANTS
#     # ==========================
#     uuid = models.UUIDField(
#         default=uuid.uuid4,
#         editable=False,
#         unique=True,
#         verbose_name=_("UUID"),
#     )

#     # ⚠️ IMPORTANT:
#     # - PAS de unique=True ici (ça casse si des lignes existantes ont reference="")
#     # - On impose l'unicité via UniqueConstraint conditionnel (Postgres)
#     reference = models.CharField(
#         max_length=20,
#         null=True,
#         blank=True,
#         db_index=True,
#         editable=False,
#         verbose_name=_("Référence"),
#         help_text=_("Auto-générée. Ex: ORD-20260124-0001"),
#     )

#     # ==========================
#     # UTILISATEUR
#     # ==========================
#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.PROTECT,
#         related_name="orders",
#         verbose_name=_("Utilisateur"),
#     )

#     customer_email = models.EmailField(
#         _("Email client"),
#         blank=True,
#         db_index=True,
#         help_text=_("Copie de l'email au moment de la commande (facture / export)."),
#     )

#     # ==========================
#     # STATUT & MONTANTS
#     # ==========================
#     status = models.CharField(
#         max_length=20,
#         choices=STATUS_CHOICES,
#         default=STATUS_PENDING,
#         verbose_name=_("Statut"),
#         db_index=True,
#     )

#     currency = models.CharField(
#         max_length=10,
#         default="XOF",
#         db_index=True,
#         verbose_name=_("Devise"),
#     )

#     subtotal_amount = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         default=D0,
#         verbose_name=_("Sous-total"),
#         help_text=_("Somme des lignes (items)."),
#     )

#     shipping_amount = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         default=D0,
#         verbose_name=_("Livraison"),
#     )

#     tax_amount = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         default=D0,
#         verbose_name=_("Taxes"),
#     )

#     discount_amount = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         default=D0,
#         verbose_name=_("Remise"),
#         help_text=_("Montant à soustraire du total."),
#     )

#     total_amount = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         default=D0,
#         verbose_name=_("Montant total"),
#     )

#     # ==========================
#     # TIMESTAMPS
#     # ==========================
#     created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Créée le"))
#     updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Mise à jour le"))

#     paid_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Payée le"))
#     shipped_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Expédiée le"))
#     completed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Terminée le"))
#     cancelled_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Annulée le"))

#     class Meta:
#         verbose_name = _("Commande")
#         verbose_name_plural = _("Commandes")
#         ordering = ["-created_at"]
#         indexes = [
#             models.Index(fields=["status"]),
#             models.Index(fields=["created_at"]),
#             models.Index(fields=["user"]),
#             models.Index(fields=["customer_email"]),
#             models.Index(fields=["reference"]),
#             models.Index(fields=["user", "created_at"]),
#         ]
#         constraints = [
#             models.CheckConstraint(check=Q(total_amount__gte=0), name="chk_order_total_gte_0"),
#             models.CheckConstraint(check=Q(subtotal_amount__gte=0), name="chk_order_subtotal_gte_0"),
#             models.CheckConstraint(check=Q(shipping_amount__gte=0), name="chk_order_shipping_gte_0"),
#             models.CheckConstraint(check=Q(tax_amount__gte=0), name="chk_order_tax_gte_0"),
#             models.CheckConstraint(check=Q(discount_amount__gte=0), name="chk_order_discount_gte_0"),

#             # ✅ Unicité "utile" : unique seulement si reference est non NULL et non vide.
#             # => évite l'erreur Postgres si des anciennes lignes ont reference="".
#             models.UniqueConstraint(
#                 fields=["reference"],
#                 condition=Q(reference__isnull=False) & ~Q(reference=""),
#                 name="uniq_order_reference_not_empty",
#             ),
#         ]

#     def __str__(self):
#         return self.reference or f"Commande {self.uuid}"

#     # ==========================
#     # DECIMAL HELPERS
#     # ==========================
#     @staticmethod
#     def _to_dec(val) -> Decimal:
#         try:
#             return Decimal(val)
#         except Exception:
#             return D0

#     @staticmethod
#     def _q2(val: Decimal) -> Decimal:
#         try:
#             return Decimal(val).quantize(Decimal("0.01"))
#         except Exception:
#             return D0

#     def _normalize_money_fields(self):
#         self.subtotal_amount = self._q2(max(D0, self._to_dec(self.subtotal_amount)))
#         self.shipping_amount = self._q2(max(D0, self._to_dec(self.shipping_amount)))
#         self.tax_amount = self._q2(max(D0, self._to_dec(self.tax_amount)))
#         self.discount_amount = self._q2(max(D0, self._to_dec(self.discount_amount)))
#         self.total_amount = self._q2(max(D0, self._to_dec(self.total_amount)))

#     def _expected_total(self, subtotal: Decimal | None = None) -> Decimal:
#         sub = self._to_dec(subtotal if subtotal is not None else self.subtotal_amount)
#         ship = self._to_dec(self.shipping_amount)
#         tax = self._to_dec(self.tax_amount)
#         disc = self._to_dec(self.discount_amount)
#         total = sub + ship + tax - disc
#         if total < 0:
#             total = D0
#         return self._q2(total)

#     @staticmethod
#     def _normalize_str(s: str | None) -> str | None:
#         if s is None:
#             return None
#         s = str(s).strip()
#         return s if s else None

#     # ==========================
#     # CALCULS
#     # ==========================
#     def calculate_subtotal(self) -> Decimal:
#         total = D0
#         for it in self.items.all():
#             try:
#                 total += (Decimal(it.unit_price) * Decimal(it.quantity))
#             except Exception:
#                 continue
#         return self._q2(total)

#     def recalc_totals(self, save: bool = True):
#         new_sub = self.calculate_subtotal()
#         new_total = self._expected_total(subtotal=new_sub)
#         self.subtotal_amount = new_sub
#         self.total_amount = new_total

#         if save and self.pk:
#             type(self).objects.filter(pk=self.pk).update(
#                 subtotal_amount=new_sub,
#                 total_amount=new_total,
#                 updated_at=timezone.now(),
#             )

#     # ==========================
#     # REFERENCE AUTO (atomic)
#     # ==========================
#     @staticmethod
#     def _reference_prefix() -> str:
#         today = timezone.now().strftime("%Y%m%d")
#         return f"ORD-{today}-"

#     @classmethod
#     def _next_reference(cls) -> str:
#         prefix = cls._reference_prefix()
#         last = (
#             cls.objects.select_for_update()
#             .filter(reference__startswith=prefix)
#             .order_by("-reference")
#             .values_list("reference", flat=True)
#             .first()
#         )
#         last_n = 0
#         if last:
#             try:
#                 last_n = int(last.split("-")[-1])
#             except Exception:
#                 last_n = 0
#         return f"{prefix}{(last_n + 1):04d}"

#     # ==========================
#     # SAVE (prod safe)
#     # ==========================
#     def save(self, *args, **kwargs):
#         # Normalisations
#         if self.currency:
#             self.currency = (self.currency or "").strip().upper() or "XOF"

#         # Email snapshot
#         if self.user_id and not self.customer_email:
#             self.customer_email = getattr(self.user, "email", "") or ""

#         # IMPORTANT: éviter "" en DB
#         self.reference = self._normalize_str(self.reference)

#         self._normalize_money_fields()

#         with transaction.atomic():
#             previous_status = None
#             if self.pk:
#                 previous_status = (
#                     type(self).objects.select_for_update()
#                     .filter(pk=self.pk)
#                     .values_list("status", flat=True)
#                     .first()
#                 )

#             # Référence auto si absente
#             if not self.reference:
#                 self.reference = self._next_reference()

#             # Timestamps de transition
#             now_ts = timezone.now()
#             if previous_status != self.status:
#                 if self.status == self.STATUS_PAID and self.paid_at is None:
#                     self.paid_at = now_ts
#                 if self.status == self.STATUS_SHIPPED and self.shipped_at is None:
#                     self.shipped_at = now_ts
#                 if self.status == self.STATUS_COMPLETED and self.completed_at is None:
#                     self.completed_at = now_ts
#                 if self.status == self.STATUS_CANCELLED and self.cancelled_at is None:
#                     self.cancelled_at = now_ts

#             # total cohérent
#             self.total_amount = self._expected_total()

#             # sécurité prod
#             self.full_clean()
#             super().save(*args, **kwargs)

#         # Recalc non récursif (update SQL)
#         try:
#             if self.pk and self.items.exists():
#                 self.recalc_totals(save=True)
#         except Exception:
#             pass

#     # ==========================
#     # HELPERS MÉTIER
#     # ==========================
#     @property
#     def is_paid(self):
#         return self.status in {self.STATUS_PAID, self.STATUS_SHIPPED, self.STATUS_COMPLETED}

#     @property
#     def is_editable(self):
#         return self.status == self.STATUS_PENDING

#     def mark_paid(self):
#         if self.status != self.STATUS_PAID:
#             self.status = self.STATUS_PAID
#         if self.paid_at is None:
#             self.paid_at = timezone.now()
#         self.save(update_fields=["status", "paid_at", "updated_at"])

#     def mark_shipped(self):
#         if self.status != self.STATUS_SHIPPED:
#             self.status = self.STATUS_SHIPPED
#         if self.shipped_at is None:
#             self.shipped_at = timezone.now()
#         self.save(update_fields=["status", "shipped_at", "updated_at"])

#     def mark_completed(self):
#         if self.status != self.STATUS_COMPLETED:
#             self.status = self.STATUS_COMPLETED
#         if self.completed_at is None:
#             self.completed_at = timezone.now()
#         self.save(update_fields=["status", "completed_at", "updated_at"])

#     def mark_cancelled(self):
#         if self.status != self.STATUS_CANCELLED:
#             self.status = self.STATUS_CANCELLED
#         if self.cancelled_at is None:
#             self.cancelled_at = timezone.now()
#         self.save(update_fields=["status", "cancelled_at", "updated_at"])





# # /economic/ecommerce/models/order.py
# from __future__ import annotations

# import uuid
# from decimal import Decimal

# from django.conf import settings
# from django.core.exceptions import ValidationError
# from django.db import models, transaction
# from django.utils import timezone
# from django.utils.translation import gettext_lazy as _


# D0 = Decimal("0.00")


# class Order(models.Model):
#     # ==========================
#     # STATUTS COMMANDE
#     # ==========================
#     STATUS_PENDING = "pending"
#     STATUS_PAID = "paid"
#     STATUS_SHIPPED = "shipped"
#     STATUS_COMPLETED = "completed"
#     STATUS_CANCELLED = "cancelled"

#     STATUS_CHOICES = [
#         (STATUS_PENDING, _("En attente")),
#         (STATUS_PAID, _("Payée")),
#         (STATUS_SHIPPED, _("Expédiée")),
#         (STATUS_COMPLETED, _("Terminée")),
#         (STATUS_CANCELLED, _("Annulée")),
#     ]

#     # ==========================
#     # IDENTIFIANTS
#     # ==========================
#     uuid = models.UUIDField(
#         default=uuid.uuid4,
#         editable=False,
#         unique=True,
#         verbose_name=_("UUID"),
#     )

#     reference = models.CharField(
#         max_length=20,
#         null=True,              # ✅ important
#         blank=True,
#         unique=True,
#         db_index=True,
#         verbose_name=_("Référence"),
#         help_text=_("Auto-générée. Ex: ORD-20260124-0001"),
#     )

#     # ==========================
#     # UTILISATEUR
#     # ==========================
#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.PROTECT,
#         related_name="orders",
#         verbose_name=_("Utilisateur"),
#     )

#     customer_email = models.EmailField(
#         _("Email client"),
#         blank=True,
#         db_index=True,
#         help_text=_("Copie de l'email au moment de la commande (facture / export)."),
#     )

#     # ==========================
#     # STATUT & MONTANTS
#     # ==========================
#     status = models.CharField(
#         max_length=20,
#         choices=STATUS_CHOICES,
#         default=STATUS_PENDING,
#         verbose_name=_("Statut"),
#         db_index=True,
#     )

#     currency = models.CharField(
#         max_length=10,
#         default="XOF",
#         db_index=True,
#         verbose_name=_("Devise"),
#     )

#     subtotal_amount = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         default=D0,
#         verbose_name=_("Sous-total"),
#         help_text=_("Somme des lignes (items)."),
#     )

#     shipping_amount = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         default=D0,
#         verbose_name=_("Livraison"),
#     )

#     tax_amount = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         default=D0,
#         verbose_name=_("Taxes"),
#     )

#     discount_amount = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         default=D0,
#         verbose_name=_("Remise"),
#         help_text=_("Montant à soustraire du total."),
#     )

#     total_amount = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         default=D0,
#         verbose_name=_("Montant total"),
#     )

#     # ==========================
#     # TIMESTAMPS
#     # ==========================
#     created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Créée le"))
#     updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Mise à jour le"))

#     paid_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Payée le"))
#     shipped_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Expédiée le"))
#     completed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Terminée le"))
#     cancelled_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Annulée le"))

#     class Meta:
#         verbose_name = _("Commande")
#         verbose_name_plural = _("Commandes")
#         ordering = ["-created_at"]
#         indexes = [
#             models.Index(fields=["status"]),
#             models.Index(fields=["created_at"]),
#             models.Index(fields=["user"]),
#             models.Index(fields=["customer_email"]),
#             models.Index(fields=["reference"]),
#             models.Index(fields=["user", "created_at"]),
#         ]
#         constraints = [
#             models.CheckConstraint(check=models.Q(total_amount__gte=0), name="chk_order_total_gte_0"),
#             models.CheckConstraint(check=models.Q(subtotal_amount__gte=0), name="chk_order_subtotal_gte_0"),
#             models.CheckConstraint(check=models.Q(shipping_amount__gte=0), name="chk_order_shipping_gte_0"),
#             models.CheckConstraint(check=models.Q(tax_amount__gte=0), name="chk_order_tax_gte_0"),
#             models.CheckConstraint(check=models.Q(discount_amount__gte=0), name="chk_order_discount_gte_0"),
#         ]

#     def __str__(self):
#         return self.reference or f"Commande {self.uuid}"

#     # ==========================
#     # DECIMAL HELPERS (prod)
#     # ==========================
#     @staticmethod
#     def _to_dec(val) -> Decimal:
#         try:
#             return Decimal(val)
#         except Exception:
#             return D0

#     @staticmethod
#     def _q2(val: Decimal) -> Decimal:
#         try:
#             return Decimal(val).quantize(Decimal("0.01"))
#         except Exception:
#             return D0

#     def _normalize_money_fields(self):
#         self.subtotal_amount = self._q2(max(D0, self._to_dec(self.subtotal_amount)))
#         self.shipping_amount = self._q2(max(D0, self._to_dec(self.shipping_amount)))
#         self.tax_amount = self._q2(max(D0, self._to_dec(self.tax_amount)))
#         self.discount_amount = self._q2(max(D0, self._to_dec(self.discount_amount)))
#         self.total_amount = self._q2(max(D0, self._to_dec(self.total_amount)))

#     def _expected_total(self, subtotal: Decimal | None = None) -> Decimal:
#         sub = self._to_dec(subtotal if subtotal is not None else self.subtotal_amount)
#         ship = self._to_dec(self.shipping_amount)
#         tax = self._to_dec(self.tax_amount)
#         disc = self._to_dec(self.discount_amount)

#         total = sub + ship + tax - disc
#         if total < 0:
#             total = D0
#         return self._q2(total)

#     # ==========================
#     # VALIDATION / NORMALISATION
#     # ==========================
#     def clean(self):
#         super().clean()

#         if self.currency:
#             self.currency = self.currency.strip().upper()

#         # Email snapshot
#         if self.user_id and not self.customer_email:
#             self.customer_email = getattr(self.user, "email", "") or ""

#         self._normalize_money_fields()

#         # On garde total cohérent (sans bloquer) : auto-corrige si besoin
#         expected = self._expected_total()
#         if self.total_amount != expected:
#             self.total_amount = expected

#     # ==========================
#     # CALCULS
#     # ==========================
#     def calculate_subtotal(self) -> Decimal:
#         total = D0
#         for it in self.items.all():
#             try:
#                 total += (Decimal(it.unit_price) * Decimal(it.quantity))
#             except Exception:
#                 continue
#         return self._q2(total)

#     def calculate_total(self) -> Decimal:
#         return self._expected_total()

#     def recalc_totals(self, save: bool = True):
#         """
#         Recalcule subtotal/total depuis les items.
#         ✅ Si save=True : update SQL direct (évite double save/re-entrance).
#         """
#         new_sub = self.calculate_subtotal()
#         new_total = self._expected_total(subtotal=new_sub)

#         self.subtotal_amount = new_sub
#         self.total_amount = new_total

#         if save and self.pk:
#             type(self).objects.filter(pk=self.pk).update(
#                 subtotal_amount=new_sub,
#                 total_amount=new_total,
#                 updated_at=timezone.now(),
#             )

#     # ==========================
#     # REFERENCE AUTO (atomic)
#     # ==========================
#     @staticmethod
#     def _reference_prefix() -> str:
#         today = timezone.now().strftime("%Y%m%d")
#         return f"ORD-{today}-"

#     @classmethod
#     def _next_reference(cls) -> str:
#         prefix = cls._reference_prefix()
#         last = (
#             cls.objects.select_for_update()
#             .filter(reference__startswith=prefix)
#             .order_by("-reference")
#             .values_list("reference", flat=True)
#             .first()
#         )
#         last_n = 0
#         if last:
#             try:
#                 last_n = int(last.split("-")[-1])
#             except Exception:
#                 last_n = 0
#         return f"{prefix}{(last_n + 1):04d}"

#     # ==========================
#     # SAVE (prod safe)
#     # ==========================
#     def save(self, *args, **kwargs):
#         """
#         - Auto-génère reference (anti-collision)
#         - Normalise currency + montants
#         - Auto timestamps de statut (paid/shipped/completed/cancelled)
#         - full_clean() (sécurité prod)
#         """
#         # Pré-normalisation
#         if self.currency:
#             self.currency = self.currency.strip().upper()
#         if self.user_id and not self.customer_email:
#             self.customer_email = getattr(self.user, "email", "") or ""

#         self._normalize_money_fields()

#         with transaction.atomic():
#             previous_status = None
#             if self.pk:
#                 previous_status = (
#                     type(self).objects.select_for_update()
#                     .filter(pk=self.pk)
#                     .values_list("status", flat=True)
#                     .first()
#                 )

#             # Reference auto (avant full_clean pour éviter unique blank)
#             if not self.reference:
#                 self.reference = self._next_reference()

#             # Auto timestamps de transition (sans écraser si déjà défini)
#             now_ts = timezone.now()
#             if previous_status != self.status:
#                 if self.status == self.STATUS_PAID and self.paid_at is None:
#                     self.paid_at = now_ts
#                 if self.status == self.STATUS_SHIPPED and self.shipped_at is None:
#                     self.shipped_at = now_ts
#                 if self.status == self.STATUS_COMPLETED and self.completed_at is None:
#                     self.completed_at = now_ts
#                 if self.status == self.STATUS_CANCELLED and self.cancelled_at is None:
#                     self.cancelled_at = now_ts

#             # total cohérent
#             self.total_amount = self._expected_total()

#             # ✅ sécurité prod
#             self.full_clean()
#             super().save(*args, **kwargs)

#         # Recalc automatique si items existent (utile quand shipping/tax/discount changent)
#         # ⚠️ ne fait pas de save() récursif : update SQL via recalc_totals()
#         try:
#             if self.pk and self.items.exists():
#                 self.recalc_totals(save=True)
#         except Exception:
#             pass

#     # ==========================
#     # HELPERS MÉTIER
#     # ==========================
#     @property
#     def is_paid(self):
#         return self.status in {self.STATUS_PAID, self.STATUS_SHIPPED, self.STATUS_COMPLETED}

#     @property
#     def is_editable(self):
#         return self.status == self.STATUS_PENDING

#     # Helpers transitions (pratiques webhooks/services)
#     def mark_paid(self):
#         if self.status != self.STATUS_PAID:
#             self.status = self.STATUS_PAID
#         if self.paid_at is None:
#             self.paid_at = timezone.now()
#         self.save(update_fields=["status", "paid_at", "updated_at"])

#     def mark_shipped(self):
#         if self.status != self.STATUS_SHIPPED:
#             self.status = self.STATUS_SHIPPED
#         if self.shipped_at is None:
#             self.shipped_at = timezone.now()
#         self.save(update_fields=["status", "shipped_at", "updated_at"])

#     def mark_completed(self):
#         if self.status != self.STATUS_COMPLETED:
#             self.status = self.STATUS_COMPLETED
#         if self.completed_at is None:
#             self.completed_at = timezone.now()
#         self.save(update_fields=["status", "completed_at", "updated_at"])

#     def mark_cancelled(self):
#         if self.status != self.STATUS_CANCELLED:
#             self.status = self.STATUS_CANCELLED
#         if self.cancelled_at is None:
#             self.cancelled_at = timezone.now()
#         self.save(update_fields=["status", "cancelled_at", "updated_at"])





# # /economic/ecommerce/models/order.py
# from __future__ import annotations

# import uuid
# from decimal import Decimal

# from django.conf import settings
# from django.core.exceptions import ValidationError
# from django.db import models, transaction
# from django.utils import timezone
# from django.utils.translation import gettext_lazy as _


# class Order(models.Model):
#     # ==========================
#     # STATUTS COMMANDE
#     # ==========================
#     STATUS_PENDING = "pending"
#     STATUS_PAID = "paid"
#     STATUS_SHIPPED = "shipped"
#     STATUS_COMPLETED = "completed"
#     STATUS_CANCELLED = "cancelled"

#     STATUS_CHOICES = [
#         (STATUS_PENDING, _("En attente")),
#         (STATUS_PAID, _("Payée")),
#         (STATUS_SHIPPED, _("Expédiée")),
#         (STATUS_COMPLETED, _("Terminée")),
#         (STATUS_CANCELLED, _("Annulée")),
#     ]

#     # ==========================
#     # IDENTIFIANTS
#     # ==========================
#     uuid = models.UUIDField(
#         default=uuid.uuid4,
#         editable=False,
#         unique=True,
#         verbose_name=_("UUID"),
#     )

#     # ✅ Référence lisible (utile support / SAV / facture)
#     reference = models.CharField(
#         max_length=20,
#         blank=True,
#         unique=True,
#         db_index=True,
#         verbose_name=_("Référence"),
#         help_text=_("Auto-générée. Ex: ORD-20260124-0001"),
#     )

#     # ==========================
#     # UTILISATEUR (source de vérité)
#     # ==========================
#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.PROTECT,  # 🔒 on ne supprime jamais une commande
#         related_name="orders",
#         verbose_name=_("Utilisateur"),
#     )

#     # ==========================
#     # SNAPSHOT EMAIL (facture / export)
#     # ==========================
#     customer_email = models.EmailField(
#         _("Email client"),
#         blank=True,
#         db_index=True,
#         help_text=_("Copie de l'email au moment de la commande (facture / export)."),
#     )

#     # ==========================
#     # STATUT & MONTANTS
#     # ==========================
#     status = models.CharField(
#         max_length=20,
#         choices=STATUS_CHOICES,
#         default=STATUS_PENDING,
#         verbose_name=_("Statut"),
#         db_index=True,
#     )

#     # ✅ Devise
#     currency = models.CharField(
#         max_length=10,
#         default="XOF",
#         db_index=True,
#         verbose_name=_("Devise"),
#     )

#     # ✅ Détails totaux (prod checkout)
#     subtotal_amount = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         default=Decimal("0.00"),
#         verbose_name=_("Sous-total"),
#         help_text=_("Somme des lignes (items)."),
#     )

#     shipping_amount = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         default=Decimal("0.00"),
#         verbose_name=_("Livraison"),
#     )

#     tax_amount = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         default=Decimal("0.00"),
#         verbose_name=_("Taxes"),
#     )

#     discount_amount = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         default=Decimal("0.00"),
#         verbose_name=_("Remise"),
#         help_text=_("Montant à soustraire du total."),
#     )

#     total_amount = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         default=Decimal("0.00"),
#         verbose_name=_("Montant total"),
#     )

#     # ==========================
#     # TIMESTAMPS
#     # ==========================
#     created_at = models.DateTimeField(
#         auto_now_add=True,
#         verbose_name=_("Créée le"),
#     )

#     updated_at = models.DateTimeField(
#         auto_now=True,
#         verbose_name=_("Mise à jour le"),
#     )

#     # ✅ Timestamps métier (très utiles en prod)
#     paid_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Payée le"))
#     shipped_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Expédiée le"))
#     completed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Terminée le"))
#     cancelled_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Annulée le"))

#     class Meta:
#         verbose_name = _("Commande")
#         verbose_name_plural = _("Commandes")
#         ordering = ["-created_at"]
#         indexes = [
#             models.Index(fields=["status"]),
#             models.Index(fields=["created_at"]),
#             models.Index(fields=["user"]),
#             models.Index(fields=["customer_email"]),
#             models.Index(fields=["reference"]),
#             models.Index(fields=["user", "created_at"]),
#         ]
#         constraints = [
#             models.CheckConstraint(check=models.Q(total_amount__gte=0), name="chk_order_total_gte_0"),
#             models.CheckConstraint(check=models.Q(subtotal_amount__gte=0), name="chk_order_subtotal_gte_0"),
#             models.CheckConstraint(check=models.Q(shipping_amount__gte=0), name="chk_order_shipping_gte_0"),
#             models.CheckConstraint(check=models.Q(tax_amount__gte=0), name="chk_order_tax_gte_0"),
#             models.CheckConstraint(check=models.Q(discount_amount__gte=0), name="chk_order_discount_gte_0"),
#         ]

#     def __str__(self):
#         return self.reference or f"Commande {self.uuid}"

#     # ==========================
#     # VALIDATION / NORMALISATION
#     # ==========================
#     def clean(self):
#         super().clean()

#         if self.currency:
#             self.currency = self.currency.strip().upper()

#         # interdit modifications après paiement (sauf si tu le forces côté admin)
#         if self.pk and not self.is_editable:
#             # pas un blocage absolu ici pour ne pas casser admin,
#             # mais on peut protéger côté services.
#             pass

#         # cohérence : total = subtotal + shipping + tax - discount
#         # (tolérance en Decimal)
#         expected = (self.subtotal_amount or 0) + (self.shipping_amount or 0) + (self.tax_amount or 0) - (self.discount_amount or 0)
#         if self.total_amount is None:
#             self.total_amount = Decimal("0.00")

#         # si total déjà rempli, on laisse; sinon on recalculera en save() si nécessaire

#         if self.user_id and not self.customer_email:
#             self.customer_email = getattr(self.user, "email", "") or ""

#     # ==========================
#     # CALCULS
#     # ==========================
#     def calculate_subtotal(self) -> Decimal:
#         """
#         Calcule le sous-total depuis les OrderItem.
#         """
#         total = Decimal("0.00")
#         for it in self.items.all():
#             try:
#                 total += (Decimal(it.unit_price) * Decimal(it.quantity))
#             except Exception:
#                 continue
#         return total.quantize(Decimal("0.01"))

#     def calculate_total(self) -> Decimal:
#         subtotal = Decimal(self.subtotal_amount or 0)
#         shipping = Decimal(self.shipping_amount or 0)
#         tax = Decimal(self.tax_amount or 0)
#         discount = Decimal(self.discount_amount or 0)
#         total = subtotal + shipping + tax - discount
#         if total < 0:
#             total = Decimal("0.00")
#         return total.quantize(Decimal("0.01"))

#     def recalc_totals(self, save: bool = True):
#         """
#         Recalcule subtotal/total depuis les items.
#         Utiliser après ajout/suppression d'items.
#         """
#         self.subtotal_amount = self.calculate_subtotal()
#         self.total_amount = self.calculate_total()
#         if save:
#             self.save(update_fields=["subtotal_amount", "total_amount", "updated_at"])

#     # ==========================
#     # REFERENCE AUTO
#     # ==========================
#     @staticmethod
#     def _generate_reference() -> str:
#         # Format: ORD-YYYYMMDD-XXXX
#         today = timezone.now().strftime("%Y%m%d")
#         # suffix généré en s’appuyant sur les dernières refs du jour (simple + robuste)
#         prefix = f"ORD-{today}-"
#         return prefix  # suffix ajouté en save() atomic

#     # ==========================
#     # SAVE
#     # ==========================
#     def save(self, *args, **kwargs):
#         """
#         - Remplit customer_email lors de la création
#         - Auto-génère reference
#         - Normalise currency
#         - Assure totals (au moins cohérents)
#         """
#         if self.user_id and not self.customer_email:
#             self.customer_email = getattr(self.user, "email", "") or ""

#         if self.currency:
#             self.currency = self.currency.strip().upper()

#         with transaction.atomic():
#             # reference auto
#             if not self.reference:
#                 base = self._generate_reference()
#                 # trouve la dernière ref du jour
#                 last = (
#                     Order.objects.select_for_update()
#                     .filter(reference__startswith=base)
#                     .order_by("-reference")
#                     .values_list("reference", flat=True)
#                     .first()
#                 )
#                 last_n = 0
#                 if last:
#                     try:
#                         last_n = int(last.split("-")[-1])
#                     except Exception:
#                         last_n = 0
#                 self.reference = f"{base}{(last_n + 1):04d}"

#             # Si subtotal/total pas encore renseignés, on initialise proprement
#             if self.subtotal_amount is None:
#                 self.subtotal_amount = Decimal("0.00")
#             if self.total_amount is None:
#                 self.total_amount = Decimal("0.00")

#             # Si total est 0 mais qu’on a déjà des items, on peut recalculer après save
#             super().save(*args, **kwargs)

#             # Recalc auto uniquement si items existent et total non cohérent
#             if self.items.exists():
#                 new_subtotal = self.calculate_subtotal()
#                 new_total = (new_subtotal + Decimal(self.shipping_amount or 0) + Decimal(self.tax_amount or 0) - Decimal(self.discount_amount or 0))
#                 if new_total < 0:
#                     new_total = Decimal("0.00")
#                 new_total = new_total.quantize(Decimal("0.01"))

#                 if (self.subtotal_amount != new_subtotal) or (self.total_amount != new_total):
#                     self.subtotal_amount = new_subtotal
#                     self.total_amount = new_total
#                     super().save(update_fields=["subtotal_amount", "total_amount", "updated_at"])

#     # ==========================
#     # HELPERS MÉTIER
#     # ==========================
#     @property
#     def is_paid(self):
#         return self.status in {
#             self.STATUS_PAID,
#             self.STATUS_SHIPPED,
#             self.STATUS_COMPLETED,
#         }

#     @property
#     def is_editable(self):
#         """
#         Une commande ne doit plus être modifiée après paiement
#         """
#         return self.status == self.STATUS_PENDING

#     # ✅ Helpers statut (pratiques pour paiements/webhooks)
#     def mark_paid(self):
#         self.status = self.STATUS_PAID
#         self.paid_at = timezone.now()
#         self.save(update_fields=["status", "paid_at", "updated_at"])

#     def mark_shipped(self):
#         self.status = self.STATUS_SHIPPED
#         self.shipped_at = timezone.now()
#         self.save(update_fields=["status", "shipped_at", "updated_at"])

#     def mark_completed(self):
#         self.status = self.STATUS_COMPLETED
#         self.completed_at = timezone.now()
#         self.save(update_fields=["status", "completed_at", "updated_at"])

#     def mark_cancelled(self):
#         self.status = self.STATUS_CANCELLED
#         self.cancelled_at = timezone.now()
#         self.save(update_fields=["status", "cancelled_at", "updated_at"])












# # /economic/ecommerce/models/order.py
# import uuid
# from django.conf import settings
# from django.db import models
# from django.utils.translation import gettext_lazy as _


# class Order(models.Model):
#     # ==========================
#     # STATUTS COMMANDE
#     # ==========================
#     STATUS_PENDING = "pending"
#     STATUS_PAID = "paid"
#     STATUS_SHIPPED = "shipped"
#     STATUS_COMPLETED = "completed"
#     STATUS_CANCELLED = "cancelled"

#     STATUS_CHOICES = [
#         (STATUS_PENDING, _("En attente")),
#         (STATUS_PAID, _("Payée")),
#         (STATUS_SHIPPED, _("Expédiée")),
#         (STATUS_COMPLETED, _("Terminée")),
#         (STATUS_CANCELLED, _("Annulée")),
#     ]

#     # ==========================
#     # IDENTIFIANT PUBLIC
#     # ==========================
#     uuid = models.UUIDField(
#         default=uuid.uuid4,
#         editable=False,
#         unique=True,
#         verbose_name=_("UUID"),
#     )

#     # ==========================
#     # UTILISATEUR
#     # ==========================
#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.PROTECT,   # 🔒 on ne supprime jamais une commande
#         related_name="orders",
#         verbose_name=_("Utilisateur"),
#     )

#     # ==========================
#     # STATUT & MONTANT
#     # ==========================
#     status = models.CharField(
#         max_length=20,
#         choices=STATUS_CHOICES,
#         default=STATUS_PENDING,
#         verbose_name=_("Statut"),
#         db_index=True,  # 🔑 important pour filtres admin / dashboard
#     )

#     total_amount = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         verbose_name=_("Montant total"),
#     )

#     # ==========================
#     # TIMESTAMPS
#     # ==========================
#     created_at = models.DateTimeField(
#         auto_now_add=True,
#         verbose_name=_("Créée le"),
#     )

#     updated_at = models.DateTimeField(
#         auto_now=True,
#         verbose_name=_("Mise à jour le"),
#     )

#     class Meta:
#         verbose_name = _("Commande")
#         verbose_name_plural = _("Commandes")
#         ordering = ["-created_at"]
#         indexes = [
#             models.Index(fields=["status"]),
#             models.Index(fields=["created_at"]),
#         ]

#     def __str__(self):
#         return f"Commande {self.uuid}"

#     # ==========================
#     # HELPERS MÉTIER
#     # ==========================
#     @property
#     def is_paid(self):
#         return self.status in {self.STATUS_PAID, self.STATUS_SHIPPED, self.STATUS_COMPLETED}

#     @property
#     def is_editable(self):
#         """
#         Une commande ne doit plus être modifiée après paiement
#         """
#         return self.status == self.STATUS_PENDING








# # /economic/ecommerce/models/order.py

# import uuid
# from django.conf import settings
# from django.db import models
# from django.utils.translation import gettext_lazy as _


# class Order(models.Model):
#     STATUS_PENDING = "pending"
#     STATUS_PAID = "paid"
#     STATUS_SHIPPED = "shipped"
#     STATUS_COMPLETED = "completed"
#     STATUS_CANCELLED = "cancelled"

#     STATUS_CHOICES = [
#         (STATUS_PENDING, _("En attente")),
#         (STATUS_PAID, _("Payée")),
#         (STATUS_SHIPPED, _("Expédiée")),
#         (STATUS_COMPLETED, _("Terminée")),
#         (STATUS_CANCELLED, _("Annulée")),
#     ]

#     uuid = models.UUIDField(
#         default=uuid.uuid4,
#         editable=False,
#         unique=True,
#         verbose_name=_("UUID"),
#     )

#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.PROTECT,
#         related_name="orders",          # 🔑 simple et sans clash
#         verbose_name=_("Utilisateur"),
#     )

#     status = models.CharField(
#         max_length=20,
#         choices=STATUS_CHOICES,
#         default=STATUS_PENDING,
#         verbose_name=_("Statut"),
#     )

#     total_amount = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         verbose_name=_("Montant total"),
#     )

#     created_at = models.DateTimeField(
#         auto_now_add=True,
#         verbose_name=_("Créée le"),
#     )

#     class Meta:
#         verbose_name = _("Commande")
#         verbose_name_plural = _("Commandes")
#         ordering = ["-created_at"]

#     def __str__(self):
#         return f"Commande {self.uuid}"
