# economic/formations/services/enrollment_service.py
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from economic.formations.models import Enrollment, Course


@dataclass(frozen=True)
class EnrollmentCreateResult:
    enrollment: Enrollment
    created: bool


class EnrollmentError(Exception):
    pass


class EnrollmentNotAllowed(EnrollmentError):
    pass


class SessionFull(EnrollmentNotAllowed):
    pass


class SessionClosed(EnrollmentNotAllowed):
    pass


def _resolve_session(course: Course, session=None):
    """
    Vérifie la cohérence course/session.
    - session peut être None (evergreen)
    - session.course doit correspondre
    """
    if session is None:
        return None

    # Import local pour éviter cycle
    from economic.formations.models import CourseSession

    if not isinstance(session, CourseSession):
        # autorise un id
        session = CourseSession.objects.select_related("course").filter(pk=session).first()
        if not session:
            raise EnrollmentNotAllowed(_("Session introuvable."))

    if session.course_id != course.id:
        raise EnrollmentNotAllowed(_("La session ne correspond pas à la formation."))

    return session


def _ensure_can_enroll(user, course: Course, session=None):
    """
    Règles d'inscription (prod):
    - course actif
    - si session: doit être active + ouverte + pas full
    """
    if not course.is_active:
        raise EnrollmentNotAllowed(_("Formation inactive."))

    if session is not None:
        # Méthode is_enrollment_open() existe dans ton CourseSession
        if hasattr(session, "is_enrollment_open") and callable(session.is_enrollment_open):
            if not session.is_enrollment_open():
                raise SessionClosed(_("Les inscriptions à cette session sont fermées."))
        else:
            # fallback minimal
            if not getattr(session, "is_active", True):
                raise SessionClosed(_("Session inactive."))
            if getattr(session, "status", "") not in ("open", "draft"):
                raise SessionClosed(_("Les inscriptions à cette session sont fermées."))

        seat_limit = getattr(session, "seat_limit", None)
        if seat_limit:
            used = session.enrollments.count()
            if used >= seat_limit:
                raise SessionFull(_("Cette session est complète."))


def _default_amount_for_course(course: Course) -> Decimal | None:
    try:
        if course.price is None:
            return None
        return Decimal(course.price)
    except Exception:
        return None


@transaction.atomic
def enroll_user(
    *,
    user,
    course: Course | int,
    session=None,
    status: str | None = None,
    auto_mark_paid_if_free: bool = True,
) -> EnrollmentCreateResult:
    """
    Inscrit un user à une formation (+ session optionnelle).
    - si course est id => fetch
    - si déjà inscrit => retourne l'existant
    - set amount/currency par défaut
    - si gratuit => peut auto-mark paid=True (legacy + payment_status=PAID) pour simplifier l'accès
    """
    if not isinstance(course, Course):
        course = Course.objects.select_related("category").get(pk=course)

    session = _resolve_session(course, session)
    _ensure_can_enroll(user, course, session=session)

    # NOTE: unique constraint sur (user, course, session)
    enrollment, created = Enrollment.objects.select_for_update().get_or_create(
        user=user,
        course=course,
        session=session,
        defaults={
            "status": status or Enrollment.Status.ACTIVE,
            "amount": _default_amount_for_course(course),
            "currency": getattr(course, "currency", "XOF") or "XOF",
            "payment_status": Enrollment.PaymentStatus.UNPAID,
            "payment_provider": Enrollment.PaymentProvider.NONE,
        },
    )

    # Harmonisation: si existant mais amount vide -> sync
    if enrollment.amount is None:
        enrollment.amount = _default_amount_for_course(course)
    if not enrollment.currency:
        enrollment.currency = getattr(course, "currency", "XOF") or "XOF"

    # Gratuit => accès direct (optionnel)
    if auto_mark_paid_if_free and course.is_free:
        enrollment.payment_provider = Enrollment.PaymentProvider.NONE
        enrollment.payment_status = Enrollment.PaymentStatus.PAID
        enrollment.paid = True
        enrollment.paid_at = enrollment.paid_at or timezone.now()

    enrollment.last_accessed_at = timezone.now()
    enrollment.save()

    return EnrollmentCreateResult(enrollment=enrollment, created=created)


@transaction.atomic
def mark_enrollment_paid(
    enrollment: Enrollment,
    *,
    provider: str = Enrollment.PaymentProvider.MANUAL,
    reference: str = "",
    amount: Decimal | None = None,
    currency: str | None = None,
    save: bool = True,
) -> Enrollment:
    """
    Marque payé via logique métier Enrollment.mark_paid + sync montant.
    """
    if amount is not None:
        enrollment.amount = amount
    if currency:
        enrollment.currency = currency

    enrollment.mark_paid(provider=provider, reference=reference, save=False)

    if save:
        enrollment.save(update_fields=[
            "amount",
            "currency",
            "payment_provider",
            "payment_status",
            "paid",
            "paid_at",
            "payment_reference",
            "updated_at",
        ])
    return enrollment


@transaction.atomic
def touch_access(enrollment: Enrollment, *, save: bool = True) -> Enrollment:
    """
    Met à jour last_accessed_at (ex: ouverture lecteur).
    """
    enrollment.last_accessed_at = timezone.now()
    if save:
        enrollment.save(update_fields=["last_accessed_at", "updated_at"])
    return enrollment


@transaction.atomic
def complete_enrollment(
    enrollment: Enrollment,
    *,
    issue_certificate: bool = False,
    generate_pdf: bool = True,
    send_email: bool = True,
) -> Enrollment:
    """
    Marque COMPLETED (status + legacy) et, optionnellement, émet le certificat.
    """
    enrollment.mark_completed(save=True)

    if issue_certificate:
        try:
            from economic.formations.services.certificate_service import issue_certificate_for_enrollment
            # on_commit pour éviter certificat en cas rollback
            transaction.on_commit(lambda: issue_certificate_for_enrollment(
                enrollment, generate_pdf=generate_pdf, send_email=send_email
            ))
        except Exception:
            # ne casse pas la complétion si service absent
            pass

    return enrollment


def can_user_access_lesson(enrollment: Enrollment, lesson) -> bool:
    """
    Règle d'accès simple:
    - preview => accessible
    - sinon => Enrollment.can_access_content()
    """
    if getattr(lesson, "is_preview", False):
        return True
    return enrollment.can_access_content()







# # economic/formations/services/enrollment_service.py
# def enroll(user, course):
#     pass

