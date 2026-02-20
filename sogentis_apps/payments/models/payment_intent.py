# payments/models/payment_intent.py
from __future__ import annotations

import uuid as uuidlib
from decimal import Decimal

from django.apps import apps
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class PaymentIntent(models.Model):
    # ----------------------------
    # Enums
    # ----------------------------
    class Status(models.TextChoices):
        CREATED = "CREATED", _("Créé")
        PENDING = "PENDING", _("En attente")
        REQUIRES_ACTION = "REQUIRES_ACTION", _("Action requise")
        PAID = "PAID", _("Payé")
        FAILED = "FAILED", _("Échoué")
        CANCELED = "CANCELED", _("Annulé")
        REFUNDED = "REFUNDED", _("Remboursé")

    class Provider(models.TextChoices):
        STRIPE = "stripe", "Stripe"
        PAYPAL = "paypal", "PayPal"
        WAVE = "wave", "Wave"
        ORANGE_MONEY = "orange_money", "Orange Money"
        ORANGE_LEGACY = "orange", "Orange (legacy)"
        VISA = "visa", "Visa"

    class Pole(models.TextChoices):
        ECONOMIC = "ECONOMIC", _("Économique")
        SOCIAL = "SOCIAL", _("Social")
        INSTITUTION = "INSTITUTION", _("Institution")
        CORE = "CORE", _("Core")

    class Purpose(models.TextChoices):
        # Social
        DONATION = "DONATION", _("Don")
        PUBLICATION = "PUBLICATION", _("Publication")
        # Economic
        ECOM_ORDER = "ECOM_ORDER", _("Commande e-commerce")
        FORMATION = "FORMATION", _("Formation")
        PRESTATION = "PRESTATION", _("Prestation")
        PACK = "PACK", _("Pack")
        # Future
        OTHER = "OTHER", _("Autre")

    # ----------------------------
    # Core fields
    # ----------------------------
    uuid = models.UUIDField(default=uuidlib.uuid4, unique=True, editable=False, db_index=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payment_intents",
    )

    reference = models.CharField(max_length=32, blank=True, default="", db_index=True)

    amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    currency = models.CharField(max_length=8, default="XOF")

    status = models.CharField(max_length=24, choices=Status.choices, default=Status.CREATED, db_index=True)
    provider = models.CharField(max_length=24, choices=Provider.choices, blank=True, default="")
    provider_ref = models.CharField(max_length=255, blank=True, default="", db_index=True)

    pole = models.CharField(max_length=16, choices=Pole.choices, default=Pole.ECONOMIC, db_index=True)
    purpose = models.CharField(max_length=24, choices=Purpose.choices, default=Purpose.OTHER, db_index=True)

    description = models.CharField(max_length=240, blank=True, default="")

    # checkout URLs (central)
    checkout_url = models.URLField(blank=True, default="")
    return_url = models.CharField(max_length=300, blank=True, default="")
    cancel_url = models.CharField(max_length=300, blank=True, default="")

    # Generic link => Order / Donation / Enrollment / Prestation / Pack / Offer etc.
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.CharField(max_length=64, blank=True, default="")
    content_object = GenericForeignKey("content_type", "object_id")

    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(fields=["status", "created_at"], name="pay_status_created_idx"),
            models.Index(fields=["provider", "provider_ref"], name="pay_provider_ref_idx"),
            models.Index(fields=["pole", "created_at"], name="pay_pole_created_idx"),
            models.Index(fields=["purpose", "created_at"], name="pay_purpose_created_idx"),
            models.Index(fields=["reference"], name="pay_reference_idx"),
        ]
        constraints = [
            models.CheckConstraint(check=Q(amount__gte=0), name="pay_amount_non_negative"),
            models.UniqueConstraint(
                fields=["provider", "provider_ref"],
                condition=~Q(provider_ref=""),
                name="pay_unique_provider_ref_not_empty",
            ),
        ]

    def __str__(self) -> str:
        ref = self.reference or str(self.uuid)
        return f"{ref} {self.amount} {self.currency} [{self.status}]"

    def save(self, *args, **kwargs):
        self.currency = (self.currency or "XOF").upper()

        if not self.reference:
            ym = timezone.now().strftime("%Y%m")
            tail = str(self.uuid).split("-")[0].upper()
            self.reference = f"PAY-{ym}-{tail}"

        super().save(*args, **kwargs)

    # ----------------------------
    # Helpers
    # ----------------------------
    @property
    def is_payable(self) -> bool:
        try:
            return Decimal(self.amount or 0) > 0
        except Exception:
            return False

    @property
    def is_paid(self) -> bool:
        return self.status == self.Status.PAID

    # ----------------------------
    # State transitions
    # ----------------------------
    def mark_pending(self, provider: str = "", provider_ref: str = "", checkout_url: str = "") -> None:
        self.status = self.Status.PENDING
        if provider:
            self.provider = provider
        if provider_ref:
            self.provider_ref = provider_ref
        if checkout_url:
            self.checkout_url = checkout_url
        self.save(update_fields=["status", "provider", "provider_ref", "checkout_url", "updated_at"])

    def mark_requires_action(self, provider: str = "", provider_ref: str = "", checkout_url: str = "") -> None:
        self.status = self.Status.REQUIRES_ACTION
        if provider:
            self.provider = provider
        if provider_ref:
            self.provider_ref = provider_ref
        if checkout_url:
            self.checkout_url = checkout_url
        self.save(update_fields=["status", "provider", "provider_ref", "checkout_url", "updated_at"])

    @transaction.atomic
    def mark_paid(self, provider: str = "", provider_ref: str = "") -> None:
        locked = PaymentIntent.objects.select_for_update().only("id", "status").get(pk=self.pk)
        if locked.status == self.Status.PAID:
            return

        self.status = self.Status.PAID
        self.paid_at = timezone.now()
        if provider:
            self.provider = provider
        if provider_ref:
            self.provider_ref = provider_ref
        self.save(update_fields=["status", "paid_at", "provider", "provider_ref", "updated_at"])

        if apps.is_installed("accounting"):
            try:
                from accounting.services.posting import post_payment_intent
                post_payment_intent(self)
            except Exception:
                pass

    def mark_failed(self, provider: str = "", provider_ref: str = "") -> None:
        self.status = self.Status.FAILED
        if provider:
            self.provider = provider
        if provider_ref:
            self.provider_ref = provider_ref
        self.save(update_fields=["status", "provider", "provider_ref", "updated_at"])

    def mark_canceled(self) -> None:
        self.status = self.Status.CANCELED
        self.save(update_fields=["status", "updated_at"])

    def mark_refunded(self) -> None:
        self.status = self.Status.REFUNDED
        self.save(update_fields=["status", "updated_at"])






# # payments/models/payment_intent.py
# from __future__ import annotations

# import uuid as uuidlib
# from decimal import Decimal

# from django.conf import settings
# from django.contrib.contenttypes.fields import GenericForeignKey
# from django.contrib.contenttypes.models import ContentType
# from django.db import models, transaction
# from django.utils import timezone
# from django.utils.translation import gettext_lazy as _


# class PaymentIntent(models.Model):
#     # ----------------------------
#     # Enums
#     # ----------------------------
#     class Status(models.TextChoices):
#         CREATED = "CREATED", _("Créé")
#         PENDING = "PENDING", _("En attente")
#         REQUIRES_ACTION = "REQUIRES_ACTION", _("Action requise")
#         PAID = "PAID", _("Payé")
#         FAILED = "FAILED", _("Échoué")
#         CANCELED = "CANCELED", _("Annulé")
#         REFUNDED = "REFUNDED", _("Remboursé")

#     class Provider(models.TextChoices):
#         STRIPE = "stripe", "Stripe"
#         PAYPAL = "paypal", "PayPal"
#         WAVE = "wave", "Wave"
#         ORANGE_MONEY = "orange_money", "Orange Money"
#         ORANGE_LEGACY = "orange", "Orange (legacy)"  # compat données anciennes si existantes
#         VISA = "visa", "Visa"

#     class Pole(models.TextChoices):
#         ECONOMIC = "ECONOMIC", _("Économique")
#         SOCIAL = "SOCIAL", _("Social")
#         INSTITUTION = "INSTITUTION", _("Institution")
#         CORE = "CORE", _("Core")

#     class Purpose(models.TextChoices):
#         # Social
#         DONATION = "DONATION", _("Don")
#         PUBLICATION = "PUBLICATION", _("Publication")
#         # Economic
#         ECOM_ORDER = "ECOM_ORDER", _("Commande e-commerce")
#         FORMATION = "FORMATION", _("Formation")
#         PRESTATION = "PRESTATION", _("Prestation")
#         PACK = "PACK", _("Pack")
#         # future
#         OTHER = "OTHER", _("Autre")

#     # ----------------------------
#     # Core fields
#     # ----------------------------
#     uuid = models.UUIDField(default=uuidlib.uuid4, unique=True, editable=False, db_index=True)

#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,  # on ne casse pas ton existant
#         related_name="payment_intents",
#     )

#     reference = models.CharField(max_length=32, blank=True, default="", db_index=True)

#     amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
#     currency = models.CharField(max_length=8, default="XOF")

#     status = models.CharField(max_length=24, choices=Status.choices, default=Status.CREATED, db_index=True)
#     provider = models.CharField(max_length=24, choices=Provider.choices, blank=True, default="")
#     provider_ref = models.CharField(max_length=255, blank=True, default="", db_index=True)

#     pole = models.CharField(max_length=16, choices=Pole.choices, default=Pole.ECONOMIC, db_index=True)
#     purpose = models.CharField(max_length=24, choices=Purpose.choices, default=Purpose.OTHER, db_index=True)

#     description = models.CharField(max_length=240, blank=True, default="")

#     # checkout URLs (central)
#     checkout_url = models.URLField(blank=True, default="")
#     return_url = models.CharField(max_length=300, blank=True, default="")
#     cancel_url = models.CharField(max_length=300, blank=True, default="")

#     # Generic link => Order / Donation / Enrollment / Prestation / Pack / Offer etc.
#     content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
#     object_id = models.CharField(max_length=64, blank=True, default="")
#     content_object = GenericForeignKey("content_type", "object_id")

#     metadata = models.JSONField(default=dict, blank=True)

#     created_at = models.DateTimeField(auto_now_add=True, db_index=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     paid_at = models.DateTimeField(null=True, blank=True)

#     class Meta:
#         ordering = ["-created_at", "-id"]
#         indexes = [
#             models.Index(fields=["status", "-created_at"]),
#             models.Index(fields=["provider", "provider_ref"]),
#             models.Index(fields=["pole", "-created_at"]),
#             models.Index(fields=["purpose", "-created_at"]),
#             models.Index(fields=["reference"]),
#         ]

#     def __str__(self) -> str:
#         return f"{self.reference or self.uuid} {self.amount} {self.currency} [{self.status}]"

#     def save(self, *args, **kwargs):
#         self.currency = (self.currency or "XOF").upper()

#         if not self.reference:
#             ym = timezone.now().strftime("%Y%m")
#             tail = str(self.uuid).split("-")[0].upper()
#             self.reference = f"PAY-{ym}-{tail}"

#         super().save(*args, **kwargs)

#     @property
#     def is_payable(self) -> bool:
#         try:
#             return Decimal(self.amount or 0) > 0
#         except Exception:
#             return False

#     # ----------------------------
#     # State transitions
#     # ----------------------------
#     def mark_pending(self, provider: str = "", provider_ref: str = "", checkout_url: str = "") -> None:
#         self.status = self.Status.PENDING
#         if provider:
#             self.provider = provider
#         if provider_ref:
#             self.provider_ref = provider_ref
#         if checkout_url:
#             self.checkout_url = checkout_url
#         self.save(update_fields=["status", "provider", "provider_ref", "checkout_url", "updated_at"])

#     def mark_requires_action(self, provider: str = "", provider_ref: str = "", checkout_url: str = "") -> None:
#         self.status = self.Status.REQUIRES_ACTION
#         if provider:
#             self.provider = provider
#         if provider_ref:
#             self.provider_ref = provider_ref
#         if checkout_url:
#             self.checkout_url = checkout_url
#         self.save(update_fields=["status", "provider", "provider_ref", "checkout_url", "updated_at"])

#     @transaction.atomic
#     def mark_paid(self, provider: str = "", provider_ref: str = "") -> None:
#         if self.status == self.Status.PAID:
#             return
#         self.status = self.Status.PAID
#         self.paid_at = timezone.now()
#         if provider:
#             self.provider = provider
#         if provider_ref:
#             self.provider_ref = provider_ref
#         self.save(update_fields=["status", "paid_at", "provider", "provider_ref", "updated_at"])

#         # Posting comptable (si accounting installé)
#         try:
#             from accounting.services.posting import post_payment_intent
#             post_payment_intent(self)
#         except Exception:
#             pass

#     def mark_failed(self, provider: str = "", provider_ref: str = "") -> None:
#         self.status = self.Status.FAILED
#         if provider:
#             self.provider = provider
#         if provider_ref:
#             self.provider_ref = provider_ref
#         self.save(update_fields=["status", "provider", "provider_ref", "updated_at"])

#     def mark_canceled(self) -> None:
#         self.status = self.Status.CANCELED
#         self.save(update_fields=["status", "updated_at"])

#     def mark_refunded(self) -> None:
#         self.status = self.Status.REFUNDED
#         self.save(update_fields=["status", "updated_at"])









# # payments/models/payment_intent.py
# from __future__ import annotations

# import uuid as uuidlib
# from decimal import Decimal

# from django.conf import settings
# from django.contrib.contenttypes.fields import GenericForeignKey
# from django.contrib.contenttypes.models import ContentType
# from django.db import models
# from django.utils import timezone
# from django.utils.translation import gettext_lazy as _


# class PaymentIntent(models.Model):
#     class Status(models.TextChoices):
#         CREATED = "CREATED", _("Créé")
#         PENDING = "PENDING", _("En attente")
#         PAID = "PAID", _("Payé")
#         FAILED = "FAILED", _("Échoué")
#         CANCELED = "CANCELED", _("Annulé")
#         REFUNDED = "REFUNDED", _("Remboursé")

#     class Provider(models.TextChoices):
#         STRIPE = "stripe", "Stripe"
#         PAYPAL = "paypal", "PayPal"
#         WAVE = "wave", "Wave"
#         ORANGE = "orange", "Orange Money"
#         VISA = "visa", "Visa"

#     class Pole(models.TextChoices):
#         ECONOMIC = "ECONOMIC", _("Économique")
#         SOCIAL = "SOCIAL", _("Social")
#         INSTITUTION = "INSTITUTION", _("Institution")
#         CORE = "CORE", _("Core")

#     uuid = models.UUIDField(default=uuidlib.uuid4, unique=True, editable=False, db_index=True)
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payment_intents")

#     amount = models.DecimalField(max_digits=12, decimal_places=2)
#     currency = models.CharField(max_length=8, default="XOF")

#     status = models.CharField(max_length=16, choices=Status.choices, default=Status.CREATED, db_index=True)
#     provider = models.CharField(max_length=16, choices=Provider.choices, blank=True, default="")
#     provider_ref = models.CharField(max_length=128, blank=True, default="", db_index=True)

#     pole = models.CharField(max_length=16, choices=Pole.choices, default=Pole.ECONOMIC, db_index=True)
#     description = models.CharField(max_length=240, blank=True, default="")

#     # Return/cancel (optionnel : si tu veux override par objet)
#     return_url = models.CharField(max_length=300, blank=True, default="")
#     cancel_url = models.CharField(max_length=300, blank=True, default="")

#     # Generic link => Order / Donation / Enrollment / Prestation / Pack / Offer etc.
#     content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
#     object_id = models.CharField(max_length=64, blank=True, default="")
#     content_object = GenericForeignKey("content_type", "object_id")

#     metadata = models.JSONField(default=dict, blank=True)

#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     paid_at = models.DateTimeField(null=True, blank=True)

#     class Meta:
#         ordering = ["-created_at", "-id"]
#         indexes = [
#             models.Index(fields=["status", "created_at"]),
#             models.Index(fields=["provider", "provider_ref"]),
#             models.Index(fields=["pole", "created_at"]),
#         ]

#     def __str__(self) -> str:
#         return f"{self.uuid} {self.amount} {self.currency} [{self.status}]"

#     @property
#     def is_payable(self) -> bool:
#         try:
#             return Decimal(self.amount or 0) > 0
#         except Exception:
#             return False

#     def mark_pending(self, provider: str = "", provider_ref: str = "") -> None:
#         self.status = self.Status.PENDING
#         if provider:
#             self.provider = provider
#         if provider_ref:
#             self.provider_ref = provider_ref
#         self.save(update_fields=["status", "provider", "provider_ref", "updated_at"])

#     def mark_paid(self, provider: str = "", provider_ref: str = "") -> None:
#         self.status = self.Status.PAID
#         self.paid_at = timezone.now()
#         if provider:
#             self.provider = provider
#         if provider_ref:
#             self.provider_ref = provider_ref
#         self.save(update_fields=["status", "paid_at", "provider", "provider_ref", "updated_at"])

#     def mark_failed(self, provider: str = "", provider_ref: str = "") -> None:
#         self.status = self.Status.FAILED
#         if provider:
#             self.provider = provider
#         if provider_ref:
#             self.provider_ref = provider_ref
#         self.save(update_fields=["status", "provider", "provider_ref", "updated_at"])
