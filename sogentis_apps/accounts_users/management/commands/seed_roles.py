from django.core.management.base import BaseCommand
from accounts_users.models.role import UserRole

class Command(BaseCommand):
    help = 'Crée les rôles utilisateur par défaut'

    def handle(self, *args, **kwargs):
        roles = ["SPONSOR", "VOLUNTEER", "MEMBER"]
        created = 0
        for role in roles:
            if not UserRole.objects.filter(role=role).exists():
                UserRole.objects.create(role=role)
                self.stdout.write(self.style.SUCCESS(f"✅ Rôle ajouté : {role}"))
                created += 1
            else:
                self.stdout.write(f"ℹ️  Rôle déjà existant : {role}")
        self.stdout.write(self.style.SUCCESS(f"🔸 {created} rôle(s) ajoutés."))
