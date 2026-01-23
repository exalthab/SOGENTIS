# accounts_users/services/phone_otp_service.py
import random
from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from accounts_users.models.phone_otp import PhoneOTP


MAX_OTP_PER_WINDOW = 3
WINDOW_MINUTES = 15
OTP_EXPIRY_MINUTES = 5


def is_phone_otp_enabled() -> bool:
    return bool(getattr(settings, "PHONE_OTP_ENABLED", False))


def generate_otp_code() -> str:
    return f"{random.randint(100000, 999999)}"


def can_send_otp(phone) -> bool:
    since = now() - timedelta(minutes=WINDOW_MINUTES)
    count = PhoneOTP.objects.filter(phone=phone, created_at__gte=since).count()
    return count < MAX_OTP_PER_WINDOW


@transaction.atomic
def create_phone_otp(phone) -> PhoneOTP:
    if not is_phone_otp_enabled():
        raise ValidationError(_("La vérification téléphone est désactivée."))

    if not can_send_otp(phone):
        raise ValidationError(_("Trop de tentatives. Réessayez plus tard."))

    PhoneOTP.objects.filter(phone=phone, is_verified=False, is_expired=False).update(is_expired=True)

    otp = PhoneOTP.objects.create(
        phone=phone,
        code=generate_otp_code(),
        expires_at=now() + timedelta(minutes=OTP_EXPIRY_MINUTES),
    )
    return otp


def is_phone_verified(phone) -> bool:
    return PhoneOTP.objects.filter(phone=phone, is_verified=True).exists()


def verify_latest_otp(phone, code: str) -> None:
    """
    Vérifie le dernier OTP actif pour ce téléphone.
    Lève ValidationError si invalide/expiré.
    """
    if not is_phone_otp_enabled():
        raise ValidationError(_("La vérification téléphone est désactivée."))

    try:
        otp = PhoneOTP.objects.filter(phone=phone, is_verified=False, is_expired=False).latest("created_at")
    except PhoneOTP.DoesNotExist:
        raise ValidationError(_("Code invalide."))

    if otp.is_expired_now():
        otp.is_expired = True
        otp.save(update_fields=["is_expired"])
        raise ValidationError(_("Code expiré."))

    if str(otp.code) != str(code).strip():
        otp.register_attempt()
        if otp.attempts >= 3:
            raise ValidationError(_("Trop de tentatives. Veuillez redemander un nouveau code."))
        raise ValidationError(_("Code incorrect."))

    otp.verify()




# import random
# from datetime import timedelta
# from django.utils.timezone import now
# from django.core.exceptions import ValidationError

# from accounts_users.models.phone_otp import PhoneOTP
# from accounts_users.models.social.social_profile import SocialProfile

# MAX_OTP_PER_WINDOW = 3
# WINDOW_MINUTES = 15
# OTP_EXPIRY_MINUTES = 5

# def generate_otp_code():
#     """Génère un code OTP à 6 chiffres."""
#     return f"{random.randint(100000, 999999)}"

# def can_send_otp(phone):
#     since = now() - timedelta(minutes=WINDOW_MINUTES)
#     count = PhoneOTP.objects.filter(phone=phone, created_at__gte=since).count()
#     return count < MAX_OTP_PER_WINDOW

# def create_phone_otp(phone):
#     if not can_send_otp(phone):
#         raise ValidationError("Trop de tentatives. Réessayez plus tard.")

#     PhoneOTP.objects.filter(phone=phone, is_verified=False, is_expired=False).update(is_expired=True)

#     otp = PhoneOTP.objects.create(
#         phone=phone,
#         code=generate_otp_code(),
#         expires_at=now() + timedelta(minutes=OTP_EXPIRY_MINUTES)
#     )

#     return otp

# def mark_profile_phone_verified(phone):
#     """Marque le téléphone comme vérifié dans le profil social."""
#     try:
#         profile = SocialProfile.objects.get(phone=phone)
#     except SocialProfile.DoesNotExist:
#         return
#     profile.mark_phone_verified()





# # accounts_users/services/phone_otp_service.py 30/12/2025
# import random
# from datetime import timedelta
# from django.utils.timezone import now
# from django.core.exceptions import ValidationError

# from accounts_users.models.phone_otp import PhoneOTP
# from accounts_users.models.social.social_profile import SocialProfile

# # =====================================================
# # ⚙️ CONSTANTES
# # =====================================================
# MAX_OTP_PER_WINDOW = 3      # Nombre max d'OTP par fenêtre
# WINDOW_MINUTES = 15         # Fenêtre de tentative en minutes
# OTP_EXPIRY_MINUTES = 5      # Durée de validité d'un OTP

# # =====================================================
# # 🔢 GÉNÉRATION OTP
# # =====================================================
# def generate_otp_code():
#     """Génère un code OTP à 6 chiffres."""
#     return f"{random.randint(100000, 999999)}"

# # =====================================================
# # 🕒 LIMITATION DE TENTATIVES
# # =====================================================
# def can_send_otp(phone):
#     """
#     Vérifie si on peut envoyer un OTP pour ce téléphone
#     dans la fenêtre de temps définie par WINDOW_MINUTES.
#     """
#     since = now() - timedelta(minutes=WINDOW_MINUTES)
#     count = PhoneOTP.objects.filter(
#         phone=phone,
#         created_at__gte=since
#     ).count()
#     return count < MAX_OTP_PER_WINDOW

# # =====================================================
# # ✨ CRÉATION OTP
# # =====================================================
# def create_phone_otp(phone):
#     """
#     Crée un OTP pour un téléphone donné.
#     Invalide les OTP précédents non vérifiés,
#     limite le nombre de tentatives dans une fenêtre donnée.
#     """
#     if not can_send_otp(phone):
#         raise ValidationError("Trop de tentatives. Réessayez plus tard.")

#     # Invalider tous les OTP actifs précédents
#     PhoneOTP.objects.filter(
#         phone=phone,
#         is_verified=False,
#         is_expired=False
#     ).update(is_expired=True)

#     # Créer le nouvel OTP
#     otp = PhoneOTP.objects.create(
#         phone=phone,
#         code=generate_otp_code(),
#         expires_at=now() + timedelta(minutes=OTP_EXPIRY_MINUTES)
#     )

#     return otp

# # =====================================================
# # ✅ MARQUER TÉLÉPHONE VÉRIFIÉ
# # =====================================================
# def mark_profile_phone_verified(phone):
#     """
#     Marque le téléphone comme vérifié dans le profil social correspondant.
#     """
#     try:
#         profile = SocialProfile.objects.get(phone=phone)
#     except SocialProfile.DoesNotExist:
#         return

#     profile.mark_phone_verified()






# # accounts_users/services/phone_otp_service.py
# import random
# from datetime import timedelta
# from django.utils.timezone import now
# from django.core.exceptions import ValidationError

# from accounts_users.models.phone_otp import PhoneOTP
# from accounts_users.models.social.social_profile import SocialProfile

# # =====================================================
# # ⚙️ CONSTANTES
# # =====================================================
# MAX_OTP_PER_WINDOW = 3      # Nombre max d'OTP par fenêtre
# WINDOW_MINUTES = 15         # Fenêtre de tentative en minutes
# OTP_EXPIRY_MINUTES = 5      # Durée de validité d'un OTP


# # =====================================================
# # 🔢 GÉNÉRATION OTP
# # =====================================================
# def generate_otp_code():
#     """Génère un code OTP à 6 chiffres."""
#     return f"{random.randint(100000, 999999)}"


# # =====================================================
# # 🕒 LIMITATION DE TENTATIVES
# # =====================================================
# def can_send_otp(phone):
#     """Vérifie si on peut envoyer un OTP pour ce téléphone dans la fenêtre donnée."""
#     since = now() - timedelta(minutes=WINDOW_MINUTES)
#     count = PhoneOTP.objects.filter(
#         phone=phone,
#         created_at__gte=since
#     ).count()
#     return count < MAX_OTP_PER_WINDOW


# # =====================================================
# # ✨ CRÉATION OTP
# # =====================================================
# def create_phone_otp(phone):
#     """
#     Crée un OTP pour un téléphone donné.
#     Invalide les OTP précédents non vérifiés,
#     limite le nombre de tentatives dans une fenêtre donnée.
#     """
#     if not can_send_otp(phone):
#         raise ValidationError("Trop de tentatives. Réessayez plus tard.")

#     # Invalider tous les OTP actifs précédents
#     PhoneOTP.objects.filter(
#         phone=phone,
#         is_verified=False,
#         is_expired=False
#     ).update(is_expired=True)

#     # Créer le nouvel OTP
#     otp = PhoneOTP.objects.create(
#         phone=phone,
#         code=generate_otp_code(),
#         expires_at=now() + timedelta(minutes=OTP_EXPIRY_MINUTES)
#     )

#     return otp

# def mark_profile_phone_verified(phone):
#     """
#     Marque le téléphone comme vérifié dans le profil social
#     """
#     try:
#         profile = SocialProfile.objects.get(phone=phone)
#     except SocialProfile.DoesNotExist:
#         return

#     profile.mark_phone_verified()
