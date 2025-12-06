from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.translation import gettext as _
from accounts_users.models.users_profile import UserProfile

@receiver(pre_save, sender=UserProfile)
def cache_old_status(sender, instance, **kwargs):
    if instance.pk:
        try:
            old = UserProfile.objects.get(pk=instance.pk)
            instance._old_status = old.status
        except UserProfile.DoesNotExist:
            instance._old_status = None

@receiver(post_save, sender=UserProfile)
def notify_profile_status_change(sender, instance, created, **kwargs):
    if not created and hasattr(instance, '_old_status'):
        if instance._old_status != instance.status:
            user = instance.user
            context = {"user": user, "profile": instance}
            if instance.status == 'approved':
                subject = _("Validation de votre profil SOGENTIS")
                message_txt = render_to_string("accounts_users/emails/profile_approved.txt", context)
                message_html = render_to_string("accounts_users/emails/profile_approved.html", context)
            elif instance.status == 'refused':
                subject = _("Refus de votre profil SOGENTIS")
                message_txt = render_to_string("accounts_users/emails/profile_refused.txt", context)
                message_html = render_to_string("accounts_users/emails/profile_refused.html", context)
            else:
                return  # On ne gère que approved/refused ici

            send_mail(
                subject=subject,
                message=message_txt,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=message_html,
                fail_silently=False,
            )
