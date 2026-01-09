# core/services/contact_mailer.py
from __future__ import annotations

import logging
from typing import Optional

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from core.models import ContactMessage

logger = logging.getLogger(__name__)


def _safe_from_email() -> Optional[str]:
    return getattr(settings, "DEFAULT_FROM_EMAIL", None) or getattr(settings, "SERVER_EMAIL", None) or None


def send_contact_verification_email(*, request, contact: ContactMessage) -> None:
    """
    Envoie l'email de vérification à l'expéditeur.
    """
    verify_url = request.build_absolute_uri(f"/contact/verify/{contact.verify_token}/")

    subject = _("Vérifiez votre email")
    from_email = _safe_from_email()
    to_email = [contact.email]

    context = {
        "contact": contact,
        "verify_url": verify_url,
        "project_name": getattr(settings, "PROJECT_NAME", ""),
    }

    text_body = render_to_string("core/emails/contact_verify_email.txt", context).strip()
    html_body = render_to_string("core/emails/contact_verify_email.html", context).strip()

    msg = EmailMultiAlternatives(subject=subject, body=text_body, from_email=from_email, to=to_email)
    msg.attach_alternative(html_body, "text/html")
    msg.send(fail_silently=False)


def send_contact_to_team(*, contact: ContactMessage) -> None:
    """
    Transmet le message à l'équipe (CONTACT_EMAIL).
    """
    contact_email = (getattr(settings, "CONTACT_EMAIL", "") or "").strip()
    if not contact_email:
        raise RuntimeError("CONTACT_EMAIL is not configured")

    subject = _("Nouveau message (Contact) - email vérifié")
    from_email = _safe_from_email()

    context = {
        "contact": contact,
        "project_name": getattr(settings, "PROJECT_NAME", ""),
    }

    text_body = render_to_string("core/emails/contact_to_team.txt", context).strip()

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=from_email,
        to=[contact_email],
        headers={"Reply-To": contact.email},  # pour répondre directement à l'expéditeur
    )
    msg.send(fail_silently=False)





# # core/services/contact_email_service.py
# from __future__ import annotations

# from django.conf import settings
# from django.core.mail import EmailMultiAlternatives
# from django.template.loader import render_to_string
# from django.urls import reverse

# from core.models import ContactMessage


# # -------------------------------------------------
# # Helpers
# # -------------------------------------------------

# def _from_email() -> str:
#     """
#     Expéditeur sécurisé (obligatoire pour SMTP).
#     """
#     return (
#         (getattr(settings, "CONTACT_FROM_EMAIL", "") or "").strip()
#         or (getattr(settings, "DEFAULT_FROM_EMAIL", "") or "").strip()
#         or "no-reply@localhost"
#     )


# def _notify_emails() -> list[str]:
#     emails = list(getattr(settings, "CONTACT_NOTIFY_EMAILS", []) or [])
#     return [e.strip() for e in emails if isinstance(e, str) and e.strip()]


# # -------------------------------------------------
# # Emails
# # -------------------------------------------------

# def send_contact_verification_email(request, contact: ContactMessage) -> None:
#     """
#     Email de confirmation utilisateur (double opt-in).
#     """
#     verify_url = request.build_absolute_uri(
#         reverse("core:contact_verify", kwargs={"token": contact.verify_token})
#     )

#     subject = getattr(
#         settings,
#         "CONTACT_VERIFY_SUBJECT",
#         "Confirmez votre message de contact",
#     )

#     ctx = {
#         "contact": contact,
#         "verify_url": verify_url,
#     }

#     text_body = render_to_string("core/emails/contact_verify_email.txt", ctx)
#     html_body = render_to_string("core/emails/contact_verify_email.html", ctx)

#     msg = EmailMultiAlternatives(
#         subject=subject,
#         body=text_body,
#         from_email=_from_email(),
#         to=[contact.email],
#     )
#     msg.attach_alternative(html_body, "text/html")
#     msg.send(fail_silently=False)


# def send_contact_to_admins(contact: ContactMessage) -> int:
#     """
#     Notification admin.
#     🔒 STRICT : uniquement après vérification email.
#     """
#     if contact.status not in {
#         ContactMessage.Status.VERIFIED,
#         ContactMessage.Status.SENT,
#     }:
#         return 0

#     recipients = _notify_emails()
#     if not recipients:
#         return 0

#     subject = getattr(
#         settings,
#         "CONTACT_ADMIN_SUBJECT",
#         "Nouveau message de contact (email vérifié)",
#     )

#     ctx = {"contact": contact}

#     text_body = render_to_string("core/emails/contact_admin_notification.txt", ctx)
#     html_body = render_to_string("core/emails/contact_admin_notification.html", ctx)

#     msg = EmailMultiAlternatives(
#         subject=subject,
#         body=text_body,
#         from_email=_from_email(),
#         to=recipients,
#         reply_to=[contact.email] if contact.email else None,
#     )
#     msg.attach_alternative(html_body, "text/html")

#     return msg.send(fail_silently=False)




# # core/services/contact_email_service.py
# from __future__ import annotations

# from django.conf import settings
# from django.core.mail import EmailMultiAlternatives
# from django.template.loader import render_to_string
# from django.urls import reverse

# from core.models import ContactMessage

# def send_contact_to_admins(contact: ContactMessage) -> int:
#     # 🔒 BLOQUANT: jamais d’email admin tant que ce n’est pas vérifié
#     if contact.status not in {ContactMessage.Status.VERIFIED, ContactMessage.Status.SENT}:
#         return 0
#     ...


# def _from_email() -> str:
#     return (getattr(settings, "CONTACT_FROM_EMAIL", "") or getattr(settings, "DEFAULT_FROM_EMAIL", "") or "").strip()


# def _notify_emails() -> list[str]:
#     emails = list(getattr(settings, "CONTACT_NOTIFY_EMAILS", []) or [])
#     return [e for e in emails if e]


# def send_contact_verification_email(request, contact: ContactMessage) -> None:
#     verify_url = request.build_absolute_uri(
#         reverse("core:contact_verify", kwargs={"token": contact.verify_token})
#     )

#     subject = getattr(settings, "CONTACT_VERIFY_SUBJECT", "Confirmez votre message de contact")
#     ctx = {"contact": contact, "verify_url": verify_url}

#     html_body = render_to_string("core/emails/contact_verify_email.html", ctx)
#     text_body = render_to_string("core/emails/contact_verify_email.txt", ctx)

#     msg = EmailMultiAlternatives(
#         subject=subject,
#         body=text_body,
#         from_email=_from_email(),
#         to=[contact.email],
#     )
#     msg.attach_alternative(html_body, "text/html")
#     msg.send(fail_silently=False)


# def send_contact_to_admins(contact: ContactMessage) -> int:
#     recipients = _notify_emails()
#     if not recipients:
#         return 0

#     subject = getattr(settings, "CONTACT_ADMIN_SUBJECT", "Nouveau message de contact (email vérifié)")
#     ctx = {"contact": contact}

#     html_body = render_to_string("core/emails/contact_admin_notification.html", ctx)
#     text_body = render_to_string("core/emails/contact_admin_notification.txt", ctx)

#     msg = EmailMultiAlternatives(
#         subject=subject,
#         body=text_body,
#         from_email=_from_email(),
#         to=recipients,
#         reply_to=[contact.email],  # pratique: répondre directement à l’expéditeur
#     )
#     msg.attach_alternative(html_body, "text/html")
#     return msg.send(fail_silently=False)

