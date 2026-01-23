# accounts_users/api/views/registration_api.py
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, Type
from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import (
    url_has_allowed_host_and_scheme,
    urlsafe_base64_decode,
    urlsafe_base64_encode,
)
from django.utils.translation import gettext_lazy as _

from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from accounts_users.tokens import account_activation_token

# ======================================================
# LOGGING
# ======================================================
logger = logging.getLogger(__name__)

User = get_user_model()

# ======================================================
# FORMS (réutilisation logique Web)
# ======================================================

# Social V2 (service-layer)
from accounts_users.forms.registration.social import SocialRegistrationV2Form
from accounts_users.models.registration import RegistrationCategory, RegistrationDocType
from accounts_users.web.services.registration_service import (
    create_application_and_docs,
    create_inactive_user_from_cleaned,
    send_activation_email,
)

# Economic (hybride 3-forms)
from accounts_users.forms.economic.economic_core_registration import UserProfileEconomicForm
from accounts_users.forms.economic.economic_signup_forms import (
    ClientSignupForm,
    CompanySignupForm,
    VendorSignupForm,
)

# UserSignupForm (fallback safe)
try:
    from accounts_users.forms.signup_forms import UserSignupForm  # type: ignore
except Exception:
    from accounts_users.forms.social.social_signup_forms import UserSignupForm  # type: ignore


# ======================================================
# HELPERS
# ======================================================
def _form_errors(form) -> dict:
    """
    Convertit les errors Django Form en dict JSON-friendly.
    """
    out = {}
    for field, errors in form.errors.items():
        out[field] = [str(e) for e in errors]
    return out


def _safe_next(request) -> str:
    """
    Sécurise next si fourni (API).
    """
    nxt = (request.data.get("next") or request.query_params.get("next") or "").strip()
    if nxt and url_has_allowed_host_and_scheme(
        url=nxt,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return nxt
    return ""


def _send_activation_email_api(request, user) -> bool:
    """
    Envoi activation email (API) — même logique que Web.
    """
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = account_activation_token.make_token(user)

    activation_url = request.build_absolute_uri(
        reverse("accounts_users:web:registration:activate", kwargs={"uidb64": uidb64, "token": token})
    )

    subject = _("Activation de votre compte")
    context = {
        "user": user,
        "activation_url": activation_url,
        "PROJECT_NAME": getattr(settings, "PROJECT_NAME", "SOGENTIS"),
    }

    html_message = render_to_string("accounts_users/registration/account_activation_email.html", context)
    text_message = render_to_string("accounts_users/registration/account_activation_email.txt", context)

    try:
        from django.core.mail import EmailMultiAlternatives

        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_message,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
            to=[user.email],
        )
        msg.attach_alternative(html_message, "text/html")
        msg.send(fail_silently=False)
        return True
    except Exception:
        logger.exception("Activation email send failed (api)")
        return False


def _attach_track_profile(user, eco_profile, economic_obj) -> None:
    """
    Rattachements robustes selon tes modèles.
    """
    if hasattr(economic_obj, "user"):
        economic_obj.user = user
    if hasattr(economic_obj, "economic_profile"):
        economic_obj.economic_profile = eco_profile
    if hasattr(economic_obj, "profile"):
        economic_obj.profile = eco_profile
    if hasattr(economic_obj, "user_profile"):
        economic_obj.user_profile = eco_profile


def _try_create_or_update_economic_profile(user, track_code: str, profile_instance=None) -> None:
    """
    Mets à jour le profil économique central (UserEconomicProfile) en mode SAFE.
    """
    try:
        from accounts_users.models.users_economic_profile import UserEconomicProfile  # type: ignore
    except Exception:
        return

    try:
        from accounts_users.models.user_role import EconomicRole  # type: ignore
    except Exception:
        EconomicRole = None  # noqa: N806

    role_map = {
        "client": getattr(EconomicRole, "CLIENT", None) if EconomicRole else None,
        "vendor": getattr(EconomicRole, "VENDOR", None) if EconomicRole else None,
        "b2b": getattr(EconomicRole, "B2B", None) if EconomicRole else None,
    }
    requires_validation = track_code in {"vendor", "b2b"}

    profile = profile_instance
    if profile is None:
        profile, _ = UserEconomicProfile.objects.get_or_create(user=user)

    if hasattr(profile, "economic_role") and role_map.get(track_code) is not None:
        profile.economic_role = role_map[track_code]

    if requires_validation:
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


# ======================================================
# TRACKS
# ======================================================
@dataclass(frozen=True)
class TrackInfo:
    code: str
    title: str
    subtitle: str
    badge: str


TRACKS: Dict[str, TrackInfo] = {
    "client": TrackInfo(
        code="client",
        title=_("Compte Client (B2C)"),
        subtitle=_("Acheter, gérer panier/favoris, suivre commandes et accéder aux services."),
        badge="🛒",
    ),
    "vendor": TrackInfo(
        code="vendor",
        title=_("Espace Vendeur"),
        subtitle=_("Vendre des produits, gérer catalogue, stock et commandes."),
        badge="🏪",
    ),
    "b2b": TrackInfo(
        code="b2b",
        title=_("Compte Entreprise (B2B)"),
        subtitle=_("Commandes en gros, RFQ, facturation et gestion d’entreprise."),
        badge="🏢",
    ),
}


def _get_track_code(request) -> str:
    raw = (request.data.get("track") or request.query_params.get("track") or "client").strip().lower()
    return raw if raw in TRACKS else "client"


def _economic_form_for(track_code: str) -> Type:
    if track_code == "vendor":
        return VendorSignupForm
    if track_code == "b2b":
        return CompanySignupForm
    return ClientSignupForm


# ======================================================
# API VIEWS
# ======================================================
class SocialRegistrationAPIView(APIView):
    """
    POST (multipart) : crée un compte inactif + application + docs + email activation.
    Repose sur SocialRegistrationV2Form (même logique que Web).
    """
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request) -> Response:
        if getattr(request.user, "is_authenticated", False):
            return Response(
                {"detail": _("Vous êtes déjà connecté.")},
                status=HTTP_400_BAD_REQUEST,
            )

        form = SocialRegistrationV2Form(request.data, request.FILES)
        if not form.is_valid():
            return Response(
                {"detail": _("Validation échouée."), "errors": _form_errors(form)},
                status=HTTP_400_BAD_REQUEST,
            )

        cleaned = form.cleaned_data

        with transaction.atomic():
            user = create_inactive_user_from_cleaned(cleaned)

            payload = {
                "country": cleaned.get("country"),
                "phone_number": str(cleaned.get("phone_number")),
                "judicial_record": bool(cleaned.get("judicial_record")),
                "role_id": cleaned["role"].id if cleaned.get("role") else None,
                "message": cleaned.get("message", ""),
                "id_doc_type": cleaned.get("id_doc_type"),
                "id_number": cleaned.get("id_number"),
            }

            files_map = {
                RegistrationDocType.ID_FRONT: cleaned.get("id_front"),
                RegistrationDocType.ID_BACK: cleaned.get("id_back"),
                RegistrationDocType.SELFIE: cleaned.get("selfie"),
                RegistrationDocType.PROOF_ADDRESS: cleaned.get("proof_address"),
            }

            create_application_and_docs(
                user=user,
                category=RegistrationCategory.SOCIAL,
                track="social",
                payload=payload,
                files_map=files_map,
            )

        # Envoi email activation (service existant)
        activation_sent = True
        try:
            send_activation_email(request, user)
        except Exception:
            activation_sent = False
            logger.exception("Activation email send failed (social api)")

        return Response(
            {
                "detail": _("Inscription réussie."),
                "track": "social",
                "activation_required": True,
                "activation_sent": activation_sent,
            },
            status=HTTP_201_CREATED,
        )


class EconomicRegistrationAPIView(APIView):
    """
    POST (multipart) : inscription économique (client/vendor/b2b)
    - 3 forms : user_form + profile_form + economic_form(track)
    - user inactif + email activation
    """
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request) -> Response:
        if getattr(request.user, "is_authenticated", False):
            return Response(
                {"detail": _("Vous êtes déjà connecté.")},
                status=HTTP_400_BAD_REQUEST,
            )

        track_code = _get_track_code(request)
        economic_form_class = _economic_form_for(track_code)

        user_form = UserSignupForm(request.data)
        profile_form = UserProfileEconomicForm(request.data, request.FILES)
        economic_form = economic_form_class(request.data, request.FILES)

        ok = user_form.is_valid() and profile_form.is_valid() and economic_form.is_valid()
        if not ok:
            return Response(
                {
                    "detail": _("Validation échouée."),
                    "errors": {
                        "user_form": _form_errors(user_form),
                        "profile_form": _form_errors(profile_form),
                        "economic_form": _form_errors(economic_form),
                    },
                    "track": track_code,
                },
                status=HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            # 1) user
            user = user_form.save(commit=False)
            user.is_active = False
            user.save()

            # 2) profil éco central
            eco_profile = profile_form.save(user=user, commit=True)

            # 3) profil track
            obj = economic_form.save(commit=False)
            _attach_track_profile(user, eco_profile, obj)
            obj.save()
            if hasattr(economic_form, "save_m2m"):
                economic_form.save_m2m()

            # 4) flags/roles
            _try_create_or_update_economic_profile(user, track_code, profile_instance=eco_profile)

        activation_sent = _send_activation_email_api(request, user)

        return Response(
            {
                "detail": _("Inscription réussie."),
                "track": track_code,
                "activation_required": True,
                "activation_sent": activation_sent,
            },
            status=HTTP_201_CREATED,
        )


class ResendActivationAPIView(APIView):
    """
    POST: {email: "..."} -> renvoie un email d’activation si user existe et est inactif.
    """
    permission_classes = [AllowAny]
    parser_classes = [FormParser]

    def post(self, request) -> Response:
        email = (request.data.get("email") or "").strip().lower()
        if not email:
            return Response({"detail": _("Email requis.")}, status=HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Réponse neutre (anti-enum)
            return Response(
                {"detail": _("Si un compte existe, un email a été renvoyé.")},
                status=HTTP_200_OK,
            )

        if user.is_active:
            return Response(
                {"detail": _("Ce compte est déjà activé.")},
                status=HTTP_200_OK,
            )

        sent = _send_activation_email_api(request, user)
        return Response(
            {"detail": _("Email d’activation renvoyé.") if sent else _("Échec d’envoi de l’email.")},
            status=HTTP_200_OK,
        )


class ActivateAccountAPIView(APIView):
    """
    POST /activate/ avec uidb64 + token (ou GET si tu préfères côté API)
    - Active le compte si token valide.
    """
    permission_classes = [AllowAny]

    def post(self, request, uidb64: str, token: str) -> Response:
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except Exception:
            return Response({"detail": _("Lien invalide.")}, status=HTTP_400_BAD_REQUEST)

        if account_activation_token.check_token(user, token):
            user.is_active = True
            user.save(update_fields=["is_active"])
            return Response({"detail": _("Compte activé avec succès.")}, status=HTTP_200_OK)

        return Response({"detail": _("Token invalide ou expiré.")}, status=HTTP_400_BAD_REQUEST)


class RegistrationMetaAPIView(APIView):
    """
    GET: renvoie les tracks disponibles (utile pour front SPA).
    """
    permission_classes = [AllowAny]

    def get(self, request) -> Response:
        return Response(
            {
                "tracks": [
                    {
                        "code": t.code,
                        "title": str(t.title),
                        "subtitle": str(t.subtitle),
                        "badge": t.badge,
                    }
                    for t in TRACKS.values()
                ]
            },
            status=HTTP_200_OK,
        )






# # accounts_users/api/views/registration_api.py
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status, permissions
# from accounts_users.forms.signup_forms import UserSignupForm 
# from accounts_users.forms.social.social_signup_forms import UserSignupForm

# class RegisterAPIView(APIView):
#     permission_classes = [permissions.AllowAny]

#     def post(self, request):
#         data = request.data.copy()
#         files = request.FILES

#         # Création des formulaires
#         user_form = UserSignupForm(data)
#         profile_form = UserSignupForm(data, files)

#         if user_form.is_valid() and profile_form.is_valid():
#             # Création de l'utilisateur
#             user = user_form.save(commit=False)
#             user.set_password(user_form.cleaned_data["password"])
#             user.save()

#             # Création du profil utilisateur
#             profile = profile_form.save(commit=False)
#             profile.user = user
#             profile.save()

#             return Response({'detail': 'Inscription réussie.'}, status=status.HTTP_201_CREATED)

#         return Response({
#             'user_errors': user_form.errors,
#             'profile_errors': profile_form.errors
#         }, status=status.HTTP_400_BAD_REQUEST)




# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status, permissions
# from accounts_users.forms.signup_forms import UserSignupForm, UserProfileForm

# class RegisterAPIView(APIView):
#     permission_classes = [permissions.AllowAny]

#     def post(self, request):
#         user_form = UserSignupForm(request.data)
#         profile_form = UserProfileForm(request.data)
#         if user_form.is_valid() and profile_form.is_valid():
#             user = user_form.save(commit=False)
#             user.set_password(user_form.cleaned_data["password"])
#             user.save()
#             profile = profile_form.save(commit=False)
#             profile.user = user
#             profile.save()
#             return Response({'detail': 'Inscription réussie.'}, status=status.HTTP_201_CREATED)
#         return Response({
#             'user_errors': user_form.errors,
#             'profile_errors': profile_form.errors
#         }, status=status.HTTP_400_BAD_REQUEST)
