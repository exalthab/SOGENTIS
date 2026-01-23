# accounts_users/services/email_otp_service.py
from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import timedelta
from typing import Optional

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage, send_mail
from django.core.validators import validate_email
from django.db import transaction
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from accounts_users.models.email_otp import EmailOTP

# Imports "safe" (ne casse pas si un module change)
try:
    from accounts_users.models.social.social_profile import SocialProfile
except Exception:  # pragma: no cover
    SocialProfile = None  # type: ignore

try:
    from accounts_users.models.users_economic_profile import UserEconomicProfile
except Exception:  # pragma: no cover
    UserEconomicProfile = None  # type: ignore


# ============================================================
# CONFIG (surchargeable via settings)
# ============================================================
MAX_OTP_PER_WINDOW = int(getattr(settings, "MAX_OTP_PER_WINDOW", 3))
WINDOW_MINUTES = int(getattr(settings, "OTP_WINDOW_MINUTES", 15))
OTP_EXPIRY_MINUTES = int(getattr(settings, "OTP_EXPIRY_MINUTES", 5))

# Anti-spam UX (cooldown entre 2 envois)
EMAIL_OTP_RESEND_COOLDOWN_SECONDS = int(
    getattr(settings, "EMAIL_OTP_RESEND_COOLDOWN_SECONDS", 60)
)

# Limite d'essais de saisie du code (par IP + email + otp.id)
EMAIL_OTP_MAX_VERIFY_ATTEMPTS = int(
    getattr(settings, "EMAIL_OTP_MAX_VERIFY_ATTEMPTS", 5)
)


# ============================================================
# HELPERS
# ============================================================
def _client_ip(request) -> str:
    if not request:
        return "0.0.0.0"
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR") or "0.0.0.0"


def _normalize_email(value: str) -> str:
    email = (value or "").strip().lower()
    if not email:
        raise ValidationError(_("Email manquant."))
    validate_email(email)
    return email


def generate_otp_code() -> str:
    """Génère un code OTP à 6 chiffres."""
    return f"{random.randint(100000, 999999)}"


def can_send_otp(email: str) -> bool:
    """
    Limitation par fenêtre :
    MAX_OTP_PER_WINDOW OTP / WINDOW_MINUTES pour un email.
    """
    since = now() - timedelta(minutes=WINDOW_MINUTES)
    count = EmailOTP.objects.filter(email=email, created_at__gte=since).count()
    return count < MAX_OTP_PER_WINDOW


def _send_otp_email(email: str, code: str) -> None:
    subject = getattr(
        settings,
        "EMAIL_OTP_SUBJECT",
        str(_("Votre code de vérification SOGENTIS")),
    )
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None)
    message = str(_("Votre code OTP est : %(code)s") % {"code": code})

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=[email],
            fail_silently=False,
        )
    except Exception:
        # fallback robuste
        msg = EmailMessage(subject=subject, body=message, from_email=from_email, to=[email])
        msg.send(fail_silently=False)


def _get_latest_active_otp(email: str) -> Optional[EmailOTP]:
    return (
        EmailOTP.objects.filter(
            email=email,
            is_verified=False,
            is_expired=False,
            expires_at__gt=now(),
        )
        .order_by("-created_at")
        .first()
    )


# ============================================================
# CORE OTP LOGIC
# ============================================================
def create_email_otp(email: str) -> EmailOTP:
    """
    Crée un OTP (6 chiffres), expire les anciens, et envoie l'email.
    """
    email = _normalize_email(email)

    if not can_send_otp(email):
        raise ValidationError(_("Trop de tentatives. Réessayez plus tard."))

    with transaction.atomic():
        EmailOTP.objects.filter(email=email, is_verified=False, is_expired=False).update(is_expired=True)

        otp = EmailOTP.objects.create(
            email=email,
            code=generate_otp_code(),
            expires_at=now() + timedelta(minutes=OTP_EXPIRY_MINUTES),
        )

    _send_otp_email(email, otp.code)
    return otp


def verify_email_otp(request, email: str, code: str) -> None:
    """
    Vérifie le code OTP en DB :
    - prend le dernier OTP actif
    - contrôle expiration
    - limite tentatives via cache (IP + email + otp.id)
    - marque is_verified=True + is_expired=True
    """
    email = _normalize_email(email)
    code = (code or "").strip()

    if not code or not code.isdigit() or len(code) != 6:
        raise ValidationError(_("Veuillez saisir un code à 6 chiffres."))

    otp = _get_latest_active_otp(email)
    if not otp:
        raise ValidationError(_("Aucun code actif. Cliquez sur “Envoyer le code”."))

    ip = _client_ip(request)
    attempts_key = f"emailotp:attempts:{ip}:{email}:{otp.id}"
    attempts = int(cache.get(attempts_key) or 0)

    if attempts >= EMAIL_OTP_MAX_VERIFY_ATTEMPTS:
        otp.is_expired = True
        otp.save(update_fields=["is_expired"])
        raise ValidationError(_("Trop de tentatives. Renvoyez un nouveau code."))

    if otp.code != code:
        cache.set(attempts_key, attempts + 1, OTP_EXPIRY_MINUTES * 60)
        raise ValidationError(_("Code invalide."))

    otp.is_verified = True
    otp.is_expired = True

    update_fields = ["is_verified", "is_expired"]
    if hasattr(otp, "verified_at"):
        otp.verified_at = now()
        update_fields.append("verified_at")

    otp.save(update_fields=update_fields)
    mark_profile_email_verified(email)


# ============================================================
# STRICT VALIDATION (UTILISÉE PAR LES VUES)
# ============================================================
def validate_latest_email_otp_or_raise(*, email: str, otp_code: str) -> None:
    """
    Validation STRICTE utilisée côté backend (views) :
    - ne dépend PAS de request
    - lève ValidationError si invalide
    - consomme l'OTP si OK
    """
    email = _normalize_email(email)
    code = (otp_code or "").strip()

    if not code or not code.isdigit() or len(code) != 6:
        raise ValidationError(_("Code OTP invalide."))

    otp = _get_latest_active_otp(email)
    if not otp:
        raise ValidationError(_("Aucun code OTP valide trouvé."))

    if otp.code != code:
        raise ValidationError(_("Code OTP incorrect."))

    otp.is_verified = True
    otp.is_expired = True

    update_fields = ["is_verified", "is_expired"]
    if hasattr(otp, "verified_at"):
        otp.verified_at = now()
        update_fields.append("verified_at")

    otp.save(update_fields=update_fields)
    mark_profile_email_verified(email)


# ============================================================
# PROFIL EMAIL VERIFIED
# ============================================================
def mark_profile_email_verified(email: str) -> None:
    """
    Marque l'email comme vérifié dans les profils si possible (sans casser).
    """
    email = (email or "").strip().lower()
    if not email:
        return

    # ---- SocialProfile ----
    if SocialProfile is not None:
        try:
            p = SocialProfile.objects.filter(email__iexact=email).first()
            if p:
                if hasattr(p, "mark_email_verified"):
                    p.mark_email_verified()
                elif hasattr(p, "email_verified"):
                    p.email_verified = True
                    p.save(update_fields=["email_verified"])
                elif hasattr(p, "is_email_verified"):
                    p.is_email_verified = True
                    p.save(update_fields=["is_email_verified"])
        except Exception:
            pass

    # ---- UserEconomicProfile ----
    if UserEconomicProfile is not None:
        try:
            qs = UserEconomicProfile.objects.all()
            if hasattr(UserEconomicProfile, "user"):
                qs = qs.filter(user__email__iexact=email)

            p = qs.first()
            if p:
                if hasattr(p, "mark_email_verified"):
                    p.mark_email_verified()
                elif hasattr(p, "email_verified"):
                    p.email_verified = True
                    p.save(update_fields=["email_verified"])
                elif hasattr(p, "is_email_verified"):
                    p.is_email_verified = True
                    p.save(update_fields=["is_email_verified"])
        except Exception:
            pass


# ============================================================
# AJAX-FRIENDLY WRAPPERS
# ============================================================
@dataclass(frozen=True)
class SendOtpResult:
    ok: bool
    message: str
    cooldown: int = EMAIL_OTP_RESEND_COOLDOWN_SECONDS
    expires_in: int = OTP_EXPIRY_MINUTES * 60


@dataclass(frozen=True)
class VerifyOtpResult:
    ok: bool
    message: str
    expires_in: int = OTP_EXPIRY_MINUTES * 60


def send_email_otp(request, email: str) -> SendOtpResult:
    """
    Wrapper AJAX :
    - cooldown IP + email
    - limite fenêtre DB
    """
    try:
        email = _normalize_email(email)
    except ValidationError as e:
        return SendOtpResult(False, " ".join(e.messages))

    ip = _client_ip(request)
    cooldown_key = f"emailotp:cooldown:{ip}:{email}"
    if cache.get(cooldown_key):
        return SendOtpResult(False, str(_("Veuillez patienter avant de renvoyer un code.")))

    try:
        create_email_otp(email)
    except ValidationError as e:
        return SendOtpResult(False, " ".join(e.messages))
    except Exception:
        return SendOtpResult(False, str(_("Erreur lors de l’envoi du code. Réessayez.")))

    cache.set(cooldown_key, True, EMAIL_OTP_RESEND_COOLDOWN_SECONDS)
    return SendOtpResult(True, str(_("Code envoyé. Vérifiez votre email puis saisissez les 6 chiffres.")))


def verify_email_otp_ajax(request, email: str, code: str) -> VerifyOtpResult:
    """
    Wrapper AJAX pour la vérification :
    - renvoie ok/message (sans stacktrace côté front)
    - conserve la logique anti-abus (tentatives) de verify_email_otp()
    """
    try:
        verify_email_otp(request, email=email, code=code)
        return VerifyOtpResult(True, str(_("Email vérifié. Vous pouvez créer votre compte.")))
    except ValidationError as e:
        return VerifyOtpResult(False, " ".join(e.messages))
    except Exception:
        return VerifyOtpResult(False, str(_("Erreur de vérification. Réessayez.")))






# # accounts_users/services/email_otp_service.py
# from __future__ import annotations

# import random
# from dataclasses import dataclass
# from datetime import timedelta
# from typing import Optional

# from django.conf import settings
# from django.core.cache import cache
# from django.core.exceptions import ValidationError
# from django.core.mail import EmailMessage, send_mail
# from django.core.validators import validate_email
# from django.db import transaction
# from django.utils.timezone import now
# from django.utils.translation import gettext_lazy as _

# from accounts_users.models.email_otp import EmailOTP

# # Imports "safe" (ne casse pas si un module change)
# try:
#     from accounts_users.models.social.social_profile import SocialProfile
# except Exception:  # pragma: no cover
#     SocialProfile = None  # type: ignore

# try:
#     from accounts_users.models.users_economic_profile import UserEconomicProfile
# except Exception:  # pragma: no cover
#     UserEconomicProfile = None  # type: ignore


# # ============================================================
# # CONFIG (surchargable via settings)
# # ============================================================
# MAX_OTP_PER_WINDOW = int(getattr(settings, "MAX_OTP_PER_WINDOW", 3))
# WINDOW_MINUTES = int(getattr(settings, "OTP_WINDOW_MINUTES", 15))
# OTP_EXPIRY_MINUTES = int(getattr(settings, "OTP_EXPIRY_MINUTES", 5))

# # Anti-spam UX (cooldown entre 2 envois)
# EMAIL_OTP_RESEND_COOLDOWN_SECONDS = int(
#     getattr(settings, "EMAIL_OTP_RESEND_COOLDOWN_SECONDS", 60)
# )

# # Limite d'essais de saisie du code (par IP + email + otp.id)
# EMAIL_OTP_MAX_VERIFY_ATTEMPTS = int(
#     getattr(settings, "EMAIL_OTP_MAX_VERIFY_ATTEMPTS", 5)
# )


# # ============================================================
# # HELPERS
# # ============================================================
# def _client_ip(request) -> str:
#     if not request:
#         return "0.0.0.0"
#     xff = request.META.get("HTTP_X_FORWARDED_FOR")
#     if xff:
#         return xff.split(",")[0].strip()
#     return request.META.get("REMOTE_ADDR") or "0.0.0.0"


# def _normalize_email(value: str) -> str:
#     email = (value or "").strip().lower()
#     if not email:
#         raise ValidationError(_("Email manquant."))
#     validate_email(email)
#     return email


# def generate_otp_code() -> str:
#     """Génère un code OTP à 6 chiffres."""
#     return f"{random.randint(100000, 999999)}"


# def can_send_otp(email: str) -> bool:
#     """
#     Limitation par fenêtre :
#     MAX_OTP_PER_WINDOW OTP / WINDOW_MINUTES pour un email.
#     """
#     since = now() - timedelta(minutes=WINDOW_MINUTES)
#     count = EmailOTP.objects.filter(email=email, created_at__gte=since).count()
#     return count < MAX_OTP_PER_WINDOW


# def _send_otp_email(email: str, code: str) -> None:
#     subject = getattr(
#         settings,
#         "EMAIL_OTP_SUBJECT",
#         str(_("Votre code de vérification SOGENTIS")),
#     )
#     from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None)
#     message = str(_("Votre code OTP est : %(code)s") % {"code": code})

#     try:
#         send_mail(
#             subject=subject,
#             message=message,
#             from_email=from_email,
#             recipient_list=[email],
#             fail_silently=False,
#         )
#     except Exception:
#         # fallback robuste
#         msg = EmailMessage(
#             subject=subject,
#             body=message,
#             from_email=from_email,
#             to=[email],
#         )
#         msg.send(fail_silently=False)


# def _get_latest_active_otp(email: str) -> Optional[EmailOTP]:
#     return (
#         EmailOTP.objects.filter(
#             email=email,
#             is_verified=False,
#             is_expired=False,
#             expires_at__gt=now(),
#         )
#         .order_by("-created_at")
#         .first()
#     )


# # ============================================================
# # CORE OTP LOGIC
# # ============================================================
# def create_email_otp(email: str) -> EmailOTP:
#     """
#     Crée un OTP (6 chiffres), expire les anciens, et envoie l'email.
#     """
#     email = _normalize_email(email)

#     if not can_send_otp(email):
#         raise ValidationError(_("Trop de tentatives. Réessayez plus tard."))

#     with transaction.atomic():
#         # Expire OTP précédents non utilisés
#         EmailOTP.objects.filter(
#             email=email,
#             is_verified=False,
#             is_expired=False,
#         ).update(is_expired=True)

#         otp = EmailOTP.objects.create(
#             email=email,
#             code=generate_otp_code(),
#             expires_at=now() + timedelta(minutes=OTP_EXPIRY_MINUTES),
#         )

#     _send_otp_email(email, otp.code)
#     return otp


# def verify_email_otp(request, email: str, code: str) -> None:
#     """
#     Vérifie le code OTP en DB :
#     - prend le dernier OTP actif
#     - contrôle expiration
#     - limite tentatives via cache (IP + email + otp.id)
#     - marque is_verified=True + is_expired=True
#     """
#     email = _normalize_email(email)
#     code = (code or "").strip()

#     if not code or not code.isdigit() or len(code) != 6:
#         raise ValidationError(_("Veuillez saisir un code à 6 chiffres."))

#     otp = _get_latest_active_otp(email)
#     if not otp:
#         raise ValidationError(_("Aucun code actif. Cliquez sur “Envoyer le code”."))

#     ip = _client_ip(request)
#     attempts_key = f"emailotp:attempts:{ip}:{email}:{otp.id}"
#     attempts = int(cache.get(attempts_key) or 0)

#     if attempts >= EMAIL_OTP_MAX_VERIFY_ATTEMPTS:
#         otp.is_expired = True
#         otp.save(update_fields=["is_expired"])
#         raise ValidationError(_("Trop de tentatives. Renvoyez un nouveau code."))

#     if otp.code != code:
#         cache.set(attempts_key, attempts + 1, OTP_EXPIRY_MINUTES * 60)
#         raise ValidationError(_("Code invalide."))

#     # OK → consommer OTP
#     otp.is_verified = True
#     otp.is_expired = True

#     update_fields = ["is_verified", "is_expired"]
#     if hasattr(otp, "verified_at"):
#         otp.verified_at = now()
#         update_fields.append("verified_at")

#     otp.save(update_fields=update_fields)

#     mark_profile_email_verified(email)


# # ============================================================
# # STRICT VALIDATION (UTILISÉE PAR LES VUES)
# # ============================================================
# def validate_latest_email_otp_or_raise(*, email: str, otp_code: str) -> None:
#     """
#     Validation STRICTE utilisée côté backend (views) :
#     - ne dépend PAS de request
#     - lève ValidationError si invalide
#     - consomme l'OTP si OK
#     """
#     email = _normalize_email(email)
#     code = (otp_code or "").strip()

#     if not code or not code.isdigit() or len(code) != 6:
#         raise ValidationError(_("Code OTP invalide."))

#     otp = _get_latest_active_otp(email)
#     if not otp:
#         raise ValidationError(_("Aucun code OTP valide trouvé."))

#     if otp.code != code:
#         raise ValidationError(_("Code OTP incorrect."))

#     otp.is_verified = True
#     otp.is_expired = True

#     update_fields = ["is_verified", "is_expired"]
#     if hasattr(otp, "verified_at"):
#         otp.verified_at = now()
#         update_fields.append("verified_at")

#     otp.save(update_fields=update_fields)

#     mark_profile_email_verified(email)


# # ============================================================
# # PROFIL EMAIL VERIFIED
# # ============================================================
# def mark_profile_email_verified(email: str) -> None:
#     """
#     Marque l'email comme vérifié dans les profils si possible (sans casser).
#     """
#     email = (email or "").strip().lower()
#     if not email:
#         return

#     # ---- SocialProfile ----
#     if SocialProfile is not None:
#         try:
#             p = SocialProfile.objects.filter(email__iexact=email).first()
#             if p:
#                 if hasattr(p, "mark_email_verified"):
#                     p.mark_email_verified()
#                 elif hasattr(p, "email_verified"):
#                     p.email_verified = True
#                     p.save(update_fields=["email_verified"])
#                 elif hasattr(p, "is_email_verified"):
#                     p.is_email_verified = True
#                     p.save(update_fields=["is_email_verified"])
#         except Exception:
#             pass

#     # ---- UserEconomicProfile ----
#     if UserEconomicProfile is not None:
#         try:
#             qs = UserEconomicProfile.objects.all()
#             if hasattr(UserEconomicProfile, "user"):
#                 qs = qs.filter(user__email__iexact=email)

#             p = qs.first()
#             if p:
#                 if hasattr(p, "mark_email_verified"):
#                     p.mark_email_verified()
#                 elif hasattr(p, "email_verified"):
#                     p.email_verified = True
#                     p.save(update_fields=["email_verified"])
#                 elif hasattr(p, "is_email_verified"):
#                     p.is_email_verified = True
#                     p.save(update_fields=["is_email_verified"])
#         except Exception:
#             pass


# # ============================================================
# # AJAX-FRIENDLY WRAPPERS
# # ============================================================
# @dataclass(frozen=True)
# class SendOtpResult:
#     ok: bool
#     message: str
#     cooldown: int = EMAIL_OTP_RESEND_COOLDOWN_SECONDS
#     expires_in: int = OTP_EXPIRY_MINUTES * 60


# @dataclass(frozen=True)
# class VerifyOtpResult:
#     ok: bool
#     message: str
#     expires_in: int = OTP_EXPIRY_MINUTES * 60


# def send_email_otp(request, email: str) -> SendOtpResult:
#     """
#     Wrapper AJAX :
#     - cooldown IP + email
#     - limite fenêtre DB
#     """
#     try:
#         email = _normalize_email(email)
#     except ValidationError as e:
#         return SendOtpResult(False, " ".join(e.messages))

#     ip = _client_ip(request)
#     cooldown_key = f"emailotp:cooldown:{ip}:{email}"
#     if cache.get(cooldown_key):
#         return SendOtpResult(False, str(_("Veuillez patienter avant de renvoyer un code.")))

#     try:
#         create_email_otp(email)
#     except ValidationError as e:
#         return SendOtpResult(False, " ".join(e.messages))
#     except Exception:
#         return SendOtpResult(False, str(_("Erreur lors de l’envoi du code. Réessayez.")))

#     cache.set(cooldown_key, True, EMAIL_OTP_RESEND_COOLDOWN_SECONDS)
#     return SendOtpResult(True, str(_("Code envoyé. Vérifiez votre email puis saisissez les 6 chiffres.")))


# def verify_email_otp_ajax(request, email: str, code: str) -> VerifyOtpResult:
#     """
#     Wrapper AJAX pour la vérification :
#     - renvoie ok/message (sans stacktrace côté front)
#     - conserve la logique anti-abus (tentatives) de verify_email_otp()
#     """
#     try:
#         verify_email_otp(request, email=email, code=code)
#         return VerifyOtpResult(True, str(_("Email vérifié. Vous pouvez créer votre compte.")))
#     except ValidationError as e:
#         return VerifyOtpResult(False, " ".join(e.messages))
#     except Exception:
#         return VerifyOtpResult(False, str(_("Erreur de vérification. Réessayez.")))







# # accounts_users/services/email_otp_service.py
# from __future__ import annotations

# import random
# from dataclasses import dataclass
# from datetime import timedelta

# from django.conf import settings
# from django.core.cache import cache
# from django.core.exceptions import ValidationError
# from django.core.mail import EmailMessage, send_mail
# from django.core.validators import validate_email
# from django.db import transaction
# from django.utils.timezone import now
# from django.utils.translation import gettext_lazy as _

# from accounts_users.models.email_otp import EmailOTP

# # Imports "safe" (ne casse pas si un module change)
# try:
#     from accounts_users.models.social.social_profile import SocialProfile
# except Exception:  # pragma: no cover
#     SocialProfile = None  # type: ignore

# try:
#     from accounts_users.models.users_economic_profile import UserEconomicProfile
# except Exception:  # pragma: no cover
#     UserEconomicProfile = None  # type: ignore


# # ============================================================
# # CONFIG (surchargable via settings)
# # ============================================================
# MAX_OTP_PER_WINDOW = int(getattr(settings, "MAX_OTP_PER_WINDOW", 3))
# WINDOW_MINUTES = int(getattr(settings, "OTP_WINDOW_MINUTES", 15))
# OTP_EXPIRY_MINUTES = int(getattr(settings, "OTP_EXPIRY_MINUTES", 5))

# # Anti-spam UX (cooldown entre 2 envois)
# EMAIL_OTP_RESEND_COOLDOWN_SECONDS = int(
#     getattr(settings, "EMAIL_OTP_RESEND_COOLDOWN_SECONDS", 60)
# )

# # Limite d'essais de saisie du code
# EMAIL_OTP_MAX_VERIFY_ATTEMPTS = int(
#     getattr(settings, "EMAIL_OTP_MAX_VERIFY_ATTEMPTS", 5)
# )


# # ============================================================
# # HELPERS
# # ============================================================

# def _client_ip(request) -> str:
#     if not request:
#         return "0.0.0.0"
#     xff = request.META.get("HTTP_X_FORWARDED_FOR")
#     if xff:
#         return xff.split(",")[0].strip()
#     return request.META.get("REMOTE_ADDR") or "0.0.0.0"


# def _normalize_email(value: str) -> str:
#     email = (value or "").strip().lower()
#     if not email:
#         raise ValidationError(_("Email manquant."))
#     validate_email(email)
#     return email


# def generate_otp_code() -> str:
#     """Génère un code OTP à 6 chiffres."""
#     return f"{random.randint(100000, 999999)}"


# def can_send_otp(email: str) -> bool:
#     """
#     Limitation par fenêtre :
#     MAX_OTP_PER_WINDOW OTP / WINDOW_MINUTES pour un email.
#     """
#     since = now() - timedelta(minutes=WINDOW_MINUTES)
#     count = EmailOTP.objects.filter(email=email, created_at__gte=since).count()
#     return count < MAX_OTP_PER_WINDOW


# def _send_otp_email(email: str, code: str) -> None:
#     subject = getattr(
#         settings,
#         "EMAIL_OTP_SUBJECT",
#         str(_("Votre code de vérification SOGENTIS")),
#     )
#     from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None)
#     message = str(_("Votre code OTP est : %(code)s") % {"code": code})

#     try:
#         send_mail(
#             subject=subject,
#             message=message,
#             from_email=from_email,
#             recipient_list=[email],
#             fail_silently=False,
#         )
#     except Exception:
#         # fallback robuste
#         msg = EmailMessage(
#             subject=subject,
#             body=message,
#             from_email=from_email,
#             to=[email],
#         )
#         msg.send(fail_silently=False)


# # ============================================================
# # CORE OTP LOGIC
# # ============================================================

# def create_email_otp(email: str) -> EmailOTP:
#     """
#     Crée un OTP (6 chiffres), expire les anciens, et envoie l'email.
#     """
#     email = _normalize_email(email)

#     if not can_send_otp(email):
#         raise ValidationError(_("Trop de tentatives. Réessayez plus tard."))

#     with transaction.atomic():
#         # Expire OTP précédents non utilisés
#         EmailOTP.objects.filter(
#             email=email,
#             is_verified=False,
#             is_expired=False,
#         ).update(is_expired=True)

#         otp = EmailOTP.objects.create(
#             email=email,
#             code=generate_otp_code(),
#             expires_at=now() + timedelta(minutes=OTP_EXPIRY_MINUTES),
#         )

#     _send_otp_email(email, otp.code)
#     return otp


# def verify_email_otp(request, email: str, code: str) -> None:
#     """
#     Vérifie le code OTP en DB :
#     - prend le dernier OTP actif
#     - contrôle expiration
#     - limite tentatives via cache
#     - marque is_verified=True + is_expired=True
#     """
#     email = _normalize_email(email)
#     code = (code or "").strip()

#     if not code or not code.isdigit() or len(code) != 6:
#         raise ValidationError(_("Veuillez saisir un code à 6 chiffres."))

#     otp = (
#         EmailOTP.objects.filter(
#             email=email,
#             is_verified=False,
#             is_expired=False,
#             expires_at__gt=now(),
#         )
#         .order_by("-created_at")
#         .first()
#     )

#     if not otp:
#         raise ValidationError(_("Aucun code actif. Cliquez sur “Envoyer le code”."))

#     ip = _client_ip(request)
#     attempts_key = f"emailotp:attempts:{ip}:{email}:{otp.id}"
#     attempts = int(cache.get(attempts_key) or 0)

#     if attempts >= EMAIL_OTP_MAX_VERIFY_ATTEMPTS:
#         otp.is_expired = True
#         otp.save(update_fields=["is_expired"])
#         raise ValidationError(_("Trop de tentatives. Renvoyez un nouveau code."))

#     if otp.code != code:
#         cache.set(attempts_key, attempts + 1, OTP_EXPIRY_MINUTES * 60)
#         raise ValidationError(_("Code invalide."))

#     # OK → consommer OTP
#     otp.is_verified = True
#     otp.is_expired = True

#     update_fields = ["is_verified", "is_expired"]
#     if hasattr(otp, "verified_at"):
#         otp.verified_at = now()
#         update_fields.append("verified_at")

#     otp.save(update_fields=update_fields)

#     mark_profile_email_verified(email)


# # ============================================================
# # STRICT VALIDATION (UTILISÉE PAR LES VUES)
# # ============================================================

# def validate_latest_email_otp_or_raise(*, email: str, otp_code: str) -> None:
#     """
#     Validation STRICTE utilisée côté backend (views) :
#     - ne dépend PAS de request
#     - lève ValidationError si invalide
#     - consomme l'OTP si OK
#     """
#     email = _normalize_email(email)
#     code = (otp_code or "").strip()

#     if not code or not code.isdigit() or len(code) != 6:
#         raise ValidationError(_("Code OTP invalide."))

#     otp = (
#         EmailOTP.objects.filter(
#             email=email,
#             is_verified=False,
#             is_expired=False,
#             expires_at__gt=now(),
#         )
#         .order_by("-created_at")
#         .first()
#     )

#     if not otp:
#         raise ValidationError(_("Aucun code OTP valide trouvé."))

#     if otp.code != code:
#         raise ValidationError(_("Code OTP incorrect."))

#     otp.is_verified = True
#     otp.is_expired = True

#     update_fields = ["is_verified", "is_expired"]
#     if hasattr(otp, "verified_at"):
#         otp.verified_at = now()
#         update_fields.append("verified_at")

#     otp.save(update_fields=update_fields)

#     mark_profile_email_verified(email)


# # ============================================================
# # PROFIL EMAIL VERIFIED
# # ============================================================

# def mark_profile_email_verified(email: str) -> None:
#     """
#     Marque l'email comme vérifié dans les profils si possible (sans casser).
#     """
#     email = (email or "").strip().lower()
#     if not email:
#         return

#     # ---- SocialProfile ----
#     if SocialProfile is not None:
#         try:
#             p = SocialProfile.objects.filter(email__iexact=email).first()
#             if p:
#                 if hasattr(p, "mark_email_verified"):
#                     p.mark_email_verified()
#                 elif hasattr(p, "email_verified"):
#                     p.email_verified = True
#                     p.save(update_fields=["email_verified"])
#                 elif hasattr(p, "is_email_verified"):
#                     p.is_email_verified = True
#                     p.save(update_fields=["is_email_verified"])
#         except Exception:
#             pass

#     # ---- UserEconomicProfile ----
#     if UserEconomicProfile is not None:
#         try:
#             qs = UserEconomicProfile.objects.all()
#             if hasattr(UserEconomicProfile, "user"):
#                 qs = qs.filter(user__email__iexact=email)

#             p = qs.first()
#             if p:
#                 if hasattr(p, "mark_email_verified"):
#                     p.mark_email_verified()
#                 elif hasattr(p, "email_verified"):
#                     p.email_verified = True
#                     p.save(update_fields=["email_verified"])
#                 elif hasattr(p, "is_email_verified"):
#                     p.is_email_verified = True
#                     p.save(update_fields=["is_email_verified"])
#         except Exception:
#             pass


# # ============================================================
# # AJAX-FRIENDLY WRAPPER
# # ============================================================

# @dataclass
# class SendOtpResult:
#     ok: bool
#     message: str
#     cooldown: int = EMAIL_OTP_RESEND_COOLDOWN_SECONDS
#     expires_in: int = OTP_EXPIRY_MINUTES * 60


# def send_email_otp(request, email: str) -> SendOtpResult:
#     """
#     Wrapper AJAX :
#     - cooldown IP + email
#     - limite fenêtre DB
#     """
#     try:
#         email = _normalize_email(email)
#     except ValidationError as e:
#         return SendOtpResult(False, " ".join(e.messages))

#     ip = _client_ip(request)
#     cooldown_key = f"emailotp:cooldown:{ip}:{email}"
#     if cache.get(cooldown_key):
#         return SendOtpResult(
#             False, str(_("Veuillez patienter avant de renvoyer un code."))
#         )

#     try:
#         create_email_otp(email)
#     except ValidationError as e:
#         return SendOtpResult(False, " ".join(e.messages))
#     except Exception:
#         return SendOtpResult(
#             False, str(_("Erreur lors de l’envoi du code. Réessayez."))
#         )

#     cache.set(cooldown_key, True, EMAIL_OTP_RESEND_COOLDOWN_SECONDS)
#     return SendOtpResult(
#         True, str(_("Code envoyé. Vérifiez votre email puis saisissez les 6 chiffres."))
#     )






# # accounts_users/services/email_otp_service.py
# from __future__ import annotations

# import random
# from dataclasses import dataclass
# from datetime import timedelta

# from django.conf import settings
# from django.core.cache import cache
# from django.core.exceptions import ValidationError
# from django.core.mail import EmailMessage, send_mail
# from django.core.validators import validate_email
# from django.db import transaction
# from django.utils.timezone import now
# from django.utils.translation import gettext_lazy as _

# from accounts_users.models.email_otp import EmailOTP

# # Imports "safe" (ne casse pas si un module change)
# try:
#     from accounts_users.models.social.social_profile import SocialProfile
# except Exception:  # pragma: no cover
#     SocialProfile = None  # type: ignore

# try:
#     from accounts_users.models.users_economic_profile import UserEconomicProfile
# except Exception:  # pragma: no cover
#     UserEconomicProfile = None  # type: ignore


# # ============================================================
# # CONFIG (surchargable via settings)
# # ============================================================
# MAX_OTP_PER_WINDOW = int(getattr(settings, "MAX_OTP_PER_WINDOW", 3))
# WINDOW_MINUTES = int(getattr(settings, "OTP_WINDOW_MINUTES", 15))
# OTP_EXPIRY_MINUTES = int(getattr(settings, "OTP_EXPIRY_MINUTES", 5))

# # Anti-spam UX (cooldown entre 2 envois)
# EMAIL_OTP_RESEND_COOLDOWN_SECONDS = int(getattr(settings, "EMAIL_OTP_RESEND_COOLDOWN_SECONDS", 60))

# # Limite d'essais de saisie du code
# EMAIL_OTP_MAX_VERIFY_ATTEMPTS = int(getattr(settings, "EMAIL_OTP_MAX_VERIFY_ATTEMPTS", 5))


# def _client_ip(request) -> str:
#     if not request:
#         return "0.0.0.0"
#     xff = request.META.get("HTTP_X_FORWARDED_FOR")
#     if xff:
#         return xff.split(",")[0].strip()
#     return request.META.get("REMOTE_ADDR") or "0.0.0.0"


# def _normalize_email(value: str) -> str:
#     email = (value or "").strip().lower()
#     if not email:
#         raise ValidationError(_("Email manquant."))
#     validate_email(email)
#     return email


# def generate_otp_code() -> str:
#     """Génère un code OTP à 6 chiffres."""
#     return f"{random.randint(100000, 999999)}"


# def can_send_otp(email: str) -> bool:
#     """
#     Limitation par fenêtre : MAX_OTP_PER_WINDOW OTP / WINDOW_MINUTES pour un email.
#     """
#     since = now() - timedelta(minutes=WINDOW_MINUTES)
#     count = EmailOTP.objects.filter(email=email, created_at__gte=since).count()
#     return count < MAX_OTP_PER_WINDOW


# def _send_otp_email(email: str, code: str) -> None:
#     subject = getattr(settings, "EMAIL_OTP_SUBJECT", str(_("Votre code de vérification SOGENTIS")))
#     from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None)
#     message = str(_("Votre code OTP est : %(code)s") % {"code": code})

#     try:
#         send_mail(
#             subject=subject,
#             message=message,
#             from_email=from_email,
#             recipient_list=[email],
#             fail_silently=False,
#         )
#     except Exception:
#         msg = EmailMessage(
#             subject=subject,
#             body=message,
#             from_email=from_email,
#             to=[email],
#         )
#         msg.send(fail_silently=False)


# def create_email_otp(email: str) -> EmailOTP:
#     """
#     Crée un OTP (6 chiffres), expire les anciens, et envoie l'email.
#     """
#     email = _normalize_email(email)

#     if not can_send_otp(email):
#         raise ValidationError(_("Trop de tentatives. Réessayez plus tard."))

#     with transaction.atomic():
#         # Expire OTP précédents non utilisés
#         EmailOTP.objects.filter(email=email, is_verified=False, is_expired=False).update(is_expired=True)

#         otp = EmailOTP.objects.create(
#             email=email,
#             code=generate_otp_code(),
#             expires_at=now() + timedelta(minutes=OTP_EXPIRY_MINUTES),
#         )

#     _send_otp_email(email, otp.code)
#     return otp


# def mark_profile_email_verified(email: str) -> None:
#     """
#     Marque l'email comme vérifié dans les profils si possible (sans casser).
#     """
#     email = (email or "").strip().lower()
#     if not email:
#         return

#     # ---- SocialProfile ----
#     if SocialProfile is not None:
#         try:
#             p = SocialProfile.objects.filter(email__iexact=email).first()
#             if p:
#                 if hasattr(p, "mark_email_verified"):
#                     p.mark_email_verified()
#                 else:
#                     if hasattr(p, "email_verified"):
#                         p.email_verified = True
#                         p.save(update_fields=["email_verified"])
#                     elif hasattr(p, "is_email_verified"):
#                         p.is_email_verified = True
#                         p.save(update_fields=["is_email_verified"])
#         except Exception:
#             pass

#     # ---- UserEconomicProfile ----
#     if UserEconomicProfile is not None:
#         try:
#             qs = UserEconomicProfile.objects.all()
#             if hasattr(UserEconomicProfile, "user"):
#                 qs = qs.filter(user__email__iexact=email)

#             p = qs.first()
#             if p:
#                 if hasattr(p, "mark_email_verified"):
#                     p.mark_email_verified()
#                 else:
#                     if hasattr(p, "email_verified"):
#                         p.email_verified = True
#                         p.save(update_fields=["email_verified"])
#                     elif hasattr(p, "is_email_verified"):
#                         p.is_email_verified = True
#                         p.save(update_fields=["is_email_verified"])
#         except Exception:
#             pass


# # ============================================================
# # AJAX-friendly wrapper (compatible avec ta view actuelle)
# # ============================================================
# @dataclass
# class SendOtpResult:
#     ok: bool
#     message: str
#     cooldown: int = EMAIL_OTP_RESEND_COOLDOWN_SECONDS
#     expires_in: int = OTP_EXPIRY_MINUTES * 60


# def send_email_otp(request, email: str) -> SendOtpResult:
#     """
#     Wrapper pour l'AJAX :
#     - cooldown via cache (évite spam immédiat)
#     - limite fenêtre DB via can_send_otp()
#     """
#     try:
#         email = _normalize_email(email)
#     except ValidationError as e:
#         return SendOtpResult(False, " ".join(e.messages))

#     ip = _client_ip(request)
#     cooldown_key = f"emailotp:cooldown:{ip}:{email}"
#     if cache.get(cooldown_key):
#         return SendOtpResult(False, str(_("Veuillez patienter avant de renvoyer un code.")))

#     try:
#         create_email_otp(email)
#     except ValidationError as e:
#         return SendOtpResult(False, " ".join(e.messages))
#     except Exception:
#         return SendOtpResult(False, str(_("Erreur lors de l’envoi du code. Réessayez.")))

#     cache.set(cooldown_key, True, EMAIL_OTP_RESEND_COOLDOWN_SECONDS)
#     return SendOtpResult(True, str(_("Code envoyé. Vérifiez votre email puis saisissez les 6 chiffres.")))


# def verify_email_otp(request, email: str, code: str) -> None:
#     """
#     Vérifie le code OTP en DB :
#     - prend le dernier OTP actif
#     - contrôle expiration
#     - limite tentatives via cache
#     - marque is_verified=True + is_expired=True
#     """
#     email = _normalize_email(email)
#     code = (code or "").strip()

#     if not code or not code.isdigit() or len(code) != 6:
#         raise ValidationError(_("Veuillez saisir un code à 6 chiffres."))

#     otp = (
#         EmailOTP.objects.filter(
#             email=email,
#             is_verified=False,
#             is_expired=False,
#             expires_at__gt=now(),
#         )
#         .order_by("-created_at")
#         .first()
#     )

#     if not otp:
#         raise ValidationError(_("Aucun code actif. Cliquez sur “Envoyer le code”."))

#     ip = _client_ip(request)
#     attempts_key = f"emailotp:attempts:{ip}:{email}:{otp.id}"
#     attempts = int(cache.get(attempts_key) or 0)

#     if attempts >= EMAIL_OTP_MAX_VERIFY_ATTEMPTS:
#         # On expire le code pour forcer renvoi
#         otp.is_expired = True
#         otp.save(update_fields=["is_expired"])
#         raise ValidationError(_("Trop de tentatives. Renvoyez un nouveau code."))

#     if otp.code != code:
#         cache.set(attempts_key, attempts + 1, OTP_EXPIRY_MINUTES * 60)
#         raise ValidationError(_("Code invalide."))

#     # OK -> consommer OTP
#     otp.is_verified = True
#     otp.is_expired = True

#     update_fields = ["is_verified", "is_expired"]
#     if hasattr(otp, "verified_at"):
#         otp.verified_at = now()
#         update_fields.append("verified_at")

#     otp.save(update_fields=update_fields)

#     # Optionnel: marquer profil
#     mark_profile_email_verified(email)






# # accounts_users/services/email_otp_service.py
# from __future__ import annotations

# import random
# from datetime import timedelta

# from django.conf import settings
# from django.core.exceptions import ValidationError
# from django.core.mail import EmailMessage, send_mail
# from django.core.validators import validate_email
# from django.db import transaction
# from django.utils.timezone import now
# from django.utils.translation import gettext_lazy as _

# from accounts_users.models.email_otp import EmailOTP

# # Imports "safe" (ne casse pas si un module change)
# try:
#     from accounts_users.models.social.social_profile import SocialProfile
# except Exception:  # pragma: no cover
#     SocialProfile = None  # type: ignore

# try:
#     from accounts_users.models.users_economic_profile import UserEconomicProfile
# except Exception:  # pragma: no cover
#     UserEconomicProfile = None  # type: ignore


# # ============================================================
# # CONFIG (surchargable via settings)
# # ============================================================
# MAX_OTP_PER_WINDOW = int(getattr(settings, "MAX_OTP_PER_WINDOW", 3))
# WINDOW_MINUTES = int(getattr(settings, "OTP_WINDOW_MINUTES", 15))
# OTP_EXPIRY_MINUTES = int(getattr(settings, "OTP_EXPIRY_MINUTES", 5))


# def _normalize_email(value: str) -> str:
#     email = (value or "").strip().lower()
#     if not email:
#         raise ValidationError(_("Email manquant."))
#     validate_email(email)
#     return email


# def generate_otp_code() -> str:
#     """Génère un code OTP à 6 chiffres."""
#     return f"{random.randint(100000, 999999)}"


# def can_send_otp(email: str) -> bool:
#     """
#     Limitation par fenêtre : MAX_OTP_PER_WINDOW OTP / WINDOW_MINUTES pour un email.
#     """
#     since = now() - timedelta(minutes=WINDOW_MINUTES)
#     count = EmailOTP.objects.filter(email=email, created_at__gte=since).count()
#     return count < MAX_OTP_PER_WINDOW


# def _send_otp_email(email: str, code: str) -> None:
#     subject = getattr(settings, "EMAIL_OTP_SUBJECT", str(_("Votre code de vérification SOGENTIS")))
#     from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None)

#     # Message simple (tu peux mettre un template HTML plus tard)
#     message = str(_("Votre code OTP est : %(code)s") % {"code": code})

#     try:
#         send_mail(
#             subject=subject,
#             message=message,
#             from_email=from_email,
#             recipient_list=[email],
#             fail_silently=False,
#         )
#     except Exception:
#         msg = EmailMessage(
#             subject=subject,
#             body=message,
#             from_email=from_email,
#             to=[email],
#         )
#         msg.send(fail_silently=False)


# def create_email_otp(email: str) -> EmailOTP:
#     """
#     Crée un OTP (6 chiffres), expire les anciens, et envoie l'email.
#     """
#     email = _normalize_email(email)

#     if not can_send_otp(email):
#         raise ValidationError(_("Trop de tentatives. Réessayez plus tard."))

#     with transaction.atomic():
#         # Expire OTP précédents non utilisés
#         EmailOTP.objects.filter(email=email, is_verified=False, is_expired=False).update(is_expired=True)

#         otp = EmailOTP.objects.create(
#             email=email,
#             code=generate_otp_code(),
#             expires_at=now() + timedelta(minutes=OTP_EXPIRY_MINUTES),
#         )

#     _send_otp_email(email, otp.code)
#     return otp


# def mark_profile_email_verified(email: str) -> None:
#     """
#     Marque l'email comme vérifié dans les profils si possible (sans casser).
#     - SocialProfile : si modèle a mark_email_verified() ou champ bool
#     - UserEconomicProfile : idem (via user.email)
#     """
#     email = (email or "").strip().lower()
#     if not email:
#         return

#     # ---- SocialProfile ----
#     if SocialProfile is not None:
#         try:
#             # Ton ancien code utilisait SocialProfile.objects.get(email=email)
#             p = SocialProfile.objects.filter(email__iexact=email).first()
#             if p:
#                 if hasattr(p, "mark_email_verified"):
#                     p.mark_email_verified()
#                 else:
#                     if hasattr(p, "email_verified"):
#                         p.email_verified = True
#                         p.save(update_fields=["email_verified"])
#                     elif hasattr(p, "is_email_verified"):
#                         p.is_email_verified = True
#                         p.save(update_fields=["is_email_verified"])
#         except Exception:
#             pass

#     # ---- UserEconomicProfile ----
#     if UserEconomicProfile is not None:
#         try:
#             qs = UserEconomicProfile.objects.all()
#             # profil économique est souvent lié à user
#             if hasattr(UserEconomicProfile, "user"):
#                 qs = qs.filter(user__email__iexact=email)

#             p = qs.first()
#             if p:
#                 if hasattr(p, "mark_email_verified"):
#                     p.mark_email_verified()
#                 else:
#                     if hasattr(p, "email_verified"):
#                         p.email_verified = True
#                         p.save(update_fields=["email_verified"])
#                     elif hasattr(p, "is_email_verified"):
#                         p.is_email_verified = True
#                         p.save(update_fields=["is_email_verified"])
#         except Exception:
#             pass







# # services/email_otp_service.py
# import random
# from datetime import timedelta
# from django.utils.timezone import now
# from django.core.exceptions import ValidationError
# from django.core.mail import send_mail
# from django.conf import settings

# from accounts_users.models.email_otp import EmailOTP
# from accounts_users.models.social.social_profile import SocialProfile

# MAX_OTP_PER_WINDOW = 3
# WINDOW_MINUTES = 15
# OTP_EXPIRY_MINUTES = 5


# def generate_otp_code():
#     """Génère un code OTP à 6 chiffres."""
#     return f"{random.randint(100000, 999999)}"


# def can_send_otp(email):
#     since = now() - timedelta(minutes=WINDOW_MINUTES)
#     count = EmailOTP.objects.filter(email=email, created_at__gte=since).count()
#     return count < MAX_OTP_PER_WINDOW


# def create_email_otp(email):
#     if not can_send_otp(email):
#         raise ValidationError("Trop de tentatives. Réessayez plus tard.")

#     # Invalider OTP précédents non vérifiés
#     EmailOTP.objects.filter(email=email, is_verified=False, is_expired=False).update(is_expired=True)

#     otp = EmailOTP.objects.create(
#         email=email,
#         code=generate_otp_code(),
#         expires_at=now() + timedelta(minutes=OTP_EXPIRY_MINUTES)
#     )

#     # Envoyer email
#     send_mail(
#         subject="Votre code de vérification SOGENTIS",
#         message=f"Votre code OTP : {otp.code}",
#         from_email=settings.DEFAULT_FROM_EMAIL,
#         recipient_list=[email],
#         fail_silently=False,
#     )

#     return otp


# def mark_profile_email_verified(email):
#     """Marque l'email comme vérifié dans le profil social."""
#     try:
#         profile = SocialProfile.objects.get(email=email)
#     except SocialProfile.DoesNotExist:
#         return
#     profile.mark_email_verified()
