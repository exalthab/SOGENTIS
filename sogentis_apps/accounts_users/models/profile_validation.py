# accounts_users/models/profile_validation.py
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from accounts_users.models.base import TimeStampedModel
from accounts_users.models.users_profile import UserProfile


class ProfileValidationStatus(models.TextChoices):
    PENDING = "pending", _("En attente")
    APPROVED = "approved", _("Approuvé")
    REFUSED = "refused", _("Refusé")


class ProfileValidation(TimeStampedModel):
    """
    Workflow de validation séparé du profil.
    ✅ Production-safe : ne touche pas aux champs d'identité du UserProfile.
    """

    profile = models.OneToOneField(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="validation",
        verbose_name=_("Profil"),
    )

    status = models.CharField(
        _("Statut"),
        max_length=20,
        choices=ProfileValidationStatus.choices,
        default=ProfileValidationStatus.PENDING,
        db_index=True,
    )

    validated_at = models.DateTimeField(_("Décision le"), null=True, blank=True)

    validated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="profile_validations",
        verbose_name=_("Décision par"),
        limit_choices_to={"is_staff": True},
    )

    note = models.TextField(_("Note"), blank=True)

    class Meta:
        verbose_name = _("Validation de profil")
        verbose_name_plural = _("Validations de profil")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.profile} — {self.status}"

    def approve(self, by_user=None, note=""):
        self.status = ProfileValidationStatus.APPROVED
        self.validated_at = timezone.now()
        self.validated_by = by_user
        self.note = note or ""
        self.save(update_fields=["status", "validated_at", "validated_by", "note", "updated_at"])

    def refuse(self, by_user=None, note=""):
        self.status = ProfileValidationStatus.REFUSED
        self.validated_at = timezone.now()
        self.validated_by = by_user
        self.note = note or ""
        self.save(update_fields=["status", "validated_at", "validated_by", "note", "updated_at"])
