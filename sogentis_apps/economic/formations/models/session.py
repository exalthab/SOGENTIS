# economic/formations/models/session.py
from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .base import TimeStampedModel
from .course import Course


class CourseSessionQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)

    def open(self):
        return self.active().filter(status=CourseSession.Status.OPEN)

    def running(self):
        return self.active().filter(status=CourseSession.Status.RUNNING)


class CourseSession(TimeStampedModel):
    """
    Session / Cohorte d'une formation (hybride / présentiel / live).

    - Formation evergreen => Enrollment.session = NULL
    - Formation par cohortes => Enrollment.session = CourseSession
    """

    class Status(models.TextChoices):
        DRAFT = "draft", _("Brouillon")
        OPEN = "open", _("Ouverte")
        CLOSED = "closed", _("Fermée")
        RUNNING = "running", _("En cours")
        ENDED = "ended", _("Terminée")
        CANCELLED = "cancelled", _("Annulée")

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="sessions",
        verbose_name=_("Formation"),
    )

    title = models.CharField(
        max_length=160,
        blank=True,
        verbose_name=_("Titre de session"),
        help_text=_("Ex: Cohorte Janvier 2026"),
    )

    # Fenêtre temporelle (✅ champs réels)
    start_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Début"))
    end_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Fin"))

    seat_limit = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Places max"),
        help_text=_("Vide = illimité."),
    )
    location = models.CharField(max_length=255, blank=True, verbose_name=_("Lieu"))
    meeting_url = models.URLField(blank=True, verbose_name=_("Lien visio"))

    instructors = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="course_sessions_teaching",
        verbose_name=_("Formateurs (session)"),
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name=_("Statut"),
    )
    is_active = models.BooleanField(default=True, verbose_name=_("Actif"))

    enroll_open_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Inscriptions ouvertes le"))
    enroll_close_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Inscriptions fermées le"))

    objects = CourseSessionQuerySet.as_manager()

    class Meta:
        verbose_name = _("Session")
        verbose_name_plural = _("Sessions")
        ordering = ["-start_at", "-created_at"]
        indexes = [
            models.Index(fields=["course", "status"]),
            models.Index(fields=["course", "is_active"]),
            models.Index(fields=["start_at"]),
            models.Index(fields=["end_at"]),
        ]

    def __str__(self):
        base = self.title or (self.course.safe_translation_getter("title", any_language=True) or self.course.slug)
        if self.start_at:
            return f"{base} — {self.start_at:%Y-%m-%d}"
        return base

    # ==========================================================
    # ✅ COMPAT TEMPLATES (tes HTML utilisent starts_at/ends_at)
    # ==========================================================
    @property
    def starts_at(self):
        return self.start_at

    @property
    def ends_at(self):
        return self.end_at

    # ----------------------------
    # Helpers UI / métier
    # ----------------------------
    @property
    def is_running(self) -> bool:
        return self.status == self.Status.RUNNING and self.is_active

    @property
    def is_cancelled(self) -> bool:
        return self.status == self.Status.CANCELLED or not self.is_active

    def is_upcoming(self, now=None) -> bool:
        now = now or timezone.now()
        return bool(self.start_at and self.start_at >= now and not self.is_cancelled)

    def is_past(self, now=None) -> bool:
        now = now or timezone.now()
        return bool(self.end_at and self.end_at < now)

    # ----------------------------
    # Métier
    # ----------------------------
    def is_enrollment_open(self, now=None) -> bool:
        """
        Détermine si on peut s'inscrire à cette session.
        """
        now = now or timezone.now()

        if not self.is_active:
            return False

        # Autorise OPEN (et DRAFT si tu veux prévente)
        if self.status not in (self.Status.OPEN, self.Status.DRAFT):
            return False

        if self.enroll_open_at and now < self.enroll_open_at:
            return False
        if self.enroll_close_at and now > self.enroll_close_at:
            return False

        # Capacité
        if self.seat_limit:
            # related_name="enrollments" sur Enrollment.session
            if self.enrollments.count() >= self.seat_limit:
                return False

        return True

    @property
    def seats_remaining(self):
        """
        None = illimité
        """
        if not self.seat_limit:
            return None
        used = self.enrollments.count()
        return max(self.seat_limit - used, 0)

    def close(self, save: bool = True):
        self.status = self.Status.CLOSED
        if save:
            self.save(update_fields=["status", "updated_at"])

    def start(self, save: bool = True):
        self.status = self.Status.RUNNING
        if save:
            self.save(update_fields=["status", "updated_at"])

    def end(self, save: bool = True):
        self.status = self.Status.ENDED
        if save:
            self.save(update_fields=["status", "updated_at"])






# # economic/formations/models/session.py
# from __future__ import annotations

# from django.conf import settings
# from django.db import models
# from django.utils import timezone
# from django.utils.translation import gettext_lazy as _

# from .base import TimeStampedModel
# from .course import Course


# class CourseSessionQuerySet(models.QuerySet):
#     def active(self):
#         return self.filter(is_active=True)

#     def open(self):
#         return self.active().filter(status=CourseSession.Status.OPEN)

#     def running(self):
#         return self.active().filter(status=CourseSession.Status.RUNNING)


# class CourseSession(TimeStampedModel):
#     """
#     Session / Cohorte d'une formation (hybride / présentiel / live).

#     Objectif:
#     - Une formation peut être "evergreen" (pas de session) => Enrollment.session = NULL
#     - Ou fonctionner par cohortes/sessions => Enrollment.session = CourseSession

#     Exemples:
#     - "Cohorte Janvier 2026"
#     - "Bootcamp Weekend #1"
#     - "Présentiel Dakar - Mars 2026"
#     """

#     class Status(models.TextChoices):
#         DRAFT = "draft", _("Brouillon")
#         OPEN = "open", _("Ouverte")
#         CLOSED = "closed", _("Fermée")
#         RUNNING = "running", _("En cours")
#         ENDED = "ended", _("Terminée")
#         CANCELLED = "cancelled", _("Annulée")

#     course = models.ForeignKey(
#         Course,
#         on_delete=models.CASCADE,
#         related_name="sessions",
#         verbose_name=_("Formation"),
#     )

#     title = models.CharField(
#         max_length=160,
#         blank=True,
#         verbose_name=_("Titre de session"),
#         help_text=_("Ex: Cohorte Janvier 2026"),
#     )

#     # Fenêtre temporelle
#     start_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Début"))
#     end_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Fin"))

#     # Capacité & logistique
#     seat_limit = models.PositiveIntegerField(
#         null=True,
#         blank=True,
#         verbose_name=_("Places max"),
#         help_text=_("Vide = illimité."),
#     )
#     location = models.CharField(max_length=255, blank=True, verbose_name=_("Lieu"))
#     meeting_url = models.URLField(blank=True, verbose_name=_("Lien visio"))

#     # Instructeurs propres à la session (optionnel)
#     instructors = models.ManyToManyField(
#         settings.AUTH_USER_MODEL,
#         blank=True,
#         related_name="course_sessions_teaching",
#         verbose_name=_("Formateurs (session)"),
#     )

#     status = models.CharField(
#         max_length=20,
#         choices=Status.choices,
#         default=Status.DRAFT,
#         verbose_name=_("Statut"),
#     )
#     is_active = models.BooleanField(default=True, verbose_name=_("Actif"))

#     enroll_open_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Inscriptions ouvertes le"))
#     enroll_close_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Inscriptions fermées le"))

#     objects = CourseSessionQuerySet.as_manager()

#     class Meta:
#         verbose_name = _("Session")
#         verbose_name_plural = _("Sessions")
#         ordering = ["-start_at", "-created_at"]
#         indexes = [
#             models.Index(fields=["course", "status"]),
#             models.Index(fields=["course", "is_active"]),
#             models.Index(fields=["start_at"]),
#             models.Index(fields=["end_at"]),
#         ]

#     def __str__(self):
#         base = self.title or (self.course.safe_translation_getter("title", any_language=True) or self.course.slug)
#         if self.start_at:
#             return f"{base} — {self.start_at:%Y-%m-%d}"
#         return base

#     # ----------------------------
#     # Métier
#     # ----------------------------
#     def is_enrollment_open(self, now=None) -> bool:
#         """
#         Détermine si on peut s'inscrire à cette session.
#         """
#         now = now or timezone.now()

#         if not self.is_active:
#             return False

#         if self.status not in (self.Status.OPEN, self.Status.DRAFT):
#             # OPEN = ouvert, DRAFT = parfois tu veux autoriser en prévente via logique custom
#             return False

#         if self.enroll_open_at and now < self.enroll_open_at:
#             return False
#         if self.enroll_close_at and now > self.enroll_close_at:
#             return False

#         if self.seat_limit:
#             # Lien avec Enrollment via related_name="enrollments"
#             if self.enrollments.count() >= self.seat_limit:
#                 return False

#         return True

#     @property
#     def seats_remaining(self):
#         """
#         None = illimité
#         """
#         if not self.seat_limit:
#             return None
#         used = self.enrollments.count()
#         return max(self.seat_limit - used, 0)

#     def close(self, save: bool = True):
#         self.status = self.Status.CLOSED
#         if save:
#             self.save(update_fields=["status", "updated_at"])

#     def start(self, save: bool = True):
#         self.status = self.Status.RUNNING
#         if save:
#             self.save(update_fields=["status", "updated_at"])

#     def end(self, save: bool = True):
#         self.status = self.Status.ENDED
#         if save:
#             self.save(update_fields=["status", "updated_at"])






# # economic/formations/models/session.py
# from django.db import models
# from django.utils.translation import gettext_lazy as _

# from .base import TimeStampedModel
# from .course import Course


# class CourseSession(TimeStampedModel, models.Model):
#     """
#     Session planifiée d’une formation (présentiel ou distanciel).
#     """

#     course = models.ForeignKey(
#         Course,
#         on_delete=models.CASCADE,
#         related_name="sessions",
#         verbose_name=_("Formation"),
#     )

#     title = models.CharField(
#         max_length=160,
#         blank=True,
#         verbose_name=_("Titre (optionnel)"),
#         help_text=_("Ex : Groupe A, Session janvier, etc."),
#     )

#     starts_at = models.DateTimeField(verbose_name=_("Début"))
#     ends_at = models.DateTimeField(verbose_name=_("Fin"))

#     location = models.CharField(
#         max_length=200,
#         blank=True,
#         verbose_name=_("Lieu"),
#     )
#     meeting_url = models.URLField(
#         blank=True,
#         verbose_name=_("Lien visio"),
#     )

#     capacity = models.PositiveIntegerField(
#         default=0,
#         verbose_name=_("Capacité"),
#         help_text=_("0 = illimité"),
#     )

#     is_cancelled = models.BooleanField(
#         default=False,
#         verbose_name=_("Annulée"),
#     )

#     class Meta:
#         verbose_name = _("Session")
#         verbose_name_plural = _("Sessions")
#         ordering = ["starts_at"]

#     def __str__(self):
#         base = self.title or str(self.course)
#         return f"{base} — {self.starts_at:%Y-%m-%d %H:%M}"





# # # economic/formations/models/session.py
# # from django.db import models
# # from django.utils.translation import gettext_lazy as _

# # from .base import TimeStampedModel
# # from .course import Course


# # class CourseSession(TimeStampedModel, models.Model):
# #     course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="sessions", verbose_name=_("Formation"))
# #     starts_at = models.DateTimeField(verbose_name=_("Début"))
# #     ends_at = models.DateTimeField(verbose_name=_("Fin"))
# #     location = models.CharField(max_length=200, blank=True, verbose_name=_("Lieu"))
# #     meeting_url = models.URLField(blank=True, verbose_name=_("Lien visio"))
# #     capacity = models.PositiveIntegerField(default=0, verbose_name=_("Capacité"), help_text=_("0 = illimité"))
# #     is_cancelled = models.BooleanField(default=False, verbose_name=_("Annulée"))

# #     class Meta:
# #         verbose_name = _("Session")
# #         verbose_name_plural = _("Sessions")
# #         ordering = ["starts_at"]

# #     def __str__(self):
# #         return f"{self.course} — {self.starts_at:%Y-%m-%d %H:%M}"
