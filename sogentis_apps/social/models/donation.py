# social/models/donation.py
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum
from .project import Project


class DonationManager(models.Manager):
    def aggregate_total_amount(self, user=None):
        """
        Retourne la somme totale des montants de dons.
        Optionnellement filtré par utilisateur connecté.
        """
        qs = self.get_queryset()
        if user:
            qs = qs.filter(user=user)
        return qs.aggregate(total=Sum("amount"))["total"] or 0


class Donation(models.Model):
    STATUS_CHOICES = [
        ("pending", _("En attente")),
        ("paid", _("Payé")),
        ("failed", _("Échoué")),
        ("cancelled", _("Annulé")),
    ]

    PAYMENT_METHOD_CHOICES = [
        ("stripe", _("Carte (Stripe)")),
        ("paypal", _("PayPal")),
        ("orange_money", _("Orange Money")),
        ("wave", _("Wave")),
        ("visa", _("Visa / Carte bancaire")),
    ]

    # Donateur connecté (optionnel)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Utilisateur")
    )

    # Donateur invité (nom/email)
    donor_name = models.CharField(_("Nom du donateur"), max_length=255, blank=True)
    email = models.EmailField(_("Email du donateur"), blank=True)

    # Projet associé (facultatif)
    project = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Projet")
    )

    # Montant et date
    amount = models.DecimalField(_("Montant du don"), max_digits=10, decimal_places=2)
    message = models.TextField(_("Message"), blank=True)

    # Paiement
    payment_method = models.CharField(
        _("Méthode de paiement"),
        max_length=50,
        choices=PAYMENT_METHOD_CHOICES,
        default="stripe"
    )
    status = models.CharField(
        _("Statut du paiement"),
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )
    monthly = models.BooleanField(_("Don mensuel récurrent ?"), default=False)

    # Reçu PDF
    pdf_receipt = models.FileField(
        _("Reçu PDF"),
        upload_to="donations/receipts/",
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)

    objects = DonationManager()

    class Meta:
        verbose_name = _("Don")
        verbose_name_plural = _("Dons")
        ordering = ['-created_at']

    def __str__(self):
        label = self.user.email if self.user else (self.donor_name or _("Anonyme"))
        type_label = _("mensuel") if self.monthly else _("ponctuel")
        return f"{label} – {self.amount} FCFA – {self.get_payment_method_display()} ({type_label})"

    def is_paid(self):
        return self.status == "paid"

    @property
    def date(self):
        return self.created_at.date()

    @property
    def donation_type(self):
        return _("Mensuel") if self.monthly else _("Ponctuel")
