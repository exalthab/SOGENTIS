# accounts_users/signals/profile_status_signal.py
from __future__ import annotations

import logging
from typing import Any, Optional

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)

try:
    from accounts_users.models.social.social_profile import SocialProfile
except Exception:
    SocialProfile = None  # type: ignore


def _send_html_mail(subject: str, to_email: str, html_template: str, context: dict) -> None:
    if not to_email:
        return

    fail_silently = bool(getattr(settings, "EMAIL_FAIL_SILENTLY", True))
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None) or getattr(settings, "SERVER_EMAIL", None)

    try:
        html = render_to_string(html_template, context)
        # tente le .txt "miroir" si présent, sinon fallback
        try:
            text = render_to_string(html_template.replace(".html", ".txt"), context)
        except Exception:
            text = ""
    except Exception:
        html = ""
        text = ""

    if not text:
        text = str(subject)

    try:
        msg = EmailMultiAlternatives(subject=str(subject), body=text, from_email=from_email, to=[to_email])
        if html:
            msg.attach_alternative(html, "text/html")
        msg.send(fail_silently=fail_silently)
    except Exception:
        logger.exception("Email send failed for %s", to_email)


if SocialProfile:

    @receiver(pre_save, sender=SocialProfile, dispatch_uid="accounts_users.social_profile_cache_old_state")
    def cache_social_old_state(sender, instance: Any, **kwargs):
        """
        Cache l'ancien état avant save pour détecter les transitions
        sans dépendre d'un type dur (évite erreurs de typing/import).
        """
        if not getattr(instance, "pk", None):
            return

        try:
            old = sender.objects.only("is_validated", "is_active_member").get(pk=instance.pk)
            instance._old_is_validated = bool(getattr(old, "is_validated", False))
            instance._old_is_active_member = bool(getattr(old, "is_active_member", False))
        except Exception:
            instance._old_is_validated = None
            instance._old_is_active_member = None

    @receiver(post_save, sender=SocialProfile, dispatch_uid="accounts_users.social_profile_notify_status_email")
    def send_social_profile_status_email(sender, instance: Any, created: bool, **kwargs):
        """
        Envoie un email UNIQUEMENT si transition vers:
        - approuvé (is_validated=True et is_active_member=True)
        - refusé   (is_validated=False et is_active_member=False)
        """
        if created:
            return

        old_v: Optional[bool] = getattr(instance, "_old_is_validated", None)
        old_a: Optional[bool] = getattr(instance, "_old_is_active_member", None)
        new_v = bool(getattr(instance, "is_validated", False))
        new_a = bool(getattr(instance, "is_active_member", False))

        # pas de changement -> pas d'email
        if old_v is not None and old_a is not None and old_v == new_v and old_a == new_a:
            return

        user = getattr(instance, "user", None)
        to_email = getattr(user, "email", "") if user else ""
        if not to_email:
            return

        if new_v and new_a:
            subject = _("Votre adhésion sociale a été approuvée")
            tpl = "accounts_users/emails/profile_approved.html"
        elif (not new_v) and (not new_a):
            subject = _("Votre adhésion sociale a été refusée")
            tpl = "accounts_users/emails/profile_refused.html"
        else:
            return  # état intermédiaire (pending) -> pas d’email

        _send_html_mail(str(subject), str(to_email), tpl, {"user": user, "profile": instance})





# # accounts_users/signals/profile_status_signal.py
# from __future__ import annotations

# import logging

# from django.conf import settings
# from django.core.mail import EmailMultiAlternatives
# from django.db.models.signals import pre_save, post_save
# from django.dispatch import receiver
# from django.template.loader import render_to_string
# from django.utils.translation import gettext_lazy as _

# from typing import Any

# logger = logging.getLogger(__name__)

# try:
#     from accounts_users.models.social.social_profile import SocialProfile
# except Exception:
#     SocialProfile = None  # type: ignore


# def _send_html_mail(subject: str, to_email: str, html_template: str, context: dict) -> None:
#     if not to_email:
#         return

#     fail_silently = bool(getattr(settings, "EMAIL_FAIL_SILENTLY", True))
#     from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None) or getattr(settings, "SERVER_EMAIL", None)

#     try:
#         html = render_to_string(html_template, context)
#         text = render_to_string(html_template.replace(".html", ".txt"), context)
#     except Exception:
#         html = ""
#         text = ""

#     if not text:
#         text = subject

#     try:
#         msg = EmailMultiAlternatives(subject=subject, body=text, from_email=from_email, to=[to_email])
#         if html:
#             msg.attach_alternative(html, "text/html")
#         msg.send(fail_silently=fail_silently)
#     except Exception:
#         logger.exception("Email send failed for %s", to_email)


# if SocialProfile:

#     @receiver(pre_save, sender=SocialProfile, dispatch_uid="accounts_users.social_profile_cache_old_state")
#     def cache_social_old_state(sender, instance: Any, **kwargs):
#         if not instance.pk:
#             return
#         try:
#             old = sender.objects.only("is_validated", "is_active_member").get(pk=instance.pk)
#             instance._old_is_validated = bool(getattr(old, "is_validated", False))
#             instance._old_is_active_member = bool(getattr(old, "is_active_member", False))
#         except Exception:
#             instance._old_is_validated = None
#             instance._old_is_active_member = None

#     @receiver(post_save, sender=SocialProfile, dispatch_uid="accounts_users.social_profile_notify_status_email")
#     def send_social_profile_status_email(sender, instance: Any, created, **kwargs):
#         """
#         Envoie un email UNIQUEMENT si transition vers:
#         - approuvé (is_validated=True et is_active_member=True)
#         - refusé   (is_validated=False et is_active_member=False)
#         """
#         if created:
#             return

#         old_v = getattr(instance, "_old_is_validated", None)
#         old_a = getattr(instance, "_old_is_active_member", None)
#         new_v = bool(getattr(instance, "is_validated", False))
#         new_a = bool(getattr(instance, "is_active_member", False))

#         # pas de changement -> pas d'email
#         if old_v is not None and old_a is not None and old_v == new_v and old_a == new_a:
#             return

#         user = getattr(instance, "user", None)
#         to_email = getattr(user, "email", "") if user else ""
#         if not to_email:
#             return

#         if new_v and new_a:
#             subject = _("Votre adhésion sociale a été approuvée")
#             tpl = "accounts_users/emails/profile_approved.html"
#         elif (not new_v) and (not new_a):
#             subject = _("Votre adhésion sociale a été refusée")
#             tpl = "accounts_users/emails/profile_refused.html"
#         else:
#             return  # état intermédiaire (pending) -> pas d’email

#         _send_html_mail(subject, to_email, tpl, {"user": user, "profile": instance})






# # accounts_users/signals/profile_status_signal.py
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.core.mail import send_mail
# from django.template.loader import render_to_string
# from django.conf import settings
# from django.utils.translation import gettext_lazy as _

# from accounts_users.models.social.social_profile import SocialProfile


# @receiver(post_save, sender=SocialProfile)
# def send_social_profile_status_email(sender, instance: SocialProfile, created, **kwargs):
#     """
#     Envoie automatiquement un email lorsque le profil social est :
#     - approuvé
#     - refusé

#     Déclenché UNIQUEMENT lors d’une mise à jour (pas à la création).
#     """
#     if created:
#         return

#     user = instance.user

#     # ==============================
#     # PROFIL SOCIAL APPROUVÉ
#     # ==============================
#     if instance.is_validated and instance.is_active_member:
#         subject = _("Votre adhésion sociale a été approuvée")
#         html_message = render_to_string(
#             "accounts_users/emails/profile_approved.html",
#             {
#                 "user": user,
#                 "profile": instance,
#             }
#         )

#     # ==============================
#     # PROFIL SOCIAL REFUSÉ
#     # ==============================
#     elif not instance.is_validated and not instance.is_active_member:
#         subject = _("Votre adhésion sociale a été refusée")
#         html_message = render_to_string(
#             "accounts_users/emails/profile_refused.html",
#             {
#                 "user": user,
#                 "profile": instance,
#             }
#         )

#     else:
#         # Cas intermédiaire (ex: en attente) → pas d’email
#         return

#     send_mail(
#         subject=subject,
#         message="",  # requis par Django
#         from_email=settings.DEFAULT_FROM_EMAIL,
#         recipient_list=[user.email],
#         html_message=html_message,
#         fail_silently=True,
#     )










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
