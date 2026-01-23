# economic/formations/models/enrollment.py
from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .base import TimeStampedModel
from .course import Course


class EnrollmentQuerySet(models.QuerySet):
    def active(self):
        return self.filter(status=Enrollment.Status.ACTIVE)

    def completed(self):
        return self.filter(status=Enrollment.Status.COMPLETED)

    def for_user(self, user):
        return self.filter(user=user)


class Enrollment(TimeStampedModel, models.Model):
    """
    Inscription d’un utilisateur à une formation.
    - Compatible legacy: `paid`, `completed`
    - Hybride: peut pointer vers une session (cohorte) si elle existe.
    - Progression: stocke un % global (fine-grain via LessonProgress si tu l'utilises).
    """

    class Status(models.TextChoices):
        PENDING = "PENDING", _("En attente")
        ACTIVE = "ACTIVE", _("Actif")
        COMPLETED = "COMPLETED", _("Terminé")
        CANCELLED = "CANCELLED", _("Annulé")

    class PaymentProvider(models.TextChoices):
        NONE = "NONE", _("Aucun")
        STRIPE = "STRIPE", _("Stripe")
        PAYPAL = "PAYPAL", _("PayPal")
        WAVE = "WAVE", _("Wave")
        ORANGE = "ORANGE_MONEY", _("Orange Money")
        VISA = "VISA", _("Carte (Visa/Mastercard)")
        MANUAL = "MANUAL", _("Manuel")

    class PaymentStatus(models.TextChoices):
        UNPAID = "UNPAID", _("Non payé")
        PAID = "PAID", _("Payé")
        FAILED = "FAILED", _("Échoué")
        REFUNDED = "REFUNDED", _("Remboursé")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="formations_enrollments",
        verbose_name=_("Utilisateur"),
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="enrollments",
        verbose_name=_("Formation"),
    )

    # ✅ Hybride / cohorte (nullable = compatible)
    session = models.ForeignKey(
        "formations.CourseSession",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="enrollments",
        verbose_name=_("Session"),
    )

    enrolled_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Inscrit le"))

    # ⚠️ Champ legacy (à terme déprécié)
    completed = models.BooleanField(default=False, verbose_name=_("Terminé (legacy)"))

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        verbose_name=_("Statut"),
    )

    # paiement (compatible `paid`)
    paid = models.BooleanField(default=False, verbose_name=_("Payé (legacy)"))
    payment_provider = models.CharField(
        max_length=20,
        choices=PaymentProvider.choices,
        default=PaymentProvider.NONE,
        verbose_name=_("Moyen de paiement"),
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.UNPAID,
        verbose_name=_("Statut paiement"),
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Montant"),
    )
    currency = models.CharField(max_length=3, default="XOF", verbose_name=_("Devise"))
    payment_reference = models.CharField(max_length=120, blank=True, verbose_name=_("Référence paiement"))
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Payé le"))

    progress_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[
            MinValueValidator(Decimal("0.00")),
            MaxValueValidator(Decimal("100.00")),
        ],
        verbose_name=_("Progression (%)"),
    )

    completed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Terminé le"))
    last_accessed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Dernier accès"))

    objects = EnrollmentQuerySet.as_manager()

    class Meta:
        verbose_name = _("Inscription")
        verbose_name_plural = _("Inscriptions")
        ordering = ["-enrolled_at"]
        constraints = [
            # Un seul enrollment par user/course/session (session nullable)
            models.UniqueConstraint(fields=["user", "course", "session"], name="uniq_enrollment_user_course_session"),
        ]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["course", "status"]),
            models.Index(fields=["course", "session", "status"]),
            models.Index(fields=["payment_status"]),
        ]

    def __str__(self):
        if self.session_id:
            return f"{self.user} → {self.course} ({self.session_id})"
        return f"{self.user} → {self.course}"

    # ---------- Métier ----------

    def sync_compat_fields(self):
        """
        Maintient la cohérence:
        - legacy `completed` <-> `status`
        - legacy `paid` <-> `payment_status`
        """
        # completed legacy -> status canonique
        if self.completed and self.status != self.Status.COMPLETED:
            self.status = self.Status.COMPLETED

        if self.status == self.Status.COMPLETED:
            if not self.completed:
                self.completed = True
            if not self.completed_at:
                self.completed_at = timezone.now()

        # paid legacy -> payment_status canonique
        if self.paid and self.payment_status != self.PaymentStatus.PAID:
            self.payment_status = self.PaymentStatus.PAID
            if not self.paid_at:
                self.paid_at = timezone.now()

        if self.payment_status == self.PaymentStatus.PAID and not self.paid:
            self.paid = True

    def mark_paid(self, provider: str = PaymentProvider.MANUAL, reference: str = "", save: bool = True):
        self.payment_provider = provider
        self.payment_status = self.PaymentStatus.PAID
        self.paid = True
        self.paid_at = self.paid_at or timezone.now()
        if reference:
            self.payment_reference = reference
        if save:
            self.save(update_fields=[
                "payment_provider",
                "payment_status",
                "paid",
                "paid_at",
                "payment_reference",
                "updated_at",
            ])

    def mark_completed(self, save: bool = True):
        self.status = self.Status.COMPLETED
        self.sync_compat_fields()
        if save:
            self.save(update_fields=["status", "completed", "completed_at", "updated_at"])

    def can_access_content(self) -> bool:
        """
        Règle simple:
        - si cours gratuit => OK
        - si payant => paiement PAID
        """
        if self.course.is_free:
            return True
        return self.payment_status == self.PaymentStatus.PAID

    def save(self, *args, **kwargs):
        self.sync_compat_fields()
        super().save(*args, **kwargs)





# # economic/formations/models/enrollment.py
# from django.conf import settings
# from django.db import models
# from django.utils import timezone
# from django.utils.translation import gettext_lazy as _

# from .base import TimeStampedModel
# from .course import Course


# class Enrollment(TimeStampedModel, models.Model):
#     """
#     Inscription d’un utilisateur à une formation.
#     Gère l’état, la progression et la compatibilité legacy.
#     """

#     class Status(models.TextChoices):
#         PENDING = "PENDING", _("En attente")
#         ACTIVE = "ACTIVE", _("Actif")
#         COMPLETED = "COMPLETED", _("Terminé")
#         CANCELLED = "CANCELLED", _("Annulé")

#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name="formations_enrollments",
#     )

#     course = models.ForeignKey(
#         Course,
#         on_delete=models.CASCADE,
#         related_name="enrollments",
#     )

#     enrolled_at = models.DateTimeField(auto_now_add=True)

#     # ⚠️ Champ legacy (à terme déprécié)
#     completed = models.BooleanField(default=False)

#     # Champs métier
#     status = models.CharField(
#         max_length=20,
#         choices=Status.choices,
#         default=Status.ACTIVE,
#     )
#     paid = models.BooleanField(
#         default=False,
#         verbose_name=_("Payé"),
#     )
#     progress_percent = models.PositiveIntegerField(
#         default=0,
#         verbose_name=_("Progression (%)"),
#     )
#     completed_at = models.DateTimeField(
#         null=True,
#         blank=True,
#     )

#     class Meta:
#         verbose_name = _("Inscription")
#         verbose_name_plural = _("Inscriptions")
#         unique_together = ("user", "course")
#         ordering = ["-enrolled_at"]

#     def __str__(self):
#         return f"{self.user} → {self.course}"

#     # ---------- Métier ----------

#     def sync_compat_fields(self):
#         """
#         Maintient la cohérence entre le champ legacy `completed`
#         et le champ canonique `status`.
#         """
#         if self.completed and self.status != self.Status.COMPLETED:
#             self.status = self.Status.COMPLETED

#         if self.status == self.Status.COMPLETED:
#             if not self.completed:
#                 self.completed = True
#             if not self.completed_at:
#                 self.completed_at = timezone.now()

#     def mark_completed(self, save: bool = True):
#         """
#         Marque l’inscription comme terminée (API métier).
#         """
#         self.status = self.Status.COMPLETED
#         self.sync_compat_fields()
#         if save:
#             self.save(update_fields=["status", "completed", "completed_at", "updated_at"])

#     def save(self, *args, **kwargs):
#         self.sync_compat_fields()
#         super().save(*args, **kwargs)






# # economic/formations/models/enrollment.py
# from django.conf import settings
# from django.db import models
# from django.utils import timezone
# from django.utils.translation import gettext_lazy as _

# from .base import TimeStampedModel
# from .course import Course


# class Enrollment(TimeStampedModel, models.Model):
#     class Status(models.TextChoices):
#         PENDING = "PENDING", _("En attente")
#         ACTIVE = "ACTIVE", _("Actif")
#         COMPLETED = "COMPLETED", _("Terminé")
#         CANCELLED = "CANCELLED", _("Annulé")

#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name="formations_enrollments",
#     )

#     course = models.ForeignKey(
#         Course,
#         on_delete=models.CASCADE,
#         related_name="enrollments",
#     )

#     enrolled_at = models.DateTimeField(auto_now_add=True)

#     # ✅ compat ancienne version
#     completed = models.BooleanField(default=False)

#     # ✅ prod
#     status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
#     paid = models.BooleanField(default=False, verbose_name=_("Payé"))
#     progress_percent = models.PositiveIntegerField(default=0, verbose_name=_("Progression (%)"))
#     completed_at = models.DateTimeField(null=True, blank=True)

#     class Meta:
#         verbose_name = _("Inscription")
#         verbose_name_plural = _("Inscriptions")
#         unique_together = ("user", "course")
#         ordering = ["-enrolled_at"]

#     def __str__(self):
#         return f"{self.user} → {self.course}"

#     def sync_compat_fields(self):
#         # garde cohérence completed <-> status
#         if self.completed and self.status != self.Status.COMPLETED:
#             self.status = self.Status.COMPLETED
#         if self.status == self.Status.COMPLETED and not self.completed:
#             self.completed = True
#         if self.status == self.Status.COMPLETED and not self.completed_at:
#             self.completed_at = timezone.now()

#     def save(self, *args, **kwargs):
#         self.sync_compat_fields()
#         super().save(*args, **kwargs)







# from django.conf import settings
# from django.db import models
# from django.utils.translation import gettext_lazy as _

# from .course import Course


# class Enrollment(models.Model):
#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name="enrollments",
#     )

#     course = models.ForeignKey(
#         Course,
#         on_delete=models.CASCADE,
#         related_name="enrollments",
#     )

#     enrolled_at = models.DateTimeField(auto_now_add=True)
#     completed = models.BooleanField(default=False)

#     class Meta:
#         verbose_name = _("Inscription")
#         verbose_name_plural = _("Inscriptions")
#         unique_together = ("user", "course")

#     def __str__(self):
#         return f"{self.user} → {self.course}"
