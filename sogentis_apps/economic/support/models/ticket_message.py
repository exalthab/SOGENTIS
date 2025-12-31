from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from .ticket import SupportTicket


class TicketMessage(models.Model):
    ticket = models.ForeignKey(
        SupportTicket,
        on_delete=models.CASCADE,
        related_name="messages",
        verbose_name=_("Ticket"),
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="support_messages",
        verbose_name=_("Auteur"),
    )

    is_staff_reply = models.BooleanField(_("Réponse staff"), default=False)

    message = models.TextField(_("Message"))

    attachment = models.FileField(
        _("Pièce jointe"),
        upload_to="support/attachments/%Y/%m/",
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)

    class Meta:
        verbose_name = _("Message ticket")
        verbose_name_plural = _("Messages tickets")
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"#{self.ticket_id} - {self.created_at:%Y-%m-%d %H:%M}"
