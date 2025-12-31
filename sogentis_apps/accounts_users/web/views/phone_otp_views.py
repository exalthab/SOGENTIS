# accounts_users/web/views/phone_otp_views.py
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from django.db import transaction

from accounts_users.models.phone_otp import PhoneOTP
from accounts_users.services.phone_otp_service import create_phone_otp
from accounts_users.services.sms_service import send_sms
from accounts_users.services.phone_otp_service import mark_profile_phone_verified  # à créer si nécessaire


# =====================================================
# 📤 ENVOI OTP TÉLÉPHONE
# =====================================================
@require_POST
def send_phone_otp(request):
    phone = request.POST.get("phone")
    if not phone:
        return JsonResponse({"ok": False, "error": "Numéro manquant"})

    # 🔒 Anti-spam simple par session (60s)
    last_sent = request.session.get("otp_last_sent_at")
    if last_sent and (now().timestamp() - last_sent) < 60:
        return JsonResponse({
            "ok": False,
            "error": "Veuillez patienter avant de redemander un code."
        })

    try:
        with transaction.atomic():
            # Invalider les OTP non vérifiés précédents
            PhoneOTP.objects.filter(phone=phone, is_verified=False).update(is_expired=True)

            # Créer un nouvel OTP
            otp = create_phone_otp(phone)

            # Envoyer le SMS
            send_sms(phone, f"Votre code SOGENTIS : {otp.code}")

            # Sauvegarder info session
            request.session["otp_phone"] = phone
            request.session["otp_last_sent_at"] = now().timestamp()

    except ValidationError as e:
        return JsonResponse({"ok": False, "error": str(e)})

    return JsonResponse({"ok": True})


# =====================================================
# ✅ VÉRIFICATION OTP TÉLÉPHONE
# =====================================================
@require_POST
def verify_phone_otp(request):
    phone = request.POST.get("phone")
    code = request.POST.get("code")

    if not phone or not code:
        return JsonResponse({"ok": False, "error": "Données manquantes"})

    # 🔐 Vérifier que la session correspond
    if request.session.get("otp_phone") != phone:
        return JsonResponse({"ok": False, "error": "Tentative non autorisée"})

    try:
        otp = PhoneOTP.objects.filter(
            phone=phone,
            is_verified=False,
            is_expired=False
        ).latest("created_at")
    except PhoneOTP.DoesNotExist:
        return JsonResponse({"ok": False, "error": "Code invalide"})

    # ⛔ OTP expiré
    if otp.is_expired_now():
        otp.is_expired = True
        otp.save(update_fields=["is_expired"])
        return JsonResponse({"ok": False, "error": "Code expiré"})

    # ⛔ Mauvais code
    if otp.code != code:
        otp.register_attempt()
        if otp.attempts >= 3:
            return JsonResponse({
                "ok": False,
                "error": "Trop de tentatives. Veuillez redemander un nouveau code."
            })
        return JsonResponse({"ok": False, "error": "Code incorrect"})

    # ✅ OTP correct
    try:
        otp.verify()
    except ValidationError as e:
        return JsonResponse({"ok": False, "error": str(e)})

    # 🔗 Lier téléphone au profil utilisateur
    mark_profile_phone_verified(phone)

    # Nettoyage session
    request.session.pop("otp_phone", None)
    request.session.pop("otp_last_sent_at", None)

    return JsonResponse({"ok": True})
