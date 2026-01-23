# core/services/contact_mailer.py
from __future__ import annotations

import logging
from typing import Optional

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.http import HttpRequest
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import gettext as _

from core.models import ContactMessage

logger = logging.getLogger(__name__)


# ============================================================
# Helpers
# ============================================================
def _safe_from_email() -> Optional[str]:
    """
    Détermine un "from" cohérent.
    - Si None, Django utilise souvent DEFAULT_FROM_EMAIL (selon backend),
      mais on préfère être explicite quand possible.
    """
    return (
        (getattr(settings, "DEFAULT_FROM_EMAIL", "") or "").strip()
        or (getattr(settings, "SERVER_EMAIL", "") or "").strip()
        or None
    )


def _get_contact_email() -> str:
    """
    Email de réception côté équipe.
    """
    contact_email = (getattr(settings, "CONTACT_EMAIL", "") or "").strip()
    if not contact_email:
        raise RuntimeError("CONTACT_EMAIL is not configured")
    return contact_email


def _build_verify_url(request: HttpRequest, token: str) -> str:
    """
    URL absolue de vérification (robuste via reverse).
    """
    path = reverse("core:contact_verify", kwargs={"token": token})
    return request.build_absolute_uri(path)


def _attach_html_if_exists(msg: EmailMultiAlternatives, template_name: str, context: dict) -> None:
    """
    Ajoute une alternative HTML si le template existe.
    Ne casse pas l'envoi si le HTML manque.
    """
    try:
        html_body = render_to_string(template_name, context).strip()
    except TemplateDoesNotExist:
        return
    except Exception as exc:
        logger.warning("Failed to render html template %s: %s", template_name, exc)
        return

    if html_body:
        msg.attach_alternative(html_body, "text/html")


# ============================================================
# Public API
# ============================================================
def send_contact_verification_email(*, request: HttpRequest, contact: ContactMessage) -> None:
    """
    Envoie l'email de vérification à l'expéditeur.
    Templates attendus:
      - core/emails/contact_verify_email.txt
      - core/emails/contact_verify_email.html (optionnel)
    """
    if not contact.email:
        raise ValueError("ContactMessage.email is empty")

    verify_url = _build_verify_url(request, contact.verify_token)

    subject = _("Vérifiez votre email")
    from_email = _safe_from_email()

    context = {
        "contact": contact,
        "verify_url": verify_url,
        "PROJECT_NAME": getattr(settings, "PROJECT_NAME", "SOGENTIS"),
        "CONTACT_EMAIL": getattr(settings, "CONTACT_EMAIL", ""),
    }

    text_body = render_to_string("core/emails/contact_verify_email.txt", context).strip()

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=from_email,
        to=[contact.email],
    )

    _attach_html_if_exists(msg, "core/emails/contact_verify_email.html", context)

    msg.send(fail_silently=False)


def send_contact_to_team(*, contact: ContactMessage) -> None:
    """
    Transmet le message à l'équipe (CONTACT_EMAIL) après vérification.
    Templates attendus:
      - core/emails/contact_to_team.txt
      - core/emails/contact_to_team.html (optionnel)
    """
    if not contact.email:
        raise ValueError("ContactMessage.email is empty")

    to_email = _get_contact_email()
    subject = _("Nouveau message (Contact) - email vérifié")
    from_email = _safe_from_email()

    context = {
        "contact": contact,
        "PROJECT_NAME": getattr(settings, "PROJECT_NAME", "SOGENTIS"),
    }

    text_body = render_to_string("core/emails/contact_to_team.txt", context).strip()

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=from_email,
        to=[to_email],
        reply_to=[contact.email],                 # ✅ meilleure pratique Django
        headers={"Reply-To": contact.email},      # ✅ compat / clients mail
    )

    _attach_html_if_exists(msg, "core/emails/contact_to_team.html", context)

    msg.send(fail_silently=False)






# # core/services/contact_mailer.py
# from __future__ import annotations

# import logging
# from typing import Optional

# from django.conf import settings
# from django.core.mail import EmailMultiAlternatives
# from django.template.loader import render_to_string
# from django.utils.translation import gettext_lazy as _

# from core.models import ContactMessage

# logger = logging.getLogger(__name__)


# def _safe_from_email() -> Optional[str]:
#     return getattr(settings, "DEFAULT_FROM_EMAIL", None) or getattr(settings, "SERVER_EMAIL", None) or None


# def send_contact_verification_email(*, request, contact: ContactMessage) -> None:
#     """
#     Envoie l'email de vérification à l'expéditeur.
#     """
#     verify_url = request.build_absolute_uri(f"/contact/verify/{contact.verify_token}/")

#     subject = _("Vérifiez votre email")
#     from_email = _safe_from_email()
#     to_email = [contact.email]

#     context = {
#         "contact": contact,
#         "verify_url": verify_url,
#         "project_name": getattr(settings, "PROJECT_NAME", ""),
#     }

#     text_body = render_to_string("core/emails/contact_verify_email.txt", context).strip()
#     html_body = render_to_string("core/emails/contact_verify_email.html", context).strip()

#     msg = EmailMultiAlternatives(subject=subject, body=text_body, from_email=from_email, to=to_email)
#     msg.attach_alternative(html_body, "text/html")
#     msg.send(fail_silently=False)


# def send_contact_to_team(*, contact: ContactMessage) -> None:
#     """
#     Transmet le message à l'équipe (CONTACT_EMAIL).
#     """
#     contact_email = (getattr(settings, "CONTACT_EMAIL", "") or "").strip()
#     if not contact_email:
#         raise RuntimeError("CONTACT_EMAIL is not configured")

#     subject = _("Nouveau message (Contact) - email vérifié")
#     from_email = _safe_from_email()

#     context = {
#         "contact": contact,
#         "project_name": getattr(settings, "PROJECT_NAME", ""),
#     }

#     text_body = render_to_string("core/emails/contact_to_team.txt", context).strip()

#     msg = EmailMultiAlternatives(
#         subject=subject,
#         body=text_body,
#         from_email=from_email,
#         to=[contact_email],
#         headers={"Reply-To": contact.email},  # pour répondre directement à l'expéditeur
#     )
#     msg.send(fail_silently=False)





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

