# accounts_users/models/phone_otp.py
import uuid
from django.db import models
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from datetime import timedelta
from phonenumber_field.modelfields import PhoneNumberField


class PhoneOTP(models.Model):
    """
    OTP téléphone – modèle unique combinant les deux versions fournies.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    phone = PhoneNumberField(
        verbose_name="Téléphone",
        region=None,
        db_index=True
    )

    code = models.CharField(
        max_length=6,
        verbose_name="Code OTP"
    )

    is_verified = models.BooleanField(
        default=False,
        verbose_name="Vérifié"
    )

    is_expired = models.BooleanField(
        default=False,
        verbose_name="Expiré"
    )

    attempts = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Tentatives"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Créé le"
    )

    verified_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Vérifié le"
    )

    expires_at = models.DateTimeField(
        verbose_name="Expire le"
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["phone"]),
            models.Index(fields=["phone", "code"]),
        ]

    def __str__(self):
        return f"OTP {self.phone} ({self.code})"

    # =====================================================
    # 🔐 LOGIQUE MÉTIER
    # =====================================================
    def save(self, *args, **kwargs):
        # Si expires_at non défini, définir à 5 minutes après création
        if not self.expires_at:
            self.expires_at = now() + timedelta(minutes=5)
        super().save(*args, **kwargs)

    def is_expired_now(self):
        """Retourne True si le code est expiré ou marqué comme expiré."""
        return self.is_expired or now() >= self.expires_at

    def register_attempt(self):
        """Incrémente le compteur de tentatives et expire si >3 tentatives."""
        self.attempts += 1
        if self.attempts >= 3:
            self.is_expired = True
        self.save(update_fields=["attempts", "is_expired"])

    def verify(self):
        """Marque l'OTP comme vérifié si non expiré, sinon lève ValidationError."""
        if self.is_expired_now():
            raise ValidationError("Code expiré")

        self.is_verified = True
        self.verified_at = now()
        self.save(update_fields=["is_verified", "verified_at"])
