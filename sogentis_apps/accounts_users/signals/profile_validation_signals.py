# accounts_users/signals/profile_validation_signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts_users.models.users_profile import UserProfile
from accounts_users.models.profile_validation import ProfileValidation


@receiver(post_save, sender=UserProfile)
def create_profile_validation(sender, instance: UserProfile, created, **kwargs):
    if created:
        ProfileValidation.objects.get_or_create(profile=instance)
