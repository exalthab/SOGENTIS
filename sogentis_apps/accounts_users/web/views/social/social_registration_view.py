# accounts_users/web/views/social/social_registration_view.py
from __future__ import annotations

import logging

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.db import IntegrityError, transaction
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import NoReverseMatch, reverse
from django.utils.encoding import force_bytes
from django.utils.http import url_has_allowed_host_and_scheme, urlsafe_base64_encode
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from accounts_users.forms.signup_forms import UserSignupForm
from accounts_users.forms.social.social_registration_form import SocialRegistrationForm
from accounts_users.models.social.social_profile import SocialProfile
from accounts_users.services.email_otp_service import (
    validate_latest_email_otp_or_raise,
    mark_profile_email_verified,
)
from accounts_users.tokens import account_activation_token
from accounts_users.web.views._helpers import build_auth_context

logger = logging.getLogger(__name__)


# ======================================================
# HELPERS
# ======================================================

def _safe_next_url(request) -> str:
    nxt = (request.POST.get("next") or request.GET.get("next") or "").strip()
    if nxt and url_has_allowed_host_and_scheme(nxt, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        return nxt
    return ""


def _safe_login_redirect(request, *, next_url: str = ""):
    """
    Compat: si tu as une route accounts_users:web:social_login, elle est utilisée.
    Sinon fallback propre vers accounts_users:web:auth:login.
    """
    try:
        base = reverse("accounts_users:web:social_login")
    except NoReverseMatch:
        base = reverse("accounts_users:web:auth:login")

    if next_url:
        sep = "&" if "?" in base else "?"
        return redirect(f"{base}{sep}next={next_url}&context=social")
    sep = "&" if "?" in base else "?"
    return redirect(f"{base}{sep}context=social")


def generate_social_code(role_code: str | None) -> str:
    """
    Génère un code court unique type:
    M001 / V002 / D003 / I004 / U005
    (moins fragile que count()+1)
    """
    role_code = (role_code or "").upper().strip()
    prefix_map = {
        "MEMBER": "M",
        "VOLUNTEER": "V",
        "SPONSOR": "D",
        "INSTITUTION": "I",
    }
    prefix = prefix_map.get(role_code, "U")

    qs = SocialProfile.objects.all()
    if role_code:
        qs = qs.filter(membership_role__code=role_code)

    last = qs.exclude(social_registration_code__isnull=True).exclude(social_registration_code="") \
             .order_by("-id").values_list("social_registration_code", flat=True).first()

    n = 0
    if last and len(last) >= 2 and last[0].upper() == prefix:
        tail = "".join(ch for ch in last[1:] if ch.isdigit())
        if tail.isdigit():
            n = int(tail)

    return f"{prefix}{n + 1:03}"


def _render_form(request, *, user_form, profile_form, excluded_profile_fields):
    return render(
        request,
        "accounts_users/registration/register_social_form.html",
        {
            "form": user_form,
            "profile_form": profile_form,
            "excluded_profile_fields": excluded_profile_fields,
            **build_auth_context("social"),
        },
    )


# ======================================================
# VIEW
# ======================================================

def social_register_view(request):
    """
    INSCRIPTION SOCIALE – MODE AVANCÉ
    1) Form User + SocialProfile
    2) OTP email obligatoire (bloquant)
    3) Création user inactif
    4) Création SocialProfile
    5) Génération code social
    6) Envoi email d’activation
    """

    if request.user.is_authenticated:
        return redirect("dashboard:hub")

    # IMPORTANT: doit matcher le template (évite doublons)
    excluded_profile_fields = [
        "terms",
        "phone_number",
        "country_of_residence",
        "profile_picture",
        "judicial_record",
    ]

    if request.method == "POST":
        user_form = UserSignupForm(request.POST)
        profile_form = SocialRegistrationForm(request.POST, request.FILES)
        next_url = _safe_next_url(request)

        if not (user_form.is_valid() and profile_form.is_valid()):
            messages.error(request, _("Merci de corriger les erreurs ci-dessous."))
            return _render_form(
                request,
                user_form=user_form,
                profile_form=profile_form,
                excluded_profile_fields=excluded_profile_fields,
            )

        email = (user_form.cleaned_data.get("email") or "").strip().lower()
        otp_code = (user_form.cleaned_data.get("email_otp_code") or "").strip()

        # ==================================================
        # OTP EMAIL — STRICT
        # ==================================================
        try:
            validate_latest_email_otp_or_raise(email=email, otp_code=otp_code)
        except Exception as e:
            user_form.add_error("email_otp_code", str(e))
            messages.error(request, _("Code de vérification invalide ou expiré."))
            return _render_form(
                request,
                user_form=user_form,
                profile_form=profile_form,
                excluded_profile_fields=excluded_profile_fields,
            )

        try:
            with transaction.atomic():
                # ================= USER =================
                user = user_form.save(commit=False)
                user.is_active = False
                user.save()

                # ================= SOCIAL PROFILE =================
                social_profile = profile_form.save(commit=False)
                social_profile.user = user

                role_code = getattr(getattr(social_profile, "membership_role", None), "code", None)
                social_profile.social_registration_code = generate_social_code(role_code)

                # miroir email si champ présent
                if hasattr(social_profile, "email") and not getattr(social_profile, "email", None):
                    social_profile.email = user.email

                social_profile.save()

                # ================= OTP CONFIRM =================
                mark_profile_email_verified(email=email)

                # ================= EMAIL ACTIVATION =================
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = account_activation_token.make_token(user)

                activation_url = request.build_absolute_uri(
                    reverse("accounts_users:web:registration:activate", kwargs={"uidb64": uid, "token": token})
                )

                html_message = render_to_string(
                    "accounts_users/emails/account_activation_email.html",
                    {"user": user, "activation_url": activation_url, "year": now().year},
                )

                send_mail(
                    subject=_("Activation de votre compte SOGENTIS"),
                    message=_("Veuillez activer votre compte via le lien reçu."),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    html_message=html_message,
                    fail_silently=False,
                )

            messages.success(request, _("Inscription réussie. Un lien d’activation vous a été envoyé."))
            return _safe_login_redirect(request, next_url=next_url)

        except IntegrityError:
            logger.warning("Inscription sociale: email déjà utilisé")
            user_form.add_error("email", _("Un utilisateur avec cet email existe déjà."))
            messages.error(request, _("Un utilisateur avec cet email existe déjà."))

        except Exception:
            logger.exception("Erreur inscription sociale avancée")
            messages.error(request, _("Une erreur technique est survenue. Veuillez réessayer."))

        return _render_form(
            request,
            user_form=user_form,
            profile_form=profile_form,
            excluded_profile_fields=excluded_profile_fields,
        )

    # ================= GET =================
    return _render_form(
        request,
        user_form=UserSignupForm(),
        profile_form=SocialRegistrationForm(),
        excluded_profile_fields=excluded_profile_fields,
    )







# # accounts_users/web/views/social/social_registration_view.py
# from __future__ import annotations

# import logging

# from django.conf import settings
# from django.contrib import messages
# from django.contrib.auth import get_user_model
# from django.core.mail import send_mail
# from django.db import IntegrityError, transaction
# from django.shortcuts import redirect, render
# from django.template.loader import render_to_string
# from django.urls import reverse
# from django.utils.encoding import force_bytes
# from django.utils.http import urlsafe_base64_encode
# from django.utils.timezone import now
# from django.utils.translation import gettext_lazy as _

# from accounts_users.forms.signup_forms import UserSignupForm
# from accounts_users.forms.social.social_registration_form import SocialRegistrationForm
# from accounts_users.models.social.social_profile import SocialProfile
# from accounts_users.services.email_otp_service import (
#     validate_latest_email_otp_or_raise,
#     mark_profile_email_verified,
# )
# from accounts_users.tokens import account_activation_token
# from accounts_users.web.views._helpers import build_auth_context

# logger = logging.getLogger(__name__)
# User = get_user_model()


# # ======================================================
# # HELPERS
# # ======================================================

# def generate_social_code(role_code: str | None) -> str:
#     """
#     Génère un code court unique type:
#     M001 / V002 / D003 / I004 / U005
#     """
#     role_code = (role_code or "").upper().strip()
#     prefix_map = {
#         "MEMBER": "M",
#         "VOLUNTEER": "V",
#         "SPONSOR": "D",
#         "INSTITUTION": "I",
#     }
#     prefix = prefix_map.get(role_code, "U")

#     qs = SocialProfile.objects.all()
#     if role_code:
#         qs = qs.filter(membership_role__code=role_code)

#     return f"{prefix}{qs.count() + 1:03}"


# def _render_form(request, *, user_form, profile_form, excluded_profile_fields):
#     return render(
#         request,
#         "accounts_users/registration/register_social_form.html",
#         {
#             "form": user_form,
#             "profile_form": profile_form,
#             "excluded_profile_fields": excluded_profile_fields,
#             **build_auth_context("social"),
#         },
#     )


# # ======================================================
# # VIEW
# # ======================================================

# def social_register_view(request):
#     """
#     INSCRIPTION SOCIALE – MODE AVANCÉ (FINAL)
#     --------------------------------------------------
#     1) Form User + SocialProfile
#     2) OTP email obligatoire (bloquant)
#     3) Création user inactif
#     4) Création SocialProfile
#     5) Génération code social
#     6) Envoi email d’activation
#     """

#     if request.user.is_authenticated:
#         return redirect("dashboard:hub")

#     excluded_profile_fields = [
#         "terms",
#         "phone_number",
#         "profile_picture",
#         "judicial_record",
#     ]

#     if request.method == "POST":
#         user_form = UserSignupForm(request.POST)
#         profile_form = SocialRegistrationForm(request.POST, request.FILES)

#         if not (user_form.is_valid() and profile_form.is_valid()):
#             messages.error(request, _("Merci de corriger les erreurs ci-dessous."))
#             return _render_form(
#                 request,
#                 user_form=user_form,
#                 profile_form=profile_form,
#                 excluded_profile_fields=excluded_profile_fields,
#             )

#         email = user_form.cleaned_data["email"].strip().lower()
#         otp_code = user_form.cleaned_data.get("email_otp_code", "").strip()

#         # ==================================================
#         # OTP EMAIL — STRICT
#         # ==================================================
#         try:
#             validate_latest_email_otp_or_raise(email=email, otp_code=otp_code)
#         except Exception as e:
#             user_form.add_error("email_otp_code", str(e))
#             messages.error(request, _("Code de vérification invalide ou expiré."))
#             return _render_form(
#                 request,
#                 user_form=user_form,
#                 profile_form=profile_form,
#                 excluded_profile_fields=excluded_profile_fields,
#             )

#         try:
#             with transaction.atomic():

#                 # ================= USER =================
#                 user = user_form.save(commit=False)
#                 user.is_active = False
#                 user.save()

#                 # ================= SOCIAL PROFILE =================
#                 social_profile = profile_form.save(commit=False)
#                 social_profile.user = user

#                 role_code = getattr(
#                     getattr(social_profile, "membership_role", None),
#                     "code",
#                     None,
#                 )

#                 social_profile.social_registration_code = generate_social_code(role_code)

#                 # miroir email si champ présent
#                 if hasattr(social_profile, "email") and not social_profile.email:
#                     social_profile.email = user.email

#                 social_profile.save()

#                 # ================= OTP CONFIRM =================
#                 mark_profile_email_verified(email)

#                 # ================= EMAIL ACTIVATION =================
#                 uid = urlsafe_base64_encode(force_bytes(user.pk))
#                 token = account_activation_token.make_token(user)

#                 activation_url = request.build_absolute_uri(
#                     reverse(
#                         "accounts_users:web:activate",
#                         kwargs={"uidb64": uid, "token": token},
#                     )
#                 )

#                 html_message = render_to_string(
#                     "accounts_users/emails/account_activation_email.html",
#                     {
#                         "user": user,
#                         "activation_url": activation_url,
#                         "year": now().year,
#                     },
#                 )

#                 send_mail(
#                     subject=_("Activation de votre compte SOGENTIS"),
#                     message=_("Veuillez activer votre compte via le lien reçu."),
#                     from_email=settings.DEFAULT_FROM_EMAIL,
#                     recipient_list=[user.email],
#                     html_message=html_message,
#                     fail_silently=False,
#                 )

#             messages.success(
#                 request,
#                 _("Inscription réussie. Un lien d’activation vous a été envoyé.")
#             )
#             return redirect("accounts_users:web:social_login")

#         except IntegrityError:
#             logger.warning("Inscription sociale: email déjà utilisé")
#             user_form.add_error("email", _("Un utilisateur avec cet email existe déjà."))
#             messages.error(request, _("Un utilisateur avec cet email existe déjà."))

#         except Exception as e:
#             logger.exception("Erreur inscription sociale avancée")
#             messages.error(
#                 request,
#                 _("Une erreur technique est survenue. Veuillez réessayer.")
#             )

#         return _render_form(
#             request,
#             user_form=user_form,
#             profile_form=profile_form,
#             excluded_profile_fields=excluded_profile_fields,
#         )

#     # ================= GET =================
#     return _render_form(
#         request,
#         user_form=UserSignupForm(),
#         profile_form=SocialRegistrationForm(),
#         excluded_profile_fields=excluded_profile_fields,
#     )




# # accounts_users/web/views/social/social_registration_view.py
# from __future__ import annotations

# import logging

# from django.conf import settings
# from django.contrib import messages
# from django.contrib.auth import get_user_model
# from django.core.mail import send_mail
# from django.db import IntegrityError, transaction
# from django.shortcuts import redirect, render
# from django.template.loader import render_to_string
# from django.urls import reverse
# from django.utils.encoding import force_bytes
# from django.utils.http import urlsafe_base64_encode
# from django.utils.timezone import now
# from django.utils.translation import gettext_lazy as _

# from accounts_users.forms.signup_forms import UserSignupForm
# from accounts_users.forms.social.social_registration_form import SocialRegistrationForm
# from accounts_users.models.social.social_profile import SocialProfile
# from accounts_users.services.email_otp_service import (
#     validate_latest_email_otp_or_raise,
#     mark_profile_email_verified,
# )
# from accounts_users.tokens import account_activation_token
# from accounts_users.web.views._helpers import build_auth_context

# logger = logging.getLogger(__name__)
# User = get_user_model()


# # ======================================================
# # HELPERS
# # ======================================================

# def generate_social_code(role_code: str | None) -> str:
#     """
#     Génère un code court unique type:
#     M001 / V002 / D003 / I004 / U005
#     """
#     role_code = (role_code or "").upper().strip()
#     prefix_map = {
#         "MEMBER": "M",
#         "VOLUNTEER": "V",
#         "SPONSOR": "D",
#         "INSTITUTION": "I",
#     }
#     prefix = prefix_map.get(role_code, "U")

#     qs = SocialProfile.objects.all()
#     if role_code:
#         qs = qs.filter(membership_role__code=role_code)

#     return f"{prefix}{qs.count() + 1:03}"


# def _render_form(request, *, user_form, profile_form, excluded_profile_fields):
#     return render(
#         request,
#         "accounts_users/registration/register_social_form.html",
#         {
#             "form": user_form,
#             "profile_form": profile_form,
#             "excluded_profile_fields": excluded_profile_fields,
#             **build_auth_context("social"),
#         },
#     )


# # ======================================================
# # VIEW
# # ======================================================

# def social_register_view(request):
#     """
#     INSCRIPTION SOCIALE – MODE AVANCÉ (FINAL)
#     --------------------------------------------------
#     1) Form User + SocialProfile
#     2) OTP email obligatoire (bloquant)
#     3) Création user inactif
#     4) Création SocialProfile
#     5) Génération code social
#     6) Envoi email d’activation
#     """

#     if request.user.is_authenticated:
#         return redirect("dashboard:hub")

#     excluded_profile_fields = [
#         "terms",
#         "phone_number",
#         "profile_picture",
#         "judicial_record",
#     ]

#     if request.method == "POST":
#         user_form = UserSignupForm(request.POST)
#         profile_form = SocialRegistrationForm(request.POST, request.FILES)

#         if not (user_form.is_valid() and profile_form.is_valid()):
#             messages.error(request, _("Merci de corriger les erreurs ci-dessous."))
#             return _render_form(
#                 request,
#                 user_form=user_form,
#                 profile_form=profile_form,
#                 excluded_profile_fields=excluded_profile_fields,
#             )

#         email = user_form.cleaned_data["email"].strip().lower()
#         otp_code = user_form.cleaned_data.get("email_otp_code", "").strip()

#         # ==================================================
#         # OTP EMAIL — STRICT
#         # ==================================================
#         try:
#             validate_latest_email_otp_or_raise(email=email, otp_code=otp_code)
#         except Exception as e:
#             user_form.add_error("email_otp_code", str(e))
#             messages.error(request, _("Code de vérification invalide ou expiré."))
#             return _render_form(
#                 request,
#                 user_form=user_form,
#                 profile_form=profile_form,
#                 excluded_profile_fields=excluded_profile_fields,
#             )

#         try:
#             with transaction.atomic():

#                 # ================= USER =================
#                 user = user_form.save(commit=False)
#                 user.is_active = False
#                 user.save()

#                 # ================= SOCIAL PROFILE =================
#                 social_profile = profile_form.save(commit=False)
#                 social_profile.user = user

#                 role_code = getattr(
#                     getattr(social_profile, "membership_role", None),
#                     "code",
#                     None,
#                 )

#                 social_profile.social_registration_code = generate_social_code(role_code)

#                 # miroir email si champ présent
#                 if hasattr(social_profile, "email") and not social_profile.email:
#                     social_profile.email = user.email

#                 social_profile.save()

#                 # ================= OTP CONFIRM =================
#                 mark_profile_email_verified(email)

#                 # ================= EMAIL ACTIVATION =================
#                 uid = urlsafe_base64_encode(force_bytes(user.pk))
#                 token = account_activation_token.make_token(user)

#                 activation_url = request.build_absolute_uri(
#                     reverse(
#                         "accounts_users:web:activate",
#                         kwargs={"uidb64": uid, "token": token},
#                     )
#                 )

#                 html_message = render_to_string(
#                     "accounts_users/emails/account_activation_email.html",
#                     {
#                         "user": user,
#                         "activation_url": activation_url,
#                         "year": now().year,
#                     },
#                 )

#                 send_mail(
#                     subject=_("Activation de votre compte SOGENTIS"),
#                     message=_("Veuillez activer votre compte via le lien reçu."),
#                     from_email=settings.DEFAULT_FROM_EMAIL,
#                     recipient_list=[user.email],
#                     html_message=html_message,
#                     fail_silently=False,
#                 )

#             messages.success(
#                 request,
#                 _("Inscription réussie. Un lien d’activation vous a été envoyé.")
#             )
#             return redirect("accounts_users:web:social_login")

#         except IntegrityError:
#             logger.warning("Inscription sociale: email déjà utilisé")
#             user_form.add_error("email", _("Un utilisateur avec cet email existe déjà."))
#             messages.error(request, _("Un utilisateur avec cet email existe déjà."))

#         except Exception as e:
#             logger.exception("Erreur inscription sociale avancée")
#             messages.error(
#                 request,
#                 _("Une erreur technique est survenue. Veuillez réessayer.")
#             )

#         return _render_form(
#             request,
#             user_form=user_form,
#             profile_form=profile_form,
#             excluded_profile_fields=excluded_profile_fields,
#         )

#     # ================= GET =================
#     return _render_form(
#         request,
#         user_form=UserSignupForm(),
#         profile_form=SocialRegistrationForm(),
#         excluded_profile_fields=excluded_profile_fields,
#     )










# from __future__ import annotations

# import logging

# from django.conf import settings
# from django.contrib import messages
# from django.shortcuts import redirect, render
# from django.utils.translation import gettext_lazy as _

# from accounts_users.forms.registration.social import SocialRegistrationV2Form
# from accounts_users.models.registration import RegistrationCategory, RegistrationDocType
# from accounts_users.web.services.registration_service import (
#     create_inactive_user_from_cleaned,
#     create_application_and_docs,
#     send_activation_email,
# )

# logger = logging.getLogger(__name__)


# def social_register_view(request):
#     """
#     Inscription sociale – MODE HYBRIDE
#     --------------------------------------------------
#     ✔ Flow V2 (service layer) ACTIF par défaut (comportement inchangé)
#     ✔ Flow avancé (OTP / SocialProfile) prêt mais OFF via settings
#     """

#     if request.user.is_authenticated:
#         return redirect("dashboard:hub")

#     # Switch (OFF par défaut)
#     # Exemple plus tard: SOCIAL_REGISTRATION_MODE="advanced"
#     mode = getattr(settings, "SOCIAL_REGISTRATION_MODE", "v2")
#     if mode == "advanced":
#         # On garde le hook sans casser le runtime si advanced n'existe pas.
#         try:
#             return _social_register_advanced(request)
#         except Exception:
#             logger.exception("SOCIAL advanced flow failed, fallback to V2")
#             messages.warning(
#                 request,
#                 _("Le mode avancé est indisponible. Bascule en mode standard (V2).")
#             )

#     return _social_register_v2(request)


# def _social_register_v2(request):
#     """
#     Flow V2 ACTUEL — inchangé, juste un peu mieux outillé (next + logs).
#     """
#     next_url = (request.POST.get("next") or request.GET.get("next") or "").strip()

#     if request.method == "POST":
#         form = SocialRegistrationV2Form(request.POST, request.FILES)
#         if form.is_valid():
#             cleaned = form.cleaned_data

#             user = create_inactive_user_from_cleaned(cleaned)

#             payload = {
#                 "country": cleaned.get("country"),
#                 "phone_number": str(cleaned.get("phone_number")),
#                 "judicial_record": bool(cleaned.get("judicial_record")),
#                 "role_id": cleaned["role"].id if cleaned.get("role") else None,
#                 "message": cleaned.get("message", ""),
#                 "id_doc_type": cleaned.get("id_doc_type"),
#                 "id_number": cleaned.get("id_number"),
#             }

#             files_map = {
#                 RegistrationDocType.ID_FRONT: cleaned.get("id_front"),
#                 RegistrationDocType.ID_BACK: cleaned.get("id_back"),
#                 RegistrationDocType.SELFIE: cleaned.get("selfie"),
#                 RegistrationDocType.PROOF_ADDRESS: cleaned.get("proof_address"),
#             }

#             create_application_and_docs(
#                 user=user,
#                 category=RegistrationCategory.SOCIAL,
#                 track="social",
#                 payload=payload,
#                 files_map=files_map,
#             )

#             try:
#                 send_activation_email(request, user)
#                 messages.success(
#                     request,
#                     _("Inscription réussie. Un email d’activation vous a été envoyé.")
#                 )
#             except Exception:
#                 logger.exception("Activation email send failed (social V2)")
#                 messages.warning(
#                     request,
#                     _("Compte créé, mais l’envoi de l’email d’activation a échoué.")
#                 )

#             return redirect("accounts_users:web:registration:register_done")

#         messages.error(request, _("Veuillez corriger les erreurs du formulaire."))
#     else:
#         form = SocialRegistrationV2Form()

#     return render(
#         request,
#         "accounts_users/registration/register_social_form.html",
#         {
#             "form": form,
#             "next": next_url,
#             "page_title": _("Inscription — Social"),
#         },
#     )


# # ======================================================
# # 🔒 FLOW AVANCÉ — DORMANT (optionnel)
# # ======================================================
# def _social_register_advanced(request):
#     """
#     OFF par défaut.
#     Ici tu brancheras plus tard:
#     - OTP email
#     - SocialProfile
#     - code social
#     - email html custom
#     """
#     raise NotImplementedError("Advanced social registration is not enabled yet.")









# # accounts_users/web/views/social/social_registration_view.py

# from __future__ import annotations

# import logging

# from django.conf import settings
# from django.contrib import messages
# from django.shortcuts import redirect, render
# from django.utils.translation import gettext_lazy as _

# # ======================================================
# # BASE ACTUELLE (FICHIER 1 – ACTIVE)
# # ======================================================

# from accounts_users.forms.registration.social import SocialRegistrationV2Form
# from accounts_users.models.registration import RegistrationCategory, RegistrationDocType
# from accounts_users.web.services.registration_service import (
#     create_inactive_user_from_cleaned,
#     create_application_and_docs,
#     send_activation_email,
# )

# # ======================================================
# # IMPORTS AVANCÉS (FICHIER 2 – SAFE / DORMANTS)
# # ======================================================

# try:
#     from django.contrib.auth import get_user_model
#     from django.db import IntegrityError, transaction
#     from django.template.loader import render_to_string
#     from django.urls import reverse
#     from django.utils.encoding import force_bytes
#     from django.utils.http import urlsafe_base64_encode
#     from django.utils.timezone import now

#     from accounts_users.forms.signup_forms import UserSignupForm
#     from accounts_users.forms.social.social_registration_form import SocialRegistrationForm
#     from accounts_users.models.social.social_profile import SocialProfile
#     from accounts_users.services.email_otp_service import mark_profile_email_verified
#     from accounts_users.tokens import account_activation_token
#     from accounts_users.web.views._helpers import (
#         build_auth_context,
#         validate_latest_email_otp_or_add_error,
#     )

#     ADVANCED_SOCIAL_AVAILABLE = True
#     User = get_user_model()
# except Exception:
#     ADVANCED_SOCIAL_AVAILABLE = False
#     User = None

# logger = logging.getLogger(__name__)

# # ======================================================
# # HELPERS AVANCÉS (SAFE)
# # ======================================================

# def generate_social_code(role_code: str | None) -> str:
#     """
#     Génère un code court type M001 / V002 / D003 / I004.
#     Utilisé uniquement si SocialProfile est actif.
#     """
#     if not ADVANCED_SOCIAL_AVAILABLE:
#         return ""

#     role_code = (role_code or "").upper().strip()
#     prefix_map = {"MEMBER": "M", "VOLUNTEER": "V", "SPONSOR": "D", "INSTITUTION": "I"}
#     prefix = prefix_map.get(role_code, "U")

#     if role_code:
#         count = SocialProfile.objects.filter(membership_role__code=role_code).count() + 1
#     else:
#         count = SocialProfile.objects.count() + 1

#     return f"{prefix}{count:03}"


# # ======================================================
# # VUE PRINCIPALE (HYBRIDE – COMPORTEMENT INCHANGÉ)
# # ======================================================

# def social_register_view(request):
#     """
#     Inscription sociale – MODE HYBRIDE
#     --------------------------------------------------
#     ✔ Flow V2 (service layer) ACTIF par défaut
#     ✔ Flow avancé OTP / SocialProfile PRÊT mais OFF
#     ✔ Aucune régression
#     """

#     if request.user.is_authenticated:
#         return redirect("dashboard:hub")

#     # ==================================================
#     # MODE ACTUEL (FICHIER 1) — ACTIF
#     # ==================================================

#     if request.method == "POST":
#         form = SocialRegistrationV2Form(request.POST, request.FILES)
#         if form.is_valid():
#             cleaned = form.cleaned_data

#             user = create_inactive_user_from_cleaned(cleaned)

#             payload = {
#                 "country": cleaned.get("country"),
#                 "phone_number": str(cleaned.get("phone_number")),
#                 "judicial_record": bool(cleaned.get("judicial_record")),
#                 "role_id": cleaned["role"].id if cleaned.get("role") else None,
#                 "message": cleaned.get("message", ""),
#                 "id_doc_type": cleaned.get("id_doc_type"),
#                 "id_number": cleaned.get("id_number"),
#             }

#             files_map = {
#                 RegistrationDocType.ID_FRONT: cleaned.get("id_front"),
#                 RegistrationDocType.ID_BACK: cleaned.get("id_back"),
#                 RegistrationDocType.SELFIE: cleaned.get("selfie"),
#                 RegistrationDocType.PROOF_ADDRESS: cleaned.get("proof_address"),
#             }

#             create_application_and_docs(
#                 user=user,
#                 category=RegistrationCategory.SOCIAL,
#                 track="social",
#                 payload=payload,
#                 files_map=files_map,
#             )

#             try:
#                 send_activation_email(request, user)
#                 messages.success(
#                     request,
#                     _("Inscription réussie. Un email d’activation vous a été envoyé.")
#                 )
#             except Exception:
#                 messages.warning(
#                     request,
#                     _("Compte créé, mais l’envoi de l’email d’activation a échoué.")
#                 )

#             return redirect("accounts_users:web:registration:register_done")

#         messages.error(request, _("Veuillez corriger les erreurs du formulaire."))
#     else:
#         form = SocialRegistrationV2Form()

#     return render(
#         request,
#         "accounts_users/registration/register_social_form.html",
#         {
#             "form": form,
#             "page_title": _("Inscription — Social"),
#         },
#     )

# # ======================================================
# # 🔒 FLOW AVANCÉ (FICHIER 2) — VOLONTAIREMENT DÉSACTIVÉ
# # ======================================================
# #
# # ➜ OTP email
# # ➜ SocialProfile
# # ➜ Code social
# # ➜ Email HTML custom
# #
# # Pour l’activer plus tard :
# #   - créer une nouvelle vue
# #   - ou basculer via feature flag
# #
# # AUCUN IMPACT ACTUEL SUR L’APP
# # ======================================================







# # accounts_users/web/views/social/social_registration_view.py
# from __future__ import annotations

# from django.contrib import messages
# from django.shortcuts import redirect, render
# from django.utils.translation import gettext_lazy as _

# from accounts_users.forms.registration.social import SocialRegistrationV2Form
# from accounts_users.models.registration import RegistrationCategory, RegistrationDocType
# from accounts_users.web.services.registration_service import (
#     create_inactive_user_from_cleaned,
#     create_application_and_docs,
#     send_activation_email,
# )


# def social_register_view(request):
#     if request.user.is_authenticated:
#         return redirect("dashboard:hub")

#     if request.method == "POST":
#         form = SocialRegistrationV2Form(request.POST, request.FILES)
#         if form.is_valid():
#             cleaned = form.cleaned_data

#             user = create_inactive_user_from_cleaned(cleaned)

#             payload = {
#                 "country": cleaned.get("country"),
#                 "phone_number": str(cleaned.get("phone_number")),
#                 "judicial_record": bool(cleaned.get("judicial_record")),
#                 "role_id": cleaned["role"].id if cleaned.get("role") else None,
#                 "message": cleaned.get("message", ""),
#                 "id_doc_type": cleaned.get("id_doc_type"),
#                 "id_number": cleaned.get("id_number"),
#             }

#             files_map = {
#                 RegistrationDocType.ID_FRONT: cleaned.get("id_front"),
#                 RegistrationDocType.ID_BACK: cleaned.get("id_back"),
#                 RegistrationDocType.SELFIE: cleaned.get("selfie"),
#                 RegistrationDocType.PROOF_ADDRESS: cleaned.get("proof_address"),
#             }

#             create_application_and_docs(
#                 user=user,
#                 category=RegistrationCategory.SOCIAL,
#                 track="social",
#                 payload=payload,
#                 files_map=files_map,
#             )

#             try:
#                 send_activation_email(request, user)
#                 messages.success(request, _("Inscription réussie. Un email d’activation vous a été envoyé."))
#             except Exception:
#                 messages.warning(request, _("Compte créé, mais l’envoi de l’email d’activation a échoué."))

#             return redirect("accounts_users:web:registration:register_done")

#         messages.error(request, _("Veuillez corriger les erreurs du formulaire."))
#     else:
#         form = SocialRegistrationV2Form()

#     return render(
#         request,
#         "accounts_users/registration/register_social.html",
#         {"form": form, "page_title": _("Inscription — Social")},
#     )
