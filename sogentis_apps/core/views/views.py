# core/views/views.py
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from django.utils.translation import gettext_lazy as _

from core.forms import ContactForm

import logging
logger = logging.getLogger(__name__)


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
    """
    Gestion du formulaire de contact avec anti-spam et captcha.
    Toute la logique de validation est dans ContactForm.
    """
    form = ContactForm(request.POST or None, request=request)

    if request.method == "POST" and form.is_valid():
        name = form.cleaned_data["name"]
        email = form.cleaned_data["email"]
        message = form.cleaned_data["message"]

        full_message = f"Message de {name} <{email}>:\n\n{message}"

        try:
            send_mail(
                subject=_("Nouveau message via le formulaire de contact"),
                message=full_message,
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
                recipient_list=getattr(
                    settings,
                    "CONTACT_NOTIFY_EMAILS",
                    [getattr(settings, "DEFAULT_FROM_EMAIL", "")]
                ),
                fail_silently=False,
                # reply_to pour pouvoir répondre directement à l'expéditeur
                reply_to=[email],
            )
        except Exception:
            logger.exception("Erreur lors de l'envoi du mail de contact")
            messages.error(
                request,
                _("Une erreur est survenue lors de l'envoi. Merci de réessayer plus tard.")
            )
            return render(request, "core/contact.html", _contact_ctx(request, form))

        messages.success(request, _("Votre message a été envoyé avec succès. Merci !"))
        return redirect("core:contact")

    return render(request, "core/contact.html", _contact_ctx(request, form))


def _contact_ctx(request, form):
    """
    Contexte commun pour le template de contact, centralisant les captchas.
    """
    return {
        "form": form,
        "TURNSTILE_SITEKEY": getattr(settings, "TURNSTILE_SITEKEY", ""),
        "HCAPTCHA_SITEKEY": getattr(settings, "HCAPTCHA_SITEKEY", ""),
        "HCAPTCHA_THEME": getattr(settings, "HCAPTCHA_THEME", "light"),
        "HCAPTCHA_REQUIRED": bool(request.session.get("contact_need_hcaptcha", False)),
    }


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





# # core/views/views.py
# from django.conf import settings
# from django.contrib import messages
# from django.core.mail import send_mail
# from django.shortcuts import redirect, render
# from django.views.decorators.http import require_http_methods
# from django.utils.translation import gettext_lazy as _

# from core.forms import ContactForm

# import logging
# logger = logging.getLogger(__name__)


# def home_view(request):
#     return render(request, "core/home.html")


# def privacy_policy(request):
#     return render(request, "core/privacy.html")


# def cgu(request):
#     return render(request, "core/cgu.html")


# def cookies_policy(request):
#     return render(request, "core/cookies.html")


# @require_http_methods(["GET", "POST"])
# def contact_view(request):
#     """
#     Toute la validation (anti-spam, captcha, DNS, honeypot)
#     est gérée dans ContactForm.
#     """
#     form = ContactForm(request.POST or None, request=request)

#     if request.method == "POST" and form.is_valid():
#         name = form.cleaned_data["name"]
#         email = form.cleaned_data["email"]
#         message = form.cleaned_data["message"]

#         full_message = f"Message de {name} <{email}>:\n\n{message}"

#         try:
#             send_mail(
#                 subject=_("Nouveau message via le formulaire de contact"),
#                 message=full_message,
#                 from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
#                 recipient_list=getattr(
#                     settings,
#                     "CONTACT_NOTIFY_EMAILS",
#                     [getattr(settings, "DEFAULT_FROM_EMAIL", "")]
#                 ),
#                 reply_to=[email],
#                 fail_silently=False,
#             )
#         except Exception:
#             logger.exception("Erreur lors de l’envoi du mail de contact")
#             messages.error(
#                 request,
#                 _("Une erreur est survenue lors de l’envoi. Merci de réessayer plus tard.")
#             )
#             return render(request, "core/contact.html", _contact_ctx(request, form))

#         messages.success(request, _("Votre message a été envoyé avec succès. Merci !"))
#         return redirect("core:contact")

#     return render(request, "core/contact.html", _contact_ctx(request, form))


# def _contact_ctx(request, form):
#     """
#     Contexte captcha centralisé
#     """
#     return {
#         "form": form,
#         "TURNSTILE_SITEKEY": getattr(settings, "TURNSTILE_SITEKEY", ""),
#         "HCAPTCHA_SITEKEY": getattr(settings, "HCAPTCHA_SITEKEY", ""),
#         "HCAPTCHA_THEME": getattr(settings, "HCAPTCHA_THEME", "light"),
#         "HCAPTCHA_REQUIRED": bool(
#             request.session.get("contact_need_hcaptcha", False)
#         ),
#     }


# # ------------------------
# # Handlers d’erreurs HTTP
# # ------------------------

# def handler400(request, exception=None):
#     return render(request, "400.html", status=400)


# def handler404(request, exception=None):
#     return render(request, "404.html", status=404)


# def handler403(request, exception=None):
#     return render(request, "403.html", status=403)


# def handler500(request, *args, **kwargs):
#     try:
#         return render(request, "500.html", status=500, context={"is_500": True})
#     except Exception:
#         from django.http import HttpResponseServerError
#         return HttpResponseServerError("Internal Server Error")





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
