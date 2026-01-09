# core/views/views.py
from __future__ import annotations

import logging

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.utils.translation import gettext_lazy as _
from django.http import HttpRequest

from core.forms import ContactForm
from core.services.hcaptcha import verify_hcaptcha
from config.settings.modules.antispam import rate_limit_reason_codes

logger = logging.getLogger(__name__)


def _get_client_ip(request: HttpRequest) -> str:
    """
    Récupère l'IP client en tenant compte des proxies.
    """
    x_forwarded_for = (request.META.get("HTTP_X_FORWARDED_FOR") or "").strip()
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return (request.META.get("REMOTE_ADDR") or "").strip()


def home_view(request):
    """Affiche la page d'accueil."""
    return render(request, "core/home.html")


def privacy_policy(request):
    """Affiche la politique de confidentialité."""
    return render(request, "core/privacy.html")


def cgu(request):
    """Affiche les conditions générales d'utilisation."""
    return render(request, "core/cgu.html")


def cookies_policy(request):
    """Affiche la politique des cookies."""
    return render(request, "core/cookies.html")


@require_http_methods(["GET", "POST"])
def contact_view(request):
    form = ContactForm(request.POST or None)

    h_enabled = bool(getattr(settings, "HCAPTCHA_ENABLED", False))
    h_sitekey = getattr(settings, "HCAPTCHA_SITEKEY", "") or ""
    fail_open = bool(getattr(settings, "HCAPTCHA_FAIL_OPEN", False))

    if request.method == "POST":
        ip = _get_client_ip(request)

        # 1) Rate limit (avant tout)
        email_guess = (request.POST.get("email") or "").strip().lower()
        rl_codes = rate_limit_reason_codes(ip=ip, email=email_guess)

        if rl_codes:
            messages.error(request, _("Trop de tentatives. Merci de réessayer dans quelques minutes."))
            if settings.DEBUG:
                messages.error(request, f"[{', '.join(rl_codes)}]")

            return render(
                request,
                "core/contact.html",
                {"form": form, "HCAPTCHA_ENABLED": h_enabled, "HCAPTCHA_SITEKEY": h_sitekey},
            )

        # 2) Vérification hCaptcha
        token = request.POST.get("h-captcha-response", "")
        ok, codes, unavailable = verify_hcaptcha(token=token, remoteip=ip)

        if not ok:
            if unavailable and fail_open:
                logger.warning(
                    "hCaptcha unavailable but FAIL_OPEN enabled; letting request pass. ip=%s codes=%s",
                    ip,
                    codes,
                )
            else:
                if settings.DEBUG and codes:
                    messages.error(
                        request,
                        f"{_('Vérification anti-spam (Captcha) échouée. Merci de réessayer.')} [{', '.join(codes)}]",
                    )
                else:
                    messages.error(request, _("Vérification anti-spam (Captcha) échouée. Merci de réessayer."))

                return render(
                    request,
                    "core/contact.html",
                    {"form": form, "HCAPTCHA_ENABLED": h_enabled, "HCAPTCHA_SITEKEY": h_sitekey},
                )

        # 3) Validation du formulaire
        if form.is_valid():
            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            message = form.cleaned_data["message"]

            full_message = f"Message de {name} <{email}>:\n\n{message}"

            contact_email = (getattr(settings, "CONTACT_EMAIL", "") or "").strip()
            if not contact_email:
                logger.error("CONTACT_EMAIL is not configured; cannot send contact form email.")
                messages.error(request, _("Configuration email manquante. Merci de réessayer plus tard."))
                return render(
                    request,
                    "core/contact.html",
                    {"form": form, "HCAPTCHA_ENABLED": h_enabled, "HCAPTCHA_SITEKEY": h_sitekey},
                )

            from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None) or getattr(settings, "SERVER_EMAIL", None) or None

            send_mail(
                subject=_("Nouveau message via le formulaire de contact"),
                message=full_message,
                from_email=from_email,
                recipient_list=[contact_email],
                fail_silently=False,
                headers={"Reply-To": email},
            )

            messages.success(request, _("Merci ! Votre message a bien été envoyé."))
            form = ContactForm()

    return render(
        request,
        "core/contact.html",
        {"form": form, "HCAPTCHA_ENABLED": h_enabled, "HCAPTCHA_SITEKEY": h_sitekey},
    )


# ------------------------
# Handlers d’erreurs HTTP
# ------------------------

def handler400(request, exception=None):
    return render(request, "400.html", status=400)


def handler404(request, exception=None):
    """Page d'erreur 404 : page non trouvée."""
    return render(request, "404.html", status=404)


def handler403(request, exception=None):
    """Page d'erreur 403 : accès interdit."""
    return render(request, "403.html", status=403)


def handler500(request, *args, **kwargs):
    """
    Page d'erreur 500 : erreur serveur.
    Handler SAFE (évite de masquer l'erreur d'origine si 500.html/base déclenche une exception).
    """
    try:
        return render(request, "500.html", status=500, context={"is_500": True})
    except Exception:
        from django.http import HttpResponseServerError
        return HttpResponseServerError("Internal Server Error")




# #core/views/views.py
# from django.conf import settings
# from django.contrib import messages
# from django.core.mail import send_mail
# from django.shortcuts import redirect, render
# from django.views.decorators.http import require_http_methods
# from django.utils.translation import gettext_lazy as _

# from core.forms import ContactForm


# def home_view(request):
#     """Render the home page."""
#     return render(request, "core/home.html")

# def privacy_policy(request):
#     return render(request, "core/privacy.html")

# def cgu(request):
#     return render(request, "core/cgu.html")

# def cookies_policy(request):
#     return render(request, "core/cookies.html")

# @require_http_methods(["GET", "POST"])
# def contact_view(request):
#     """Handle the contact form submission."""
#     form = ContactForm(request.POST or None)

#     if form.is_valid():
#         name = form.cleaned_data["name"]
#         email = form.cleaned_data["email"]
#         message = form.cleaned_data["message"]

#         full_message = f"Message de {name} <{email}>:\n\n{message}"

#         try:
#             send_mail(
#                 subject="Nouveau message via le formulaire de contact",
#                 message=full_message,
#                 from_email=settings.DEFAULT_FROM_EMAIL,
#                 recipient_list=[settings.CONTACT_EMAIL],
#                 fail_silently=False,
#             )
#             messages.success(request, "Votre message a bien été envoyé. Merci !")
#         except Exception as e:
#             messages.error(request, f"Une erreur est survenue : {str(e)}")

#         return redirect("core:contact")

#     return render(request, "core/contact.html", {"form": form})


# # ------------------------
# # Handlers d’erreurs HTTP
# # ------------------------

# def handler400(request, exception=None):
#     return render(request, "400.html", status=400)

# def handler404(request, exception):
#     """Page d’erreur 404 : page non trouvée."""
#     return render(request, "404.html", status=404)

# def handler403(request, exception=None):
#     """Page d’erreur 403 : accès interdit."""
#     return render(request, "403.html", status=403)

# def handler500(request):
#     """Page d’erreur 500 : erreur serveur."""
#     return render(request, "500.html", status=500)
