# accounts_users/models/email_otp.py
import uuid
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.timezone import now


class EmailOTP(models.Model):
    """
    OTP Email – modèle pour la vérification des emails.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(db_index=True)
    code = models.CharField(max_length=6, verbose_name="Code OTP")

    is_verified = models.BooleanField(default=False, verbose_name="Vérifié")
    is_expired = models.BooleanField(default=False, verbose_name="Expiré")
    attempts = models.PositiveSmallIntegerField(default=0, verbose_name="Tentatives")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    verified_at = models.DateTimeField(null=True, blank=True, verbose_name="Vérifié le")
    expires_at = models.DateTimeField(verbose_name="Expire le")

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["email", "code"]),
            models.Index(fields=["email", "created_at"]),
        ]

    def __str__(self):
        return f"OTP {self.email} ({self.code})"

    # =====================================================
    # LOGIQUE MÉTIER
    # =====================================================
    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = now() + timedelta(minutes=5)
        super().save(*args, **kwargs)

    def is_expired_now(self) -> bool:
        return bool(self.is_expired) or now() >= self.expires_at

    def register_attempt(self, max_attempts: int = 3):
        self.attempts = int(self.attempts or 0) + 1
        if self.attempts >= max_attempts:
            self.is_expired = True
        self.save(update_fields=["attempts", "is_expired"])

    def verify(self):
        if self.is_expired_now():
            raise ValidationError("Code expiré")
        self.is_verified = True
        self.verified_at = now()
        self.save(update_fields=["is_verified", "verified_at"])







# # models/email_otp.py
# import uuid
# from django.db import models
# from django.utils.timezone import now
# from django.core.exceptions import ValidationError
# from datetime import timedelta


# class EmailOTP(models.Model):
#     """
#     OTP Email – modèle pour la vérification des emails.
#     """

#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     email = models.EmailField(unique=False, db_index=True)
#     code = models.CharField(max_length=6, verbose_name="Code OTP")
#     is_verified = models.BooleanField(default=False, verbose_name="Vérifié")
#     is_expired = models.BooleanField(default=False, verbose_name="Expiré")
#     attempts = models.PositiveSmallIntegerField(default=0, verbose_name="Tentatives")
#     created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
#     verified_at = models.DateTimeField(null=True, blank=True, verbose_name="Vérifié le")
#     expires_at = models.DateTimeField(verbose_name="Expire le")

#     class Meta:
#         ordering = ["-created_at"]
#         indexes = [
#             models.Index(fields=["email"]),
#             models.Index(fields=["email", "code"]),
#         ]

#     def __str__(self):
#         return f"OTP {self.email} ({self.code})"

#     # =====================================================
#     # 🔐 LOGIQUE MÉTIER
#     # =====================================================
#     def save(self, *args, **kwargs):
#         if not self.expires_at:
#             self.expires_at = now() + timedelta(minutes=5)
#         super().save(*args, **kwargs)

#     def is_expired_now(self):
#         return self.is_expired or now() >= self.expires_at

#     def register_attempt(self):
#         self.attempts += 1
#         if self.attempts >= 3:
#             self.is_expired = True
#         self.save(update_fields=["attempts", "is_expired"])

#     def verify(self):
#         if self.is_expired_now():
#             raise ValidationError("Code expiré")
#         self.is_verified = True
#         self.verified_at = now()
#         self.save(update_fields=["is_verified", "verified_at"])
