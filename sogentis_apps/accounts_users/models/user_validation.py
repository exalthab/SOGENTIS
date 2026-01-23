# accounts_users/models/user_validation.py
from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from accounts_users.models.base import TimeStampedModel


class UserValidationStatus(models.TextChoices):
    PENDING = "pending", _("En attente")
    APPROVED = "approved", _("Approuvé")
    REFUSED = "refused", _("Refusé")


class UserValidation(TimeStampedModel):
    """
    ✅ Validation globale au niveau USER (zéro doublon).
    - 1 utilisateur = 1 validation
    - couvre social + economic + institution + etc.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="validation",
        verbose_name=_("Utilisateur"),
    )

    status = models.CharField(
        _("Statut"),
        max_length=20,
        choices=UserValidationStatus.choices,
        default=UserValidationStatus.PENDING,
        db_index=True,
    )

    decided_at = models.DateTimeField(_("Décision le"), null=True, blank=True)
    decided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="validations_decided",
        verbose_name=_("Décision par"),
        limit_choices_to={"is_staff": True},
    )

    note = models.TextField(_("Note"), blank=True, default="")

    class Meta:
        verbose_name = _("Validation utilisateur")
        verbose_name_plural = _("Validations utilisateurs")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{getattr(self.user, 'email', self.user_id)} — {self.status}"

    @property
    def is_approved(self) -> bool:
        return self.status == UserValidationStatus.APPROVED

    def approve(self, by_user=None, note: str = "") -> None:
        self.status = UserValidationStatus.APPROVED
        self.decided_at = timezone.now()
        self.decided_by = by_user
        self.note = note or ""
        self.save(update_fields=["status", "decided_at", "decided_by", "note", "updated_at"])

        # Option prod: activer le compte à la validation (si tu veux)
        try:
            if hasattr(self.user, "is_active") and not self.user.is_active:
                self.user.is_active = True
                self.user.save(update_fields=["is_active"])
        except Exception:
            pass

    def refuse(self, by_user=None, note: str = "") -> None:
        self.status = UserValidationStatus.REFUSED
        self.decided_at = timezone.now()
        self.decided_by = by_user
        self.note = note or ""
        self.save(update_fields=["status", "decided_at", "decided_by", "note", "updated_at"])
