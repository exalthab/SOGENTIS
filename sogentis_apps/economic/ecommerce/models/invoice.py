# economic/ecommerce/models/invoice.py
from __future__ import annotations

import hashlib
import uuid
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import IntegrityError, models, transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .order import Order


D0 = Decimal("0.00")


class Invoice(models.Model):
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        verbose_name=_("UUID"),
    )

    # ✅ Numéro facture lisible (compta/support)
    invoice_number = models.CharField(
        max_length=24,
        blank=True,
        unique=True,
        db_index=True,
        verbose_name=_("Numéro de facture"),
        help_text=_("Auto-généré. Ex: INV-20260124-0001"),
    )

    # ✅ Recommandé en prod: ne pas supprimer une facture par cascade
    # (si tu veux absolument CASCADE, remets-le, mais PROTECT protège mieux ta compta)
    order = models.OneToOneField(
        Order,
        on_delete=models.PROTECT,
        related_name="invoice",
        verbose_name=_("Commande"),
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=D0,
        verbose_name=_("Montant"),
    )

    currency = models.CharField(
        max_length=10,
        default="XOF",
        db_index=True,
        verbose_name=_("Devise"),
    )

    # ✅ Statut facture (prod)
    STATUS_DRAFT = "draft"
    STATUS_ISSUED = "issued"
    STATUS_VOID = "void"

    STATUS_CHOICES = [
        (STATUS_DRAFT, _("Brouillon")),
        (STATUS_ISSUED, _("Émise")),
        (STATUS_VOID, _("Annulée")),
    ]

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT,
        db_index=True,
        verbose_name=_("Statut"),
    )

    file = models.FileField(
        upload_to="invoices/%Y/%m/",
        verbose_name=_("Fichier PDF"),
        blank=True,
        null=True,
    )

    checksum = models.CharField(
        max_length=64,
        blank=True,
        verbose_name=_("Checksum"),
        help_text=_("Optionnel: hash du PDF pour traçabilité."),
    )

    issued_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Émise le"))
    voided_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Annulée le"))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Créée le"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Mise à jour le"))

    class Meta:
        verbose_name = _("Facture")
        verbose_name_plural = _("Factures")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["invoice_number"]),
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["order"]),
        ]
        constraints = [
            models.CheckConstraint(check=models.Q(amount__gte=0), name="chk_invoice_amount_gte_0"),
        ]

    def __str__(self):
        return self.invoice_number or f"Facture {self.uuid}"

    # -------------------------
    # Utils
    # -------------------------
    @staticmethod
    def _q2(val) -> Decimal:
        try:
            return Decimal(val).quantize(Decimal("0.01"))
        except Exception:
            return D0

    @staticmethod
    def _generate_invoice_prefix() -> str:
        today = timezone.now().strftime("%Y%m%d")
        return f"INV-{today}-"

    def _compute_checksum_sha256(self) -> str:
        """
        Calcule sha256 du fichier PDF (si présent).
        """
        if not self.file:
            return ""
        try:
            h = hashlib.sha256()
            self.file.open("rb")
            for chunk in self.file.chunks(1024 * 1024):
                h.update(chunk)
            self.file.close()
            return h.hexdigest()
        except Exception:
            try:
                self.file.close()
            except Exception:
                pass
            return ""

    # -------------------------
    # Validation / normalisation
    # -------------------------
    def clean(self):
        super().clean()

        if self.currency:
            self.currency = self.currency.strip().upper()

        if self.amount is None:
            self.amount = D0
        if self.amount < 0:
            raise ValidationError({"amount": _("Le montant ne peut pas être négatif.")})

        self.amount = self._q2(self.amount)

        # snapshots depuis Order (si dispo)
        if self.order_id:
            try:
                if (self.amount == D0) and getattr(self.order, "total_amount", None) is not None:
                    self.amount = self._q2(self.order.total_amount)
            except Exception:
                pass
            try:
                if getattr(self.order, "currency", None):
                    self.currency = (self.order.currency or "XOF").strip().upper()
            except Exception:
                pass

        # cohérence status ↔ timestamps
        if self.status == self.STATUS_ISSUED:
            if self.issued_at is None:
                self.issued_at = timezone.now()
            self.voided_at = None
        elif self.status == self.STATUS_VOID:
            if self.voided_at is None:
                self.voided_at = timezone.now()
        else:
            # draft: on ne force rien
            pass

        if self.checksum:
            self.checksum = self.checksum.strip()

    # -------------------------
    # Save (anti-collision)
    # -------------------------
    def save(self, *args, **kwargs):
        # normalise vite
        if self.currency:
            self.currency = self.currency.strip().upper()
        self.amount = self._q2(self.amount if self.amount is not None else D0)

        # cohérence status timestamps (même hors admin)
        if self.status == self.STATUS_ISSUED and self.issued_at is None:
            self.issued_at = timezone.now()
            self.voided_at = None
        if self.status == self.STATUS_VOID and self.voided_at is None:
            self.voided_at = timezone.now()

        # sécurité
        self.full_clean()

        # génération robuste invoice_number (retry sur collisions)
        for _ in range(5):
            try:
                with transaction.atomic():
                    if not self.invoice_number:
                        base = self._generate_invoice_prefix()

                        last = (
                            Invoice.objects.select_for_update()
                            .filter(invoice_number__startswith=base)
                            .order_by("-invoice_number")
                            .values_list("invoice_number", flat=True)
                            .first()
                        )
                        last_n = 0
                        if last:
                            try:
                                last_n = int(last.split("-")[-1])
                            except Exception:
                                last_n = 0

                        self.invoice_number = f"{base}{(last_n + 1):04d}"

                    super().save(*args, **kwargs)
                break
            except IntegrityError:
                # collision rare (concurrence) → retry
                self.invoice_number = ""
                continue

        # checksum auto si PDF présent et checksum vide
        if self.file and not self.checksum:
            digest = self._compute_checksum_sha256()
            if digest:
                self.checksum = digest
                super().save(update_fields=["checksum", "updated_at"])

    # -------------------------
    # Helpers métier
    # -------------------------
    @property
    def is_issued(self) -> bool:
        return self.status == self.STATUS_ISSUED

    def mark_issued(self):
        self.status = self.STATUS_ISSUED
        self.issued_at = timezone.now()
        self.voided_at = None
        self.save(update_fields=["status", "issued_at", "voided_at", "updated_at"])

    def mark_void(self):
        self.status = self.STATUS_VOID
        self.voided_at = timezone.now()
        self.save(update_fields=["status", "voided_at", "updated_at"])






# # economic/ecommerce/models/invoice.py
# from __future__ import annotations

# import uuid
# from decimal import Decimal

# from django.db import models, transaction
# from django.utils import timezone
# from django.utils.translation import gettext_lazy as _

# from .order import Order


# class Invoice(models.Model):
#     uuid = models.UUIDField(
#         default=uuid.uuid4,
#         editable=False,
#         unique=True,
#         verbose_name=_("UUID"),
#     )

#     # ✅ Numéro facture lisible (compta/support)
#     invoice_number = models.CharField(
#         max_length=24,
#         blank=True,
#         unique=True,
#         db_index=True,
#         verbose_name=_("Numéro de facture"),
#         help_text=_("Auto-généré. Ex: INV-20260124-0001"),
#     )

#     order = models.OneToOneField(
#         Order,
#         on_delete=models.CASCADE,
#         related_name="invoice",
#         verbose_name=_("Commande"),
#     )

#     # ✅ Snapshots utiles
#     amount = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         default=Decimal("0.00"),
#         verbose_name=_("Montant"),
#     )

#     currency = models.CharField(
#         max_length=10,
#         default="XOF",
#         db_index=True,
#         verbose_name=_("Devise"),
#     )

#     # ✅ Statut facture (prod)
#     STATUS_DRAFT = "draft"
#     STATUS_ISSUED = "issued"
#     STATUS_VOID = "void"

#     STATUS_CHOICES = [
#         (STATUS_DRAFT, _("Brouillon")),
#         (STATUS_ISSUED, _("Émise")),
#         (STATUS_VOID, _("Annulée")),
#     ]

#     status = models.CharField(
#         max_length=10,
#         choices=STATUS_CHOICES,
#         default=STATUS_DRAFT,
#         db_index=True,
#         verbose_name=_("Statut"),
#     )

#     file = models.FileField(
#         upload_to="invoices/%Y/%m/",
#         verbose_name=_("Fichier PDF"),
#         blank=True,
#         null=True,
#     )

#     # ✅ Optionnel: empreinte simple si tu veux détecter un remplacement de fichier
#     checksum = models.CharField(
#         max_length=64,
#         blank=True,
#         verbose_name=_("Checksum"),
#         help_text=_("Optionnel: hash du PDF pour traçabilité."),
#     )

#     issued_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Émise le"))
#     voided_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Annulée le"))

#     created_at = models.DateTimeField(
#         auto_now_add=True,
#         verbose_name=_("Créée le"),
#     )

#     updated_at = models.DateTimeField(
#         auto_now=True,
#         verbose_name=_("Mise à jour le"),
#     )

#     class Meta:
#         verbose_name = _("Facture")
#         verbose_name_plural = _("Factures")
#         ordering = ["-created_at"]
#         indexes = [
#             models.Index(fields=["invoice_number"]),
#             models.Index(fields=["status", "created_at"]),
#             models.Index(fields=["order"]),
#         ]

#     def __str__(self):
#         return self.invoice_number or f"Facture {self.uuid}"

#     @staticmethod
#     def _generate_invoice_number() -> str:
#         today = timezone.now().strftime("%Y%m%d")
#         return f"INV-{today}-"

#     def save(self, *args, **kwargs):
#         # snapshots
#         if self.order_id:
#             if not self.amount or self.amount == Decimal("0.00"):
#                 try:
#                     self.amount = self.order.total_amount
#                 except Exception:
#                     pass
#             if self.order.currency:
#                 self.currency = (self.order.currency or "XOF").strip().upper()

#         if self.currency:
#             self.currency = self.currency.strip().upper()

#         with transaction.atomic():
#             if not self.invoice_number:
#                 base = self._generate_invoice_number()
#                 last = (
#                     Invoice.objects.select_for_update()
#                     .filter(invoice_number__startswith=base)
#                     .order_by("-invoice_number")
#                     .values_list("invoice_number", flat=True)
#                     .first()
#                 )
#                 last_n = 0
#                 if last:
#                     try:
#                         last_n = int(last.split("-")[-1])
#                     except Exception:
#                         last_n = 0
#                 self.invoice_number = f"{base}{(last_n + 1):04d}"

#             super().save(*args, **kwargs)

#     # Helpers métier
#     @property
#     def is_issued(self) -> bool:
#         return self.status == self.STATUS_ISSUED

#     def mark_issued(self):
#         self.status = self.STATUS_ISSUED
#         self.issued_at = timezone.now()
#         self.voided_at = None
#         self.save(update_fields=["status", "issued_at", "voided_at", "updated_at"])

#     def mark_void(self):
#         self.status = self.STATUS_VOID
#         self.voided_at = timezone.now()
#         self.save(update_fields=["status", "voided_at", "updated_at"])






# # economic/ecommerce/models/invoice.py
# import uuid
# from django.db import models
# from django.utils.translation import gettext_lazy as _

# from .order import Order


# class Invoice(models.Model):
#     uuid = models.UUIDField(
#         default=uuid.uuid4,
#         editable=False,
#         unique=True,
#         verbose_name=_("UUID"),
#     )

#     order = models.OneToOneField(
#         Order,
#         on_delete=models.CASCADE,
#         related_name="invoice",
#         verbose_name=_("Commande"),
#     )

#     file = models.FileField(
#         upload_to="invoices/%Y/%m/",
#         verbose_name=_("Fichier PDF"),
#     )

#     created_at = models.DateTimeField(
#         auto_now_add=True,
#         verbose_name=_("Créée le"),
#     )

#     class Meta:
#         verbose_name = _("Facture")
#         verbose_name_plural = _("Factures")

#     def __str__(self):
#         return f"Facture {self.uuid}"
