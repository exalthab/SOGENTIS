# economic/formations/models/course_instructor.py
from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from .base import TimeStampedModel
from .course import Course


class CourseInstructor(TimeStampedModel):
    class Role(models.TextChoices):
        LEAD = "lead", _("Principal")
        ASSISTANT = "assistant", _("Assistant")
        GUEST = "guest", _("Invité")

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="course_instructors",
        verbose_name=_("Formation"),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="teaching_courses_links",
        verbose_name=_("Utilisateur"),
    )

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.LEAD, verbose_name=_("Rôle"))
    display_order = models.PositiveIntegerField(default=0, verbose_name=_("Ordre d’affichage"))
    is_active = models.BooleanField(default=True, verbose_name=_("Actif"))

    class Meta:
        verbose_name = _("Formateur")
        verbose_name_plural = _("Formateurs")
        ordering = ["course_id", "display_order", "id"]
        constraints = [
            models.UniqueConstraint(fields=["course", "user"], name="uniq_course_instructor"),
        ]
        indexes = [
            models.Index(fields=["course", "is_active"]),
        ]

    def __str__(self):
        return f"{self.course_id} / {self.user_id} ({self.role})"
