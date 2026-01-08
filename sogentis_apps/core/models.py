# core/models.py
# core/models.py (optionnel: mêmes champs + indexes + helpers)
from __future__ import annotations

import uuid
from datetime import timedelta

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class ContactMessage(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", _("En attente de vérification")
        VERIFIED = "VERIFIED", _("Email vérifié")
        SENT = "SENT", _("Transmis à l'équipe")
        REJECTED = "REJECTED", _("Rejeté")

    name = models.CharField(_("Nom"), max_length=255)
    email = models.EmailField(_("Adresse email"))
    message = models.TextField(_("Message"))

    status = models.CharField(
        _("Statut"),
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )

    verify_token = models.UUIDField(
        _("Token de vérification"),
        default=uuid.uuid4,
        unique=True,
        editable=False,
        db_index=True,
    )
    token_expires_at = models.DateTimeField(_("Expiration du token"), null=True, blank=True)

    verified_at = models.DateTimeField(_("Vérifié le"), null=True, blank=True)
    sent_at = models.DateTimeField(_("Transmis le"), null=True, blank=True)

    sender_ip = models.GenericIPAddressField(_("IP expéditeur"), null=True, blank=True)
    user_agent = models.CharField(_("User agent"), max_length=512, blank=True)

    created_at = models.DateTimeField(_("Envoyé le"), auto_now_add=True)

    class Meta:
        verbose_name = _("Message de contact")
        verbose_name_plural = _("Messages de contact")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["email", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} <{self.email}> - {self.created_at:%d/%m/%Y %H:%M}"

    def ensure_expiry(self, hours: int = 24, save: bool = True) -> None:
        if not self.token_expires_at:
            self.token_expires_at = timezone.now() + timedelta(hours=hours)
            if save:
                self.save(update_fields=["token_expires_at"])

    def is_token_valid(self) -> bool:
        return (
            self.status == self.Status.PENDING
            and self.token_expires_at is not None
            and timezone.now() <= self.token_expires_at
        )

    @property
    def is_verified(self) -> bool:
        return self.status == self.Status.VERIFIED

    def rotate_token(self, hours: int = 24, save: bool = True) -> None:
        self.verify_token = uuid.uuid4()
        self.token_expires_at = timezone.now() + timedelta(hours=hours)
        self.status = self.Status.PENDING
        self.verified_at = None
        self.sent_at = None
        if save:
            self.save(update_fields=["verify_token", "token_expires_at", "status", "verified_at", "sent_at"])







# # core/models.py

# from django.db import models
# from django.utils.translation import gettext_lazy as _

# class ContactMessage(models.Model):
#     name = models.CharField(_("Nom"), max_length=255)
#     email = models.EmailField(_("Adresse email"))
#     message = models.TextField(_("Message"))
#     created_at = models.DateTimeField(_("Envoyé le"), auto_now_add=True)  # Bonne pratique

#     class Meta:
#         verbose_name = _("Message de contact")
#         verbose_name_plural = _("Messages de contact")
#         ordering = ['-created_at']

#     def __str__(self):
#         return f"{self.name} <{self.email}> - {self.created_at:%d/%m/%Y %H:%M}"

# #core/models.py
# from django.db import models
# from django.utils import timezone


# class ContactMessage(models.Model):
#     name = models.CharField(max_length=255)
#     email = models.EmailField()
#     message = models.TextField()
#     created_at = models.DateTimeField(default=timezone.now)

#     def __str__(self):
#         return f"Message from {self.name} <{self.email}>"
