# economic/formations/services/certificate_service.py
from __future__ import annotations

from dataclasses import dataclass

from django.db import transaction
from django.utils.translation import gettext_lazy as _

from economic.formations.models import Enrollment, Certificate


@dataclass(frozen=True)
class CertificateIssueResult:
    certificate: Certificate
    created: bool
    pdf_generated: bool
    email_sent: bool


def _is_enrollment_completed(enrollment: Enrollment) -> bool:
    """
    Compatible:
    - enrollment.status == COMPLETED (canonique)
    - enrollment.completed == True (legacy)
    """
    try:
        if getattr(enrollment, "status", None) == Enrollment.Status.COMPLETED:
            return True
    except Exception:
        pass
    return bool(getattr(enrollment, "completed", False))


def _sync_certificate_from_enrollment(cert: Certificate, enrollment: Enrollment) -> bool:
    """
    Force la cohérence (course/session).
    Retourne True si update effectué.
    """
    changed = False

    if cert.course_id != enrollment.course_id:
        cert.course_id = enrollment.course_id
        changed = True

    # session optionnelle
    if hasattr(cert, "session_id") and getattr(cert, "session_id", None) != getattr(enrollment, "session_id", None):
        cert.session_id = enrollment.session_id
        changed = True

    return changed


def _generate_pdf(cert: Certificate, *, force: bool = False) -> bool:
    """
    Appelle certificate_pdf.generate_certificate_pdf_and_attach si dispo.
    """
    try:
        from economic.formations.services.certificate_pdf import generate_certificate_pdf_and_attach
    except Exception:
        return False

    try:
        return bool(generate_certificate_pdf_and_attach(cert, force=force))
    except Exception:
        return False


def _send_email(cert: Certificate) -> bool:
    """
    Appelle certificate_email.send_certificate_email si dispo.
    """
    try:
        from economic.formations.services.certificate_email import send_certificate_email
    except Exception:
        return False

    try:
        return bool(send_certificate_email(cert))
    except Exception:
        return False


@transaction.atomic
def issue_certificate_for_enrollment(
    enrollment: Enrollment,
    *,
    generate_pdf: bool = True,
    send_email: bool = True,
    force_pdf: bool = False,
) -> CertificateIssueResult:
    """
    Pipeline complet:
    1) Valide enrollment complété
    2) get_or_create Certificate(enrollment=...)
    3) sync course/session
    4) PDF (optionnel)
    5) Email (optionnel)
    """
    if not _is_enrollment_completed(enrollment):
        raise ValueError(_("L'inscription n'est pas terminée."))

    cert, created = Certificate.objects.get_or_create(
        enrollment=enrollment,
        defaults={
            "course": enrollment.course,
            # session peut exister (si champ présent dans Certificate)
            **({"session": enrollment.session} if hasattr(Certificate, "session") else {}),
        },
    )

    # sécurité: synchro course/session
    changed = _sync_certificate_from_enrollment(cert, enrollment)
    if changed:
        fields = ["course"]
        if hasattr(cert, "session_id"):
            fields.append("session")
        cert.save(update_fields=fields)

    # ne pas émettre/traiter si révoqué
    if getattr(cert, "revoked", False):
        return CertificateIssueResult(
            certificate=cert,
            created=created,
            pdf_generated=False,
            email_sent=False,
        )

    pdf_generated = False
    email_sent = False

    # PDF
    if generate_pdf:
        pdf_generated = _generate_pdf(cert, force=force_pdf)

    # Email
    if send_email:
        # si pdf demandé mais non généré et cert.pdf_file absent, on tente une dernière fois
        if generate_pdf and not getattr(cert, "pdf_file", None):
            _generate_pdf(cert, force=force_pdf)
        email_sent = _send_email(cert)

    return CertificateIssueResult(
        certificate=cert,
        created=created,
        pdf_generated=pdf_generated,
        email_sent=email_sent,
    )
