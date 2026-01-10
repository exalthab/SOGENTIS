# accounts_users/signals/membership_role_signals.py
from django.db.models.signals import post_migrate
from django.dispatch import receiver

from accounts_users.models.membership_role import MembershipRole


@receiver(post_migrate)
def seed_membership_roles(sender, **kwargs):
    """
    Seed idempotent des rôles d’adhésion.
    Déclenché après migrate. On limite à l’app accounts_users.
    """
    # post_migrate est appelé pour chaque app → on filtre
    if getattr(sender, "label", None) != "accounts_users":
        return

    roles = [
        ("MEMBER", "Membre"),
        ("VOLUNTEER", "Volontaire"),
        ("SPONSOR", "Donateur"),
        ("INSTITUTION", "Institution"),
    ]

    for code, label in roles:
        MembershipRole.objects.update_or_create(
            code=code,  # ton save() upper/strip + contrainte CI => OK
            defaults={
                "label": label,
                "is_active": True,
            },
        )
