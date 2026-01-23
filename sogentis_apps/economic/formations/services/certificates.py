# economic/formations/services/certificates.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from django.db import transaction
from django.utils.translation import gettext_lazy as _

from economic.formations.models import Enrollment, Certificate


@dataclass(frozen=True)
class CertificateGenerationResult:
    certificate: Certificate
    created: bool
    pdf_generated: bool
    email_sent: bool


def _is_enrollment_completed(enrollment: Enrollment) -> bool:
    """
    Vérifie si l'enrollment est terminé.
    Compatible avec :
    - enrollment.status == COMPLETED (nouveau modèle)
    - enrollment.completed == True (ancien champ)
    """
    status_completed = getattr(Enrollment, "Status", None) and getattr(enrollment, "status", None) == Enrollment.Status.COMPLETED
    legacy_completed = bool(getattr(enrollment, "completed", False))
    return bool(status_completed or legacy_completed)


@transaction.atomic
def issue_certificate_for_enrollment(enrollment: Enrollment) -> Tuple[Certificate, bool]:
    """
    Crée le certificat si absent.
    À appeler quand l'inscription passe en COMPLETED (ou completed=True).
    Retourne (certificat, created).
    """
    if not _is_enrollment_completed(enrollment):
        raise ValueError(_("L'inscription n'est pas terminée."))

    cert, created = Certificate.objects.get_or_create(
        enrollment=enrollment,
        defaults={"course": enrollment.course},
    )

    # Sécurité : synchronisation course pour les anciens cas
    if cert.course_id != enrollment.course_id:
        cert.course = enrollment.course
        cert.save(update_fields=["course"])

    return cert, created


def generate_certificate(
    enrollment: Enrollment,
    *,
    generate_pdf: bool = True,
    send_email: bool = True,
) -> CertificateGenerationResult:
    """
    Pipeline complet :
    1) émettre (ou récupérer) le certificat
    2) générer le PDF (si service disponible) + l'attacher
    3) envoyer l'email (si service disponible)

    Ne plante pas si PDF/email non implémentés.
    """
    cert, created = issue_certificate_for_enrollment(enrollment)

    pdf_generated = False
    email_sent = False

    # ---- PDF ----
    if generate_pdf:
        if not getattr(cert, "pdf_file", None):
            try:
                from economic.formations.services.certificate_pdf import generate_certificate_pdf_and_attach
                pdf_generated = bool(generate_certificate_pdf_and_attach(cert))
            except ModuleNotFoundError:
                pdf_generated = False

    # ---- EMAIL ----
    if send_email:
        try:
            from economic.formations.services.certificate_email import send_certificate_email
            email_sent = bool(send_certificate_email(cert))
        except ModuleNotFoundError:
            email_sent = False

    return CertificateGenerationResult(
        certificate=cert,
        created=created,
        pdf_generated=pdf_generated,
        email_sent=email_sent
    )






# # economic/formations/services/certificate.py
# from django.db import transaction
# from django.utils.translation import gettext_lazy as _

# from economic.formations.models import Enrollment, Certificate


# @transaction.atomic
# def issue_certificate_for_enrollment(enrollment: Enrollment) -> Certificate:
#     """
#     Crée le certificat si absent.
#     À appeler quand l'inscription passe en COMPLETED.
#     """
#     if enrollment.status != Enrollment.Status.COMPLETED and not enrollment.completed:
#         raise ValueError(_("L'inscription n'est pas terminée."))

#     cert, _created = Certificate.objects.get_or_create(
#         enrollment=enrollment,
#         defaults={"course": enrollment.course},
#     )
#     return cert


# def generate_certificate(enrollment):
#      pass
