# accounts_users/web/views/email_otp_views.py
import json

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import transaction
from django.http import JsonResponse
from django.utils.timezone import now
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect

from accounts_users.models.email_otp import EmailOTP
from accounts_users.services.email_otp_service import (
    create_email_otp,
    mark_profile_email_verified,
)

EMAIL_VERIFICATION_ENABLED = getattr(settings, "EMAIL_VERIFICATION_ENABLED", True)
OTP_RESEND_INTERVAL = int(getattr(settings, "OTP_RESEND_INTERVAL", 60))  # secondes
MAX_OTP_ATTEMPTS = int(getattr(settings, "MAX_OTP_ATTEMPTS", 3))


def _json_response(ok: bool, *, message: str = "", error: str = "", status: int = 200, **extra):
    payload = {"ok": ok}
    if message:
        payload["message"] = message
    if error:
        payload["error"] = error
    payload.update(extra)
    return JsonResponse(payload, status=status)


def _read_payload(request):
    content_type = (request.headers.get("Content-Type") or "").lower()
    if "application/json" in content_type:
        try:
            body = request.body.decode("utf-8") if request.body else ""
            return json.loads(body) if body else {}
        except Exception:
            return {}
    return request.POST.dict()


def _normalize_email(value: str) -> str:
    email = (value or "").strip().lower()
    if not email:
        raise ValidationError("Email manquant.")
    validate_email(email)
    return email


@require_POST
@csrf_protect
def send_email_otp(request):
    if not EMAIL_VERIFICATION_ENABLED:
        return _json_response(True, message="Vérification email désactivée.", skipped=True)

    data = _read_payload(request)
    try:
        email = _normalize_email(data.get("email", ""))
    except ValidationError as e:
        return _json_response(False, error=str(e), status=400)

    # Rate-limit (session)
    last_sent = request.session.get("otp_last_sent_at_email")
    if last_sent:
        elapsed = now().timestamp() - float(last_sent)
        if elapsed < OTP_RESEND_INTERVAL:
            retry_after = int(OTP_RESEND_INTERVAL - elapsed)
            return _json_response(
                False,
                error="Veuillez patienter avant de redemander un code.",
                status=429,
                retry_after=retry_after,
            )

    try:
        with transaction.atomic():
            # Expire OTP précédents non utilisés
            EmailOTP.objects.filter(email=email, is_verified=False, is_expired=False).update(is_expired=True)

            # Crée et envoie un nouveau OTP
            create_email_otp(email)

            # Trace session (anti-renvoi + sécurité verify)
            request.session["otp_email"] = email
            request.session["otp_last_sent_at_email"] = now().timestamp()

            # Si l'utilisateur relance un OTP, on invalide l'état "verified"
            request.session.pop("email_otp_verified_for_signup", None)
            request.session.modified = True

    except ValidationError as e:
        return _json_response(False, error=str(e), status=400)
    except Exception:
        return _json_response(False, error="Une erreur est survenue lors de l’envoi du code.", status=500)

    return _json_response(True, message="Code envoyé. Vérifiez votre email.")


@require_POST
@csrf_protect
def verify_email_otp(request):
    if not EMAIL_VERIFICATION_ENABLED:
        return _json_response(True, message="Vérification email désactivée.", skipped=True)

    data = _read_payload(request)

    try:
        email = _normalize_email(data.get("email", ""))
    except ValidationError as e:
        return _json_response(False, error=str(e), status=400)

    code = (data.get("code") or "").strip()
    if not code or not code.isdigit() or len(code) != 6:
        return _json_response(False, error="Veuillez saisir un code à 6 chiffres.", status=400)

    sess_email = request.session.get("otp_email")
    if sess_email and sess_email != email:
        return _json_response(False, error="Tentative non autorisée.", status=403)

    try:
        otp = EmailOTP.objects.filter(
            email=email,
            is_verified=False,
            is_expired=False,
        ).latest("created_at")
    except EmailOTP.DoesNotExist:
        return _json_response(False, error="Code invalide ou expiré.", status=400)

    # Expiration (robuste)
    try:
        if hasattr(otp, "is_expired_now") and otp.is_expired_now():
            otp.is_expired = True
            otp.save(update_fields=["is_expired"])
            return _json_response(False, error="Code expiré.", status=400)
        if hasattr(otp, "expires_at") and otp.expires_at and otp.expires_at <= now():
            otp.is_expired = True
            otp.save(update_fields=["is_expired"])
            return _json_response(False, error="Code expiré.", status=400)
    except Exception:
        pass

    if otp.code != code:
        # attempts
        try:
            if hasattr(otp, "register_attempt"):
                otp.register_attempt()
            else:
                otp.attempts = (getattr(otp, "attempts", 0) or 0) + 1
                otp.save(update_fields=["attempts"])
        except Exception:
            pass

        attempts = getattr(otp, "attempts", 0) or 0
        if attempts >= MAX_OTP_ATTEMPTS:
            otp.is_expired = True
            otp.save(update_fields=["is_expired"])
            return _json_response(False, error="Trop de tentatives. Veuillez redemander un nouveau code.", status=400)

        return _json_response(False, error="Code incorrect.", status=400, attempts=attempts)

    # Succès
    try:
        if hasattr(otp, "verify"):
            otp.verify()
        else:
            otp.is_verified = True
            otp.save(update_fields=["is_verified"])
    except ValidationError as e:
        return _json_response(False, error=str(e), status=400)
    except Exception:
        return _json_response(False, error="Une erreur est survenue lors de la vérification.", status=500)

    try:
        mark_profile_email_verified(email)
    except Exception:
        pass

    # ✅ marquer session "OK pour signup"
    request.session["email_otp_verified_for_signup"] = email
    request.session["email_otp_verified_at"] = now().timestamp()

    # Nettoyage session OTP “en cours”
    request.session.pop("otp_email", None)
    request.session.pop("otp_last_sent_at_email", None)
    request.session.modified = True

    return _json_response(True, message="Email vérifié avec succès.")








# # accounts_users/web/views/email_otp_views.py
# import json

# from django.conf import settings
# from django.core.exceptions import ValidationError
# from django.core.validators import validate_email
# from django.db import transaction
# from django.http import JsonResponse
# from django.utils.timezone import now
# from django.views.decorators.http import require_POST

# from accounts_users.models.email_otp import EmailOTP
# from accounts_users.services.email_otp_service import (
#     create_email_otp,
#     mark_profile_email_verified,
# )

# # ============================================================
# # CONFIG (surchargable via settings si tu veux)
# # ============================================================
# EMAIL_VERIFICATION_ENABLED = getattr(settings, "EMAIL_VERIFICATION_ENABLED", True)
# OTP_RESEND_INTERVAL = int(getattr(settings, "OTP_RESEND_INTERVAL", 60))  # secondes
# MAX_OTP_ATTEMPTS = int(getattr(settings, "MAX_OTP_ATTEMPTS", 3))


# # ============================================================
# # HELPERS
# # ============================================================
# def _json_response(ok: bool, *, message: str = "", error: str = "", status: int = 200, **extra):
#     payload = {"ok": ok}
#     if message:
#         payload["message"] = message
#     if error:
#         payload["error"] = error
#     payload.update(extra)
#     return JsonResponse(payload, status=status)


# def _read_payload(request):
#     """
#     Supporte:
#     - fetch JSON: Content-Type: application/json
#     - form POST classique: request.POST
#     """
#     # 1) JSON
#     content_type = (request.headers.get("Content-Type") or "").lower()
#     if "application/json" in content_type:
#         try:
#             body = request.body.decode("utf-8") if request.body else ""
#             return json.loads(body) if body else {}
#         except Exception:
#             return {}

#     # 2) Form data
#     return request.POST.dict()


# def _normalize_email(value: str) -> str:
#     email = (value or "").strip().lower()
#     if not email:
#         raise ValidationError("Email manquant.")
#     validate_email(email)
#     return email


# # ============================================================
# # SEND OTP
# # ============================================================
# @require_POST
# def send_email_otp(request):
#     """
#     Envoie un code OTP à l'email de l'utilisateur.
#     Limite le renvoi à une fois toutes les OTP_RESEND_INTERVAL secondes (session).
#     Compatible JSON (fetch) + POST classique.
#     """
#     if not EMAIL_VERIFICATION_ENABLED:
#         return _json_response(True, message="Vérification email désactivée.", skipped=True)

#     data = _read_payload(request)
#     try:
#         email = _normalize_email(data.get("email", ""))
#     except ValidationError as e:
#         # e.message peut ne pas exister selon cas -> str(e)
#         return _json_response(False, error=str(e), status=400)

#     # Rate-limit (session)
#     last_sent = request.session.get("otp_last_sent_at_email")
#     if last_sent:
#         elapsed = now().timestamp() - float(last_sent)
#         if elapsed < OTP_RESEND_INTERVAL:
#             retry_after = int(OTP_RESEND_INTERVAL - elapsed)
#             return _json_response(
#                 False,
#                 error="Veuillez patienter avant de redemander un code.",
#                 status=429,
#                 retry_after=retry_after,
#             )

#     try:
#         with transaction.atomic():
#             # Expire les OTP précédents non utilisés (sécurité)
#             EmailOTP.objects.filter(email=email, is_verified=False, is_expired=False).update(is_expired=True)

#             # Crée et envoie un nouveau OTP (via ton service)
#             create_email_otp(email)

#             # Trace session (anti-renvoi)
#             request.session["otp_email"] = email
#             request.session["otp_last_sent_at_email"] = now().timestamp()
#             request.session.modified = True

#     except ValidationError as e:
#         return _json_response(False, error=str(e), status=400)
#     except Exception:
#         return _json_response(False, error="Une erreur est survenue lors de l’envoi du code.", status=500)

#     return _json_response(True, message="Code envoyé. Vérifiez votre email.")


# # ============================================================
# # VERIFY OTP (optionnel: si tu veux valider avant submit)
# # ============================================================
# @require_POST
# def verify_email_otp(request):
#     """
#     Vérifie le code OTP soumis par l'utilisateur.
#     Marque l'email comme vérifié en cas de succès.
#     Compatible JSON (fetch) + POST classique.
#     """
#     if not EMAIL_VERIFICATION_ENABLED:
#         return _json_response(True, message="Vérification email désactivée.", skipped=True)

#     data = _read_payload(request)

#     try:
#         email = _normalize_email(data.get("email", ""))
#     except ValidationError as e:
#         return _json_response(False, error=str(e), status=400)

#     code = (data.get("code") or "").strip()
#     if not code:
#         return _json_response(False, error="Code OTP manquant.", status=400)

#     # Sécurité : email doit correspondre à celui stocké en session (si présent)
#     sess_email = request.session.get("otp_email")
#     if sess_email and sess_email != email:
#         return _json_response(False, error="Tentative non autorisée.", status=403)

#     try:
#         otp = EmailOTP.objects.filter(
#             email=email,
#             is_verified=False,
#             is_expired=False,
#         ).latest("created_at")
#     except EmailOTP.DoesNotExist:
#         return _json_response(False, error="Code invalide ou expiré.", status=400)

#     # Expiration (si ton modèle a is_expired_now())
#     try:
#         if hasattr(otp, "is_expired_now") and otp.is_expired_now():
#             otp.is_expired = True
#             otp.save(update_fields=["is_expired"])
#             return _json_response(False, error="Code expiré.", status=400)
#     except Exception:
#         # Si jamais une erreur sur la méthode
#         pass

#     # Mauvais code -> attempts
#     if otp.code != code:
#         try:
#             if hasattr(otp, "register_attempt"):
#                 otp.register_attempt()
#             else:
#                 otp.attempts = (otp.attempts or 0) + 1
#                 otp.save(update_fields=["attempts"])
#         except Exception:
#             pass

#         # si trop de tentatives
#         attempts = getattr(otp, "attempts", 0) or 0
#         if attempts >= MAX_OTP_ATTEMPTS:
#             otp.is_expired = True
#             otp.save(update_fields=["is_expired"])
#             return _json_response(
#                 False,
#                 error="Trop de tentatives. Veuillez redemander un nouveau code.",
#                 status=400,
#             )

#         return _json_response(False, error="Code incorrect.", status=400, attempts=attempts)

#     # Succès
#     try:
#         if hasattr(otp, "verify"):
#             otp.verify()
#         else:
#             otp.is_verified = True
#             otp.save(update_fields=["is_verified"])
#     except ValidationError as e:
#         return _json_response(False, error=str(e), status=400)
#     except Exception:
#         return _json_response(False, error="Une erreur est survenue lors de la vérification.", status=500)

#     # (optionnel) Marquer profil email verified
#     try:
#         mark_profile_email_verified(email)
#     except Exception:
#         # on ne bloque pas la vérification OTP si le profil n’existe pas encore
#         pass

#     # Nettoyage session
#     request.session.pop("otp_email", None)
#     request.session.pop("otp_last_sent_at_email", None)
#     request.session.modified = True

#     return _json_response(True, message="Email vérifié avec succès.")





# # accounts_users/web/views/email_otp_views.py
# from django.http import JsonResponse
# from django.views.decorators.http import require_POST
# from django.utils.timezone import now
# from django.db import transaction
# from django.core.exceptions import ValidationError

# from accounts_users.models.email_otp import EmailOTP
# from accounts_users.services.email_otp_service import create_email_otp, mark_profile_email_verified

# EMAIL_VERIFICATION_ENABLED = True
# OTP_RESEND_INTERVAL = 60  # secondes
# MAX_OTP_ATTEMPTS = 3


# @require_POST
# def send_email_otp(request):
#     """
#     Envoie un code OTP à l'email de l'utilisateur.
#     Limite le renvoi à une fois toutes les 60s.
#     """
#     if not EMAIL_VERIFICATION_ENABLED:
#         return JsonResponse({"ok": True, "skipped": True})

#     email = request.POST.get("email")
#     if not email:
#         return JsonResponse({"ok": False, "error": "Email manquant"})

#     # Limitation d'envoi par session
#     last_sent = request.session.get("otp_last_sent_at_email")
#     if last_sent and (now().timestamp() - last_sent) < OTP_RESEND_INTERVAL:
#         return JsonResponse({"ok": False, "error": "Veuillez patienter avant de redemander un code."})

#     try:
#         with transaction.atomic():
#             # Expire les OTP précédents non utilisés
#             EmailOTP.objects.filter(email=email, is_verified=False).update(is_expired=True)
#             # Crée un nouveau OTP
#             otp = create_email_otp(email)
#             # Stocke info en session
#             request.session["otp_email"] = email
#             request.session["otp_last_sent_at_email"] = now().timestamp()
#     except ValidationError as e:
#         return JsonResponse({"ok": False, "error": str(e)})

#     return JsonResponse({"ok": True})


# @require_POST
# def verify_email_otp(request):
#     """
#     Vérifie le code OTP soumis par l'utilisateur.
#     Marque l'email comme vérifié en cas de succès.
#     """
#     if not EMAIL_VERIFICATION_ENABLED:
#         return JsonResponse({"ok": True, "skipped": True})

#     email = request.POST.get("email")
#     code = request.POST.get("code")
#     if not email or not code:
#         return JsonResponse({"ok": False, "error": "Données manquantes"})

#     # Sécurité : l'email doit correspondre à celui de la session
#     if request.session.get("otp_email") != email:
#         return JsonResponse({"ok": False, "error": "Tentative non autorisée"})

#     try:
#         otp = EmailOTP.objects.filter(
#             email=email, is_verified=False, is_expired=False
#         ).latest("created_at")
#     except EmailOTP.DoesNotExist:
#         return JsonResponse({"ok": False, "error": "Code invalide"})

#     # Vérification expiration
#     if otp.is_expired_now():
#         otp.is_expired = True
#         otp.save(update_fields=["is_expired"])
#         return JsonResponse({"ok": False, "error": "Code expiré"})

#     # Vérification du code
#     if otp.code != code:
#         otp.register_attempt()
#         if otp.attempts >= MAX_OTP_ATTEMPTS:
#             return JsonResponse({"ok": False, "error": "Trop de tentatives. Veuillez redemander un nouveau code."})
#         return JsonResponse({"ok": False, "error": "Code incorrect"})

#     # Succès
#     try:
#         otp.verify()
#     except ValidationError as e:
#         return JsonResponse({"ok": False, "error": str(e)})

#     mark_profile_email_verified(email)

#     # Nettoyage session
#     request.session.pop("otp_email", None)
#     request.session.pop("otp_last_sent_at_email", None)

#     return JsonResponse({"ok": True})






# from django.http import JsonResponse
# from django.views.decorators.http import require_POST
# from django.utils.timezone import now
# from django.db import transaction
# from django.core.exceptions import ValidationError

# from accounts_users.models.email_otp import EmailOTP
# from accounts_users.services.email_otp_service import create_email_otp, mark_profile_email_verified

# EMAIL_VERIFICATION_ENABLED = True


# @require_POST
# def send_email_otp(request):
#     if not EMAIL_VERIFICATION_ENABLED:
#         return JsonResponse({"ok": True, "skipped": True})

#     email = request.POST.get("email")
#     if not email:
#         return JsonResponse({"ok": False, "error": "Email manquant"})

#     last_sent = request.session.get("otp_last_sent_at_email")
#     if last_sent and (now().timestamp() - last_sent) < 60:
#         return JsonResponse({"ok": False, "error": "Veuillez patienter avant de redemander un code."})

#     try:
#         with transaction.atomic():
#             EmailOTP.objects.filter(email=email, is_verified=False).update(is_expired=True)
#             otp = create_email_otp(email)
#             request.session["otp_email"] = email
#             request.session["otp_last_sent_at_email"] = now().timestamp()
#     except ValidationError as e:
#         return JsonResponse({"ok": False, "error": str(e)})

#     return JsonResponse({"ok": True})


# @require_POST
# def verify_email_otp(request):
#     if not EMAIL_VERIFICATION_ENABLED:
#         return JsonResponse({"ok": True, "skipped": True})

#     email = request.POST.get("email")
#     code = request.POST.get("code")
#     if not email or not code:
#         return JsonResponse({"ok": False, "error": "Données manquantes"})

#     if request.session.get("otp_email") != email:
#         return JsonResponse({"ok": False, "error": "Tentative non autorisée"})

#     try:
#         otp = EmailOTP.objects.filter(email=email, is_verified=False, is_expired=False).latest("created_at")
#     except EmailOTP.DoesNotExist:
#         return JsonResponse({"ok": False, "error": "Code invalide"})

#     if otp.is_expired_now():
#         otp.is_expired = True
#         otp.save(update_fields=["is_expired"])
#         return JsonResponse({"ok": False, "error": "Code expiré"})

#     if otp.code != code:
#         otp.register_attempt()
#         if otp.attempts >= 3:
#             return JsonResponse({"ok": False, "error": "Trop de tentatives. Veuillez redemander un nouveau code."})
#         return JsonResponse({"ok": False, "error": "Code incorrect"})

#     try:
#         otp.verify()
#     except ValidationError as e:
#         return JsonResponse({"ok": False, "error": str(e)})

#     mark_profile_email_verified(email)
#     request.session.pop("otp_email", None)
#     request.session.pop("otp_last_sent_at_email", None)

#     return JsonResponse({"ok": True})
