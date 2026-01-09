# core/views/contact.py
from __future__ import annotations

import logging
from typing import Optional

from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.decorators.http import require_http_methods

from config.settings.modules.antispam import rate_limit_reason_codes
from core.forms import ContactForm
from core.models import ContactMessage
from core.services.hcaptcha import verify_hcaptcha

logger = logging.getLogger(__name__)


def _get_client_ip(request: HttpRequest) -> str:
    xff = (request.META.get("HTTP_X_FORWARDED_FOR") or "").strip()
    if xff:
        return xff.split(",")[0].strip()
    return (request.META.get("REMOTE_ADDR") or "").strip()


def _safe_from_email() -> Optional[str]:
    return getattr(settings, "DEFAULT_FROM_EMAIL", None) or getattr(settings, "SERVER_EMAIL", None) or None


def _send_verification_email(request: HttpRequest, cm: ContactMessage) -> None:
    """
    Email simple (sans dépendre d'un template) pour éviter les erreurs de fichiers manquants.
    """
    verify_url = request.build_absolute_uri(reverse("core:contact_verify", kwargs={"token": cm.verify_token}))

    subject = _("Vérifiez votre adresse email")
    body = _(
        "Bonjour {name},\n\n"
        "Merci pour votre message.\n"
        "Veuillez vérifier votre adresse email en cliquant sur ce lien :\n"
        "{url}\n\n"
        "Si vous n’êtes pas à l’origine de cette demande, ignorez cet email."
    ).format(name=cm.name, url=verify_url)

    msg = EmailMultiAlternatives(
        subject=subject,
        body=body,
        from_email=_safe_from_email(),
        to=[cm.email],
    )
    msg.send(fail_silently=False)


def _send_admin_notification(cm: ContactMessage) -> None:
    contact_email = (getattr(settings, "CONTACT_EMAIL", "") or "").strip()
    if not contact_email:
        raise RuntimeError("CONTACT_EMAIL is not configured")

    admin_url = ""
    try:
        # si admin est monté sur /admin/
        admin_url = reverse("admin:core_contactmessage_change", args=[cm.pk])
    except Exception:
        admin_url = ""

    context = {
        "contact": cm,
        "admin_url": admin_url,
        "PROJECT_NAME": getattr(settings, "PROJECT_NAME", ""),
    }

    subject = _("Nouveau message de contact (email vérifié)")
    text_body = render_to_string("core/emails/contact_admin_notification.txt", context).strip()
    html_body = render_to_string("core/emails/contact_admin_notification.html", context).strip()

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=_safe_from_email(),
        to=[contact_email],
        headers={"Reply-To": cm.email},
    )
    msg.attach_alternative(html_body, "text/html")
    msg.send(fail_silently=False)


@require_http_methods(["GET", "POST"])
def contact_view(request: HttpRequest):
    form = ContactForm(request.POST or None)

    h_enabled = bool(getattr(settings, "HCAPTCHA_ENABLED", False))
    h_sitekey = getattr(settings, "HCAPTCHA_SITEKEY", "") or ""
    fail_open = bool(getattr(settings, "HCAPTCHA_FAIL_OPEN", False))

    if request.method == "POST":
        ip = _get_client_ip(request)

        # Rate-limit
        email_guess = (request.POST.get("email") or "").strip().lower()
        rl_codes = rate_limit_reason_codes(ip=ip, email=email_guess)
        if rl_codes:
            messages.error(request, _("Trop de tentatives. Merci de réessayer dans quelques minutes."))
            return render(request, "core/contact.html", {"form": form, "HCAPTCHA_ENABLED": h_enabled, "HCAPTCHA_SITEKEY": h_sitekey})

        # hCaptcha
        token = request.POST.get("h-captcha-response", "")
        ok, codes, unavailable = verify_hcaptcha(token=token, remoteip=ip)
        if not ok and not (unavailable and fail_open):
            messages.error(request, _("Vérification anti-spam (Captcha) échouée. Merci de réessayer."))
            return render(request, "core/contact.html", {"form": form, "HCAPTCHA_ENABLED": h_enabled, "HCAPTCHA_SITEKEY": h_sitekey})

        if form.is_valid():
            cm = ContactMessage.objects.create(
                name=form.cleaned_data["name"],
                email=form.cleaned_data["email"],
                message=form.cleaned_data["message"],
                sender_ip=ip or None,
                user_agent=(request.META.get("HTTP_USER_AGENT") or "")[:512],
            )
            cm.ensure_expiry(hours=24, save=True)

            try:
                _send_verification_email(request, cm)
            except Exception as exc:
                logger.exception("Contact verification email failed: %s", exc)
                messages.error(request, _("Impossible d’envoyer l’email de vérification. Merci de réessayer plus tard."))
                return render(request, "core/contact.html", {"form": form, "HCAPTCHA_ENABLED": h_enabled, "HCAPTCHA_SITEKEY": h_sitekey})

            return redirect("core:contact_verify_sent")

    return render(request, "core/contact.html", {"form": form, "HCAPTCHA_ENABLED": h_enabled, "HCAPTCHA_SITEKEY": h_sitekey})


@require_http_methods(["GET"])
def contact_verify_sent_view(request: HttpRequest):
    return render(request, "core/contact_verify_sent.html")


@require_http_methods(["GET"])
def contact_verify_view(request: HttpRequest, token):
    cm = get_object_or_404(ContactMessage, verify_token=token)

    if cm.is_verified:
        messages.info(request, _("Votre email a déjà été vérifié."))
        return redirect("core:contact")

    if not cm.is_token_valid():
        messages.error(request, _("Lien invalide ou expiré. Merci de renvoyer un message via le formulaire."))
        return redirect("core:contact")

    cm.mark_verified(save=True)

    try:
        _send_admin_notification(cm)
        cm.mark_sent(save=True)
        messages.success(request, _("Merci ! Votre email est vérifié et votre message a été transmis."))
    except Exception as exc:
        logger.exception("Admin notification failed: %s", exc)
        messages.warning(request, _("Votre email est vérifié, mais la transmission a échoué. L’équipe sera notifiée manuellement."))

    return redirect("core:contact")





# # core/views/contact.py
# from __future__ import annotations

# from django.conf import settings
# from django.contrib import messages
# from django.db import transaction
# from django.shortcuts import get_object_or_404, redirect, render
# from django.utils import timezone
# from django.utils.translation import gettext_lazy as _
# from django.views.decorators.http import require_http_methods

# from core.forms import ContactForm
# from core.models import ContactMessage
# from core.services.contact_email_service import send_contact_to_admins, send_contact_verification_email
# from config.settings.modules.antispam import rate_limited


# def _client_ip(request) -> str | None:
#     """
#     Récupère l'IP client depuis X-Forwarded-For ou REMOTE_ADDR.
#     """
#     xff = request.META.get("HTTP_X_FORWARDED_FOR", "")
#     if xff:
#         return xff.split(",")[0].strip()
#     return (request.META.get("REMOTE_ADDR") or "").strip() or None


# def _captcha_ctx(request) -> dict:
#     """
#     Contexte commun pour le template de contact avec captchas.
#     """
#     return {
#         "TURNSTILE_SITEKEY": getattr(settings, "TURNSTILE_SITEKEY", ""),
#         "HCAPTCHA_SITEKEY": getattr(settings, "HCAPTCHA_SITEKEY", ""),
#         "HCAPTCHA_THEME": getattr(settings, "HCAPTCHA_THEME", "light"),
#         "HCAPTCHA_REQUIRED": bool(request.session.get("contact_need_hcaptcha", False)),
#     }


# @require_http_methods(["GET", "POST"])
# def contact_view(request):
#     """
#     Affiche et traite le formulaire de contact avec anti-spam, captcha et rate-limit.
#     """
#     ip = _client_ip(request)
#     form = ContactForm(request.POST or None, request=request)

#     if request.method == "POST":
#         key = f"contact:rl:{ip}" if ip else "contact:rl:unknown"
#         if rate_limited(key, limit=int(getattr(settings, "CONTACT_RATE_LIMIT_MAX", 5)),
#                         window_seconds=int(getattr(settings, "CONTACT_RATE_LIMIT_WINDOW", 300))):
#             request.session["contact_need_hcaptcha"] = True
#             messages.error(request, _("Trop de tentatives. Merci de réessayer plus tard."))
#             return render(request, "core/contact.html", {"form": form, **_captcha_ctx(request)})

#         if form.is_valid():
#             contact: ContactMessage = form.save(commit=False)
#             contact.sender_ip = ip
#             contact.user_agent = (request.META.get("HTTP_USER_AGENT") or "")[:512]
#             contact.status = ContactMessage.Status.PENDING
#             contact.ensure_expiry(hours=int(getattr(settings, "CONTACT_VERIFY_TOKEN_HOURS", 48)), save=False)

#             with transaction.atomic():
#                 contact.save()
#                 transaction.on_commit(lambda: send_contact_verification_email(request, contact))

#             request.session.pop("contact_need_hcaptcha", None)

#             messages.success(
#                 request,
#                 _("Merci ! Nous venons de vous envoyer un email de confirmation. Cliquez sur le lien pour valider l’envoi."),
#             )
#             return redirect("core:contact_verify_sent")

#         # Si Turnstile échoue => prochain rendu exige hCaptcha (fallback)
#         for e in form.non_field_errors().as_data():
#             if getattr(e, "code", "") == "turnstile_failed":
#                 request.session["contact_need_hcaptcha"] = True
#                 break

#     return render(request, "core/contact.html", {"form": form, **_captcha_ctx(request)})


# @require_http_methods(["GET"])
# def contact_verify_sent_view(request):
#     """Page indiquant que l'email de vérification a été envoyé."""
#     return render(request, "core/contact_verify_sent.html")


# @require_http_methods(["GET"])
# def contact_verify_view(request, token):
#     """
#     Vérifie le token envoyé par email, marque le message comme VERIFIED et envoie aux admins.
#     """
#     with transaction.atomic():
#         contact = get_object_or_404(ContactMessage.objects.select_for_update(), verify_token=token)

#         # Déjà confirmé
#         if contact.status in {ContactMessage.Status.VERIFIED, ContactMessage.Status.SENT}:
#             return render(
#                 request,
#                 "core/contact_verified.html",
#                 {"contact": contact, "already": True, "sent": contact.status == ContactMessage.Status.SENT},
#             )

#         # Token expiré
#         if not contact.is_token_valid():
#             contact.rotate_token(hours=int(getattr(settings, "CONTACT_VERIFY_TOKEN_HOURS", 48)), save=True)
#             transaction.on_commit(lambda: send_contact_verification_email(request, contact))
#             messages.warning(request, _("Ce lien avait expiré. Un nouveau lien de confirmation vient d’être renvoyé."))
#             return redirect("core:contact_verify_sent")

#         # Token valide => marquer comme vérifié
#         contact.status = ContactMessage.Status.VERIFIED
#         contact.verified_at = timezone.now()
#         contact.save(update_fields=["status", "verified_at"])

#     # Envoi aux admins
#     sent = False
#     try:
#         count = send_contact_to_admins(contact)
#         sent = count > 0
#     except Exception:
#         sent = False

#     if sent:
#         now = timezone.now()
#         ContactMessage.objects.filter(pk=contact.pk).update(status=ContactMessage.Status.SENT, sent_at=now)
#         contact.status = ContactMessage.Status.SENT
#         contact.sent_at = now

#     return render(request, "core/contact_verified.html", {"contact": contact, "already": False, "sent": sent})




# # core/views/contact.py
# from __future__ import annotations

# import uuid
# from datetime import timedelta

# from django.conf import settings
# from django.contrib import messages
# from django.db import transaction
# from django.shortcuts import get_object_or_404, redirect, render
# from django.utils import timezone
# from django.utils.translation import gettext_lazy as _
# from django.views.decorators.http import require_http_methods

# from core.forms import ContactForm
# from core.models import ContactMessage
# from core.services.contact_email_service import send_contact_to_admins, send_contact_verification_email
# from core.services.rate_limit import rate_limited


# def _client_ip(request) -> str:
#     """
#     Récupère l'IP client à partir du header X-Forwarded-For ou REMOTE_ADDR.
#     """
#     xff = request.META.get("HTTP_X_FORWARDED_FOR", "")
#     if xff:
#         return xff.split(",")[0].strip()
#     return (request.META.get("REMOTE_ADDR") or "").strip()


# def _captcha_ctx(request) -> dict:
#     """
#     Contexte commun pour le template de contact avec captchas.
#     """
#     return {
#         "TURNSTILE_SITEKEY": getattr(settings, "TURNSTILE_SITEKEY", ""),
#         "HCAPTCHA_SITEKEY": getattr(settings, "HCAPTCHA_SITEKEY", ""),
#         "HCAPTCHA_THEME": getattr(settings, "HCAPTCHA_THEME", "light"),
#         "HCAPTCHA_REQUIRED": bool(request.session.get("contact_need_hcaptcha", False)),
#     }


# @require_http_methods(["GET", "POST"])
# def contact_view(request):
#     """
#     Affiche et traite le formulaire de contact avec anti-spam, captcha et rate-limit.
#     """
#     ip = _client_ip(request)
#     form = ContactForm(request.POST or None, request=request)

#     if request.method == "POST":
#         key = f"contact:rl:{ip}" if ip else "contact:rl:unknown"

#         if rate_limited(key, limit=int(settings.CONTACT_RATE_LIMIT_MAX), window_seconds=int(settings.CONTACT_RATE_LIMIT_WINDOW)):
#             request.session["contact_need_hcaptcha"] = True
#             messages.error(request, _("Trop de tentatives. Merci de réessayer plus tard."))
#             return render(request, "core/contact.html", {"form": form, **_captcha_ctx(request)})

#         if form.is_valid():
#             contact: ContactMessage = form.save(commit=False)
#             contact.sender_ip = ip or None
#             contact.user_agent = (request.META.get("HTTP_USER_AGENT") or "")[:512]
#             contact.status = ContactMessage.Status.PENDING
#             contact.ensure_expiry(hours=int(settings.CONTACT_VERIFY_TOKEN_HOURS), save=False)

#             with transaction.atomic():
#                 contact.save()
#                 transaction.on_commit(lambda: send_contact_verification_email(request, contact))

#             request.session.pop("contact_need_hcaptcha", None)

#             messages.success(
#                 request,
#                 _("Merci ! Nous venons de vous envoyer un email de confirmation. Cliquez sur le lien pour valider l’envoi."),
#             )
#             return redirect("core:contact_verify_sent")

#         # Si Turnstile échoue => prochain rendu exige hCaptcha (mode fallback)
#         for e in form.non_field_errors().as_data():
#             if getattr(e, "code", "") == "turnstile_failed":
#                 request.session["contact_need_hcaptcha"] = True
#                 break

#     return render(request, "core/contact.html", {"form": form, **_captcha_ctx(request)})


# @require_http_methods(["GET"])
# def contact_verify_sent_view(request):
#     """
#     Page d'information que l'email de vérification a été envoyé.
#     """
#     return render(request, "core/contact_verify_sent.html")


# @require_http_methods(["GET"])
# def contact_verify_view(request, token):
#     """
#     Vérifie le token envoyé par email, marque le message comme VERIFIED et envoie aux admins.
#     """
#     with transaction.atomic():
#         contact = get_object_or_404(ContactMessage.objects.select_for_update(), verify_token=token)

#         # Déjà confirmé
#         if contact.status in {ContactMessage.Status.VERIFIED, ContactMessage.Status.SENT}:
#             return render(
#                 request,
#                 "core/contact_verified.html",
#                 {"contact": contact, "already": True, "sent": contact.status == ContactMessage.Status.SENT},
#             )

#         # Token expiré
#         if not contact.is_token_valid():
#             contact.rotate_token(hours=int(settings.CONTACT_VERIFY_TOKEN_HOURS), save=True)
#             transaction.on_commit(lambda: send_contact_verification_email(request, contact))
#             messages.warning(request, _("Ce lien avait expiré. Un nouveau lien de confirmation vient d’être renvoyé."))
#             return redirect("core:contact_verify_sent")

#         # Token valide => marquer comme vérifié
#         contact.status = ContactMessage.Status.VERIFIED
#         contact.verified_at = timezone.now()
#         contact.save(update_fields=["status", "verified_at"])

#     # Envoi aux admins
#     sent = False
#     try:
#         count = send_contact_to_admins(contact)
#         sent = count > 0
#     except Exception:
#         sent = False

#     if sent:
#         now = timezone.now()
#         ContactMessage.objects.filter(pk=contact.pk).update(status=ContactMessage.Status.SENT, sent_at=now)
#         contact.status = ContactMessage.Status.SENT
#         contact.sent_at = now

#     return render(request, "core/contact_verified.html", {"contact": contact, "already": False, "sent": sent})





# # core/views/contact.py
# from __future__ import annotations

# import uuid
# from datetime import timedelta

# from django.conf import settings
# from django.contrib import messages
# from django.db import transaction
# from django.shortcuts import get_object_or_404, redirect, render
# from django.utils import timezone
# from django.utils.translation import gettext_lazy as _
# from django.views.decorators.http import require_http_methods

# from core.forms import ContactForm
# from core.models import ContactMessage
# from core.services.contact_email_service import send_contact_to_admins, send_contact_verification_email
# from core.services.rate_limit import rate_limited


# def _client_ip(request) -> str:
#     xff = request.META.get("HTTP_X_FORWARDED_FOR", "")
#     if xff:
#         return xff.split(",")[0].strip()
#     return (request.META.get("REMOTE_ADDR") or "").strip()


# def _captcha_ctx(request) -> dict:
#     return {
#         "TURNSTILE_SITEKEY": getattr(settings, "TURNSTILE_SITEKEY", ""),
#         "HCAPTCHA_SITEKEY": getattr(settings, "HCAPTCHA_SITEKEY", ""),
#         "HCAPTCHA_THEME": getattr(settings, "HCAPTCHA_THEME", "light"),
#         "HCAPTCHA_REQUIRED": bool(request.session.get("contact_need_hcaptcha", False)),
#     }


# @require_http_methods(["GET", "POST"])
# def contact_view(request):
#     ip = _client_ip(request)
#     form = ContactForm(request.POST or None, request=request)

#     if request.method == "POST":
#         key = f"contact:rl:{ip}" if ip else "contact:rl:unknown"
#         if rate_limited(key, limit=int(settings.CONTACT_RATE_LIMIT_MAX), window_seconds=int(settings.CONTACT_RATE_LIMIT_WINDOW)):
#             request.session["contact_need_hcaptcha"] = True
#             messages.error(request, _("Trop de tentatives. Merci de réessayer plus tard."))
#             return render(request, "core/contact.html", {"form": form, **_captcha_ctx(request)})

#         if form.is_valid():
#             contact: ContactMessage = form.save(commit=False)
#             contact.sender_ip = ip or None
#             contact.user_agent = (request.META.get("HTTP_USER_AGENT") or "")[:512]
#             contact.status = ContactMessage.Status.PENDING
#             contact.ensure_expiry(hours=int(settings.CONTACT_VERIFY_TOKEN_HOURS), save=False)

#             with transaction.atomic():
#                 contact.save()
#                 transaction.on_commit(lambda: send_contact_verification_email(request, contact))

#             request.session.pop("contact_need_hcaptcha", None)

#             messages.success(
#                 request,
#                 _("Merci ! Nous venons de vous envoyer un email de confirmation. Cliquez sur le lien pour valider l’envoi."),
#             )
#             return redirect("core:contact_verify_sent")

#         # ✅ Si Turnstile échoue => prochain rendu exige hCaptcha (fallback)
#         for e in form.non_field_errors().as_data():
#             if getattr(e, "code", "") == "turnstile_failed":
#                 request.session["contact_need_hcaptcha"] = True
#                 break

#     return render(request, "core/contact.html", {"form": form, **_captcha_ctx(request)})


# @require_http_methods(["GET"])
# def contact_verify_sent_view(request):
#     return render(request, "core/contact_verify_sent.html")


# @require_http_methods(["GET"])
# def contact_verify_view(request, token):
#     with transaction.atomic():
#         contact = get_object_or_404(ContactMessage.objects.select_for_update(), verify_token=token)

#         if contact.status in {ContactMessage.Status.VERIFIED, ContactMessage.Status.SENT}:
#             return render(
#                 request,
#                 "core/contact_verified.html",
#                 {"contact": contact, "already": True, "sent": contact.status == ContactMessage.Status.SENT},
#             )

#         if not contact.is_token_valid():
#             contact.verify_token = uuid.uuid4()
#             contact.token_expires_at = timezone.now() + timedelta(hours=int(settings.CONTACT_VERIFY_TOKEN_HOURS))
#             contact.status = ContactMessage.Status.PENDING
#             contact.verified_at = None
#             contact.sent_at = None
#             contact.save(update_fields=["verify_token", "token_expires_at", "status", "verified_at", "sent_at"])

#             transaction.on_commit(lambda: send_contact_verification_email(request, contact))
#             messages.warning(request, _("Ce lien avait expiré. Un nouveau lien de confirmation vient d’être renvoyé."))
#             return redirect("core:contact_verify_sent")

#         contact.status = ContactMessage.Status.VERIFIED
#         contact.verified_at = timezone.now()
#         contact.save(update_fields=["status", "verified_at"])

#     sent = False
#     try:
#         count = send_contact_to_admins(contact)
#         sent = count > 0
#     except Exception:
#         sent = False

#     if sent:
#         ContactMessage.objects.filter(pk=contact.pk).update(status=ContactMessage.Status.SENT, sent_at=timezone.now())
#         contact.status = ContactMessage.Status.SENT
#         contact.sent_at = timezone.now()

#     return render(request, "core/contact_verified.html", {"contact": contact, "already": False, "sent": sent})




# # core/views/contact.py
# from __future__ import annotations

# import uuid

# from django.conf import settings
# from django.contrib import messages
# from django.db import transaction
# from django.shortcuts import get_object_or_404, redirect, render
# from django.utils import timezone
# from django.utils.translation import gettext_lazy as _
# from django.views.decorators.http import require_http_methods

# from core.forms import ContactForm
# from core.models import ContactMessage
# from core.services.contact_email_service import send_contact_to_admins, send_contact_verification_email
# from core.services.rate_limit import rate_limited


# def _client_ip(request) -> str:
#     xff = request.META.get("HTTP_X_FORWARDED_FOR", "")
#     if xff:
#         return xff.split(",")[0].strip()
#     return (request.META.get("REMOTE_ADDR") or "").strip()


# def _captcha_ctx(request) -> dict:
#     return {
#         "TURNSTILE_SITEKEY": getattr(settings, "TURNSTILE_SITEKEY", ""),
#         "HCAPTCHA_SITEKEY": getattr(settings, "HCAPTCHA_SITEKEY", ""),
#         "HCAPTCHA_THEME": getattr(settings, "HCAPTCHA_THEME", "light"),
#         "HCAPTCHA_REQUIRED": bool(request.session.get("contact_need_hcaptcha", False)),
#     }


# @require_http_methods(["GET", "POST"])
# def contact_view(request):
#     ip = _client_ip(request)
#     form = ContactForm(request.POST or None, request=request)

#     if request.method == "POST":
#         key = f"contact:rl:{ip}" if ip else "contact:rl:unknown"
#         if rate_limited(key, limit=int(settings.CONTACT_RATE_LIMIT_MAX), window_seconds=int(settings.CONTACT_RATE_LIMIT_WINDOW)):
#             request.session["contact_need_hcaptcha"] = True
#             messages.error(request, _("Trop de tentatives. Merci de réessayer plus tard."))
#             return render(request, "core/contact.html", {"form": form, **_captcha_ctx(request)})

#         if form.is_valid():
#             contact: ContactMessage = form.save(commit=False)
#             contact.sender_ip = ip or None
#             contact.user_agent = (request.META.get("HTTP_USER_AGENT") or "")[:512]
#             contact.status = ContactMessage.Status.PENDING
#             contact.ensure_expiry(hours=int(settings.CONTACT_VERIFY_TOKEN_HOURS), save=False)

#             with transaction.atomic():
#                 contact.save()
#                 transaction.on_commit(lambda: send_contact_verification_email(request, contact))

#             # reset fallback si succès de validation
#             request.session.pop("contact_need_hcaptcha", None)

#             messages.success(
#                 request,
#                 _("Merci ! Nous venons de vous envoyer un email de confirmation. Cliquez sur le lien pour valider l’envoi."),
#             )
#             return redirect("core:contact_verify_sent")

#         # si Turnstile/hCaptcha échoue => activer fallback hCaptcha pour le prochain rendu
#         for e in form.non_field_errors().as_data():
#             if getattr(e, "code", "") in {"turnstile_failed", "hcaptcha_failed"}:
#                 request.session["contact_need_hcaptcha"] = True
#                 break

#     return render(request, "core/contact.html", {"form": form, **_captcha_ctx(request)})


# @require_http_methods(["GET"])
# def contact_verify_sent_view(request):
#     return render(request, "core/contact_verify_sent.html")


# @require_http_methods(["GET"])
# def contact_verify_view(request, token):
#     """
#     - Si déjà VERIFIED/SENT => page "déjà confirmé"
#     - Si PENDING + expiré => rotate token + renvoi email
#     - Si PENDING + valide => VERIFIED puis notification admins => SENT si ok
#     """
#     with transaction.atomic():
#         contact = get_object_or_404(ContactMessage.objects.select_for_update(), verify_token=token)

#         if contact.status in {ContactMessage.Status.VERIFIED, ContactMessage.Status.SENT}:
#             return render(request, "core/contact_verified.html", {"contact": contact, "already": True, "sent": contact.status == ContactMessage.Status.SENT})

#         # PENDING mais expiré
#         if not contact.is_token_valid():
#             contact.verify_token = uuid.uuid4()
#             contact.ensure_expiry(hours=int(settings.CONTACT_VERIFY_TOKEN_HOURS), save=False)
#             contact.save(update_fields=["verify_token", "token_expires_at"])

#             transaction.on_commit(lambda: send_contact_verification_email(request, contact))
#             messages.warning(request, _("Ce lien avait expiré. Un nouveau lien de confirmation vient d’être renvoyé."))
#             return redirect("core:contact_verify_sent")

#         # Token OK => vérifier
#         contact.status = ContactMessage.Status.VERIFIED
#         contact.verified_at = timezone.now()
#         contact.save(update_fields=["status", "verified_at"])

#     # envoi admin hors lock DB
#     sent = False
#     try:
#         count = send_contact_to_admins(contact)
#         sent = count > 0
#     except Exception:
#         sent = False

#     if sent:
#         ContactMessage.objects.filter(pk=contact.pk).update(status=ContactMessage.Status.SENT, sent_at=timezone.now())
#         contact.status = ContactMessage.Status.SENT
#         contact.sent_at = timezone.now()

#     return render(request, "core/contact_verified.html", {"contact": contact, "already": False, "sent": sent})
