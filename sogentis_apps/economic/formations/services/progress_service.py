# economic/formations/services/progress_service.py
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from economic.formations.models import Enrollment


@dataclass(frozen=True)
class ProgressResult:
    enrollment_id: int
    total_lessons: int
    completed_lessons: int
    percent: Decimal
    changed: bool


def _quantize_percent(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _safe_percent(numerator: int, denominator: int) -> Decimal:
    if denominator <= 0:
        return Decimal("0.00")
    return _quantize_percent((Decimal(numerator) / Decimal(denominator)) * Decimal("100.00"))


def _get_models():
    """
    Import local pour éviter cycles.
    Retourne (Lesson, LessonProgress|None)
    """
    from economic.formations.models import Lesson  # noqa
    try:
        from economic.formations.models import LessonProgress  # noqa
    except Exception:
        LessonProgress = None
    return Lesson, LessonProgress


def _lessons_base_q(course, *, exclude_preview: bool):
    """
    Base queryset des leçons actives d'un cours.
    """
    Lesson, _ = _get_models()
    qs = Lesson.objects.filter(
        module__course=course,
        module__is_active=True,
        is_active=True,
    )
    if exclude_preview and hasattr(Lesson, "is_preview"):
        qs = qs.filter(is_preview=False)
    return qs


def recompute_enrollment_progress(
    enrollment: Enrollment,
    *,
    save: bool = True,
    mark_completed_if_100: bool = True,
    exclude_preview_for_paid_courses: bool = False,
) -> ProgressResult:
    """
    Recalcule Enrollment.progress_percent à partir de LessonProgress.

    - total_lessons = leçons actives (et modules actifs)
    - completed_lessons = LessonProgress completed_at != null OR progress_percent >= 100
      (+ completed=True si le champ existe)
    - percent = completed / total * 100
    - si percent == 100 => optionnellement enrollment.mark_completed()
    """
    course = enrollment.course
    Lesson, LessonProgress = _get_models()

    exclude_preview = bool(exclude_preview_for_paid_courses and (not getattr(course, "is_free", False)))
    lessons_qs = _lessons_base_q(course, exclude_preview=exclude_preview)

    total_lessons = lessons_qs.count()

    completed_lessons = 0
    if LessonProgress:
        # On évite lesson__in=lessons_qs (potentiellement lourd)
        lp_qs = LessonProgress.objects.filter(
            enrollment=enrollment,
            lesson__module__course=course,
            lesson__module__is_active=True,
            lesson__is_active=True,
        )
        if exclude_preview and hasattr(Lesson, "is_preview"):
            lp_qs = lp_qs.filter(lesson__is_preview=False)

        completed_filter = Q(completed_at__isnull=False) | Q(progress_percent__gte=Decimal("100.00"))
        # Si ton LessonProgress a un bool "completed", on l'intègre
        if hasattr(LessonProgress, "completed"):
            completed_filter = completed_filter | Q(completed=True)

        completed_lessons = lp_qs.filter(completed_filter).count()
        if completed_lessons > total_lessons:
            completed_lessons = total_lessons

    percent = _safe_percent(completed_lessons, total_lessons)

    old = enrollment.progress_percent
    if old is None:
        old = Decimal("0.00")
    changed = (Decimal(old) != Decimal(percent))

    if save:
        with transaction.atomic():
            enrollment.progress_percent = percent
            enrollment.last_accessed_at = timezone.now()

            if mark_completed_if_100 and total_lessons > 0 and percent >= Decimal("100.00"):
                enrollment.mark_completed(save=False)

            enrollment.save(update_fields=[
                "progress_percent",
                "last_accessed_at",
                "status",
                "completed",
                "completed_at",
                "updated_at",
            ])

    return ProgressResult(
        enrollment_id=enrollment.pk,
        total_lessons=total_lessons,
        completed_lessons=completed_lessons,
        percent=percent,
        changed=changed,
    )


def recompute_course_progress_for_user(
    *,
    user,
    course,
    save: bool = True,
    mark_completed_if_100: bool = True,
    exclude_preview_for_paid_courses: bool = False,
) -> ProgressResult | None:
    """
    Recalcule la progression pour le dernier enrollment (user+course).
    """
    enrollment = Enrollment.objects.filter(user=user, course=course).order_by("-enrolled_at").first()
    if not enrollment:
        return None
    return recompute_enrollment_progress(
        enrollment,
        save=save,
        mark_completed_if_100=mark_completed_if_100,
        exclude_preview_for_paid_courses=exclude_preview_for_paid_courses,
    )


def bulk_recompute_progress(queryset, *, save: bool = True) -> list[ProgressResult]:
    """
    Recalcule en masse (simple & fiable).
    Optimisation possible ensuite (pré-agrégations), mais ce bloc est safe en prod.
    """
    results: list[ProgressResult] = []
    for e in queryset.select_related("course"):
        results.append(recompute_enrollment_progress(e, save=save))
    return results
