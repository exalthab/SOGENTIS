# accounts_users/signals/profile_validation_signals.py
from __future__ import annotations

from django.apps import apps
from django.db.models.signals import post_save
from django.dispatch import receiver

try:
    from accounts_users.models.users_profile import UserProfile  # profil social principal
except Exception:
    UserProfile = None  # type: ignore


if UserProfile:

    @receiver(post_save, sender=UserProfile, dispatch_uid="accounts_users.create_profile_validation")
    def create_profile_validation(sender, instance, created, **kwargs):
        """
        Workflow social optionnel:
        crée ProfileValidation pour chaque UserProfile social créé.
        """
        if not created:
            return
        try:
            ProfileValidation = apps.get_model("accounts_users", "ProfileValidation")
            ProfileValidation.objects.get_or_create(profile=instance)
        except Exception:
            # ne bloque jamais la création du profil
            pass





# # accounts_users/signals/profile_validation_signals.py
# from django.db.models.signals import post_save
# from django.dispatch import receiver

# from accounts_users.models.users_profile import UserProfile
# from accounts_users.models.profile_validation import ProfileValidation


# @receiver(post_save, sender=UserProfile)
# def create_profile_validation(sender, instance: UserProfile, created, **kwargs):
#     if created:
#         ProfileValidation.objects.get_or_create(profile=instance)
