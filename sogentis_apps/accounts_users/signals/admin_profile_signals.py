# accounts_users/signals/admin_profile_signals.py
from __future__ import annotations

import logging
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts_users.services.admin_profile_activation_service import activate_admin_user

logger = logging.getLogger(__name__)


@receiver(post_save, sender=get_user_model(), dispatch_uid="accounts_users.admin_profile_auto_activate")
def auto_activate_admin_profiles(sender, instance, created, raw, **kwargs):
    """
    Si un user devient staff/superuser, on force l’activation/approbation des profils liés.
    """
    if raw:
        return

    try:
        if getattr(instance, "is_superuser", False) or getattr(instance, "is_staff", False):
            activate_admin_user(instance, ensure_is_active=True)
    except Exception as e:
        logger.warning("Auto-activation admin échouée pour %s: %s", getattr(instance, "pk", None), e)
