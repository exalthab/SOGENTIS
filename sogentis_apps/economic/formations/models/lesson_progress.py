# economic/formations/models/lesson_progress.py
from __future__ import annotations

from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .base import TimeStampedModel
from .enrollment import Enrollment
from .lesson import Lesson


class LessonProgress(TimeStampedModel):
    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name="lesson_progress",
        verbose_name=_("Inscription"),
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="progress_items",
        verbose_name=_("Leçon"),
    )

    started_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Démarré le"))
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Terminé le"))

    last_position_seconds = models.PositiveIntegerField(default=0, verbose_name=_("Dernière position (s)"))
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

    class Meta:
        verbose_name = _("Progression leçon")
        verbose_name_plural = _("Progressions leçon")
        ordering = ["-updated_at"]
        constraints = [
            models.UniqueConstraint(fields=["enrollment", "lesson"], name="uniq_lesson_progress_enrollment_lesson"),
        ]
        indexes = [
            models.Index(fields=["enrollment", "lesson"]),
        ]

    def __str__(self):
        return f"{self.enrollment_id} / {self.lesson_id} ({self.progress_percent}%)"

    def mark_started(self, save: bool = True):
        if not self.started_at:
            self.started_at = timezone.now()
        if save:
            self.save(update_fields=["started_at", "updated_at"])

    def mark_completed(self, save: bool = True):
        self.progress_percent = Decimal("100.00")
        if not self.started_at:
            self.started_at = timezone.now()
        self.completed_at = timezone.now()
        if save:
            self.save(update_fields=["progress_percent", "started_at", "completed_at", "updated_at"])
