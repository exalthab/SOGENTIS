# economic/support/models/support_ticket.py
import uuid
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class SupportTicket(models.Model):
    class Priority(models.TextChoices):
        LOW = "LOW", _("Basse")
        MEDIUM = "MEDIUM", _("Moyenne")
        HIGH = "HIGH", _("Haute")
        URGENT = "URGENT", _("Urgente")

    class Status(models.TextChoices):
        OPEN = "OPEN", _("Ouvert")
        IN_PROGRESS = "IN_PROGRESS", _("En cours")
        WAITING_CUSTOMER = "WAITING_CUSTOMER", _("En attente du client")
        RESOLVED = "RESOLVED", _("Résolu")
        CLOSED = "CLOSED", _("Clôturé")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="support_tickets",
        verbose_name=_("Utilisateur"),
    )

    subject = models.CharField(_("Sujet"), max_length=180)
    description = models.TextField(_("Description"))

    priority = models.CharField(
        _("Priorité"),
        max_length=12,
        choices=Priority.choices,
        default=Priority.MEDIUM,
    )

    status = models.CharField(
        _("Statut"),
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
        db_index=True,
    )

    order_ref = models.CharField(
        _("Référence commande (optionnel)"),
        max_length=64,
        blank=True,
        default="",
        db_index=True,
    )

    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)
    closed_at = models.DateTimeField(_("Clôturé le"), null=True, blank=True)

    class Meta:
        verbose_name = _("Ticket support")
        verbose_name_plural = _("Tickets support")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["user", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.subject} ({self.get_status_display()})"







# from django.db import models


# class SupportTicket(models.Model):
#     subject = models.CharField(max_length=255)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.subject
    
