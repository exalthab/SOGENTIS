# social/models/donation.py
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from .project import Project


class DonationManager(models.Manager):
    def aggregate_total_amount(self, user=None):
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

    # 🔹 Donateur
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Utilisateur"),
        related_name="donations"
    )
    donor_name = models.CharField(_("Nom du donateur"), max_length=255, blank=True)
    email = models.EmailField(_("Email du donateur"), blank=True)

    # 🔹 Projet optionnel
    project = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Projet"),
        related_name="donations"
    )

    # 🔥 Cible explicite
    target_type = models.CharField(
        _("Type de cible"),
        max_length=50,
        null=True,
        blank=True,
        help_text=_("mother / child / project")
    )
    target_id = models.PositiveIntegerField(
        _("ID brut de la cible"),
        null=True,
        blank=True
    )

    # 🔥 GenericForeignKey
    target_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Type de cible")
    )
    target_object_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("ID de la cible")
    )
    target = GenericForeignKey("target_content_type", "target_object_id")

    # 💰 Montant et message
    amount = models.DecimalField(_("Montant du don"), max_digits=10, decimal_places=2)
    message = models.TextField(_("Message"), blank=True)

    # 💳 Paiement
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

    # 📄 PDF du reçu
    pdf_receipt = models.FileField(
        _("Reçu PDF"),
        upload_to="donations/receipts/",
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)

    # Manager custom
    objects = DonationManager()

    class Meta:
        verbose_name = _("Don")
        verbose_name_plural = _("Dons")
        ordering = ['-created_at']

    # ---------------------------------------------------------
    # 🔹 Affichage
    # ---------------------------------------------------------
    def __str__(self):
        donor = self.user.email if self.user else (self.donor_name or _("Anonyme"))
        target_label = f" → {self.target}" if self.target else ""
        return f"{donor} – {self.amount} FCFA{target_label}"

    # ---------------------------------------------------------
    # 🔹 Helpers
    # ---------------------------------------------------------
    def is_paid(self):
        return self.status == "paid"

    @property
    def date(self):
        return self.created_at.date()

    @property
    def donation_type(self):
        return _("Mensuel") if self.monthly else _("Ponctuel")
