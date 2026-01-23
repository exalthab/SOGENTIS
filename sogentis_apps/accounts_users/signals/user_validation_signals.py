# accounts_users/signals/user_validation_signals.py
from __future__ import annotations

from django.apps import apps
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=settings.AUTH_USER_MODEL, dispatch_uid="accounts_users.ensure_user_validation")
def ensure_user_validation(sender, instance, created, **kwargs):
    """
    Validation globale (1 user = 1 validation).
    """
    if not created:
        return
    try:
        UserValidation = apps.get_model("accounts_users", "UserValidation")
        UserValidation.objects.get_or_create(user=instance)
    except Exception:
        pass






# # accounts_users/signals/user_validation_signals.py
# from __future__ import annotations

# from django.conf import settings
# from django.db.models.signals import post_save
# from django.dispatch import receiver

# from django.apps import apps


# @receiver(post_save, sender=settings.AUTH_USER_MODEL)
# def ensure_user_validation(sender, instance, created, **kwargs):
#     if not created:
#         return

#     UserValidation = apps.get_model("accounts_users", "UserValidation")
#     try:
#         UserValidation.objects.get_or_create(user=instance)
#     except Exception:
#         # ne bloque jamais l'inscription
#         pass
