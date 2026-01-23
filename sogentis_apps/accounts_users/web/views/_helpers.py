# accounts_users/web/views/_helpers.py
from __future__ import annotations

from typing import Any, Dict, Optional

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from accounts_users.models.email_otp import EmailOTP


EMAIL_VERIFICATION_ENABLED = bool(getattr(settings, "EMAIL_VERIFICATION_ENABLED", True))
MAX_OTP_ATTEMPTS = int(getattr(settings, "MAX_OTP_ATTEMPTS", 3))


def build_auth_context(pole: str) -> Dict[str, str]:
    """
    Contexte standard UI pour templates auth/register.
    pole: social|economic|generic
    """
    pole = (pole or "generic").strip().lower()
    if pole not in ("social", "economic", "generic"):
        pole = "generic"
    return {"auth_pole": pole, "login_context": pole}


def validate_latest_email_otp_or_add_error(
    request,
    *,
    email: str,
    otp_code: str,
    form,
    field_name: str = "email_otp_code",
) -> bool:
    """
    Valide l'OTP email côté serveur (DB EmailOTP).
    - sécurise contre changement d'email (session otp_email)
    - gère expiration + attempts
    - marque OTP vérifié si OK
    - nettoie la session OTP si OK
    """
    if not EMAIL_VERIFICATION_ENABLED:
        return True

    email = (email or "").strip().lower()
    otp_code = (otp_code or "").strip()

    if not otp_code:
        form.add_error(field_name, _("Code OTP manquant."))
        return False

    sess_email = request.session.get("otp_email")
    if sess_email and sess_email != email:
        form.add_error(field_name, _("Tentative non autorisée."))
        return False

    try:
        otp = EmailOTP.objects.filter(
            email=email,
            is_verified=False,
            is_expired=False,
        ).latest("created_at")
    except EmailOTP.DoesNotExist:
        form.add_error(field_name, _("Le code OTP est invalide ou expiré."))
        return False

    # Expiration robuste
    try:
        if hasattr(otp, "is_expired_now") and callable(getattr(otp, "is_expired_now")):
            if otp.is_expired_now():
                otp.is_expired = True
                otp.save(update_fields=["is_expired"])
                form.add_error(field_name, _("Le code OTP est expiré."))
                return False
        elif hasattr(otp, "expires_at") and otp.expires_at and otp.expires_at <= now():
            otp.is_expired = True
            otp.save(update_fields=["is_expired"])
            form.add_error(field_name, _("Le code OTP est expiré."))
            return False
    except Exception:
        # si le check échoue, on continue (mais on reste safe sur la suite)
        pass

    # Mauvais code => attempts
    if getattr(otp, "code", None) != otp_code:
        try:
            if hasattr(otp, "register_attempt") and callable(getattr(otp, "register_attempt")):
                otp.register_attempt()
            else:
                otp.attempts = (getattr(otp, "attempts", 0) or 0) + 1
                otp.save(update_fields=["attempts"])
        except Exception:
            pass

        attempts = int(getattr(otp, "attempts", 0) or 0)
        if attempts >= MAX_OTP_ATTEMPTS:
            try:
                otp.is_expired = True
                otp.save(update_fields=["is_expired"])
            except Exception:
                pass
            form.add_error(field_name, _("Trop de tentatives. Veuillez redemander un nouveau code."))
            return False

        form.add_error(field_name, _("Code OTP incorrect."))
        return False

    # Succès => verify
    try:
        if hasattr(otp, "verify") and callable(getattr(otp, "verify")):
            otp.verify()
        else:
            otp.is_verified = True
            otp.is_expired = True
            otp.save(update_fields=["is_verified", "is_expired"])
    except (ValidationError, Exception):
        form.add_error(field_name, _("Le code OTP est invalide ou expiré."))
        return False

    # Nettoyage session OTP
    request.session.pop("otp_email", None)
    request.session.pop("otp_last_sent_at_email", None)
    request.session.modified = True
    return True
