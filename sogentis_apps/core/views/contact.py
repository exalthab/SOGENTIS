# core/views/contact.py
from __future__ import annotations

import uuid
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods

from core.forms import ContactForm
from core.models import ContactMessage
from core.services.contact_email_service import send_contact_to_admins, send_contact_verification_email
from core.services.rate_limit import rate_limited


def _client_ip(request) -> str:
    xff = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if xff:
        return xff.split(",")[0].strip()
    return (request.META.get("REMOTE_ADDR") or "").strip()


def _captcha_ctx(request) -> dict:
    return {
        "TURNSTILE_SITEKEY": getattr(settings, "TURNSTILE_SITEKEY", ""),
        "HCAPTCHA_SITEKEY": getattr(settings, "HCAPTCHA_SITEKEY", ""),
        "HCAPTCHA_THEME": getattr(settings, "HCAPTCHA_THEME", "light"),
        "HCAPTCHA_REQUIRED": bool(request.session.get("contact_need_hcaptcha", False)),
    }


@require_http_methods(["GET", "POST"])
def contact_view(request):
    ip = _client_ip(request)
    form = ContactForm(request.POST or None, request=request)

    if request.method == "POST":
        key = f"contact:rl:{ip}" if ip else "contact:rl:unknown"
        if rate_limited(key, limit=int(settings.CONTACT_RATE_LIMIT_MAX), window_seconds=int(settings.CONTACT_RATE_LIMIT_WINDOW)):
            request.session["contact_need_hcaptcha"] = True
            messages.error(request, _("Trop de tentatives. Merci de réessayer plus tard."))
            return render(request, "core/contact.html", {"form": form, **_captcha_ctx(request)})

        if form.is_valid():
            contact: ContactMessage = form.save(commit=False)
            contact.sender_ip = ip or None
            contact.user_agent = (request.META.get("HTTP_USER_AGENT") or "")[:512]
            contact.status = ContactMessage.Status.PENDING
            contact.ensure_expiry(hours=int(settings.CONTACT_VERIFY_TOKEN_HOURS), save=False)

            with transaction.atomic():
                contact.save()
                transaction.on_commit(lambda: send_contact_verification_email(request, contact))

            request.session.pop("contact_need_hcaptcha", None)

            messages.success(
                request,
                _("Merci ! Nous venons de vous envoyer un email de confirmation. Cliquez sur le lien pour valider l’envoi."),
            )
            return redirect("core:contact_verify_sent")

        # ✅ Si Turnstile échoue => prochain rendu exige hCaptcha (fallback)
        for e in form.non_field_errors().as_data():
            if getattr(e, "code", "") == "turnstile_failed":
                request.session["contact_need_hcaptcha"] = True
                break

    return render(request, "core/contact.html", {"form": form, **_captcha_ctx(request)})


@require_http_methods(["GET"])
def contact_verify_sent_view(request):
    return render(request, "core/contact_verify_sent.html")


@require_http_methods(["GET"])
def contact_verify_view(request, token):
    with transaction.atomic():
        contact = get_object_or_404(ContactMessage.objects.select_for_update(), verify_token=token)

        if contact.status in {ContactMessage.Status.VERIFIED, ContactMessage.Status.SENT}:
            return render(
                request,
                "core/contact_verified.html",
                {"contact": contact, "already": True, "sent": contact.status == ContactMessage.Status.SENT},
            )

        if not contact.is_token_valid():
            contact.verify_token = uuid.uuid4()
            contact.token_expires_at = timezone.now() + timedelta(hours=int(settings.CONTACT_VERIFY_TOKEN_HOURS))
            contact.status = ContactMessage.Status.PENDING
            contact.verified_at = None
            contact.sent_at = None
            contact.save(update_fields=["verify_token", "token_expires_at", "status", "verified_at", "sent_at"])

            transaction.on_commit(lambda: send_contact_verification_email(request, contact))
            messages.warning(request, _("Ce lien avait expiré. Un nouveau lien de confirmation vient d’être renvoyé."))
            return redirect("core:contact_verify_sent")

        contact.status = ContactMessage.Status.VERIFIED
        contact.verified_at = timezone.now()
        contact.save(update_fields=["status", "verified_at"])

    sent = False
    try:
        count = send_contact_to_admins(contact)
        sent = count > 0
    except Exception:
        sent = False

    if sent:
        ContactMessage.objects.filter(pk=contact.pk).update(status=ContactMessage.Status.SENT, sent_at=timezone.now())
        contact.status = ContactMessage.Status.SENT
        contact.sent_at = timezone.now()

    return render(request, "core/contact_verified.html", {"contact": contact, "already": False, "sent": sent})




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
