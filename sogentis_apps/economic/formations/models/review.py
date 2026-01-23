# economic/formations/models/review.py
from __future__ import annotations

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from .base import TimeStampedModel
from .course import Course


class CourseReview(TimeStampedModel):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name=_("Formation"),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="course_reviews",
        verbose_name=_("Utilisateur"),
    )

    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_("Note (1-5)"),
    )
    title = models.CharField(max_length=120, blank=True, verbose_name=_("Titre"))
    comment = models.TextField(blank=True, verbose_name=_("Commentaire"))
    is_public = models.BooleanField(default=True, verbose_name=_("Visible"))

    class Meta:
        verbose_name = _("Avis")
        verbose_name_plural = _("Avis")
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["course", "user"], name="uniq_review_course_user"),
        ]

    def __str__(self):
        return f"{self.course.slug} — {self.rating}/5"
