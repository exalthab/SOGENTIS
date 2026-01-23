# economic/formations/services/certificate_email.py
from __future__ import annotations

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.translation import gettext as _

from economic.formations.models import Certificate
from economic.formations.services.certificate_pdf import generate_certificate_pdf_and_attach


def _recipient_email(user) -> str:
    return (getattr(user, "email", "") or "").strip()


def send_certificate_email(
    certificate: Certificate,
    *,
    to_email: str | None = None,
    from_email: str | None = None,
) -> bool:
    """
    Envoie un email avec le certificat en PJ.
    Retourne True si envoyé, sinon False.
    """
    if certificate.revoked:
        return False

    user = certificate.enrollment.user
    recipient = (to_email or _recipient_email(user)).strip()
    if not recipient:
        return False

    # PDF si pas encore généré
    if not certificate.pdf_file:
        generate_certificate_pdf_and_attach(certificate)

    project_name = getattr(settings, "PROJECT_NAME", "SOGENTIS")
    site_url = getattr(settings, "SITE_URL", "")

    context = {
        "project_name": project_name,
        "site_url": site_url,
        "user": user,
        "certificate": certificate,
        "course": certificate.course,
    }

    subject = render_to_string(
        "economic/formations/emails/certificate_issued_subject.txt", context
    ).strip() or _("Votre certificat est disponible")

    body_txt = render_to_string(
        "economic/formations/emails/certificate_issued.txt", context
    )

    body_html = render_to_string(
        "economic/formations/emails/certificate_issued.html", context
    )

    _from = from_email or getattr(settings, "DEFAULT_FROM_EMAIL", None) or f"no-reply@{getattr(settings, 'ALLOWED_HOSTS', ['localhost'])[0]}"
    msg = EmailMultiAlternatives(subject=subject, body=body_txt, from_email=_from, to=[recipient])
    if body_html.strip():
        msg.attach_alternative(body_html, "text/html")

    # Attacher le PDF
    if certificate.pdf_file:
        try:
            with certificate.pdf_file.open("rb") as f:
                msg.attach(
                    filename=getattr(certificate, "download_filename", lambda: "certificate.pdf")(),
                    content=f.read(),
                    mimetype="application/pdf",
                )
        except Exception:
            # on envoie quand même sans PJ si lecture impossible
            pass

    msg.send(fail_silently=False)
    return True
