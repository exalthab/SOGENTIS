# economic/prestations/models/prestations_quote.py
from __future__ import annotations

import uuid
from decimal import Decimal, ROUND_HALF_UP

from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from django_ckeditor_5.fields import CKEditor5Field

from .prestations import Prestation
from .prestations_package import PrestationPackage


DEC_0 = Decimal("0.00")
DEC_100 = Decimal("100.00")


def _q2(value: Decimal) -> Decimal:
    """Quantize à 2 décimales (arrondi bancaire simple)."""
    return (value or DEC_0).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class Quote(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", _("Brouillon")
        SENT = "sent", _("Envoyé")
        ACCEPTED = "accepted", _("Accepté")
        REJECTED = "rejected", _("Refusé")
        EXPIRED = "expired", _("Expiré")
        CANCELLED = "cancelled", _("Annulé")

    class Source(models.TextChoices):
        WEB = "web", _("Web")
        ADMIN = "admin", _("Admin")
        EMAIL = "email", _("Email")
        PHONE = "phone", _("Téléphone")
        OTHER = "other", _("Autre")

    class Currency(models.TextChoices):
        EUR = "EUR", "EUR"
        XOF = "XOF", "XOF"

    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    quote_number = models.CharField(
        max_length=32,
        unique=True,
        blank=True,
        null=True,
        verbose_name=_("Numéro de devis"),
        help_text=_("Auto-généré si vide."),
    )

    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT, db_index=True)
    source = models.CharField(max_length=16, choices=Source.choices, default=Source.ADMIN, db_index=True)
    is_active = models.BooleanField(default=True, verbose_name=_("Actif"))

    client_name = models.CharField(max_length=160, blank=True, verbose_name=_("Nom client"))
    client_email = models.EmailField(blank=True, verbose_name=_("Email client"))
    client_phone = models.CharField(max_length=60, blank=True, verbose_name=_("Téléphone client"))
    company_name = models.CharField(max_length=160, blank=True, verbose_name=_("Entreprise"))

    country = models.CharField(max_length=80, blank=True, verbose_name=_("Pays"))
    city = models.CharField(max_length=120, blank=True, verbose_name=_("Ville"))
    address = models.CharField(max_length=255, blank=True, verbose_name=_("Adresse"))

    subject = models.CharField(max_length=200, blank=True, verbose_name=_("Objet"))
    message = CKEditor5Field(blank=True, verbose_name=_("Message / Besoin client"))
    terms = CKEditor5Field(blank=True, verbose_name=_("Conditions / Modalités"))
    internal_notes = CKEditor5Field(blank=True, verbose_name=_("Notes internes"))

    currency = models.CharField(max_length=3, choices=Currency.choices, default=Currency.EUR, verbose_name=_("Devise"))
    tax_rate = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=DEC_0,
        verbose_name=_("TVA (%)"),
        help_text=_("Ex: 18.00 pour 18%."),
    )

    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=DEC_0, verbose_name=_("Sous-total"))
    discount_total = models.DecimalField(max_digits=12, decimal_places=2, default=DEC_0, verbose_name=_("Remises"))
    tax_total = models.DecimalField(max_digits=12, decimal_places=2, default=DEC_0, verbose_name=_("TVA"))
    total = models.DecimalField(max_digits=12, decimal_places=2, default=DEC_0, verbose_name=_("Total"))

    issued_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Émis le"))
    valid_until = models.DateField(null=True, blank=True, verbose_name=_("Valide jusqu’au"))

    created_at = models.DateTimeField(default=timezone.now, editable=False, verbose_name=_("Créé le"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Mis à jour le"))

    class Meta:
        verbose_name = _("Devis")
        verbose_name_plural = _("Devis")
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(fields=["status", "is_active", "created_at"]),
            models.Index(fields=["currency", "created_at"]),
        ]

    def __str__(self) -> str:
        return self.quote_number or f"Quote #{self.pk or 'new'}"

    def _ensure_quote_number(self):
        if self.quote_number:
            return
        d = timezone.localdate()
        suffix = str(self.public_id).split("-")[0].upper()
        self.quote_number = f"Q-{d:%Y%m%d}-{suffix}"

    def recalculate(self, save: bool = True):
        subtotal = DEC_0
        discount_total = DEC_0

        for line in self.lines.all():
            subtotal += line.line_subtotal
            discount_total += line.line_discount

        subtotal = _q2(subtotal)
        discount_total = _q2(discount_total)

        taxable = subtotal - discount_total
        if taxable < DEC_0:
            taxable = DEC_0

        tax_rate = _q2(self.tax_rate)
        tax_total = _q2((taxable * tax_rate) / DEC_100) if tax_rate > DEC_0 else DEC_0
        total = _q2(taxable + tax_total)

        self.subtotal = subtotal
        self.discount_total = discount_total
        self.tax_total = tax_total
        self.total = total

        if save and self.pk:
            Quote.objects.filter(pk=self.pk).update(
                subtotal=self.subtotal,
                discount_total=self.discount_total,
                tax_total=self.tax_total,
                total=self.total,
                updated_at=timezone.now(),
            )

    def mark_sent(self):
        self.status = self.Status.SENT
        if not self.issued_at:
            self.issued_at = timezone.now()
        self.save(update_fields=["status", "issued_at", "updated_at"])

    def mark_accepted(self):
        self.status = self.Status.ACCEPTED
        self.save(update_fields=["status", "updated_at"])

    def mark_rejected(self):
        self.status = self.Status.REJECTED
        self.save(update_fields=["status", "updated_at"])

    def mark_cancelled(self):
        self.status = self.Status.CANCELLED
        self.save(update_fields=["status", "updated_at"])

    def is_expired(self) -> bool:
        if not self.valid_until:
            return False
        return timezone.localdate() > self.valid_until

    def clean(self):
        if self.tax_rate is not None and (self.tax_rate < DEC_0 or self.tax_rate > DEC_100):
            raise ValidationError({"tax_rate": _("La TVA doit être comprise entre 0 et 100.")})

    def save(self, *args, **kwargs):
        if not self.public_id:
            self.public_id = uuid.uuid4()
        self._ensure_quote_number()
        super().save(*args, **kwargs)


class QuoteLine(models.Model):
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE, related_name="lines", verbose_name=_("Devis"))

    prestation = models.ForeignKey(
        Prestation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="quote_lines",
        verbose_name=_("Prestation"),
    )
    package = models.ForeignKey(
        PrestationPackage,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="quote_lines",
        verbose_name=_("Pack"),
    )

    title_override = models.CharField(max_length=200, blank=True, verbose_name=_("Titre (override)"))
    description_override = CKEditor5Field(blank=True, verbose_name=_("Description (override)"))

    quantity = models.PositiveIntegerField(default=1, verbose_name=_("Quantité"))
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=DEC_0, verbose_name=_("Prix unitaire"))

    discount_rate = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=DEC_0,
        verbose_name=_("Remise (%)"),
        help_text=_("Ex: 10.00 pour 10%."),
    )

    order = models.PositiveIntegerField(default=100, verbose_name=_("Ordre"))
    created_at = models.DateTimeField(default=timezone.now, editable=False, verbose_name=_("Créé le"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Mis à jour le"))

    class Meta:
        verbose_name = _("Ligne de devis")
        verbose_name_plural = _("Lignes de devis")
        ordering = ["order", "id"]
        indexes = [models.Index(fields=["quote", "order"])]
        constraints = [
            models.CheckConstraint(
                condition=(
                    (models.Q(prestation__isnull=False) & models.Q(package__isnull=True))
                    | (models.Q(prestation__isnull=True) & models.Q(package__isnull=False))
                    | (models.Q(prestation__isnull=True) & models.Q(package__isnull=True))
                ),
                name="quote_line_one_ref_or_none",
            ),
        ]

    def __str__(self) -> str:
        return self.display_title or f"Line #{self.pk}"

    @property
    def display_title(self) -> str:
        if self.title_override:
            return self.title_override
        if self.prestation_id:
            return self.prestation.safe_translation_getter("title", any_language=True) or _("Prestation")
        if self.package_id:
            return self.package.safe_translation_getter("name", any_language=True) or _("Pack")
        return _("Ligne")

    def clean(self):
        if self.discount_rate is not None and (self.discount_rate < DEC_0 or self.discount_rate > DEC_100):
            raise ValidationError({"discount_rate": _("La remise doit être comprise entre 0 et 100.")})

        if self.prestation_id and self.package_id:
            raise ValidationError(_("Une ligne ne peut référencer qu’une Prestation OU un Pack (pas les deux)."))

        if self.quantity <= 0:
            raise ValidationError({"quantity": _("La quantité doit être supérieure à 0.")})

    @property
    def line_subtotal(self) -> Decimal:
        return _q2(Decimal(self.quantity) * (self.unit_price or DEC_0))

    @property
    def line_discount(self) -> Decimal:
        rate = _q2(self.discount_rate or DEC_0)
        if rate <= DEC_0:
            return DEC_0
        return _q2((self.line_subtotal * rate) / DEC_100)

    @property
    def line_total(self) -> Decimal:
        v = self.line_subtotal - self.line_discount
        return _q2(v if v > DEC_0 else DEC_0)

    def save(self, *args, **kwargs):
        if (self.unit_price is None or self.unit_price == DEC_0) and (self.prestation_id or self.package_id):
            if self.prestation_id:
                self.unit_price = self.prestation.base_price or DEC_0
            elif self.package_id:
                self.unit_price = self.package.total_price or DEC_0

        super().save(*args, **kwargs)

        if self.quote_id:
            def _recalc():
                try:
                    q = Quote.objects.get(pk=self.quote_id)
                    q.recalculate(save=True)
                except Quote.DoesNotExist:
                    return

            transaction.on_commit(_recalc)






# # economic/prestations/models/prestations_quote.py
# from __future__ import annotations

# import uuid
# from decimal import Decimal, ROUND_HALF_UP
# from typing import Optional

# from django.core.exceptions import ValidationError
# from django.db import models, transaction
# from django.utils import timezone
# from django.utils.translation import gettext_lazy as _

# from django_ckeditor_5.fields import CKEditor5Field

# from .prestations import Service
# from .prestations_package import ServicePackage


# DEC_0 = Decimal("0.00")
# DEC_100 = Decimal("100.00")


# def _q2(value: Decimal) -> Decimal:
#     """Quantize à 2 décimales (arrondi bancaire simple)."""
#     return (value or DEC_0).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


# class Quote(models.Model):
#     """
#     Devis (Quote) — pilotable depuis l’admin, et exploitable en public via public_id.

#     ✅ Ajoute ce qui manquait :
#     - Statuts (draft/sent/accepted/rejected/expired/cancelled)
#     - Totaux calculés (subtotal/discount/tax/total)
#     - TVA configurable (tax_rate)
#     - valid_until
#     - notes/terms en CKEditor5
#     - Lignes (QuoteLine) liées à Service ou ServicePackage
#     """

#     class Status(models.TextChoices):
#         DRAFT = "draft", _("Brouillon")
#         SENT = "sent", _("Envoyé")
#         ACCEPTED = "accepted", _("Accepté")
#         REJECTED = "rejected", _("Refusé")
#         EXPIRED = "expired", _("Expiré")
#         CANCELLED = "cancelled", _("Annulé")

#     class Source(models.TextChoices):
#         WEB = "web", _("Web")
#         ADMIN = "admin", _("Admin")
#         EMAIL = "email", _("Email")
#         PHONE = "phone", _("Téléphone")
#         OTHER = "other", _("Autre")

#     class Currency(models.TextChoices):
#         EUR = "EUR", "EUR"
#         XOF = "XOF", "XOF"

#     # Identifiants
#     public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
#     quote_number = models.CharField(
#         max_length=32,
#         unique=True,
#         blank=True,
#         null=True,
#         verbose_name=_("Numéro de devis"),
#         help_text=_("Auto-généré si vide."),
#     )

#     # Meta
#     status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT, db_index=True)
#     source = models.CharField(max_length=16, choices=Source.choices, default=Source.ADMIN, db_index=True)
#     is_active = models.BooleanField(default=True, verbose_name=_("Actif"))

#     # Client (minimal mais pro)
#     client_name = models.CharField(max_length=160, blank=True, verbose_name=_("Nom client"))
#     client_email = models.EmailField(blank=True, verbose_name=_("Email client"))
#     client_phone = models.CharField(max_length=60, blank=True, verbose_name=_("Téléphone client"))
#     company_name = models.CharField(max_length=160, blank=True, verbose_name=_("Entreprise"))

#     country = models.CharField(max_length=80, blank=True, verbose_name=_("Pays"))
#     city = models.CharField(max_length=120, blank=True, verbose_name=_("Ville"))
#     address = models.CharField(max_length=255, blank=True, verbose_name=_("Adresse"))

#     # Contenu éditorial
#     subject = models.CharField(max_length=200, blank=True, verbose_name=_("Objet"))
#     message = CKEditor5Field(blank=True, verbose_name=_("Message / Besoin client"))
#     terms = CKEditor5Field(blank=True, verbose_name=_("Conditions / Modalités"))
#     internal_notes = CKEditor5Field(blank=True, verbose_name=_("Notes internes"))

#     # Pricing
#     currency = models.CharField(max_length=3, choices=Currency.choices, default=Currency.EUR, verbose_name=_("Devise"))
#     tax_rate = models.DecimalField(
#         max_digits=6,
#         decimal_places=2,
#         default=DEC_0,
#         verbose_name=_("TVA (%)"),
#         help_text=_("Ex: 18.00 pour 18%."),
#     )

#     subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=DEC_0, verbose_name=_("Sous-total"))
#     discount_total = models.DecimalField(max_digits=12, decimal_places=2, default=DEC_0, verbose_name=_("Remises"))
#     tax_total = models.DecimalField(max_digits=12, decimal_places=2, default=DEC_0, verbose_name=_("TVA"))
#     total = models.DecimalField(max_digits=12, decimal_places=2, default=DEC_0, verbose_name=_("Total"))

#     # Dates
#     issued_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Émis le"))
#     valid_until = models.DateField(null=True, blank=True, verbose_name=_("Valide jusqu’au"))

#     created_at = models.DateTimeField(default=timezone.now, editable=False, verbose_name=_("Créé le"))
#     updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Mis à jour le"))

#     class Meta:
#         verbose_name = _("Devis")
#         verbose_name_plural = _("Devis")
#         ordering = ["-created_at", "-id"]
#         indexes = [
#             models.Index(fields=["status", "is_active", "created_at"]),
#             models.Index(fields=["currency", "created_at"]),
#         ]

#     def __str__(self) -> str:
#         return self.quote_number or f"Quote #{self.pk or 'new'}"

#     # --------------------------
#     # Numérotation (safe, sans lock)
#     # --------------------------
#     def _ensure_quote_number(self):
#         if self.quote_number:
#             return
#         # Format stable, sans collision pratique : Q-YYYYMMDD-XXXXXX
#         # (basé sur public_id)
#         d = timezone.localdate()
#         suffix = str(self.public_id).split("-")[0].upper()
#         self.quote_number = f"Q-{d:%Y%m%d}-{suffix}"

#     # --------------------------
#     # Calculs
#     # --------------------------
#     def recalculate(self, save: bool = True):
#         """
#         Recalcule les montants depuis les lignes.
#         - subtotal : somme (qty * unit_price)
#         - discount_total : somme remises lignes
#         - tax_total : TVA sur (subtotal - discount_total)
#         - total : net + tax
#         """
#         subtotal = DEC_0
#         discount_total = DEC_0

#         # On itère sur les lignes existantes
#         for line in self.lines.all():
#             subtotal += line.line_subtotal
#             discount_total += line.line_discount

#         subtotal = _q2(subtotal)
#         discount_total = _q2(discount_total)

#         taxable = subtotal - discount_total
#         if taxable < DEC_0:
#             taxable = DEC_0

#         tax_rate = _q2(self.tax_rate)
#         tax_total = _q2((taxable * tax_rate) / DEC_100) if tax_rate > DEC_0 else DEC_0
#         total = _q2(taxable + tax_total)

#         self.subtotal = subtotal
#         self.discount_total = discount_total
#         self.tax_total = tax_total
#         self.total = total

#         if save:
#             Quote.objects.filter(pk=self.pk).update(
#                 subtotal=self.subtotal,
#                 discount_total=self.discount_total,
#                 tax_total=self.tax_total,
#                 total=self.total,
#                 updated_at=timezone.now(),
#             )

#     def mark_sent(self):
#         self.status = self.Status.SENT
#         if not self.issued_at:
#             self.issued_at = timezone.now()
#         self.save(update_fields=["status", "issued_at", "updated_at"])

#     def mark_accepted(self):
#         self.status = self.Status.ACCEPTED
#         self.save(update_fields=["status", "updated_at"])

#     def mark_rejected(self):
#         self.status = self.Status.REJECTED
#         self.save(update_fields=["status", "updated_at"])

#     def mark_cancelled(self):
#         self.status = self.Status.CANCELLED
#         self.save(update_fields=["status", "updated_at"])

#     def is_expired(self) -> bool:
#         if not self.valid_until:
#             return False
#         return timezone.localdate() > self.valid_until

#     def clean(self):
#         # TVA raisonnable 0..100
#         if self.tax_rate is not None and (self.tax_rate < DEC_0 or self.tax_rate > DEC_100):
#             raise ValidationError({"tax_rate": _("La TVA doit être comprise entre 0 et 100.")})

#     def save(self, *args, **kwargs):
#         if not self.public_id:
#             self.public_id = uuid.uuid4()

#         self._ensure_quote_number()

#         # issued_at auto si on passe de draft -> sent ailleurs : ici on ne force pas
#         super().save(*args, **kwargs)


# class QuoteLine(models.Model):
#     """
#     Ligne de devis :
#     - référence soit un Service, soit un ServicePackage (exactement un des deux)
#     - unit_price + qty + discount_rate
#     - calc line_subtotal/line_discount/line_total
#     """

#     quote = models.ForeignKey(Quote, on_delete=models.CASCADE, related_name="lines", verbose_name=_("Devis"))

#     service = models.ForeignKey(
#         Service,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name="quote_lines",
#         verbose_name=_("Service"),
#     )
#     package = models.ForeignKey(
#         ServicePackage,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name="quote_lines",
#         verbose_name=_("Pack"),
#     )

#     title_override = models.CharField(max_length=200, blank=True, verbose_name=_("Titre (override)"))
#     description_override = CKEditor5Field(blank=True, verbose_name=_("Description (override)"))

#     quantity = models.PositiveIntegerField(default=1, verbose_name=_("Quantité"))
#     unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=DEC_0, verbose_name=_("Prix unitaire"))

#     discount_rate = models.DecimalField(
#         max_digits=6,
#         decimal_places=2,
#         default=DEC_0,
#         verbose_name=_("Remise (%)"),
#         help_text=_("Ex: 10.00 pour 10%."),
#     )

#     order = models.PositiveIntegerField(default=100, verbose_name=_("Ordre"))
#     created_at = models.DateTimeField(default=timezone.now, editable=False, verbose_name=_("Créé le"))
#     updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Mis à jour le"))

#     class Meta:
#         verbose_name = _("Ligne de devis")
#         verbose_name_plural = _("Lignes de devis")
#         ordering = ["order", "id"]
#         indexes = [
#             models.Index(fields=["quote", "order"]),
#         ]
#         constraints = [
#             # Empêche les doublons "service+pack" non souhaités : validation logique fait le reste
#             models.CheckConstraint(
#                 check=(
#                     (models.Q(service__isnull=False) & models.Q(package__isnull=True))
#                     | (models.Q(service__isnull=True) & models.Q(package__isnull=False))
#                     | (models.Q(service__isnull=True) & models.Q(package__isnull=True))  # autorise override seul
#                 ),
#                 name="quote_line_one_ref_or_none",
#             ),
#         ]

#     def __str__(self) -> str:
#         return self.display_title or f"Line #{self.pk}"

#     @property
#     def display_title(self) -> str:
#         if self.title_override:
#             return self.title_override
#         if self.service_id:
#             return self.service.safe_translation_getter("title", any_language=True) or _("Service")
#         if self.package_id:
#             return self.package.safe_translation_getter("name", any_language=True) or _("Pack")
#         return _("Ligne")

#     def clean(self):
#         # Remise raisonnable 0..100
#         if self.discount_rate is not None and (self.discount_rate < DEC_0 or self.discount_rate > DEC_100):
#             raise ValidationError({"discount_rate": _("La remise doit être comprise entre 0 et 100.")})

#         # Autorisé :
#         # - service seul
#         # - package seul
#         # - aucun des deux (ligne custom via override)
#         # Interdit : les deux à la fois
#         if self.service_id and self.package_id:
#             raise ValidationError(_("Une ligne ne peut référencer qu’un Service OU un Pack (pas les deux)."))

#         if self.quantity <= 0:
#             raise ValidationError({"quantity": _("La quantité doit être supérieure à 0.")})

#     @property
#     def line_subtotal(self) -> Decimal:
#         return _q2(Decimal(self.quantity) * (self.unit_price or DEC_0))

#     @property
#     def line_discount(self) -> Decimal:
#         rate = _q2(self.discount_rate or DEC_0)
#         if rate <= DEC_0:
#             return DEC_0
#         return _q2((self.line_subtotal * rate) / DEC_100)

#     @property
#     def line_total(self) -> Decimal:
#         v = self.line_subtotal - self.line_discount
#         return _q2(v if v > DEC_0 else DEC_0)

#     def save(self, *args, **kwargs):
#         # Auto-price simple si non renseigné :
#         # - si service: base_price
#         # - si package: total_price
#         if (self.unit_price is None or self.unit_price == DEC_0) and (self.service_id or self.package_id):
#             if self.service_id:
#                 self.unit_price = self.service.base_price or DEC_0
#             elif self.package_id:
#                 self.unit_price = self.package.total_price or DEC_0

#         super().save(*args, **kwargs)

#         # Recalcule le devis après save (safe)
#         if self.quote_id:
#             def _recalc():
#                 try:
#                     q = Quote.objects.get(pk=self.quote_id)
#                     q.recalculate(save=True)
#                 except Quote.DoesNotExist:
#                     return

#             transaction.on_commit(_recalc)
