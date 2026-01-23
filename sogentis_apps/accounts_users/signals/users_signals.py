# accounts_users/signals/users_signals.py
from __future__ import annotations

import logging

from django.apps import apps
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


def _get_economic_profile_model():
    """
    Tolérant: selon ton projet, le modèle peut s'appeler UserEconomicProfile
    (recommandé) ou UserProfile (ancien).
    """
    for name in ("UserEconomicProfile", "UserProfile"):
        try:
            return apps.get_model("accounts_users", name)
        except Exception:
            continue
    return None


EconomicProfile = _get_economic_profile_model()


def _send_html_mail(subject: str, to_email: str, html_template: str, context: dict) -> None:
    if not to_email:
        return
    fail_silently = bool(getattr(settings, "EMAIL_FAIL_SILENTLY", True))
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None) or getattr(settings, "SERVER_EMAIL", None)

    try:
        html = render_to_string(html_template, context)
        text = render_to_string(html_template.replace(".html", ".txt"), context)
    except Exception:
        html = ""
        text = ""

    if not text:
        text = subject

    try:
        msg = EmailMultiAlternatives(subject=subject, body=text, from_email=from_email, to=[to_email])
        if html:
            msg.attach_alternative(html, "text/html")
        msg.send(fail_silently=fail_silently)
    except Exception:
        logger.exception("Email send failed for %s", to_email)


if EconomicProfile:

    @receiver(pre_save, sender=EconomicProfile, dispatch_uid="accounts_users.economic_profile_cache_old_status")
    def cache_old_status(sender, instance, **kwargs):
        if not instance.pk:
            return
        try:
            old = sender.objects.only("status").get(pk=instance.pk)
            instance._old_status = getattr(old, "status", None)
        except Exception:
            instance._old_status = None

    @receiver(post_save, sender=EconomicProfile, dispatch_uid="accounts_users.economic_profile_notify_status_change")
    def notify_profile_status_change(sender, instance, created, **kwargs):
        if created:
            return

        if not hasattr(instance, "_old_status"):
            return

        old_status = getattr(instance, "_old_status", None)
        new_status = getattr(instance, "status", None)

        if old_status == new_status:
            return

        user = getattr(instance, "user", None)
        to_email = getattr(user, "email", "") if user else ""
        if not to_email:
            return

        status = (new_status or "").lower()

        approved_values = {"approved", "active"}
        refused_values = {"refused", "rejected", "suspended"}

        if status in approved_values:
            subject = _("Validation de votre profil SOGENTIS")
            tpl = "accounts_users/emails/profile_approved.html"
        elif status in refused_values:
            subject = _("Refus de votre profil SOGENTIS")
            tpl = "accounts_users/emails/profile_refused.html"
        else:
            return  # pending / autre -> pas d'email

        _send_html_mail(subject, to_email, tpl, {"user": user, "profile": instance})





# # accounts_users/signals/users_signals.py
# from django.db.models.signals import pre_save, post_save
# from django.dispatch import receiver
# from django.core.mail import send_mail
# from django.template.loader import render_to_string
# from django.conf import settings
# from django.utils.translation import gettext as _
# from accounts_users.models.users_economic_profile import UserProfile

# @receiver(pre_save, sender=UserProfile)
# def cache_old_status(sender, instance, **kwargs):
#     if instance.pk:
#         try:
#             old = UserProfile.objects.get(pk=instance.pk)
#             instance._old_status = old.status
#         except UserProfile.DoesNotExist:
#             instance._old_status = None

# @receiver(post_save, sender=UserProfile)
# def notify_profile_status_change(sender, instance, created, **kwargs):
#     if not created and hasattr(instance, '_old_status'):
#         if instance._old_status != instance.status:
#             user = instance.user
#             context = {"user": user, "profile": instance}
#             if instance.status == 'approved':
#                 subject = _("Validation de votre profil SOGENTIS")
#                 message_txt = render_to_string("accounts_users/emails/profile_approved.txt", context)
#                 message_html = render_to_string("accounts_users/emails/profile_approved.html", context)
#             elif instance.status == 'refused':
#                 subject = _("Refus de votre profil SOGENTIS")
#                 message_txt = render_to_string("accounts_users/emails/profile_refused.txt", context)
#                 message_html = render_to_string("accounts_users/emails/profile_refused.html", context)
#             else:
#                 return  # On ne gère que approved/refused ici

#             send_mail(
#                 subject=subject,
#                 message=message_txt,
#                 from_email=settings.DEFAULT_FROM_EMAIL,
#                 recipient_list=[user.email],
#                 html_message=message_html,
#                 fail_silently=False,
#             )
