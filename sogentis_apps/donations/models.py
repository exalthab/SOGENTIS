# donations/models.py
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Donation(models.Model):
    STATUS_PENDING = "pending"
    STATUS_COMPLETED = "completed"
    STATUS_FAILED = "failed"

    STATUS_CHOICES = (
        (STATUS_PENDING, _("En attente")),
        (STATUS_COMPLETED, _("Complété")),
        (STATUS_FAILED, _("Échoué")),
    )

    # Méthodes de paiement (adaptable)
    PM_STRIPE = "stripe"
    PM_PAYPAL = "paypal"
    PM_WAVE = "wave"
    PM_ORANGE_MONEY = "orange_money"
    PM_CARD = "card"
    PM_BANK = "bank"
    PM_CASH = "cash"
    PM_OTHER = "other"

    PAYMENT_METHOD_CHOICES = (
        (PM_STRIPE, _("Stripe")),
        (PM_PAYPAL, _("PayPal")),
        (PM_WAVE, _("Wave")),
        (PM_ORANGE_MONEY, _("Orange Money")),
        (PM_CARD, _("Carte")),
        (PM_BANK, _("Virement bancaire")),
        (PM_CASH, _("Espèces")),
        (PM_OTHER, _("Autre")),
    )

    # Devises (tu peux en ajouter)
    CUR_XOF = "XOF"
    CUR_EUR = "EUR"
    CUR_USD = "USD"

    CURRENCY_CHOICES = (
        (CUR_XOF, _("XOF")),
        (CUR_EUR, _("EUR")),
        (CUR_USD, _("USD")),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="donation_donations",
        related_query_name="donation_donation",
        verbose_name=_("Utilisateur"),
    )

    project = models.ForeignKey(
        "social.Project",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="donation_donations",
        related_query_name="donation_donation",
        verbose_name=_("Projet"),
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Montant"),
    )

    currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default=CUR_XOF,
        db_index=True,
        verbose_name=_("Devise"),
    )

    payment_method = models.CharField(
        max_length=30,
        choices=PAYMENT_METHOD_CHOICES,
        blank=True,
        default="",
        db_index=True,
        verbose_name=_("Méthode de paiement"),
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        db_index=True,
        verbose_name=_("Statut"),
    )

    receipt_pdf = models.FileField(
        upload_to="donations/receipts/",
        null=True,
        blank=True,
        verbose_name=_("Reçu PDF"),
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Créé le"))

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Don")
        verbose_name_plural = _("Dons")
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["currency"]),
            models.Index(fields=["payment_method"]),
        ]

    def __str__(self):
        return f"Donation #{self.id} - {self.amount} {self.currency}"






# # donations/models.py
# from django.conf import settings
# from django.db import models


# class Donation(models.Model):
#     STATUS_PENDING = "pending"
#     STATUS_COMPLETED = "completed"
#     STATUS_FAILED = "failed"

#     STATUS_CHOICES = (
#         (STATUS_PENDING, "En attente"),
#         (STATUS_COMPLETED, "Complété"),
#         (STATUS_FAILED, "Échoué"),
#     )

#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name="donation_donations",
#         related_query_name="donation_donation",
#     )

#     project = models.ForeignKey(
#         "social.Project",
#         null=True,
#         blank=True,
#         on_delete=models.SET_NULL,
#         related_name="donation_donations",
#         related_query_name="donation_donation",
#     )

#     amount = models.DecimalField(
#         max_digits=10,
#         decimal_places=2,
#     )

#     status = models.CharField(
#         max_length=20,
#         choices=STATUS_CHOICES,
#         default=STATUS_PENDING,
#     )

#     receipt_pdf = models.FileField(
#         upload_to="donations/receipts/",
#         null=True,
#         blank=True,
#     )

#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         ordering = ["-created_at"]

#     def __str__(self):
#         return f"Donation #{self.id} - {self.amount}"
