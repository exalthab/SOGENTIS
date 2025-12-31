# accounts_users/signals/profile_status_signal.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from accounts_users.models.social.social_profile import SocialProfile


@receiver(post_save, sender=SocialProfile)
def send_social_profile_status_email(sender, instance: SocialProfile, created, **kwargs):
    """
    Envoie automatiquement un email lorsque le profil social est :
    - approuvé
    - refusé

    Déclenché UNIQUEMENT lors d’une mise à jour (pas à la création).
    """
    if created:
        return

    user = instance.user

    # ==============================
    # PROFIL SOCIAL APPROUVÉ
    # ==============================
    if instance.is_validated and instance.is_active_member:
        subject = _("Votre adhésion sociale a été approuvée")
        html_message = render_to_string(
            "accounts_users/emails/profile_approved.html",
            {
                "user": user,
                "profile": instance,
            }
        )

    # ==============================
    # PROFIL SOCIAL REFUSÉ
    # ==============================
    elif not instance.is_validated and not instance.is_active_member:
        subject = _("Votre adhésion sociale a été refusée")
        html_message = render_to_string(
            "accounts_users/emails/profile_refused.html",
            {
                "user": user,
                "profile": instance,
            }
        )

    else:
        # Cas intermédiaire (ex: en attente) → pas d’email
        return

    send_mail(
        subject=subject,
        message="",  # requis par Django
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=True,
    )










# # accounts_users/signals/profile_status_signal.py
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.core.mail import send_mail
# from django.template.loader import render_to_string
# from django.conf import settings

# from accounts_users.models.users_economic_profile import UserProfile


# @receiver(post_save, sender=UserProfile)
# def send_profile_status_email(sender, instance, created, **kwargs):
#     """
#     Envoie automatiquement un email quand :
#     - le profil est validé → profile_approved.html
#     - le profil est refusé → profile_refused.html
#     """
#     if created:
#         return  # Ne rien faire à la création

#     user = instance.user
#     status = instance.status

#     # PROFIL APPROUVÉ
#     if status == "approved":
#         subject = "Votre profil a été validé"
#         html_message = render_to_string(
#             "accounts_users/emails/profile_approved.html",
#             {"user": user}
#         )
#         send_mail(
#             subject,
#             "",
#             settings.DEFAULT_FROM_EMAIL,
#             [user.email],
#             html_message=html_message,
#         )

#     # PROFIL REFUSÉ
#     elif status == "refused":
#         subject = "Votre profil a été refusé"
#         html_message = render_to_string(
#             "accounts_users/emails/profile_refused.html",
#             {"user": user}
#         )
#         send_mail(
#             subject,
#             "",
#             settings.DEFAULT_FROM_EMAIL,
#             [user.email],
#             html_message=html_message,
#         )
