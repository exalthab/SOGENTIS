from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class DocumentPurchase(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("Utilisateur"),
        related_name="document_purchases"
    )
    publication = models.ForeignKey(
        'social.Publication',
        on_delete=models.CASCADE,
        verbose_name=_("Document / Publication"),
        related_name="purchases"
    )
    email = models.EmailField(_("Email de réception"))
    amount_paid = models.DecimalField(
        _("Montant payé (FCFA)"),
        max_digits=9,
        decimal_places=2
    )
    payment_method = models.CharField(
        _("Méthode de paiement"),
        max_length=20
    )
    payment_id = models.CharField(
        _("ID paiement (Stripe/Paypal/autre)"),
        max_length=100,
        blank=True
    )
    purchased_at = models.DateTimeField(_("Acheté le"), auto_now_add=True)

    # Champs supplémentaires pour le contrôle
    copy_number = models.PositiveIntegerField(
        _("N° de copie"),
        null=True,
        blank=True,
        help_text=_("Numéro de copie séquentiel attribué à cet achat.")
    )
    has_downloaded = models.BooleanField(
        _("Déjà téléchargé ?"),
        default=False,
        help_text=_("Empêche le téléchargement multiple. Si True, une demande manuelle est requise.")
    )

    class Meta:
        verbose_name = _("Achat de document")
        verbose_name_plural = _("Achats de documents")
        unique_together = [("user", "publication")]
        ordering = ["-purchased_at"]

    def __str__(self):
        return f"{self.user.email} – {self.publication.title} ({self.amount_paid} FCFA)"

    @property
    def is_paid(self):
        return self.amount_paid > 0
