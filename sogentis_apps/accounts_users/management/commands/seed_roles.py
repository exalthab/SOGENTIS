# accounts_users/management/commands/seed_roles.py
from django.core.management.base import BaseCommand
from accounts_users.models.membership_role import MembershipRole


class Command(BaseCommand):
    help = "Crée les rôles d’adhésion par défaut"

    def handle(self, *args, **kwargs):
        roles = [
            ("MEMBER", "Membre"),
            ("VOLUNTEER", "Volontaire"),
            ("SPONSOR", "Donateur"),
            ("INSTITUTION", "Institution"),
        ]

        created = 0
        for code, label in roles:
            obj, was_created = MembershipRole.objects.get_or_create(
                code=code,
                defaults={"label": label},
            )
            if was_created:
                self.stdout.write(self.style.SUCCESS(f"✅ Rôle créé : {code}"))
                created += 1
            else:
                self.stdout.write(f"ℹ️  Rôle déjà existant : {code}")

        self.stdout.write(self.style.SUCCESS(f"🔸 {created} rôle(s) ajouté(s)."))





# # accounts_users/management/commands/seed_roles.py
# from django.core.management.base import BaseCommand
# from accounts_users.models.staff_role import UserRole

# class Command(BaseCommand):
#     help = 'Crée les rôles utilisateur par défaut'

#     def handle(self, *args, **kwargs):
#         roles = ["SPONSOR", "VOLUNTEER", "MEMBER"]
#         created = 0
#         for role in roles:
#             if not UserRole.objects.filter(role=role).exists():
#                 UserRole.objects.create(role=role)
#                 self.stdout.write(self.style.SUCCESS(f"✅ Rôle ajouté : {role}"))
#                 created += 1
#             else:
#                 self.stdout.write(f"ℹ️  Rôle déjà existant : {role}")
#         self.stdout.write(self.style.SUCCESS(f"🔸 {created} rôle(s) ajoutés."))

