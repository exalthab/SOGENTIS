# economic/formations/models/certificate.py
from __future__ import annotations

import secrets
import uuid

from django.db import models, transaction, IntegrityError
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from .base import TimeStampedModel
from .course import Course
from .enrollment import Enrollment


class Certificate(TimeStampedModel):
    """
    Certificat délivré à l’issue d’une formation complétée.
    - 1 certificat par inscription
    - code lisible + uuid
    - PDF attachable
    """

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    enrollment = models.OneToOneField(
        Enrollment,
        on_delete=models.CASCADE,
        related_name="certificate",
        verbose_name=_("Inscription"),
    )

    # Conservé pour compat/perf (synchronisé automatiquement)
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="certificates",
        verbose_name=_("Formation"),
        editable=False,
    )

    # Cohorte (optionnel)
    session = models.ForeignKey(
        "formations.CourseSession",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="certificates",
        verbose_name=_("Session"),
        editable=False,
    )

    code = models.CharField(
        max_length=40,
        unique=True,
        db_index=True,
        blank=True,
        verbose_name=_("Code"),
    )

    issued_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Délivré le"))

    pdf_file = models.FileField(
        upload_to="formations/certificates/%Y/%m/",
        blank=True,
        null=True,
        verbose_name=_("PDF"),
    )

    revoked = models.BooleanField(default=False, verbose_name=_("Révoqué"))
    revoked_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Révoqué le"))
    revoke_reason = models.CharField(max_length=255, blank=True, verbose_name=_("Motif"))

    class Meta:
        verbose_name = _("Certificat")
        verbose_name_plural = _("Certificats")
        ordering = ["-issued_at"]
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["revoked"]),
        ]

    def __str__(self) -> str:
        return f"{self.code or self.uuid} — {self.course}"

    # --------------------
    # Métier
    # --------------------
    @staticmethod
    def _generate_code() -> str:
        # 8 hex chars => 32 bits : collisions très faibles, uppercase lisible
        token = secrets.token_hex(4).upper()
        return f"CERT-{token}"

    def _sync_from_enrollment(self) -> None:
        if not self.enrollment_id:
            return
        # évite des writes inutiles
        if self.course_id != self.enrollment.course_id:
            self.course_id = self.enrollment.course_id
        if getattr(self, "session_id", None) != getattr(self.enrollment, "session_id", None):
            self.session_id = getattr(self.enrollment, "session_id", None)

    def save(self, *args, **kwargs):
        """
        - Synchronise automatiquement la formation (+ session) depuis l’inscription
        - Génère un code unique lisible si absent (robuste en concurrence)
        """
        self._sync_from_enrollment()

        # Si code déjà présent, on sauvegarde normalement
        if self.code:
            return super().save(*args, **kwargs)

        # Génération robuste : on tente plusieurs insertions avec codes différents
        # (utile si 2 saves concurrents tombent sur une collision)
        max_attempts = 8
        last_exc: Exception | None = None

        for _ in range(max_attempts):
            self.code = self._generate_code()
            try:
                with transaction.atomic():
                    return super().save(*args, **kwargs)
            except IntegrityError as exc:
                # collision sur "code" unique
                last_exc = exc
                self.code = ""

        # Si on arrive ici : trop de collisions (anormal)
        raise IntegrityError("Unable to generate unique certificate code") from last_exc

    def revoke(self, reason: str = "", save: bool = True):
        self.revoked = True
        self.revoked_at = timezone.now()
        self.revoke_reason = reason or self.revoke_reason
        if save:
            self.save(update_fields=["revoked", "revoked_at", "revoke_reason", "updated_at"])

    def download_filename(self) -> str:
        # slug propre + longueur maîtrisée
        raw = ""
        if self.course_id and getattr(self.course, "slug", None):
            raw = self.course.slug
        elif self.course_id:
            raw = str(self.course_id)
        else:
            raw = "course"

        safe_slug = slugify(raw)[:48] or "course"
        ident = (self.code or str(self.uuid))[:40]
        return f"certificate-{safe_slug}-{ident}.pdf"





# # economic/formations/models/certificate.py
# from __future__ import annotations

# import secrets
# import uuid

# from django.db import models
# from django.utils import timezone
# from django.utils.translation import gettext_lazy as _

# from .base import TimeStampedModel
# from .course import Course
# from .enrollment import Enrollment


# class Certificate(TimeStampedModel):
#     """
#     Certificat délivré à l’issue d’une formation complétée.
#     - 1 certificat par inscription
#     - code lisible + uuid
#     - PDF attachable
#     """

#     uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

#     enrollment = models.OneToOneField(
#         Enrollment,
#         on_delete=models.CASCADE,
#         related_name="certificate",
#         verbose_name=_("Inscription"),
#     )

#     # conservé pour compat / performance (synchronisé automatiquement)
#     course = models.ForeignKey(
#         Course,
#         on_delete=models.CASCADE,
#         related_name="certificates",
#         verbose_name=_("Formation"),
#         editable=False,
#     )

#     # cohorte (optionnel)
#     session = models.ForeignKey(
#         "formations.CourseSession",
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name="certificates",
#         verbose_name=_("Session"),
#         editable=False,
#     )

#     code = models.CharField(
#         max_length=40,
#         unique=True,
#         db_index=True,
#         blank=True,
#         verbose_name=_("Code"),
#     )

#     issued_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Délivré le"))

#     pdf_file = models.FileField(
#         upload_to="formations/certificates/%Y/%m/",
#         blank=True,
#         null=True,
#         verbose_name=_("PDF"),
#     )

#     revoked = models.BooleanField(default=False, verbose_name=_("Révoqué"))
#     revoked_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Révoqué le"))
#     revoke_reason = models.CharField(max_length=255, blank=True, verbose_name=_("Motif"))

#     class Meta:
#         verbose_name = _("Certificat")
#         verbose_name_plural = _("Certificats")
#         ordering = ["-issued_at"]
#         indexes = [
#             models.Index(fields=["code"]),
#             models.Index(fields=["revoked"]),
#         ]

#     def __str__(self):
#         return f"{self.code or self.uuid} — {self.course}"

#     # ---------- Métier ----------

#     def save(self, *args, **kwargs):
#         """
#         - Synchronise automatiquement la formation (+ session) depuis l’inscription
#         - Génère un code unique lisible si absent
#         """
#         if self.enrollment_id:
#             self.course_id = self.enrollment.course_id
#             self.session_id = self.enrollment.session_id

#         if not self.code:
#             token = secrets.token_hex(4).upper()
#             base = f"CERT-{token}"
#             self.code = base

#             i = 2
#             while Certificate.objects.filter(code=self.code).exclude(pk=self.pk).exists():
#                 self.code = f"{base}-{i}"
#                 i += 1

#         super().save(*args, **kwargs)

#     def revoke(self, reason: str = "", save: bool = True):
#         self.revoked = True
#         self.revoked_at = timezone.now()
#         self.revoke_reason = reason or self.revoke_reason
#         if save:
#             self.save(update_fields=["revoked", "revoked_at", "revoke_reason", "updated_at"])

#     def download_filename(self) -> str:
#         slug = self.course.slug if self.course_id else "course"
#         return f"certificate-{slug}-{self.code or self.uuid}.pdf"





# # economic/formations/models/certificate.py
# import uuid
# import secrets
# from django.db import models
# from django.utils.translation import gettext_lazy as _

# from .base import TimeStampedModel
# from .course import Course
# from .enrollment import Enrollment


# class Certificate(TimeStampedModel, models.Model):
#     """
#     Certificat délivré à l’issue d’une formation complétée.
#     """

#     uuid = models.UUIDField(
#         default=uuid.uuid4,
#         editable=False,
#         unique=True,
#     )

#     enrollment = models.OneToOneField(
#         Enrollment,
#         on_delete=models.CASCADE,
#         related_name="certificate",
#         verbose_name=_("Inscription"),
#     )

#     # conservé pour compat / performance (synchronisé automatiquement)
#     course = models.ForeignKey(
#         Course,
#         on_delete=models.CASCADE,
#         verbose_name=_("Formation"),
#         editable=False,
#     )

#     code = models.CharField(
#         max_length=40,
#         unique=True,
#         db_index=True,
#         blank=True,
#         verbose_name=_("Code"),
#     )

#     issued_at = models.DateTimeField(auto_now_add=True)

#     pdf_file = models.FileField(
#         upload_to="formations/certificates/%Y/%m/",
#         blank=True,
#         null=True,
#         verbose_name=_("PDF"),
#     )

#     revoked = models.BooleanField(
#         default=False,
#         verbose_name=_("Révoqué"),
#     )

#     class Meta:
#         verbose_name = _("Certificat")
#         verbose_name_plural = _("Certificats")
#         ordering = ["-issued_at"]

#     def __str__(self):
#         return f"{self.code or self.uuid} — {self.course}"

#     # ---------- Métier ----------

#     def save(self, *args, **kwargs):
#         """
#         - Synchronise automatiquement la formation depuis l’inscription
#         - Génère un code unique lisible si absent
#         """
#         if self.enrollment_id:
#             self.course = self.enrollment.course

#         if not self.code:
#             token = secrets.token_hex(4).upper()
#             base = f"CERT-{token}"
#             self.code = base

#             i = 2
#             while Certificate.objects.filter(code=self.code).exclude(pk=self.pk).exists():
#                 self.code = f"{base}-{i}"
#                 i += 1

#         super().save(*args, **kwargs)

#     def download_filename(self) -> str:
#         slug = self.course.slug if self.course_id else "course"
#         return f"certificate-{slug}-{self.code or self.uuid}.pdf"





# # economic/formations/models/certificate.py
# import uuid
# import secrets
# from django.db import models
# from django.utils.translation import gettext_lazy as _

# from .base import TimeStampedModel
# from .course import Course
# from .enrollment import Enrollment


# class Certificate(TimeStampedModel, models.Model):
#     # ✅ on garde ton uuid existant (compatible)
#     uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

#     enrollment = models.OneToOneField(
#         Enrollment,
#         on_delete=models.CASCADE,
#         related_name="certificate",
#     )

#     # ✅ on garde course pour compat (mais on le synchronise automatiquement)
#     course = models.ForeignKey(
#         Course,
#         on_delete=models.CASCADE,
#         verbose_name=_("Formation"),
#         editable=False,
#     )

#     code = models.CharField(max_length=40, unique=True, db_index=True, blank=True)
#     issued_at = models.DateTimeField(auto_now_add=True)

#     pdf_file = models.FileField(upload_to="formations/certificates/", blank=True, null=True)
#     revoked = models.BooleanField(default=False)

#     class Meta:
#         verbose_name = _("Certificat")
#         verbose_name_plural = _("Certificats")
#         ordering = ["-issued_at"]

#     def __str__(self):
#         return f"Certificat {self.course} ({self.code})"

#     def save(self, *args, **kwargs):
#         # force course = enrollment.course
#         if self.enrollment_id:
#             self.course = self.enrollment.course

#         # génère un code si vide
#         if not self.code:
#             # ex: CERT-8F3A2C1D
#             token = secrets.token_hex(4).upper()
#             self.code = f"CERT-{token}"
#             i = 2
#             base = self.code
#             while Certificate.objects.filter(code=self.code).exclude(pk=self.pk).exists():
#                 self.code = f"{base}-{i}"
#                 i += 1

#         super().save(*args, **kwargs)

#     def download_filename(self) -> str:
#         return f"certificate-{self.course.slug}-{self.code}.pdf"







# import uuid
# from django.db import models
# from django.utils.translation import gettext_lazy as _

# from .course import Course
# from .enrollment import Enrollment


# class Certificate(models.Model):
#     uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

#     enrollment = models.OneToOneField(
#         Enrollment,
#         on_delete=models.CASCADE,
#         related_name="certificate",
#     )

#     course = models.ForeignKey(
#         Course,
#         on_delete=models.CASCADE,
#         verbose_name=_("Formation"),
#     )

#     issued_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         verbose_name = _("Certificat")
#         verbose_name_plural = _("Certificats")

#     def __str__(self):
#         return f"Certificat {self.course}"
