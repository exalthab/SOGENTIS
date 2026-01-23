# accounts_users/web/views/economic/registration_economic.py
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict
from urllib.parse import urlencode

from django.contrib import messages
from django.db import IntegrityError, transaction
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods

from accounts_users.forms.economic.economic_core_registration import UserProfileEconomicForm
from accounts_users.forms.economic.economic_signup_forms import (
    ClientSignupForm,
    VendorSignupForm,
    CompanySignupForm,
)
from accounts_users.forms.signup_forms import UserSignupForm
from accounts_users.web.views._helpers import build_auth_context, validate_latest_email_otp_or_add_error

logger = logging.getLogger(__name__)
DEFAULT_TRACK = "client"

# SAFE FALLBACKS
try:
    from accounts_users.models.user_role import EconomicRole
except Exception:
    EconomicRole = None


@dataclass(frozen=True)
class TrackInfo:
    code: str
    title: str
    subtitle: str
    badge: str


TRACKS: Dict[str, TrackInfo] = {
    "client": TrackInfo(
        "client",
        _("Compte Client (B2C)"),
        _("Acheter, gérer panier/favoris, suivre commandes et accéder aux services."),
        "🛒",
    ),
    "vendor": TrackInfo(
        "vendor",
        _("Espace Vendeur"),
        _("Vendre des produits, gérer catalogue, stock et commandes."),
        "🏪",
    ),
    "b2b": TrackInfo(
        "b2b",
        _("Compte Entreprise (B2B)"),
        _("Commandes en gros, RFQ, facturation et gestion d’entreprise."),
        "🏢",
    ),
}

ECONOMIC_REGISTRATION_MAP = {
    "client": {
        "label": _("Client"),
        "role": getattr(EconomicRole, "CLIENT", "CLIENT"),
        "form": ClientSignupForm,
        "requires_validation": False,
    },
    "vendor": {
        "label": _("Vendeur"),
        "role": getattr(EconomicRole, "VENDOR", "VENDOR"),
        "form": VendorSignupForm,
        "requires_validation": True,
    },
    "b2b": {
        "label": _("Entreprise"),
        "role": getattr(EconomicRole, "B2B", "B2B"),
        "form": CompanySignupForm,
        "requires_validation": True,
    },
}


def _get_track_code(request: HttpRequest) -> str:
    """
    Détermine le parcours économique.
    Accepte track (POST/GET) ou type (GET) pour compat templates.
    """
    raw = (
        request.POST.get("track")
        or request.GET.get("track")
        or request.GET.get("type")
        or DEFAULT_TRACK
    )
    raw = (raw or DEFAULT_TRACK).strip().lower()
    return raw if raw in ECONOMIC_REGISTRATION_MAP else DEFAULT_TRACK


def _safe_next(request: HttpRequest) -> str:
    """
    Sécurise ?next= (ou POST next) pour éviter les open redirects.
    Retourne "" si invalide.
    """
    nxt = (request.POST.get("next") or request.GET.get("next") or "").strip()
    if nxt and url_has_allowed_host_and_scheme(
        url=nxt,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return nxt
    return ""


def _render_form(
    request: HttpRequest,
    *,
    user_form,
    profile_form,
    economic_form,
    economic_type: str,
    next_url: str,
) -> HttpResponse:
    track_info = TRACKS.get(economic_type, TRACKS[DEFAULT_TRACK])
    config = ECONOMIC_REGISTRATION_MAP.get(economic_type, ECONOMIC_REGISTRATION_MAP[DEFAULT_TRACK])

    ctx = {
        "user_form": user_form,
        "profile_form": profile_form,
        "economic_form": economic_form,
        "economic_type": economic_type,
        "track": economic_type,  # compat template
        "track_title": track_info.title,
        "track_subtitle": track_info.subtitle,
        "track_badge": track_info.badge,
        "page_title": track_info.title,  # utile pour les fallbacks template
        "economic_config": config,
        "next": next_url,
        **build_auth_context("economic"),
    }
    return render(request, "accounts_users/registration/register_economic_form.html", ctx)


@require_http_methods(["GET", "POST"])
def register_economic_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        messages.info(request, _("Vous êtes déjà connecté."))
        return redirect("dashboard:hub")

    economic_type = _get_track_code(request)
    config = ECONOMIC_REGISTRATION_MAP[economic_type]
    next_url = _safe_next(request)

    user_form = UserSignupForm(request.POST or None)
    profile_form = UserProfileEconomicForm(request.POST or None, request.FILES or None)
    economic_form = config["form"](request.POST or None, request.FILES or None)

    if request.method == "POST":
        if user_form.is_valid() and profile_form.is_valid() and economic_form.is_valid():
            email = (user_form.cleaned_data.get("email") or "").strip().lower()
            otp_code = (user_form.cleaned_data.get("email_otp_code") or "").strip()

            if not validate_latest_email_otp_or_add_error(
                request,
                email=email,
                otp_code=otp_code,
                form=user_form,
                field_name="email_otp_code",
            ):
                messages.error(request, _("Le code OTP est invalide, expiré, ou incorrect."))
                return _render_form(
                    request,
                    user_form=user_form,
                    profile_form=profile_form,
                    economic_form=economic_form,
                    economic_type=economic_type,
                    next_url=next_url,
                )

            try:
                with transaction.atomic():
                    user = user_form.save(commit=False)
                    # OTP email OK -> user actif (validation vendeurs/b2b se fait via profil)
                    user.is_active = True
                    user.save()

                    profile = profile_form.save(commit=False)
                    profile.user = user

                    if hasattr(profile, "economic_role"):
                        profile.economic_role = config["role"]

                    if config["requires_validation"]:
                        if hasattr(profile, "is_validated"):
                            profile.is_validated = False
                        if hasattr(profile, "validation_status"):
                            profile.validation_status = "PENDING"
                    else:
                        if hasattr(profile, "is_validated"):
                            profile.is_validated = True
                        if hasattr(profile, "validation_status"):
                            profile.validation_status = "APPROVED"

                    profile.save()

                    econ_profile = economic_form.save(commit=False)
                    if hasattr(econ_profile, "profile"):
                        econ_profile.profile = profile
                    if hasattr(econ_profile, "user"):
                        econ_profile.user = user
                    econ_profile.save()

            except IntegrityError:
                messages.error(request, _("Cette adresse email est déjà utilisée."))
                return _render_form(
                    request,
                    user_form=user_form,
                    profile_form=profile_form,
                    economic_form=economic_form,
                    economic_type=economic_type,
                    next_url=next_url,
                )
            except Exception:
                logger.exception("Erreur création compte économique (type=%s)", economic_type)
                messages.error(request, _("Une erreur est survenue lors de la création du compte."))
                return _render_form(
                    request,
                    user_form=user_form,
                    profile_form=profile_form,
                    economic_form=economic_form,
                    economic_type=economic_type,
                    next_url=next_url,
                )

            if config["requires_validation"]:
                messages.success(request, _("Compte créé. Votre profil est en attente de validation."))
            else:
                messages.success(request, _("Votre compte a été créé avec succès."))

            # Redirection login standard avec context=economic
            login_url = reverse("accounts_users:web:auth:login")
            qs = {"context": "economic"}
            if next_url:
                qs["next"] = next_url
            return redirect(f"{login_url}?{urlencode(qs)}")

        messages.error(request, _("Veuillez corriger les erreurs du formulaire."))

    return _render_form(
        request,
        user_form=user_form,
        profile_form=profile_form,
        economic_form=economic_form,
        economic_type=economic_type,
        next_url=next_url,
    )







# # accounts_users/web/views/economic/registration_economic.py
# from __future__ import annotations

# import logging
# from dataclasses import dataclass
# from typing import Dict
# from urllib.parse import urlencode

# from django.conf import settings
# from django.contrib import messages
# from django.db import IntegrityError, transaction
# from django.http import HttpRequest, HttpResponse
# from django.shortcuts import redirect, render
# from django.urls import reverse
# from django.utils.http import url_has_allowed_host_and_scheme
# from django.utils.translation import gettext_lazy as _
# from django.views.decorators.http import require_http_methods

# from accounts_users.forms.economic.economic_core_registration import UserProfileEconomicForm
# from accounts_users.forms.economic.economic_signup_forms import (
#     ClientSignupForm,
#     VendorSignupForm,
#     CompanySignupForm,
# )
# from accounts_users.forms.signup_forms import UserSignupForm
# from accounts_users.web.views._helpers import build_auth_context, validate_latest_email_otp_or_add_error

# logger = logging.getLogger(__name__)

# # SAFE FALLBACKS
# try:
#     from accounts_users.models.user_role import EconomicRole
# except Exception:
#     EconomicRole = None


# @dataclass(frozen=True)
# class TrackInfo:
#     code: str
#     title: str
#     subtitle: str
#     badge: str


# TRACKS: Dict[str, TrackInfo] = {
#     "client": TrackInfo(
#         "client",
#         _("Compte Client (B2C)"),
#         _("Acheter, gérer panier/favoris, suivre commandes et accéder aux services."),
#         "🛒",
#     ),
#     "vendor": TrackInfo(
#         "vendor",
#         _("Espace Vendeur"),
#         _("Vendre des produits, gérer catalogue, stock et commandes."),
#         "🏪",
#     ),
#     "b2b": TrackInfo(
#         "b2b",
#         _("Compte Entreprise (B2B)"),
#         _("Commandes en gros, RFQ, facturation et gestion d’entreprise."),
#         "🏢",
#     ),
# }

# ECONOMIC_REGISTRATION_MAP = {
#     "client": {
#         "label": _("Client"),
#         "role": getattr(EconomicRole, "CLIENT", "CLIENT"),
#         "form": ClientSignupForm,
#         "requires_validation": False,
#     },
#     "vendor": {
#         "label": _("Vendeur"),
#         "role": getattr(EconomicRole, "VENDOR", "VENDOR"),
#         "form": VendorSignupForm,
#         "requires_validation": True,
#     },
#     "b2b": {
#         "label": _("Entreprise"),
#         "role": getattr(EconomicRole, "B2B", "B2B"),
#         "form": CompanySignupForm,
#         "requires_validation": True,
#     },
# }


# def _get_track_code(request: HttpRequest) -> str:
#     # On accepte track OU type (pour compat avec templates)
#     raw = (
#         request.POST.get("track")
#         or request.GET.get("track")
#         or request.GET.get("type")
#         or "client"
#     )
#     raw = (raw or "client").strip().lower()
#     return raw if raw in ECONOMIC_REGISTRATION_MAP else "client"


# def _safe_next(request: HttpRequest) -> str:
#     nxt = (request.POST.get("next") or request.GET.get("next") or "").strip()
#     if nxt and url_has_allowed_host_and_scheme(
#         url=nxt,
#         allowed_hosts={request.get_host()},
#         require_https=request.is_secure(),
#     ):
#         return nxt
#     return ""


# def _render_form(request, *, user_form, profile_form, economic_form, economic_type: str, next_url: str):
#     track_info = TRACKS.get(economic_type, TRACKS["client"])
#     config = ECONOMIC_REGISTRATION_MAP.get(economic_type)

#     ctx = {
#         "user_form": user_form,
#         "profile_form": profile_form,
#         "economic_form": economic_form,
#         "economic_type": economic_type,
#         "track": economic_type,
#         "track_title": track_info.title,
#         "track_subtitle": track_info.subtitle,
#         "track_badge": track_info.badge,
#         "economic_config": config,
#         "next": next_url,
#         **build_auth_context("economic"),
#     }
#     return render(request, "accounts_users/registration/register_economic_form.html", ctx)


# @require_http_methods(["GET", "POST"])
# def register_economic_view(request: HttpRequest) -> HttpResponse:
#     if request.user.is_authenticated:
#         messages.info(request, _("Vous êtes déjà connecté."))
#         return redirect("dashboard:hub")

#     economic_type = _get_track_code(request)
#     config = ECONOMIC_REGISTRATION_MAP[economic_type]
#     next_url = _safe_next(request)

#     user_form = UserSignupForm(request.POST or None)
#     profile_form = UserProfileEconomicForm(request.POST or None, request.FILES or None)
#     economic_form = config["form"](request.POST or None, request.FILES or None)

#     if request.method == "POST":
#         if user_form.is_valid() and profile_form.is_valid() and economic_form.is_valid():
#             email = (user_form.cleaned_data.get("email") or "").strip().lower()
#             otp_code = (user_form.cleaned_data.get("email_otp_code") or "").strip()

#             if not validate_latest_email_otp_or_add_error(
#                 request,
#                 email=email,
#                 otp_code=otp_code,
#                 form=user_form,
#                 field_name="email_otp_code",
#             ):
#                 messages.error(request, _("Le code OTP est invalide, expiré, ou incorrect."))
#                 return _render_form(
#                     request,
#                     user_form=user_form,
#                     profile_form=profile_form,
#                     economic_form=economic_form,
#                     economic_type=economic_type,
#                     next_url=next_url,
#                 )

#             try:
#                 with transaction.atomic():
#                     user = user_form.save(commit=False)
#                     # OTP email OK -> user actif (la validation vendeurs/b2b se fait via profil)
#                     user.is_active = True
#                     user.save()

#                     profile = profile_form.save(commit=False)
#                     profile.user = user

#                     if hasattr(profile, "economic_role"):
#                         profile.economic_role = config["role"]

#                     if config["requires_validation"]:
#                         if hasattr(profile, "is_validated"):
#                             profile.is_validated = False
#                         if hasattr(profile, "validation_status"):
#                             profile.validation_status = "PENDING"
#                     else:
#                         if hasattr(profile, "is_validated"):
#                             profile.is_validated = True
#                         if hasattr(profile, "validation_status"):
#                             profile.validation_status = "APPROVED"

#                     profile.save()

#                     econ_profile = economic_form.save(commit=False)
#                     if hasattr(econ_profile, "profile"):
#                         econ_profile.profile = profile
#                     if hasattr(econ_profile, "user"):
#                         econ_profile.user = user
#                     econ_profile.save()

#             except IntegrityError:
#                 messages.error(request, _("Cette adresse email est déjà utilisée."))
#                 return _render_form(
#                     request,
#                     user_form=user_form,
#                     profile_form=profile_form,
#                     economic_form=economic_form,
#                     economic_type=economic_type,
#                     next_url=next_url,
#                 )
#             except Exception:
#                 logger.exception("Erreur création compte économique (type=%s)", economic_type)
#                 messages.error(request, _("Une erreur est survenue lors de la création du compte."))
#                 return _render_form(
#                     request,
#                     user_form=user_form,
#                     profile_form=profile_form,
#                     economic_form=economic_form,
#                     economic_type=economic_type,
#                     next_url=next_url,
#                 )

#             if config["requires_validation"]:
#                 messages.success(request, _("Compte créé. Votre profil est en attente de validation."))
#             else:
#                 messages.success(request, _("Votre compte a été créé avec succès."))

#             # Redirection login standard avec context=economic
#             login_url = reverse("accounts_users:web:auth:login")
#             qs = {"context": "economic"}
#             if next_url:
#                 qs["next"] = next_url
#             return redirect(f"{login_url}?{urlencode(qs)}")

#         messages.error(request, _("Veuillez corriger les erreurs du formulaire."))

#     return _render_form(
#         request,
#         user_form=user_form,
#         profile_form=profile_form,
#         economic_form=economic_form,
#         economic_type=economic_type,
#         next_url=next_url,
#     )





# # accounts_users/web/views/economic/registration_economic.py
# from __future__ import annotations

# import logging
# from dataclasses import dataclass
# from typing import Dict, Type
# from urllib.parse import urlencode

# from django.conf import settings
# from django.contrib import messages
# from django.db import IntegrityError, transaction
# from django.http import HttpRequest, HttpResponse
# from django.shortcuts import redirect, render
# from django.template.loader import render_to_string
# from django.urls import reverse
# from django.utils.encoding import force_bytes
# from django.utils.http import url_has_allowed_host_and_scheme, urlsafe_base64_encode
# from django.utils.translation import gettext_lazy as _
# from django.views.decorators.http import require_http_methods

# from accounts_users.tokens import account_activation_token
# from accounts_users.forms.economic.economic_core_registration import UserProfileEconomicForm
# from accounts_users.forms.economic.economic_signup_forms import (
#     ClientSignupForm,
#     VendorSignupForm,
#     CompanySignupForm,
# )
# from accounts_users.forms.signup_forms import UserSignupForm

# # SAFE FALLBACKS
# try:
#     from accounts_users.models.user_role import EconomicRole
# except Exception:
#     EconomicRole = None

# try:
#     from accounts_users.models.users_economic_profile import UserEconomicProfile
# except Exception:
#     UserEconomicProfile = None

# # HELPERS
# from accounts_users.web.views._helpers import build_auth_context, validate_latest_email_otp_or_add_error

# logger = logging.getLogger(__name__)

# # ---------------------------------------------------------------------
# # TRACKS & CONFIGURATION
# # ---------------------------------------------------------------------
# @dataclass(frozen=True)
# class TrackInfo:
#     code: str
#     title: str
#     subtitle: str
#     badge: str


# TRACKS: Dict[str, TrackInfo] = {
#     "client": TrackInfo(
#         "client",
#         _("Compte Client (B2C)"),
#         _("Acheter, gérer panier/favoris, suivre commandes et accéder aux services."),
#         "🛒",
#     ),
#     "vendor": TrackInfo(
#         "vendor",
#         _("Espace Vendeur"),
#         _("Vendre des produits, gérer catalogue, stock et commandes."),
#         "🏪",
#     ),
#     "b2b": TrackInfo(
#         "b2b",
#         _("Compte Entreprise (B2B)"),
#         _("Commandes en gros, RFQ, facturation et gestion d’entreprise."),
#         "🏢",
#     ),
# }

# ECONOMIC_REGISTRATION_MAP = {
#     "client": {
#         "label": _("Client"),
#         "role": getattr(EconomicRole, "CLIENT", None),
#         "form": ClientSignupForm,
#         "requires_validation": False,
#     },
#     "vendor": {
#         "label": _("Vendeur"),
#         "role": getattr(EconomicRole, "VENDOR", None),
#         "form": VendorSignupForm,
#         "requires_validation": True,
#     },
#     "b2b": {
#         "label": _("Entreprise"),
#         "role": getattr(EconomicRole, "B2B", None),
#         "form": CompanySignupForm,
#         "requires_validation": True,
#     },
# }


# def _get_track(request: HttpRequest) -> TrackInfo:
#     raw = (request.POST.get("track") or request.GET.get("track") or "client").strip().lower()
#     return TRACKS.get(raw, TRACKS["client"])


# def _safe_next(request: HttpRequest) -> str:
#     nxt = (request.POST.get("next") or request.GET.get("next") or "").strip()
#     if nxt and url_has_allowed_host_and_scheme(
#         url=nxt,
#         allowed_hosts={request.get_host()},
#         require_https=request.is_secure(),
#     ):
#         return nxt
#     return ""


# # ---------------------------------------------------------------------
# # CHOICE VIEW
# # ---------------------------------------------------------------------
# def register_economic_choice_view(request: HttpRequest) -> HttpResponse:
#     return render(
#         request,
#         "accounts_users/registration/register_economic_choice.html",
#         {**build_auth_context("economic"), "choices": ECONOMIC_REGISTRATION_MAP},
#     )


# # ---------------------------------------------------------------------
# # EMAIL ACTIVATION
# # ---------------------------------------------------------------------
# def _send_activation_email(request: HttpRequest, user) -> bool:
#     uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
#     token = account_activation_token.make_token(user)

#     activation_url = request.build_absolute_uri(
#         reverse(
#             "accounts_users:web:registration:activate",
#             kwargs={"uidb64": uidb64, "token": token},
#         )
#     )

#     context = {
#         "user": user,
#         "activation_url": activation_url,
#         "PROJECT_NAME": getattr(settings, "PROJECT_NAME", "SOGENTIS"),
#     }

#     try:
#         html = render_to_string("accounts_users/registration/account_activation_email.html", context)
#         text = render_to_string("accounts_users/registration/account_activation_email.txt", context)

#         from django.core.mail import EmailMultiAlternatives

#         msg = EmailMultiAlternatives(
#             subject=_("Activation de votre compte"),
#             body=text,
#             from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
#             to=[user.email],
#         )
#         msg.attach_alternative(html, "text/html")
#         msg.send(fail_silently=False)
#         return True

#     except Exception:
#         logger.exception("Activation email failed (economic)")
#         return False


# # ---------------------------------------------------------------------
# # FORM RENDER HELPER
# # ---------------------------------------------------------------------
# def _render_form(request, *, user_form, profile_form, economic_form, economic_type):
#     config = ECONOMIC_REGISTRATION_MAP.get(economic_type)
#     ctx = {
#         "user_form": user_form,
#         "profile_form": profile_form,
#         "economic_form": economic_form,
#         "economic_type": economic_type,
#         "economic_config": config,
#         **build_auth_context("economic"),
#     }
#     return render(request, "accounts_users/registration/register_economic_form.html", ctx)


# # ---------------------------------------------------------------------
# # MAIN VIEW
# # ---------------------------------------------------------------------
# @require_http_methods(["GET", "POST"])
# def register_economic_view(request: HttpRequest) -> HttpResponse:
#     if request.user.is_authenticated:
#         messages.info(request, _("Vous êtes déjà connecté."))
#         return redirect("dashboard:hub")

#     economic_type = (request.GET.get("type") or "").strip().lower()
#     if economic_type not in ECONOMIC_REGISTRATION_MAP:
#         messages.error(request, _("Type de compte économique invalide."))
#         return redirect("accounts_users:web:registration:choice")

#     config = ECONOMIC_REGISTRATION_MAP[economic_type]

#     user_form = UserSignupForm(request.POST or None)
#     profile_form = UserProfileEconomicForm(request.POST or None, request.FILES or None)
#     economic_form = config["form"](request.POST or None, request.FILES or None)

#     if request.method == "POST":
#         if user_form.is_valid() and profile_form.is_valid() and economic_form.is_valid():
#             email = (user_form.cleaned_data.get("email") or "").strip().lower()
#             otp_code = (user_form.cleaned_data.get("email_otp_code") or "").strip()

#             # OTP validation (file2 feature)
#             if not validate_latest_email_otp_or_add_error(
#                 request,
#                 email=email,
#                 otp_code=otp_code,
#                 form=user_form,
#                 field_name="email_otp_code",
#             ):
#                 messages.error(request, _("Le code OTP est invalide, expiré, ou incorrect."))
#                 return _render_form(
#                     request,
#                     user_form=user_form,
#                     profile_form=profile_form,
#                     economic_form=economic_form,
#                     economic_type=economic_type,
#                 )

#             try:
#                 with transaction.atomic():
#                     # Création utilisateur
#                     user = user_form.save(commit=False)
#                     user.is_active = not config["requires_validation"]
#                     user.save()

#                     # Profil économique central
#                     profile = profile_form.save(commit=False)
#                     profile.user = user
#                     profile.economic_role = config["role"]

#                     if config["requires_validation"]:
#                         if hasattr(profile, "is_validated"):
#                             profile.is_validated = False
#                         if hasattr(profile, "validation_status"):
#                             profile.validation_status = "PENDING"
#                     else:
#                         if hasattr(profile, "is_validated"):
#                             profile.is_validated = True
#                         if hasattr(profile, "validation_status"):
#                             profile.validation_status = "APPROVED"

#                     profile.save()

#                     # Profil spécifique track
#                     econ_profile = economic_form.save(commit=False)
#                     if hasattr(econ_profile, "profile"):
#                         econ_profile.profile = profile
#                     if hasattr(econ_profile, "user"):
#                         econ_profile.user = user
#                     econ_profile.save()

#             except Exception:
#                 logger.exception("Erreur création compte économique (type=%s)", economic_type)
#                 messages.error(request, _("Une erreur est survenue lors de la création du compte."))
#                 return redirect("accounts_users:web:registration:choice")

#             if config["requires_validation"]:
#                 messages.success(request, _("Votre compte a été créé. Activation après validation."))
#             else:
#                 messages.success(request, _("Votre compte a été créé avec succès."))

#             return redirect("accounts_users:web:login_economic")

#         messages.error(request, _("Veuillez corriger les erreurs du formulaire."))

#     return _render_form(
#         request,
#         user_form=user_form,
#         profile_form=profile_form,
#         economic_form=economic_form,
#         economic_type=economic_type,
#     )






# # accounts_users/web/views/economic/registration_economic.py
# from __future__ import annotations

# import logging
# from dataclasses import dataclass
# from typing import Dict, Type
# from urllib.parse import urlencode

# from django.conf import settings
# from django.contrib import messages
# from django.db import IntegrityError, transaction
# from django.http import HttpRequest, HttpResponse
# from django.shortcuts import redirect, render
# from django.template.loader import render_to_string
# from django.urls import reverse
# from django.utils.encoding import force_bytes
# from django.utils.http import url_has_allowed_host_and_scheme, urlsafe_base64_encode
# from django.utils.translation import gettext_lazy as _

# from accounts_users.tokens import account_activation_token
# from accounts_users.forms.economic.economic_core_registration import UserProfileEconomicForm
# from accounts_users.forms.economic.economic_signup_forms import (
#     ClientSignupForm,
#     VendorSignupForm,
#     CompanySignupForm,
# )

# logger = logging.getLogger(__name__)

# # ---------------------------------------------------------------------
# # USER FORM (fallback SAFE)
# # ---------------------------------------------------------------------
# try:
#     from accounts_users.forms.signup_forms import UserSignupForm  # type: ignore
# except Exception:
#     from accounts_users.forms.social.social_signup_forms import UserSignupForm  # type: ignore


# # ---------------------------------------------------------------------
# # TRACKS
# # ---------------------------------------------------------------------
# @dataclass(frozen=True)
# class TrackInfo:
#     code: str
#     title: str
#     subtitle: str
#     badge: str


# TRACKS: Dict[str, TrackInfo] = {
#     "client": TrackInfo(
#         "client",
#         _("Compte Client (B2C)"),
#         _("Acheter, gérer panier/favoris, suivre commandes et accéder aux services."),
#         "🛒",
#     ),
#     "vendor": TrackInfo(
#         "vendor",
#         _("Espace Vendeur"),
#         _("Vendre des produits, gérer catalogue, stock et commandes."),
#         "🏪",
#     ),
#     "b2b": TrackInfo(
#         "b2b",
#         _("Compte Entreprise (B2B)"),
#         _("Commandes en gros, RFQ, facturation et gestion d’entreprise."),
#         "🏢",
#     ),
# }


# def _get_track(request: HttpRequest) -> TrackInfo:
#     raw = (request.POST.get("track") or request.GET.get("track") or "client").strip().lower()
#     return TRACKS.get(raw, TRACKS["client"])


# def _safe_next(request: HttpRequest) -> str:
#     nxt = (request.POST.get("next") or request.GET.get("next") or "").strip()
#     if nxt and url_has_allowed_host_and_scheme(
#         url=nxt,
#         allowed_hosts={request.get_host()},
#         require_https=request.is_secure(),
#     ):
#         return nxt
#     return ""


# # ---------------------------------------------------------------------
# # REDIRECT CHOICE (legacy compatible)
# # ---------------------------------------------------------------------
# def register_economic_choice_view(request: HttpRequest) -> HttpResponse:
#     next_url = _safe_next(request)
#     base = reverse("accounts_users:web:registration:choice")
#     params = {"focus": "economic"}
#     if next_url:
#         params["next"] = next_url
#     return redirect(f"{base}?{urlencode(params)}#economic")


# # ---------------------------------------------------------------------
# # ECONOMIC ROLE / VALIDATION (SAFE)
# # ---------------------------------------------------------------------
# try:
#     from accounts_users.models.user_role import EconomicRole  # type: ignore
# except Exception:
#     EconomicRole = None


# ECONOMIC_ADVANCED_MAP = {
#     "client": {"role": getattr(EconomicRole, "CLIENT", None), "requires_validation": False},
#     "vendor": {"role": getattr(EconomicRole, "VENDOR", None), "requires_validation": True},
#     "b2b": {"role": getattr(EconomicRole, "B2B", None), "requires_validation": True},
# }


# def _try_create_or_update_economic_profile(user, track_code: str, profile_instance=None) -> None:
#     try:
#         from accounts_users.models.users_economic_profile import UserEconomicProfile  # type: ignore
#     except Exception:
#         return

#     profile = profile_instance or UserEconomicProfile.objects.get_or_create(user=user)[0]
#     config = ECONOMIC_ADVANCED_MAP.get(track_code) or {}

#     role = config.get("role")
#     requires_validation = bool(config.get("requires_validation"))

#     if role is not None and hasattr(profile, "economic_role"):
#         profile.economic_role = role

#     if requires_validation:
#         if hasattr(profile, "is_validated"):
#             profile.is_validated = False
#         if hasattr(profile, "validation_status"):
#             profile.validation_status = "PENDING"
#     else:
#         if hasattr(profile, "is_validated"):
#             profile.is_validated = True
#         if hasattr(profile, "validation_status"):
#             profile.validation_status = "APPROVED"

#     profile.save()


# # ---------------------------------------------------------------------
# # EMAIL ACTIVATION
# # ---------------------------------------------------------------------
# def _send_activation_email(request: HttpRequest, user) -> bool:
#     uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
#     token = account_activation_token.make_token(user)

#     activation_url = request.build_absolute_uri(
#         reverse(
#             "accounts_users:web:registration:activate",
#             kwargs={"uidb64": uidb64, "token": token},
#         )
#     )

#     context = {
#         "user": user,
#         "activation_url": activation_url,
#         "PROJECT_NAME": getattr(settings, "PROJECT_NAME", "SOGENTIS"),
#     }

#     try:
#         html = render_to_string("accounts_users/registration/account_activation_email.html", context)
#         text = render_to_string("accounts_users/registration/account_activation_email.txt", context)

#         from django.core.mail import EmailMultiAlternatives

#         msg = EmailMultiAlternatives(
#             subject=_("Activation de votre compte"),
#             body=text,
#             from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
#             to=[user.email],
#         )
#         msg.attach_alternative(html, "text/html")
#         msg.send(fail_silently=False)
#         return True

#     except Exception:
#         logger.exception("Activation email failed (economic)")
#         return False


# # ---------------------------------------------------------------------
# # MAIN VIEW (PROD READY)
# # ---------------------------------------------------------------------
# def register_economic_view(request: HttpRequest) -> HttpResponse:
#     if request.user.is_authenticated:
#         messages.info(request, _("Vous êtes déjà connecté."))
#         return redirect("dashboard:hub")

#     track = _get_track(request)
#     next_url = _safe_next(request)

#     economic_form_class: Type = ClientSignupForm
#     if track.code == "vendor":
#         economic_form_class = VendorSignupForm
#     elif track.code == "b2b":
#         economic_form_class = CompanySignupForm

#     if request.method == "POST":
#         user_form = UserSignupForm(request.POST)
#         profile_form = UserProfileEconomicForm(request.POST, request.FILES)
#         economic_form = economic_form_class(request.POST, request.FILES)

#         if user_form.is_valid() and profile_form.is_valid() and economic_form.is_valid():
#             try:
#                 with transaction.atomic():
#                     # USER
#                     user = user_form.save(commit=False)
#                     user.is_active = False
#                     user.save()

#                     # PROFIL ÉCONOMIQUE CENTRAL
#                     eco_profile = profile_form.save(user=user, commit=True)

#                     # PROFIL TRACK (SAFE)
#                     obj = economic_form.save(commit=False)
#                     if hasattr(obj, "user"):
#                         obj.user = user
#                     if hasattr(obj, "profile"):
#                         obj.profile = eco_profile
#                     if hasattr(obj, "economic_profile"):
#                         obj.economic_profile = eco_profile
#                     if hasattr(obj, "user_profile"):
#                         obj.user_profile = eco_profile
#                     obj.save()

#                     if hasattr(economic_form, "save_m2m"):
#                         economic_form.save_m2m()

#                     _try_create_or_update_economic_profile(user, track.code, eco_profile)

#             except IntegrityError:
#                 messages.error(
#                     request,
#                     _("Impossible de finaliser l’inscription (données déjà utilisées)."),
#                 )
#             else:
#                 if _send_activation_email(request, user):
#                     messages.success(
#                         request,
#                         _("Inscription réussie. Un email d’activation vous a été envoyé."),
#                     )
#                 else:
#                     messages.warning(
#                         request,
#                         _("Compte créé, mais l’envoi de l’email d’activation a échoué."),
#                     )

#                 request.session["ECONOMIC_TRACK"] = track.code
#                 if next_url:
#                     request.session["POST_AUTH_NEXT"] = next_url
#                 request.session.modified = True

#                 return redirect("accounts_users:web:registration:register_done")

#         else:
#             messages.error(request, _("Veuillez corriger les erreurs du formulaire."))

#     else:
#         user_form = UserSignupForm()
#         profile_form = UserProfileEconomicForm()
#         economic_form = economic_form_class()

#     return render(
#         request,
#         "accounts_users/registration/register_economic_form.html",
#         {
#             "user_form": user_form,
#             "profile_form": profile_form,
#             "economic_form": economic_form,
#             "track": track.code,
#             "economic_type": track.code,  # compat templates legacy
#             "track_title": track.title,
#             "track_subtitle": track.subtitle,
#             "track_badge": track.badge,
#             "next": next_url,
#             "page_title": _("Inscription — Pôle économique"),
#         },
#     )







# # accounts_users/web/views/economic/registration_economic.py
# from __future__ import annotations

# import logging
# from dataclasses import dataclass
# from typing import Dict, Type
# from urllib.parse import urlencode

# from django.conf import settings
# from django.contrib import messages
# from django.http import HttpRequest, HttpResponse
# from django.shortcuts import redirect, render
# from django.template.loader import render_to_string
# from django.urls import reverse
# from django.utils.encoding import force_bytes
# from django.utils.http import url_has_allowed_host_and_scheme, urlsafe_base64_encode
# from django.utils.translation import gettext_lazy as _

# from accounts_users.tokens import account_activation_token

# from accounts_users.forms.economic.economic_core_registration import UserProfileEconomicForm
# from accounts_users.forms.economic.economic_signup_forms import (
#     ClientSignupForm,
#     VendorSignupForm,
#     CompanySignupForm,
# )

# logger = logging.getLogger(__name__)

# # --- User form (fallbacks selon ta base) ---
# try:
#     # si tu as déjà un forms/signup_forms.py
#     from accounts_users.forms.signup_forms import UserSignupForm  # type: ignore
# except Exception:
#     # ton fichier fourni : accounts_users/forms/social/social_signup_forms.py
#     from accounts_users.forms.social.social_signup_forms import UserSignupForm  # type: ignore


# # ======================================================
# # 1) TRACKS
# # ======================================================
# @dataclass(frozen=True)
# class TrackInfo:
#     code: str
#     title: str
#     subtitle: str
#     badge: str


# TRACKS: Dict[str, TrackInfo] = {
#     "client": TrackInfo(
#         code="client",
#         title=_("Compte Client (B2C)"),
#         subtitle=_("Acheter, gérer panier/favoris, suivre commandes et accéder aux services."),
#         badge="🛒",
#     ),
#     "vendor": TrackInfo(
#         code="vendor",
#         title=_("Espace Vendeur"),
#         subtitle=_("Vendre des produits, gérer catalogue, stock et commandes."),
#         badge="🏪",
#     ),
#     "b2b": TrackInfo(
#         code="b2b",
#         title=_("Compte Entreprise (B2B)"),
#         subtitle=_("Commandes en gros, RFQ, facturation et gestion d’entreprise."),
#         badge="🏢",
#     ),
# }


# def _get_track(request: HttpRequest) -> TrackInfo:
#     raw = (request.POST.get("track") or request.GET.get("track") or "client").strip().lower()
#     return TRACKS.get(raw, TRACKS["client"])


# def _safe_next(request: HttpRequest) -> str:
#     nxt = (request.POST.get("next") or request.GET.get("next") or "").strip()
#     if nxt and url_has_allowed_host_and_scheme(
#         url=nxt,
#         allowed_hosts={request.get_host()},
#         require_https=request.is_secure(),
#     ):
#         return nxt
#     return ""


# def register_economic_choice_view(request: HttpRequest) -> HttpResponse:
#     """
#     Route optionnelle (si tu veux garder name="register_economic_choice").
#     Redirige vers le hub d’inscription, focus économique.
#     """
#     next_url = _safe_next(request)
#     base = reverse("accounts_users:web:registration:choice")
#     params = {"focus": "economic"}
#     if next_url:
#         params["next"] = next_url
#     return redirect(f"{base}?{urlencode(params)}#economic")


# # ======================================================
# # 2) LOGIQUE PROFIL ÉCO (SAFE)
# # ======================================================
# try:
#     from accounts_users.models.user_role import EconomicRole  # type: ignore
# except Exception:
#     EconomicRole = None


# ECONOMIC_ADVANCED_MAP = {
#     "client": {"role": getattr(EconomicRole, "CLIENT", None), "requires_validation": False},
#     "vendor": {"role": getattr(EconomicRole, "VENDOR", None), "requires_validation": True},
#     "b2b": {"role": getattr(EconomicRole, "B2B", None), "requires_validation": True},
# }


# def _try_create_or_update_economic_profile(user, track_code: str, profile_instance=None) -> None:
#     """
#     Mets à jour le profil économique central (UserEconomicProfile).
#     - safe: vérifie les attributs avant d’écrire.
#     """
#     try:
#         from accounts_users.models.users_economic_profile import UserEconomicProfile  # type: ignore
#     except Exception:
#         return

#     profile = profile_instance
#     if profile is None:
#         profile, _ = UserEconomicProfile.objects.get_or_create(user=user)

#     config = ECONOMIC_ADVANCED_MAP.get(track_code) or {}
#     role = config.get("role")
#     requires_validation = bool(config.get("requires_validation"))

#     if role is not None and hasattr(profile, "economic_role"):
#         profile.economic_role = role

#     if requires_validation:
#         if hasattr(profile, "is_validated"):
#             profile.is_validated = False
#         if hasattr(profile, "validation_status"):
#             profile.validation_status = "PENDING"
#     else:
#         if hasattr(profile, "is_validated"):
#             profile.is_validated = True
#         if hasattr(profile, "validation_status"):
#             profile.validation_status = "APPROVED"

#     profile.save()


# # ======================================================
# # 3) EMAIL D’ACTIVATION
# # ======================================================
# def _send_activation_email(request: HttpRequest, user) -> bool:
#     uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
#     token = account_activation_token.make_token(user)

#     activation_url = request.build_absolute_uri(
#         reverse("accounts_users:web:registration:activate", kwargs={"uidb64": uidb64, "token": token})
#     )

#     subject = _("Activation de votre compte")
#     context = {
#         "user": user,
#         "activation_url": activation_url,
#         "PROJECT_NAME": getattr(settings, "PROJECT_NAME", "SOGENTIS"),
#     }

#     html_message = render_to_string("accounts_users/registration/account_activation_email.html", context)
#     text_message = render_to_string("accounts_users/registration/account_activation_email.txt", context)

#     try:
#         from django.core.mail import EmailMultiAlternatives

#         msg = EmailMultiAlternatives(
#             subject=subject,
#             body=text_message,
#             from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
#             to=[user.email],
#         )
#         msg.attach_alternative(html_message, "text/html")
#         msg.send(fail_silently=False)
#         return True
#     except Exception:
#         logger.exception("Activation email send failed (economic)")
#         return False


# # ======================================================
# # 4) VUE PRINCIPALE (3 FORMS)
# # ======================================================
# def register_economic_view(request: HttpRequest) -> HttpResponse:
#     """
#     Inscription économique (client / vendor / b2b)
#     - 3 forms : user_form + profile_form + economic_form(track)
#     - user inactif + email activation
#     - profil économique central mis à jour
#     """

#     if request.user.is_authenticated:
#         messages.info(request, _("Vous êtes déjà connecté."))
#         return redirect("dashboard:hub")

#     track = _get_track(request)
#     next_url = _safe_next(request)

#     # Track-specific form
#     economic_form_class: Type = ClientSignupForm
#     if track.code == "vendor":
#         economic_form_class = VendorSignupForm
#     elif track.code == "b2b":
#         economic_form_class = CompanySignupForm

#     if request.method == "POST":
#         user_form = UserSignupForm(request.POST)
#         profile_form = UserProfileEconomicForm(request.POST, request.FILES)
#         economic_form = economic_form_class(request.POST, request.FILES)

#         valid = user_form.is_valid() and profile_form.is_valid() and economic_form.is_valid()

#         if valid:
#             # 1) USER
#             user = user_form.save(commit=False)
#             user.is_active = False
#             user.save()

#             # 2) PROFIL ÉCO CENTRAL
#             eco_profile = profile_form.save(user=user, commit=True)

#             # 3) PROFIL TRACK (Client/Vendor/Company)
#             obj = economic_form.save(commit=False)

#             # rattachements safe (selon tes modèles)
#             if hasattr(obj, "user"):
#                 obj.user = user
#             if hasattr(obj, "economic_profile"):
#                 obj.economic_profile = eco_profile
#             if hasattr(obj, "profile"):
#                 obj.profile = eco_profile
#             if hasattr(obj, "user_profile"):
#                 obj.user_profile = eco_profile

#             obj.save()
#             if hasattr(economic_form, "save_m2m"):
#                 economic_form.save_m2m()

#             # 4) Flags/Role/Validation
#             _try_create_or_update_economic_profile(user, track.code, profile_instance=eco_profile)

#             # 5) Email activation
#             if _send_activation_email(request, user):
#                 messages.success(request, _("Inscription réussie. Un email d’activation vous a été envoyé."))
#             else:
#                 messages.warning(request, _("Compte créé, mais l’envoi de l’email d’activation a échoué."))

#             # stocker track/next (optionnel)
#             request.session["ECONOMIC_TRACK"] = track.code
#             if next_url:
#                 request.session["POST_AUTH_NEXT"] = next_url
#             request.session.modified = True

#             return redirect("accounts_users:web:registration:register_done")

#         messages.error(request, _("Veuillez corriger les erreurs du formulaire."))

#     else:
#         user_form = UserSignupForm()
#         profile_form = UserProfileEconomicForm()
#         economic_form = economic_form_class()

#     context = {
#         "user_form": user_form,
#         "profile_form": profile_form,
#         "economic_form": economic_form,
#         "track": track.code,
#         "economic_type": track.code,  # compat template existant
#         "track_title": track.title,
#         "track_subtitle": track.subtitle,
#         "track_badge": track.badge,
#         "next": next_url,
#         "page_title": _("Inscription — Pôle économique"),
#     }

#     return render(request, "accounts_users/registration/register_economic_form.html", context)






# # accounts_users/web/views/economic/registration_economic.py
# from __future__ import annotations

# from dataclasses import dataclass
# from typing import Dict

# from django.conf import settings
# from django.contrib import messages
# from django.http import HttpRequest, HttpResponse
# from django.shortcuts import redirect, render
# from django.template.loader import render_to_string
# from django.urls import reverse
# from django.utils.encoding import force_bytes
# from django.utils.http import urlsafe_base64_encode
# from django.utils.translation import gettext_lazy as _

# from accounts_users.tokens import account_activation_token
# from accounts_users.forms.economic.economic_core_registration import (
#     UserProfileEconomicForm,
# )

# # ======================================================
# # OPTIONAL IMPORTS FROM REGISTRATION V2 (SAFE)
# # ======================================================

# try:
#     from accounts_users.forms.registration.economic import (
#         EconomicClientRegistrationV2Form,
#         EconomicVendorRegistrationV2Form,
#         EconomicB2BRegistrationV2Form,
#     )
# except Exception:
#     EconomicClientRegistrationV2Form = None
#     EconomicVendorRegistrationV2Form = None
#     EconomicB2BRegistrationV2Form = None

# try:
#     from accounts_users.models.registration import (
#         RegistrationCategory,
#         RegistrationDocType,
#     )
# except Exception:
#     RegistrationCategory = None
#     RegistrationDocType = None

# # ======================================================
# # 1) TRACKS (UX / HUB ÉCONOMIQUE)
# # ======================================================

# @dataclass(frozen=True)
# class TrackInfo:
#     code: str
#     title: str
#     subtitle: str
#     badge: str


# TRACKS: Dict[str, TrackInfo] = {
#     "client": TrackInfo(
#         code="client",
#         title=_("Compte Client (B2C)"),
#         subtitle=_("Acheter, gérer panier/favoris, suivre commandes et accéder aux services."),
#         badge="🛒",
#     ),
#     "vendor": TrackInfo(
#         code="vendor",
#         title=_("Espace Vendeur"),
#         subtitle=_("Vendre des produits, gérer catalogue, stock et commandes."),
#         badge="🏪",
#     ),
#     "b2b": TrackInfo(
#         code="b2b",
#         title=_("Compte Entreprise (B2B)"),
#         subtitle=_("Commandes en gros, RFQ, facturation et gestion d’entreprise."),
#         badge="🏢",
#     ),
# }


# def _get_track(request: HttpRequest) -> TrackInfo:
#     raw = (request.POST.get("track") or request.GET.get("track") or "client").strip().lower()
#     return TRACKS.get(raw, TRACKS["client"])


# # ======================================================
# # 2) LOGIQUE MÉTIER ÉCONOMIQUE (HYBRIDE SAFE)
# # ======================================================

# try:
#     from accounts_users.models.user_role import EconomicRole
# except Exception:
#     EconomicRole = None


# ECONOMIC_ADVANCED_MAP = {
#     "client": {
#         "role": getattr(EconomicRole, "CLIENT", None),
#         "requires_validation": False,
#     },
#     "vendor": {
#         "role": getattr(EconomicRole, "VENDOR", None),
#         "requires_validation": True,
#     },
#     "b2b": {
#         "role": getattr(EconomicRole, "B2B", None),
#         "requires_validation": True,
#     },
# }


# def _try_create_or_update_economic_profile(user, track_code: str) -> None:
#     """
#     Crée / met à jour le profil économique.
#     Compatible V1 + V2 sans dépendance forte.
#     """
#     try:
#         from accounts_users.models.users_economic_profile import UserEconomicProfile
#     except Exception:
#         return

#     config = ECONOMIC_ADVANCED_MAP.get(track_code)
#     profile, _ = UserEconomicProfile.objects.get_or_create(user=user)

#     if config and config["role"] is not None:
#         profile.economic_role = config["role"]

#         if config["requires_validation"]:
#             if hasattr(profile, "is_validated"):
#                 profile.is_validated = False
#             if hasattr(profile, "validation_status"):
#                 profile.validation_status = "PENDING"
#         else:
#             if hasattr(profile, "is_validated"):
#                 profile.is_validated = True
#             if hasattr(profile, "validation_status"):
#                 profile.validation_status = "APPROVED"

#     # Alignement Registration V2 (OPTIONNEL)
#     if RegistrationCategory and hasattr(profile, "registration_category"):
#         if track_code == "client":
#             profile.registration_category = RegistrationCategory.ECONOMIC_CLIENT
#         elif track_code == "vendor":
#             profile.registration_category = RegistrationCategory.ECONOMIC_VENDOR
#         elif track_code == "b2b":
#             profile.registration_category = RegistrationCategory.ECONOMIC_B2B

#     profile.save()


# # ======================================================
# # 3) EMAIL D’ACTIVATION (V1 CONSERVÉ)
# # ======================================================

# def _send_activation_email(request: HttpRequest, user) -> bool:
#     uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
#     token = account_activation_token.make_token(user)

#     activation_url = request.build_absolute_uri(
#         reverse(
#             "accounts_users:web:registration:activate",
#             kwargs={"uidb64": uidb64, "token": token},
#         )
#     )

#     subject = _("Activation de votre compte")
#     context = {
#         "user": user,
#         "activation_url": activation_url,
#         "PROJECT_NAME": getattr(settings, "PROJECT_NAME", "SOGENTIS"),
#     }

#     html_message = render_to_string(
#         "accounts_users/registration/account_activation_email.html", context
#     )
#     text_message = render_to_string(
#         "accounts_users/registration/account_activation_email.txt", context
#     )

#     try:
#         from django.core.mail import EmailMultiAlternatives

#         msg = EmailMultiAlternatives(
#             subject=subject,
#             body=text_message,
#             from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
#             to=[user.email],
#         )
#         msg.attach_alternative(html_message, "text/html")
#         msg.send(fail_silently=False)
#         return True
#     except Exception:
#         return False


# # ======================================================
# # 4) VUE PRINCIPALE (HYBRIDE – COMPORTEMENT INCHANGÉ)
# # ======================================================

# # def register_economic_view(request: HttpRequest) -> HttpResponse:
# #     """
# #     Inscription Pôle Économique
# #     - V1 actif par défaut
# #     - V2 prêt mais DÉSACTIVÉ
# #     - aucune régression
# #     """

# #     if request.user.is_authenticated:
# #         messages.info(request, _("Vous êtes déjà connecté."))
# #         return redirect("dashboard:hub")

# #     track = _get_track(request)

# #     # 🔒 V1 PAR DÉFAUT (SAFE)
# #     form_class = UserProfileEconomicForm

# #     # 💤 FUTUR : activation V2 (désactivée volontairement)
# #     if False:
# #         if track.code == "vendor" and EconomicVendorRegistrationV2Form:
# #             form_class = EconomicVendorRegistrationV2Form
# #         elif track.code == "b2b" and EconomicB2BRegistrationV2Form:
# #             form_class = EconomicB2BRegistrationV2Form
# #         elif EconomicClientRegistrationV2Form:
# #             form_class = EconomicClientRegistrationV2Form

# #     if request.method == "POST":
# #         form = form_class(request.POST, request.FILES)

# #         if form.is_valid():
# #             user = form.save(commit=False)
# #             user.is_active = False
# #             user.save()

# #             if hasattr(form, "save_m2m"):
# #                 form.save_m2m()

# #             _try_create_or_update_economic_profile(user, track.code)

# #             request.session["ECONOMIC_TRACK"] = track.code
# #             request.session.modified = True

# #             if _send_activation_email(request, user):
# #                 messages.success(
# #                     request,
# #                     _("Inscription réussie. Un email d’activation vous a été envoyé.")
# #                 )
# #             else:
# #                 messages.warning(
# #                     request,
# #                     _("Compte créé, mais l’envoi de l’email d’activation a échoué.")
# #                 )

# #             return redirect("accounts_users:web:registration:register_done")

# #         messages.error(request, _("Veuillez corriger les erreurs du formulaire."))
# #     else:
# #         form = form_class()

# #     context = {
# #         "form": form,
# #         "track": track.code,
# #         "track_title": track.title,
# #         "track_subtitle": track.subtitle,
# #         "track_badge": track.badge,
# #         "page_title": _("Inscription — Pôle économique"),
# #     }

# #     return render(
# #         request,
# #         "accounts_users/registration/choice.html",
# #         context,
# #     )

# def register_economic_view(request: HttpRequest) -> HttpResponse:
#     if request.user.is_authenticated:
#         messages.info(request, _("Vous êtes déjà connecté."))
#         return redirect("dashboard:hub")

#     track = _get_track(request)

#     form_class = UserProfileEconomicForm

#     if request.method == "POST":
#         form = form_class(request.POST, request.FILES)
#         if form.is_valid():
#             user = form.save(commit=False)
#             user.is_active = False
#             user.save()

#             if hasattr(form, "save_m2m"):
#                 form.save_m2m()

#             _try_create_or_update_economic_profile(user, track.code)

#             request.session["ECONOMIC_TRACK"] = track.code
#             request.session.modified = True

#             if _send_activation_email(request, user):
#                 messages.success(request, _("Inscription réussie. Un email d’activation vous a été envoyé."))
#             else:
#                 messages.warning(request, _("Compte créé, mais l’envoi de l’email d’activation a échoué."))

#             return redirect("accounts_users:web:registration:register_done")

#         messages.error(request, _("Veuillez corriger les erreurs du formulaire."))
#     else:
#         form = form_class()

#     context = {
#         "form": form,
#         "track": track.code,
#         "track_title": track.title,
#         "track_subtitle": track.subtitle,
#         "track_badge": track.badge,
#         "page_title": _("Inscription — Pôle économique"),
#     }

#     return render(
#         request,
#         "accounts_users/registration/register_economic_form.html",
#         context,
#     )





# # # accounts_users/web/views/economic/registration_economic.py
# from __future__ import annotations

# from dataclasses import dataclass
# from typing import Dict

# from django.conf import settings
# from django.contrib import messages
# from django.http import HttpRequest, HttpResponse
# from django.shortcuts import redirect, render
# from django.template.loader import render_to_string
# from django.urls import reverse
# from django.utils.encoding import force_bytes
# from django.utils.http import urlsafe_base64_encode
# from django.utils.translation import gettext_lazy as _

# from accounts_users.tokens import account_activation_token
# from accounts_users.forms.economic.economic_core_registration import (
#     UserProfileEconomicForm,
# )

# # ===============================
# # 1) TRACKS (UX / Hub économique)
# # ===============================

# @dataclass(frozen=True)
# class TrackInfo:
#     code: str
#     title: str
#     subtitle: str
#     badge: str


# TRACKS: Dict[str, TrackInfo] = {
#     "client": TrackInfo(
#         code="client",
#         title=_("Compte Client (B2C)"),
#         subtitle=_(
#             "Acheter, gérer panier/favoris, suivre commandes et accéder aux services."
#         ),
#         badge="🛒",
#     ),
#     "vendor": TrackInfo(
#         code="vendor",
#         title=_("Espace Vendeur"),
#         subtitle=_(
#             "Vendre des produits, gérer catalogue, stock et commandes."
#         ),
#         badge="🏪",
#     ),
#     "b2b": TrackInfo(
#         code="b2b",
#         title=_("Compte Entreprise (B2B)"),
#         subtitle=_(
#             "Commandes en gros, RFQ, facturation et gestion d’entreprise."
#         ),
#         badge="🏢",
#     ),
# }


# def _get_track(request: HttpRequest) -> TrackInfo:
#     raw = (
#         request.POST.get("track")
#         or request.GET.get("track")
#         or "client"
#     ).strip().lower()
#     return TRACKS.get(raw, TRACKS["client"])


# # ======================================================
# # 2) LOGIQUE ÉCONOMIQUE AVANCÉE (absorbe fichier n°2)
# # ======================================================

# try:
#     from accounts_users.models.user_role import EconomicRole
# except Exception:
#     EconomicRole = None  # SAFE fallback


# ECONOMIC_ADVANCED_MAP = {
#     "client": {
#         "role": getattr(EconomicRole, "CLIENT", None),
#         "requires_validation": False,
#     },
#     "vendor": {
#         "role": getattr(EconomicRole, "VENDOR", None),
#         "requires_validation": True,
#     },
#     "b2b": {
#         "role": getattr(EconomicRole, "B2B", None),
#         "requires_validation": True,
#     },
# }


# def _try_create_or_update_economic_profile(user, track_code: str) -> None:
#     """
#     Crée / met à jour le profil économique sans casser l’inscription
#     même si certains modèles ou champs n’existent pas.
#     """
#     try:
#         from accounts_users.models.users_economic_profile import UserEconomicProfile
#     except Exception:
#         return

#     config = ECONOMIC_ADVANCED_MAP.get(track_code)

#     profile, _ = UserEconomicProfile.objects.get_or_create(user=user)

#     if config and config["role"] is not None:
#         profile.economic_role = config["role"]

#         if config["requires_validation"]:
#             if hasattr(profile, "is_validated"):
#                 profile.is_validated = False
#             if hasattr(profile, "validation_status"):
#                 profile.validation_status = "PENDING"
#         else:
#             if hasattr(profile, "is_validated"):
#                 profile.is_validated = True
#             if hasattr(profile, "validation_status"):
#                 profile.validation_status = "APPROVED"

#     profile.save()


# # ===============================
# # 3) EMAIL D’ACTIVATION
# # ===============================

# def _send_activation_email(request: HttpRequest, user) -> bool:
#     uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
#     token = account_activation_token.make_token(user)

#     activation_url = request.build_absolute_uri(
#         reverse(
#             "accounts_users:web:registration:activate",
#             kwargs={"uidb64": uidb64, "token": token},
#         )
#     )

#     subject = _("Activation de votre compte")
#     context = {
#         "user": user,
#         "activation_url": activation_url,
#         "PROJECT_NAME": getattr(settings, "PROJECT_NAME", "SOGENTIS"),
#     }

#     html_message = render_to_string(
#         "accounts_users/registration/account_activation_email.html",
#         context,
#     )
#     text_message = render_to_string(
#         "accounts_users/registration/account_activation_email.txt",
#         context,
#     )

#     try:
#         from django.core.mail import EmailMultiAlternatives

#         msg = EmailMultiAlternatives(
#             subject=subject,
#             body=text_message,
#             from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
#             to=[user.email],
#         )
#         msg.attach_alternative(html_message, "text/html")
#         msg.send(fail_silently=False)
#         return True
#     except Exception:
#         return False


# # ===============================
# # 4) VUE PRINCIPALE (SAFE)
# # ===============================

# def register_economic_view(request: HttpRequest) -> HttpResponse:
#     """
#     Inscription Pôle Économique
#     - track = client | vendor | b2b
#     - activation par email conservée
#     - rôles + validation intégrés
#     """

#     if request.user.is_authenticated:
#         messages.info(request, _("Vous êtes déjà connecté."))
#         return redirect("dashboard:hub")

#     track = _get_track(request)

#     if request.method == "POST":
#         form = UserProfileEconomicForm(request.POST, request.FILES)

#         if form.is_valid():
#             # Création user INACTIF (activation email)
#             user = form.save(commit=False)
#             user.is_active = False
#             user.save()

#             if hasattr(form, "save_m2m"):
#                 form.save_m2m()

#             # Profil économique enrichi
#             _try_create_or_update_economic_profile(user, track.code)

#             # UX / tracking
#             request.session["ECONOMIC_TRACK"] = track.code
#             request.session.modified = True

#             # Email activation
#             if _send_activation_email(request, user):
#                 messages.success(
#                     request,
#                     _(
#                         "Inscription réussie. "
#                         "Un email d’activation vous a été envoyé."
#                     ),
#                 )
#             else:
#                 messages.warning(
#                     request,
#                     _(
#                         "Compte créé, mais l’envoi de l’email "
#                         "d’activation a échoué."
#                     ),
#                 )

#             return redirect(
#                 "accounts_users:web:registration:register_done"
#             )

#         messages.error(
#             request,
#             _("Veuillez corriger les erreurs du formulaire.")
#         )
#     else:
#         form = UserProfileEconomicForm()

#     context = {
#         "form": form,
#         "track": track.code,
#         "track_title": track.title,
#         "track_subtitle": track.subtitle,
#         "track_badge": track.badge,
#         "page_title": _("Inscription — Pôle économique"),
#     }

#     return render(
#         request,
#         "accounts_users/registration/choice.html",
#         context,
#     )







# # accounts_users/web/views/economic/registration_economic.py
# from __future__ import annotations

# from dataclasses import dataclass
# from typing import Dict, Optional

# from django.conf import settings
# from django.contrib import messages
# from django.contrib.auth import login
# from django.http import HttpRequest, HttpResponse
# from django.shortcuts import redirect, render
# from django.template.loader import render_to_string
# from django.urls import reverse
# from django.utils.encoding import force_bytes
# from django.utils.http import urlsafe_base64_encode
# from django.utils.translation import gettext_lazy as _

# from accounts_users.tokens import account_activation_token  # <-- ton token generator
# from accounts_users.forms.economic.economic_core_registration import UserProfileEconomicForm


# # -------------------------------------------------------------------
# # 1) Track = client/vendor/b2b (hub économique)
# # -------------------------------------------------------------------
# @dataclass(frozen=True)
# class TrackInfo:
#     code: str
#     title: str
#     subtitle: str
#     badge: str


# TRACKS: Dict[str, TrackInfo] = {
#     "client": TrackInfo(
#         code="client",
#         title=_("Compte Client (B2C)"),
#         subtitle=_("Acheter, gérer panier/favoris, suivre commandes et accéder aux services & formations."),
#         badge="🛒",
#     ),
#     "vendor": TrackInfo(
#         code="vendor",
#         title=_("Espace Vendeur"),
#         subtitle=_("Vendre des produits, gérer catalogue, stock et commandes."),
#         badge="🏪",
#     ),
#     "b2b": TrackInfo(
#         code="b2b",
#         title=_("Compte Entreprise (B2B)"),
#         subtitle=_("Gérer entreprise, commandes en gros, RFQ et factures."),
#         badge="🏢",
#     ),
# }


# def _get_track(request: HttpRequest) -> TrackInfo:
#     raw = (request.POST.get("track") or request.GET.get("track") or "client").strip().lower()
#     return TRACKS.get(raw, TRACKS["client"])


# def _try_create_or_update_economic_profile(user, track_code: str) -> None:
#     """
#     Optionnel : si tu as un EconomicProfile, on le crée/maj.
#     On reste SAFE : si le modèle n'existe pas, on n'échoue pas l'inscription.
#     """
#     try:
#         # Adapte si ton modèle n'est pas là
#         from accounts_users.models.users_economic_profile import UserEconomicProfile
#     except Exception:
#         return

#     profile, _ =  UserProfileEconomicForm.objects.get_or_create(user=user)

#     # Tente d'écrire le type de compte si le champ existe
#     for field in ("track", "account_type", "account_kind", "kind", "profile_type"):
#         if hasattr(profile, field):
#             setattr(profile, field, track_code)
#             break

#     profile.save(update_fields=None)


# def _send_activation_email(request: HttpRequest, user) -> bool:
#     """
#     Envoie l'email d'activation.
#     Retourne True/False.
#     """
#     uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
#     token = account_activation_token.make_token(user)

#     activation_url = request.build_absolute_uri(
#         reverse(
#             "accounts_users:web:registration:activate",
#             kwargs={"uidb64": uidb64, "token": token},
#         )
#     )

#     subject = _("Activation de votre compte")
#     context = {
#         "user": user,
#         "activation_url": activation_url,
#         "PROJECT_NAME": getattr(settings, "PROJECT_NAME", "SOGENTIS"),
#     }

#     html_message = render_to_string("accounts_users/registration/account_activation_email.html", context)
#     text_message = render_to_string("accounts_users/registration/account_activation_email.txt", context)

#     try:
#         from django.core.mail import EmailMultiAlternatives

#         msg = EmailMultiAlternatives(
#             subject=subject,
#             body=text_message,
#             from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
#             to=[user.email],
#         )
#         msg.attach_alternative(html_message, "text/html")
#         msg.send(fail_silently=False)
#         return True
#     except Exception:
#         return False


# # -------------------------------------------------------------------
# # 2) Vue principale : register_economic_view
# # -------------------------------------------------------------------
# def register_economic_view(request: HttpRequest) -> HttpResponse:
#     """
#     Inscription Économique.
#     - support track=client|vendor|b2b (depuis le hub)
#     - crée un user inactif
#     - envoie email d'activation
#     - redirige vers register_done
#     """
#     # Déjà connecté => à toi de choisir la destination
#     if request.user.is_authenticated:
#         messages.info(request, _("Vous êtes déjà connecté."))
#         return redirect("dashboard:hub")

#     track = _get_track(request)

#     if request.method == "POST":
#         form = UserProfileEconomicForm(request.POST, request.FILES)

#         if form.is_valid():
#             # Crée user inactif (activation email)
#             user = form.save(commit=False)
#             user.is_active = False
#             user.save()

#             # Si le form a des M2M
#             if hasattr(form, "save_m2m"):
#                 form.save_m2m()

#             # Optionnel : crée/maj economic profile
#             _try_create_or_update_economic_profile(user, track.code)

#             # Enregistre le track en session (utile pour UX post-inscription)
#             if hasattr(request, "session"):
#                 request.session["ECONOMIC_TRACK"] = track.code
#                 request.session.modified = True

#             # Envoi email activation
#             ok = _send_activation_email(request, user)
#             if ok:
#                 messages.success(
#                     request,
#                     _("Inscription réussie. Un email d’activation vous a été envoyé."),
#                 )
#             else:
#                 messages.warning(
#                     request,
#                     _("Compte créé, mais l’envoi de l’email d’activation a échoué. Veuillez réessayer."),
#                 )

#             # Page confirmation (ton URL name existe dans registration_urls.py)
#             return redirect("accounts_users:web:registration:register_done")

#         messages.error(request, _("Veuillez corriger les erreurs du formulaire."))
#     else:
#         form = UserProfileEconomicForm()

#     context = {
#         "form": form,
#         "track": track.code,
#         "track_title": track.title,
#         "track_subtitle": track.subtitle,
#         "track_badge": track.badge,
#         "page_title": _("Inscription — Pôle économique"),
#     }

#     # Template à toi : mets celui que tu utilises réellement
#     # (ex: accounts_users/registration/register_economic.html)
#     return render(request, "accounts_users/registration/choice.html", context)

