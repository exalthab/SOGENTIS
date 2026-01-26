# /economic/ecommerce/models/payment_transaction.py
from __future__ import annotations

import uuid
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import connection, models, transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .order import Order


D0 = Decimal("0.00")
Q = models.Q


class PaymentTransaction(models.Model):
    # ==========================
    # PROVIDERS
    # ==========================
    PROVIDER_STRIPE = "stripe"
    PROVIDER_PAYPAL = "paypal"
    PROVIDER_WAVE = "wave"
    PROVIDER_ORANGE = "orange_money"

    PROVIDERS = [
        (PROVIDER_STRIPE, "Stripe"),
        (PROVIDER_PAYPAL, "PayPal"),
        (PROVIDER_WAVE, "Wave"),
        (PROVIDER_ORANGE, "Orange Money"),
    ]

    # ==========================
    # STATUTS
    # ==========================
    STATUS_INITIATED = "initiated"
    STATUS_PENDING = "pending"
    STATUS_SUCCEEDED = "succeeded"
    STATUS_FAILED = "failed"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_INITIATED, _("Initiée")),
        (STATUS_PENDING, _("En attente")),
        (STATUS_SUCCEEDED, _("Réussie")),
        (STATUS_FAILED, _("Échouée")),
        (STATUS_CANCELLED, _("Annulée")),
    ]

    # ==========================
    # IDENTIFIANTS
    # ==========================
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        verbose_name=_("UUID"),
    )

    # ✅ Idempotence (retries / webhooks doublés)
    idempotency_key = models.CharField(
        max_length=80,
        blank=True,
        db_index=True,
        verbose_name=_("Clé d'idempotence"),
        help_text=_("Optionnel: empêche la création de doublons en cas de retry."),
    )

    # ==========================
    # COMMANDE
    # ==========================
    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,
        related_name="payments",
        verbose_name=_("Commande"),
    )

    # ==========================
    # PAIEMENT
    # ==========================
    provider = models.CharField(
        max_length=20,
        choices=PROVIDERS,
        verbose_name=_("Prestataire"),
        db_index=True,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_INITIATED,
        verbose_name=_("Statut"),
        db_index=True,
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_("Montant"),
    )

    currency = models.CharField(
        max_length=10,
        default="XOF",
        verbose_name=_("Devise"),
        db_index=True,
    )

    provider_fee = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=D0,
        verbose_name=_("Frais prestataire"),
    )

    # ==========================
    # PROVIDER IDS / WEBHOOKS
    # ==========================
    provider_payment_id = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name=_("ID paiement prestataire"),
    )

    # ⚠️ unique + NULL ok en Postgres (les NULL ne clashent pas)
    provider_event_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        unique=True,
        verbose_name=_("ID événement prestataire"),
        help_text=_("ID unique d’événement webhook (utile pour éviter les doublons)."),
    )

    payment_url = models.URLField(
        blank=True,
        verbose_name=_("URL de paiement"),
    )

    payload = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Payload prestataire"),
    )

    # ==========================
    # OBSERVABILITÉ / RETRIES
    # ==========================
    attempt_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Nombre de tentatives"),
        help_text=_("Incrémenté à chaque retry / relance."),
    )

    last_webhook_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Dernier webhook reçu le"),
    )

    failure_code = models.CharField(
        max_length=80,
        blank=True,
        verbose_name=_("Code d'échec"),
    )

    failure_message = models.TextField(
        blank=True,
        verbose_name=_("Message d'échec"),
    )

    # ✅ Timestamps métier
    succeeded_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Réussie le"))
    failed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Échouée le"))
    cancelled_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Annulée le"))

    # ==========================
    # TIMESTAMPS
    # ==========================
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Créée le"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Modifiée le"))

    class Meta:
        verbose_name = _("Transaction de paiement")
        verbose_name_plural = _("Transactions de paiement")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["provider", "status"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["order", "created_at"]),
            models.Index(fields=["provider_payment_id"]),
            models.Index(fields=["idempotency_key"]),
        ]
        constraints = [
            models.CheckConstraint(condition=Q(amount__gte=0), name="chk_payment_amount_gte_0"),
            models.CheckConstraint(condition=Q(provider_fee__gte=0), name="chk_payment_fee_gte_0"),
            # ✅ Unique partiel (Postgres) : seulement si key non vide
            models.UniqueConstraint(
                fields=["provider", "idempotency_key"],
                condition=~Q(idempotency_key=""),
                name="uniq_payment_provider_idempotency_nonempty",
            ),
        ]

    def __str__(self):
        return (
            f"{self.get_provider_display()} · "
            f"{self.get_status_display()} · "
            f"{self.amount} {self.currency}"
        )

    # ==========================
    # NORMALISATION / VALIDATION
    # ==========================
    @staticmethod
    def _to_dec(val) -> Decimal:
        try:
            return Decimal(val)
        except Exception:
            return D0

    @staticmethod
    def _q2(val: Decimal) -> Decimal:
        try:
            return Decimal(val).quantize(Decimal("0.01"))
        except Exception:
            return D0

    @staticmethod
    def _norm_str(s: str | None) -> str:
        return " ".join((s or "").strip().split())

    @staticmethod
    def _norm_upper(s: str | None) -> str:
        return (s or "").strip().upper()

    def clean(self):
        super().clean()

        # currency align + normalize
        if self.order_id and not self.currency:
            self.currency = getattr(self.order, "currency", "XOF") or "XOF"
        self.currency = self._norm_upper(self.currency) or "XOF"

        # provider ids normalize
        self.idempotency_key = self._norm_str(self.idempotency_key)
        self.provider_payment_id = self._norm_str(self.provider_payment_id)
        self.payment_url = (self.payment_url or "").strip()

        # important: provider_event_id unique => éviter "" en base
        pev = self._norm_str(self.provider_event_id)
        self.provider_event_id = pev or None

        # payload must be dict
        if self.payload is None:
            self.payload = {}
        if not isinstance(self.payload, dict):
            raise ValidationError({"payload": _("Le payload doit être un objet JSON (dict).")})

        # money
        if self.amount is None:
            raise ValidationError({"amount": _("Le montant est obligatoire.")})
        if self.amount is not None and self.amount < 0:
            raise ValidationError({"amount": _("Le montant ne peut pas être négatif.")})

        if self.provider_fee is None:
            self.provider_fee = D0
        if self.provider_fee is not None and self.provider_fee < 0:
            raise ValidationError({"provider_fee": _("Les frais ne peuvent pas être négatifs.")})

        self.amount = self._q2(self._to_dec(self.amount))
        self.provider_fee = self._q2(max(D0, self._to_dec(self.provider_fee)))

        # idempotency fallback (si DB ne supporte pas le partial unique)
        # (Postgres OK -> on évite un SELECT inutile en prod)
        if self.idempotency_key and connection.vendor != "postgresql":
            qs = type(self).objects.filter(provider=self.provider, idempotency_key=self.idempotency_key)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError({"idempotency_key": _("Clé d'idempotence déjà utilisée pour ce prestataire.")})

        # status <-> timestamps consistency
        if self.status == self.STATUS_SUCCEEDED:
            if self.succeeded_at is None:
                self.succeeded_at = timezone.now()
            self.failed_at = None
            self.cancelled_at = None
            self.failure_code = ""
            self.failure_message = ""
        elif self.status == self.STATUS_FAILED:
            if self.failed_at is None:
                self.failed_at = timezone.now()
            self.succeeded_at = None
        elif self.status == self.STATUS_CANCELLED:
            if self.cancelled_at is None:
                self.cancelled_at = timezone.now()
            self.succeeded_at = None
        else:
            # initiated/pending => pas de timestamps finaux
            self.succeeded_at = None
            self.failed_at = None
            self.cancelled_at = None

    def save(self, *args, **kwargs):
        # micro-normalisation
        if self.order_id and not self.currency:
            self.currency = getattr(self.order, "currency", "XOF") or "XOF"
        self.currency = self._norm_upper(self.currency) or "XOF"
        self.idempotency_key = self._norm_str(self.idempotency_key)
        self.provider_payment_id = self._norm_str(self.provider_payment_id)
        pev = self._norm_str(self.provider_event_id)
        self.provider_event_id = pev or None

        self.amount = self._q2(self._to_dec(self.amount))
        self.provider_fee = self._q2(max(D0, self._to_dec(self.provider_fee)))

        self.full_clean()
        super().save(*args, **kwargs)

    # ==========================
    # HELPERS
    # ==========================
    @property
    def is_success(self) -> bool:
        return self.status == self.STATUS_SUCCEEDED

    @property
    def is_pending(self) -> bool:
        return self.status in {self.STATUS_INITIATED, self.STATUS_PENDING}

    @property
    def is_final(self) -> bool:
        return self.status in {self.STATUS_SUCCEEDED, self.STATUS_FAILED, self.STATUS_CANCELLED}

    @property
    def net_amount(self) -> Decimal:
        net = self._to_dec(self.amount) - self._to_dec(self.provider_fee or 0)
        if net < 0:
            net = D0
        return self._q2(net)

    # ==========================
    # WEBHOOK / RETRIES
    # ==========================
    def mark_webhook_received(self, save: bool = True):
        self.last_webhook_at = timezone.now()
        if save and self.pk:
            type(self).objects.filter(pk=self.pk).update(
                last_webhook_at=self.last_webhook_at,
                updated_at=timezone.now(),
            )

    def bump_attempt(self, save: bool = True):
        if self.pk and save:
            type(self).objects.filter(pk=self.pk).update(
                attempt_count=models.F("attempt_count") + 1,
                updated_at=timezone.now(),
            )
            self.refresh_from_db(fields=["attempt_count", "updated_at"])
        else:
            self.attempt_count = int(self.attempt_count or 0) + 1

    # ==========================
    # TRANSITIONS STATUT (prod safe)
    # ==========================
    def mark_pending(self):
        if self.status not in {self.STATUS_INITIATED, self.STATUS_PENDING}:
            # on ne rétrograde pas une transaction finale
            return
        self.status = self.STATUS_PENDING
        self.save(update_fields=["status", "updated_at"])

    def mark_succeeded(self, provider_payment_id: str | None = None):
        """
        ✅ Atomic + idempotent + sync Order -> paid
        """
        if not self.pk:
            self.save()

        with transaction.atomic():
            tx = type(self).objects.select_for_update().select_related("order").get(pk=self.pk)

            if tx.status != self.STATUS_SUCCEEDED:
                tx.status = self.STATUS_SUCCEEDED
                tx.succeeded_at = timezone.now()
                tx.failed_at = None
                tx.cancelled_at = None
                tx.failure_code = ""
                tx.failure_message = ""

            if provider_payment_id and not tx.provider_payment_id:
                tx.provider_payment_id = provider_payment_id

            tx.full_clean()
            tx.save(update_fields=[
                "status", "succeeded_at", "failed_at", "cancelled_at",
                "failure_code", "failure_message", "provider_payment_id", "updated_at"
            ])

            # sync order
            try:
                order = tx.order
                if hasattr(order, "mark_paid") and not getattr(order, "is_paid", False):
                    order.mark_paid()
            except Exception:
                pass

        self.refresh_from_db()

    def mark_failed(self, code: str = "", message: str = ""):
        if not self.pk:
            self.save()

        with transaction.atomic():
            tx = type(self).objects.select_for_update().get(pk=self.pk)

            # ne pas écraser un succès
            if tx.status == self.STATUS_SUCCEEDED:
                return

            tx.status = self.STATUS_FAILED
            tx.failed_at = timezone.now()
            tx.failure_code = self._norm_str(code)
            tx.failure_message = (message or "").strip()
            tx.full_clean()
            tx.save(update_fields=["status", "failed_at", "failure_code", "failure_message", "updated_at"])

        self.refresh_from_db()

    def mark_cancelled(self, message: str = ""):
        if not self.pk:
            self.save()

        with transaction.atomic():
            tx = type(self).objects.select_for_update().get(pk=self.pk)

            if tx.status == self.STATUS_SUCCEEDED:
                return

            tx.status = self.STATUS_CANCELLED
            tx.cancelled_at = timezone.now()
            if message:
                tx.failure_message = (message or "").strip()
            tx.full_clean()
            tx.save(update_fields=["status", "cancelled_at", "failure_message", "updated_at"])

        self.refresh_from_db()






# # /economic/ecommerce/models/payment_transaction.py
# from __future__ import annotations

# import uuid
# from decimal import Decimal

# from django.core.exceptions import ValidationError
# from django.db import models, transaction
# from django.utils import timezone
# from django.utils.translation import gettext_lazy as _

# from .order import Order


# D0 = Decimal("0.00")


# class PaymentTransaction(models.Model):
#     # ==========================
#     # PROVIDERS
#     # ==========================
#     PROVIDER_STRIPE = "stripe"
#     PROVIDER_PAYPAL = "paypal"
#     PROVIDER_WAVE = "wave"
#     PROVIDER_ORANGE = "orange_money"

#     PROVIDERS = [
#         (PROVIDER_STRIPE, "Stripe"),
#         (PROVIDER_PAYPAL, "PayPal"),
#         (PROVIDER_WAVE, "Wave"),
#         (PROVIDER_ORANGE, "Orange Money"),
#     ]

#     # ==========================
#     # STATUTS
#     # ==========================
#     STATUS_INITIATED = "initiated"
#     STATUS_PENDING = "pending"
#     STATUS_SUCCEEDED = "succeeded"
#     STATUS_FAILED = "failed"
#     STATUS_CANCELLED = "cancelled"

#     STATUS_CHOICES = [
#         (STATUS_INITIATED, _("Initiée")),
#         (STATUS_PENDING, _("En attente")),
#         (STATUS_SUCCEEDED, _("Réussie")),
#         (STATUS_FAILED, _("Échouée")),
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

#     # ✅ Idempotence (retries / webhooks doublés)
#     idempotency_key = models.CharField(
#         max_length=80,
#         blank=True,
#         db_index=True,
#         verbose_name=_("Clé d'idempotence"),
#         help_text=_("Optionnel: empêche la création de doublons en cas de retry."),
#     )

#     # ==========================
#     # COMMANDE
#     # ==========================
#     order = models.ForeignKey(
#         Order,
#         on_delete=models.PROTECT,
#         related_name="payments",
#         verbose_name=_("Commande"),
#     )

#     # ==========================
#     # PAIEMENT
#     # ==========================
#     provider = models.CharField(
#         max_length=20,
#         choices=PROVIDERS,
#         verbose_name=_("Prestataire"),
#         db_index=True,
#     )

#     status = models.CharField(
#         max_length=20,
#         choices=STATUS_CHOICES,
#         default=STATUS_INITIATED,
#         verbose_name=_("Statut"),
#         db_index=True,
#     )

#     amount = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         verbose_name=_("Montant"),
#     )

#     currency = models.CharField(
#         max_length=10,
#         default="XOF",
#         verbose_name=_("Devise"),
#         db_index=True,
#     )

#     provider_fee = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         default=D0,
#         verbose_name=_("Frais prestataire"),
#     )

#     # ==========================
#     # PROVIDER IDS / WEBHOOKS
#     # ==========================
#     provider_payment_id = models.CharField(
#         max_length=255,
#         blank=True,
#         db_index=True,
#         verbose_name=_("ID paiement prestataire"),
#     )

#     provider_event_id = models.CharField(
#         max_length=255,
#         blank=True,
#         null=True,
#         unique=True,
#         verbose_name=_("ID événement prestataire"),
#     )

#     payment_url = models.URLField(
#         blank=True,
#         verbose_name=_("URL de paiement"),
#     )

#     payload = models.JSONField(
#         default=dict,
#         blank=True,
#         verbose_name=_("Payload prestataire"),
#     )

#     # ==========================
#     # OBSERVABILITÉ / RETRIES
#     # ==========================
#     attempt_count = models.PositiveIntegerField(
#         default=0,
#         verbose_name=_("Nombre de tentatives"),
#         help_text=_("Incrémenté à chaque retry / relance."),
#     )

#     last_webhook_at = models.DateTimeField(
#         null=True,
#         blank=True,
#         verbose_name=_("Dernier webhook reçu le"),
#     )

#     failure_code = models.CharField(
#         max_length=80,
#         blank=True,
#         verbose_name=_("Code d'échec"),
#     )

#     failure_message = models.TextField(
#         blank=True,
#         verbose_name=_("Message d'échec"),
#     )

#     # ✅ Timestamps métier
#     succeeded_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Réussie le"))
#     failed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Échouée le"))
#     cancelled_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Annulée le"))

#     # ==========================
#     # TIMESTAMPS
#     # ==========================
#     created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Créée le"))
#     updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Modifiée le"))

#     class Meta:
#         verbose_name = _("Transaction de paiement")
#         verbose_name_plural = _("Transactions de paiement")
#         ordering = ["-created_at"]
#         indexes = [
#             models.Index(fields=["provider", "status"]),
#             models.Index(fields=["created_at"]),
#             models.Index(fields=["order", "created_at"]),
#             models.Index(fields=["provider_payment_id"]),
#             models.Index(fields=["idempotency_key"]),
#         ]
#         constraints = [
#             models.CheckConstraint(check=models.Q(amount__gte=0), name="chk_payment_amount_gte_0"),
#             models.CheckConstraint(check=models.Q(provider_fee__gte=0), name="chk_payment_fee_gte_0"),

#             # ✅ Idempotence réelle (Postgres): unique seulement si non vide
#             models.UniqueConstraint(
#                 fields=["provider", "idempotency_key"],
#                 condition=~models.Q(idempotency_key=""),
#                 name="uniq_payment_provider_idempotency_nonempty",
#             ),
#         ]

#     def __str__(self):
#         return (
#             f"{self.get_provider_display()} · "
#             f"{self.get_status_display()} · "
#             f"{self.amount} {self.currency}"
#         )

#     # ==========================
#     # NORMALISATION / VALIDATION
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

#     def clean(self):
#         super().clean()

#         if self.currency:
#             self.currency = self.currency.strip().upper()

#         if self.idempotency_key:
#             self.idempotency_key = self.idempotency_key.strip()

#         # payload: garantir dict (évite bugs admin/webhook)
#         if self.payload is None:
#             self.payload = {}
#         if not isinstance(self.payload, dict):
#             raise ValidationError({"payload": _("Le payload doit être un objet JSON (dict).")})

#         # montants
#         if self.amount is None:
#             raise ValidationError({"amount": _("Le montant est obligatoire.")})
#         if self.amount is not None and self.amount < 0:
#             raise ValidationError({"amount": _("Le montant ne peut pas être négatif.")})

#         if self.provider_fee is None:
#             self.provider_fee = D0
#         if self.provider_fee is not None and self.provider_fee < 0:
#             raise ValidationError({"provider_fee": _("Les frais ne peuvent pas être négatifs.")})

#         self.amount = self._q2(self._to_dec(self.amount))
#         self.provider_fee = self._q2(max(D0, self._to_dec(self.provider_fee)))

#         # idempotence (fallback Python si DB ne supporte pas contrainte conditionnelle)
#         if self.idempotency_key:
#             qs = type(self).objects.filter(provider=self.provider, idempotency_key=self.idempotency_key)
#             if self.pk:
#                 qs = qs.exclude(pk=self.pk)
#             if qs.exists():
#                 raise ValidationError({"idempotency_key": _("Clé d'idempotence déjà utilisée pour ce prestataire.")})

#         # cohérence timestamps vs status
#         if self.status == self.STATUS_SUCCEEDED:
#             if self.succeeded_at is None:
#                 self.succeeded_at = timezone.now()
#             self.failed_at = None
#             self.cancelled_at = None
#         elif self.status == self.STATUS_FAILED:
#             if self.failed_at is None:
#                 self.failed_at = timezone.now()
#             self.succeeded_at = None
#         elif self.status == self.STATUS_CANCELLED:
#             if self.cancelled_at is None:
#                 self.cancelled_at = timezone.now()
#             self.succeeded_at = None

#     def save(self, *args, **kwargs):
#         # normalise rapide (hors admin aussi)
#         if self.currency:
#             self.currency = self.currency.strip().upper()
#         if self.idempotency_key:
#             self.idempotency_key = self.idempotency_key.strip()

#         # quantize
#         self.amount = self._q2(self._to_dec(self.amount))
#         self.provider_fee = self._q2(max(D0, self._to_dec(self.provider_fee)))

#         self.full_clean()
#         super().save(*args, **kwargs)

#     # ==========================
#     # HELPERS
#     # ==========================
#     @property
#     def is_success(self) -> bool:
#         return self.status == self.STATUS_SUCCEEDED

#     @property
#     def is_pending(self) -> bool:
#         return self.status in {self.STATUS_INITIATED, self.STATUS_PENDING}

#     @property
#     def net_amount(self) -> Decimal:
#         """Montant net = amount - fee (sans descendre sous 0)."""
#         net = self._to_dec(self.amount) - self._to_dec(self.provider_fee or 0)
#         if net < 0:
#             net = D0
#         return self._q2(net)

#     # ==========================
#     # WEBHOOK / RETRIES
#     # ==========================
#     def mark_webhook_received(self, save: bool = True):
#         self.last_webhook_at = timezone.now()
#         if save and self.pk:
#             type(self).objects.filter(pk=self.pk).update(
#                 last_webhook_at=self.last_webhook_at,
#                 updated_at=timezone.now(),
#             )

#     def bump_attempt(self, save: bool = True):
#         """Incrémente attempt_count (utile retries)."""
#         if self.pk and save:
#             type(self).objects.filter(pk=self.pk).update(
#                 attempt_count=models.F("attempt_count") + 1,
#                 updated_at=timezone.now(),
#             )
#             self.refresh_from_db(fields=["attempt_count", "updated_at"])
#         else:
#             self.attempt_count = int(self.attempt_count or 0) + 1

#     # ==========================
#     # TRANSITIONS STATUT (prod safe)
#     # ==========================
#     def mark_pending(self):
#         if self.status != self.STATUS_PENDING:
#             self.status = self.STATUS_PENDING
#         self.full_clean()
#         self.save(update_fields=["status", "updated_at"])

#     def mark_succeeded(self, provider_payment_id: str | None = None):
#         """
#         ✅ Atomic + optionnel: passe la commande en PAID si possible.
#         """
#         with transaction.atomic():
#             tx = type(self).objects.select_for_update().get(pk=self.pk)

#             # idempotent: si déjà succeeded, on complète juste provider_payment_id si nécessaire
#             if tx.status != self.STATUS_SUCCEEDED:
#                 tx.status = self.STATUS_SUCCEEDED
#                 tx.succeeded_at = timezone.now()
#                 tx.failed_at = None
#                 tx.cancelled_at = None
#                 tx.failure_code = ""
#                 tx.failure_message = ""

#             if provider_payment_id and not tx.provider_payment_id:
#                 tx.provider_payment_id = provider_payment_id

#             tx.full_clean()
#             tx.save(update_fields=[
#                 "status", "succeeded_at", "failed_at", "cancelled_at",
#                 "failure_code", "failure_message", "provider_payment_id", "updated_at"
#             ])

#             # sync Order (sans dépendance forte)
#             try:
#                 order = tx.order
#                 if hasattr(order, "mark_paid") and not order.is_paid:
#                     order.mark_paid()
#             except Exception:
#                 pass

#             # refresh local instance
#             self.refresh_from_db()

#     def mark_failed(self, code: str = "", message: str = ""):
#         with transaction.atomic():
#             tx = type(self).objects.select_for_update().get(pk=self.pk)

#             # idempotent: ne pas écraser un succès
#             if tx.status == self.STATUS_SUCCEEDED:
#                 return

#             tx.status = self.STATUS_FAILED
#             tx.failed_at = timezone.now()
#             tx.failure_code = (code or "").strip()
#             tx.failure_message = (message or "").strip()
#             tx.full_clean()
#             tx.save(update_fields=["status", "failed_at", "failure_code", "failure_message", "updated_at"])
#             self.refresh_from_db()

#     def mark_cancelled(self, message: str = ""):
#         with transaction.atomic():
#             tx = type(self).objects.select_for_update().get(pk=self.pk)

#             if tx.status == self.STATUS_SUCCEEDED:
#                 return

#             tx.status = self.STATUS_CANCELLED
#             tx.cancelled_at = timezone.now()
#             if message:
#                 tx.failure_message = (message or "").strip()
#             tx.full_clean()
#             tx.save(update_fields=["status", "cancelled_at", "failure_message", "updated_at"])
#             self.refresh_from_db()






# # economic/ecommerce/models/payment_transaction.py
# from __future__ import annotations

# import uuid
# from decimal import Decimal

# from django.core.exceptions import ValidationError
# from django.db import models
# from django.utils import timezone
# from django.utils.translation import gettext_lazy as _

# from .order import Order


# class PaymentTransaction(models.Model):
#     # ==========================
#     # PROVIDERS
#     # ==========================
#     PROVIDER_STRIPE = "stripe"
#     PROVIDER_PAYPAL = "paypal"
#     PROVIDER_WAVE = "wave"
#     PROVIDER_ORANGE = "orange_money"

#     PROVIDERS = [
#         (PROVIDER_STRIPE, "Stripe"),
#         (PROVIDER_PAYPAL, "PayPal"),
#         (PROVIDER_WAVE, "Wave"),
#         (PROVIDER_ORANGE, "Orange Money"),
#     ]

#     # ==========================
#     # STATUTS
#     # ==========================
#     STATUS_INITIATED = "initiated"
#     STATUS_PENDING = "pending"
#     STATUS_SUCCEEDED = "succeeded"
#     STATUS_FAILED = "failed"
#     STATUS_CANCELLED = "cancelled"

#     STATUS_CHOICES = [
#         (STATUS_INITIATED, _("Initiée")),
#         (STATUS_PENDING, _("En attente")),
#         (STATUS_SUCCEEDED, _("Réussie")),
#         (STATUS_FAILED, _("Échouée")),
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

#     # ✅ Idempotence (utile prod: retries, webhooks en double, relances)
#     idempotency_key = models.CharField(
#         max_length=80,
#         blank=True,
#         db_index=True,
#         verbose_name=_("Clé d'idempotence"),
#         help_text=_("Optionnel: empêche la création de doublons en cas de retry."),
#     )

#     # ==========================
#     # COMMANDE
#     # ==========================
#     order = models.ForeignKey(
#         Order,
#         on_delete=models.PROTECT,  # 🔒 on ne supprime jamais une transaction
#         related_name="payments",
#         verbose_name=_("Commande"),
#     )

#     # ==========================
#     # PAIEMENT
#     # ==========================
#     provider = models.CharField(
#         max_length=20,
#         choices=PROVIDERS,
#         verbose_name=_("Prestataire"),
#         db_index=True,
#     )

#     status = models.CharField(
#         max_length=20,
#         choices=STATUS_CHOICES,
#         default=STATUS_INITIATED,
#         verbose_name=_("Statut"),
#         db_index=True,
#     )

#     amount = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         verbose_name=_("Montant"),
#     )

#     currency = models.CharField(
#         max_length=10,
#         default="XOF",
#         verbose_name=_("Devise"),
#         db_index=True,
#     )

#     # ✅ Frais éventuels (utile si provider prélève une commission)
#     provider_fee = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         default=Decimal("0.00"),
#         verbose_name=_("Frais prestataire"),
#     )

#     # ==========================
#     # PROVIDER IDS / WEBHOOKS
#     # ==========================
#     provider_payment_id = models.CharField(
#         max_length=255,
#         blank=True,
#         db_index=True,
#         verbose_name=_("ID paiement prestataire"),
#     )

#     provider_event_id = models.CharField(
#         max_length=255,
#         blank=True,
#         null=True,
#         unique=True,
#         verbose_name=_("ID événement prestataire"),
#     )

#     payment_url = models.URLField(
#         blank=True,
#         verbose_name=_("URL de paiement"),
#     )

#     payload = models.JSONField(
#         default=dict,
#         blank=True,
#         verbose_name=_("Payload prestataire"),
#     )

#     # ✅ Diagnostics / retries / observabilité
#     attempt_count = models.PositiveIntegerField(
#         default=0,
#         verbose_name=_("Nombre de tentatives"),
#         help_text=_("Incrémenté à chaque retry / relance."),
#     )

#     last_webhook_at = models.DateTimeField(
#         null=True,
#         blank=True,
#         verbose_name=_("Dernier webhook reçu le"),
#     )

#     failure_code = models.CharField(
#         max_length=80,
#         blank=True,
#         verbose_name=_("Code d'échec"),
#     )

#     failure_message = models.TextField(
#         blank=True,
#         verbose_name=_("Message d'échec"),
#     )

#     # ✅ Timestamps métier (très utile en prod)
#     succeeded_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Réussie le"))
#     failed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Échouée le"))
#     cancelled_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Annulée le"))

#     # ==========================
#     # TIMESTAMPS
#     # ==========================
#     created_at = models.DateTimeField(
#         auto_now_add=True,
#         verbose_name=_("Créée le"),
#     )

#     updated_at = models.DateTimeField(
#         auto_now=True,
#         verbose_name=_("Modifiée le"),
#     )

#     class Meta:
#         verbose_name = _("Transaction de paiement")
#         verbose_name_plural = _("Transactions de paiement")
#         ordering = ["-created_at"]
#         indexes = [
#             models.Index(fields=["provider", "status"]),
#             models.Index(fields=["created_at"]),
#             models.Index(fields=["order", "created_at"]),
#             models.Index(fields=["provider_payment_id"]),
#             models.Index(fields=["idempotency_key"]),
#         ]
#         constraints = [
#             models.CheckConstraint(check=models.Q(amount__gte=0), name="chk_payment_amount_gte_0"),
#             models.CheckConstraint(check=models.Q(provider_fee__gte=0), name="chk_payment_fee_gte_0"),
#         ]

#     def __str__(self):
#         return (
#             f"{self.get_provider_display()} · "
#             f"{self.get_status_display()} · "
#             f"{self.amount} {self.currency}"
#         )

#     def clean(self):
#         super().clean()
#         if self.currency:
#             self.currency = self.currency.strip().upper()
#         if self.idempotency_key:
#             self.idempotency_key = self.idempotency_key.strip()

#         if self.amount is None:
#             raise ValidationError({"amount": _("Le montant est obligatoire.")})
#         if self.amount is not None and self.amount < 0:
#             raise ValidationError({"amount": _("Le montant ne peut pas être négatif.")})

#         if self.provider_fee is not None and self.provider_fee < 0:
#             raise ValidationError({"provider_fee": _("Les frais ne peuvent pas être négatifs.")})

#     # ==========================
#     # HELPERS
#     # ==========================
#     @property
#     def is_success(self):
#         return self.status == self.STATUS_SUCCEEDED

#     @property
#     def is_pending(self):
#         return self.status in {self.STATUS_INITIATED, self.STATUS_PENDING}

#     @property
#     def net_amount(self) -> Decimal:
#         """Montant net = amount - fee (sans descendre sous 0)."""
#         try:
#             net = Decimal(self.amount) - Decimal(self.provider_fee or 0)
#             return max(net, Decimal("0.00")).quantize(Decimal("0.01"))
#         except Exception:
#             return Decimal("0.00")

#     def mark_webhook_received(self):
#         self.last_webhook_at = timezone.now()
#         self.save(update_fields=["last_webhook_at", "updated_at"])

#     def mark_pending(self):
#         self.status = self.STATUS_PENDING
#         self.save(update_fields=["status", "updated_at"])

#     def mark_succeeded(self, provider_payment_id: str | None = None):
#         self.status = self.STATUS_SUCCEEDED
#         self.succeeded_at = timezone.now()
#         self.failed_at = None
#         self.cancelled_at = None
#         if provider_payment_id:
#             self.provider_payment_id = provider_payment_id
#         self.save(update_fields=["status", "succeeded_at", "failed_at", "cancelled_at", "provider_payment_id", "updated_at"])

#     def mark_failed(self, code: str = "", message: str = ""):
#         self.status = self.STATUS_FAILED
#         self.failed_at = timezone.now()
#         self.failure_code = (code or "").strip()
#         self.failure_message = (message or "").strip()
#         self.save(update_fields=["status", "failed_at", "failure_code", "failure_message", "updated_at"])

#     def mark_cancelled(self, message: str = ""):
#         self.status = self.STATUS_CANCELLED
#         self.cancelled_at = timezone.now()
#         if message:
#             self.failure_message = (message or "").strip()
#         self.save(update_fields=["status", "cancelled_at", "failure_message", "updated_at"])






# # economic/ecommerce/models/payment_transaction.py

# import uuid
# from django.db import models
# from django.utils.translation import gettext_lazy as _

# from .order import Order


# class PaymentTransaction(models.Model):
#     # ==========================
#     # PROVIDERS
#     # ==========================
#     PROVIDER_STRIPE = "stripe"
#     PROVIDER_PAYPAL = "paypal"
#     PROVIDER_WAVE = "wave"
#     PROVIDER_ORANGE = "orange_money"

#     PROVIDERS = [
#         (PROVIDER_STRIPE, "Stripe"),
#         (PROVIDER_PAYPAL, "PayPal"),
#         (PROVIDER_WAVE, "Wave"),
#         (PROVIDER_ORANGE, "Orange Money"),
#     ]

#     # ==========================
#     # STATUTS
#     # ==========================
#     STATUS_INITIATED = "initiated"
#     STATUS_PENDING = "pending"
#     STATUS_SUCCEEDED = "succeeded"
#     STATUS_FAILED = "failed"
#     STATUS_CANCELLED = "cancelled"

#     STATUS_CHOICES = [
#         (STATUS_INITIATED, _("Initiée")),
#         (STATUS_PENDING, _("En attente")),
#         (STATUS_SUCCEEDED, _("Réussie")),
#         (STATUS_FAILED, _("Échouée")),
#         (STATUS_CANCELLED, _("Annulée")),
#     ]

#     # ==========================
#     # IDENTIFIANT
#     # ==========================
#     uuid = models.UUIDField(
#         default=uuid.uuid4,
#         editable=False,
#         unique=True,
#         verbose_name=_("UUID"),
#     )

#     # ==========================
#     # COMMANDE
#     # ==========================
#     order = models.ForeignKey(
#         Order,
#         on_delete=models.PROTECT,        # 🔒 on ne supprime jamais une transaction
#         related_name="payments",
#         verbose_name=_("Commande"),
#     )

#     # ==========================
#     # PAIEMENT
#     # ==========================
#     provider = models.CharField(
#         max_length=20,
#         choices=PROVIDERS,
#         verbose_name=_("Prestataire"),
#         db_index=True,
#     )

#     status = models.CharField(
#         max_length=20,
#         choices=STATUS_CHOICES,
#         default=STATUS_INITIATED,
#         verbose_name=_("Statut"),
#         db_index=True,
#     )

#     amount = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         verbose_name=_("Montant"),
#     )

#     currency = models.CharField(
#         max_length=10,
#         default="XOF",
#         verbose_name=_("Devise"),
#     )

#     # ==========================
#     # PROVIDER IDS / WEBHOOKS
#     # ==========================
#     provider_payment_id = models.CharField(
#         max_length=255,
#         blank=True,
#         db_index=True,
#         verbose_name=_("ID paiement prestataire"),
#     )

#     provider_event_id = models.CharField(
#         max_length=255,
#         blank=True,
#         null=True,
#         unique=True,
#         verbose_name=_("ID événement prestataire"),
#     )

#     # URL de redirection (Stripe checkout, PayPal approve, etc.)
#     payment_url = models.URLField(
#         blank=True,
#         verbose_name=_("URL de paiement"),
#     )

#     payload = models.JSONField(
#         default=dict,
#         blank=True,
#         verbose_name=_("Payload prestataire"),
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
#         verbose_name=_("Modifiée le"),
#     )

#     class Meta:
#         verbose_name = _("Transaction de paiement")
#         verbose_name_plural = _("Transactions de paiement")
#         ordering = ["-created_at"]
#         indexes = [
#             models.Index(fields=["provider", "status"]),
#             models.Index(fields=["created_at"]),
#         ]

#     def __str__(self):
#         return (
#             f"{self.get_provider_display()} · "
#             f"{self.get_status_display()} · "
#             f"{self.amount} {self.currency}"
#         )

#     # ==========================
#     # HELPERS
#     # ==========================
#     @property
#     def is_success(self):
#         return self.status == self.STATUS_SUCCEEDED

#     @property
#     def is_pending(self):
#         return self.status in {self.STATUS_INITIATED, self.STATUS_PENDING}








# # economic/ecommerce/models/payment_transaction.py

# import uuid
# from django.db import models
# from django.utils.translation import gettext_lazy as _

# from .order import Order


# class PaymentTransaction(models.Model):
#     PROVIDER_STRIPE = "stripe"
#     PROVIDER_PAYPAL = "paypal"
#     PROVIDER_WAVE = "wave"
#     PROVIDER_ORANGE = "orange"

#     PROVIDERS = [
#         (PROVIDER_STRIPE, "Stripe"),
#         (PROVIDER_PAYPAL, "PayPal"),
#         (PROVIDER_WAVE, "Wave"),
#         (PROVIDER_ORANGE, "Orange Money"),
#     ]

#     STATUS_INITIATED = "initiated"
#     STATUS_PENDING = "pending"
#     STATUS_SUCCEEDED = "succeeded"
#     STATUS_FAILED = "failed"
#     STATUS_CANCELLED = "cancelled"

#     STATUS_CHOICES = [
#         (STATUS_INITIATED, _("Initiée")),
#         (STATUS_PENDING, _("En attente")),
#         (STATUS_SUCCEEDED, _("Réussie")),
#         (STATUS_FAILED, _("Échouée")),
#         (STATUS_CANCELLED, _("Annulée")),
#     ]

#     uuid = models.UUIDField(
#         default=uuid.uuid4,
#         editable=False,
#         unique=True,
#         verbose_name=_("UUID"),
#     )

#     order = models.ForeignKey(
#         Order,
#         on_delete=models.CASCADE,
#         related_name="payments",
#         verbose_name=_("Commande"),
#     )

#     provider = models.CharField(
#         max_length=20,
#         choices=PROVIDERS,
#         verbose_name=_("Prestataire"),
#     )

#     status = models.CharField(
#         max_length=20,
#         choices=STATUS_CHOICES,
#         default=STATUS_INITIATED,
#         verbose_name=_("Statut"),
#     )

#     # Identifiants côté prestataire (idempotence / webhooks)
#     provider_payment_id = models.CharField(
#         max_length=255,
#         blank=True,
#         db_index=True,
#         verbose_name=_("ID paiement prestataire"),
#     )

#     provider_event_id = models.CharField(
#         max_length=255,
#         blank=True,
#         unique=True,
#         db_index=True,
#         verbose_name=_("ID événement prestataire"),
#     )

#     amount = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         verbose_name=_("Montant"),
#     )

#     currency = models.CharField(
#         max_length=10,
#         default="XOF",
#         verbose_name=_("Devise"),
#     )

#     payload = models.JSONField(
#         default=dict,
#         blank=True,
#         verbose_name=_("Payload prestataire"),
#     )

#     created_at = models.DateTimeField(
#         auto_now_add=True,
#         verbose_name=_("Créée le"),
#     )

#     updated_at = models.DateTimeField(
#         auto_now=True,
#         verbose_name=_("Modifiée le"),
#     )

#     class Meta:
#         verbose_name = _("Transaction de paiement")
#         verbose_name_plural = _("Transactions de paiement")
#         ordering = ["-created_at"]

#     def __str__(self):
#         return f"{self.get_provider_display()} · {self.get_status_display()} · {self.amount} {self.currency}"
