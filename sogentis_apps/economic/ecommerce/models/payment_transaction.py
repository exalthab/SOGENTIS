import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _

from .order import Order


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
    # IDENTIFIANT
    # ==========================
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        verbose_name=_("UUID"),
    )

    # ==========================
    # COMMANDE
    # ==========================
    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,        # 🔒 on ne supprime jamais une transaction
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

    provider_event_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        unique=True,
        verbose_name=_("ID événement prestataire"),
    )

    # URL de redirection (Stripe checkout, PayPal approve, etc.)
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
    # TIMESTAMPS
    # ==========================
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Créée le"),
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Modifiée le"),
    )

    class Meta:
        verbose_name = _("Transaction de paiement")
        verbose_name_plural = _("Transactions de paiement")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["provider", "status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return (
            f"{self.get_provider_display()} · "
            f"{self.get_status_display()} · "
            f"{self.amount} {self.currency}"
        )

    # ==========================
    # HELPERS
    # ==========================
    @property
    def is_success(self):
        return self.status == self.STATUS_SUCCEEDED

    @property
    def is_pending(self):
        return self.status in {self.STATUS_INITIATED, self.STATUS_PENDING}








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
