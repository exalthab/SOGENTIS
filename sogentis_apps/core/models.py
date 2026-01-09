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
    sent_at = models.DateTimeField(_("Transmis à l'équipe"), null=True, blank=True)

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

    def save(self, *args, **kwargs):
        if self.status == self.Status.PENDING and (not self.token_expires_at):
            self.token_expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)

    def ensure_expiry(self, hours: int = 24, save: bool = True) -> None:
        now = timezone.now()
        if not self.token_expires_at or self.token_expires_at <= now:
            self.token_expires_at = now + timedelta(hours=hours)
            if save:
                self.save(update_fields=["token_expires_at"])

    def is_token_valid(self) -> bool:
        if self.status != self.Status.PENDING:
            return False
        if not self.token_expires_at:
            return False
        return timezone.now() <= self.token_expires_at

    @property
    def is_verified(self) -> bool:
        return self.status in {self.Status.VERIFIED, self.Status.SENT}

    def rotate_token(self, hours: int = 24, save: bool = True) -> None:
        self.verify_token = uuid.uuid4()
        self.token_expires_at = timezone.now() + timedelta(hours=hours)
        self.status = self.Status.PENDING
        self.verified_at = None
        self.sent_at = None
        if save:
            self.save(
                update_fields=[
                    "verify_token",
                    "token_expires_at",
                    "status",
                    "verified_at",
                    "sent_at",
                ]
            )

    def mark_verified(self, save: bool = True) -> None:
        self.status = self.Status.VERIFIED
        self.verified_at = timezone.now()
        if save:
            self.save(update_fields=["status", "verified_at"])

    def mark_sent(self, save: bool = True) -> None:
        self.status = self.Status.SENT
        self.sent_at = timezone.now()
        if save:
            self.save(update_fields=["status", "sent_at"])

    def mark_rejected(self, save: bool = True) -> None:
        self.status = self.Status.REJECTED
        if save:
            self.save(update_fields=["status"])





# # core/models.py
# from __future__ import annotations

# import uuid
# from datetime import timedelta

# from django.db import models
# from django.utils import timezone
# from django.utils.translation import gettext_lazy as _


# class ContactMessage(models.Model):
#     class Status(models.TextChoices):
#         PENDING = "PENDING", _("En attente de vérification")
#         VERIFIED = "VERIFIED", _("Email vérifié")
#         SENT = "SENT", _("Transmis à l'équipe")
#         REJECTED = "REJECTED", _("Rejeté")

#     name = models.CharField(_("Nom"), max_length=255)
#     email = models.EmailField(_("Adresse email"))
#     message = models.TextField(_("Message"))

#     status = models.CharField(
#         _("Statut"),
#         max_length=20,
#         choices=Status.choices,
#         default=Status.PENDING,
#         db_index=True,
#     )

#     verify_token = models.UUIDField(
#         _("Token de vérification"),
#         default=uuid.uuid4,
#         unique=True,
#         editable=False,
#         db_index=True,
#     )
#     token_expires_at = models.DateTimeField(_("Expiration du token"), null=True, blank=True)

#     verified_at = models.DateTimeField(_("Vérifié le"), null=True, blank=True)
#     sent_at = models.DateTimeField(_("Transmis le"), null=True, blank=True)

#     sender_ip = models.GenericIPAddressField(_("IP expéditeur"), null=True, blank=True)
#     user_agent = models.CharField(_("User agent"), max_length=512, blank=True)

#     created_at = models.DateTimeField(_("Envoyé le"), auto_now_add=True)

#     class Meta:
#         verbose_name = _("Message de contact")
#         verbose_name_plural = _("Messages de contact")
#         ordering = ["-created_at"]
#         indexes = [
#             models.Index(fields=["status", "created_at"]),
#             models.Index(fields=["email", "created_at"]),
#         ]

#     def __str__(self) -> str:
#         return f"{self.name} <{self.email}> - {self.created_at:%d/%m/%Y %H:%M}"

#     # -------------------------------------------------
#     # Métier
#     # -------------------------------------------------

#     def ensure_expiry(self, hours: int = 24, save: bool = True) -> None:
#         """
#         Assure qu’un token a une expiration valide.
#         """
#         now = timezone.now()
#         if not self.token_expires_at or self.token_expires_at <= now:
#             self.token_expires_at = now + timedelta(hours=hours)
#             if save:
#                 self.save(update_fields=["token_expires_at"])

#     def is_token_valid(self) -> bool:
#         """
#         Token valide uniquement si:
#         - message en attente
#         - expiration définie
#         - pas expiré
#         """
#         if self.status != self.Status.PENDING:
#             return False
#         if not self.token_expires_at:
#             return False
#         return timezone.now() <= self.token_expires_at

#     @property
#     def is_verified(self) -> bool:
#         """
#         VERIFIED ou SENT = email vérifié
#         """
#         return self.status in {self.Status.VERIFIED, self.Status.SENT}

#     def rotate_token(self, hours: int = 24, save: bool = True) -> None:
#         """
#         Génère un nouveau token et remet l’état à PENDING.
#         """
#         self.verify_token = uuid.uuid4()
#         self.token_expires_at = timezone.now() + timedelta(hours=hours)
#         self.status = self.Status.PENDING
#         self.verified_at = None
#         self.sent_at = None

#         if save:
#             self.save(
#                 update_fields=[
#                     "verify_token",
#                     "token_expires_at",
#                     "status",
#                     "verified_at",
#                     "sent_at",
#                 ]
#             )


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
