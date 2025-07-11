from django.core.management.base import BaseCommand
from accounts_users.models.membership_role import MembershipRole

class Command(BaseCommand):
    help = 'Crée les rôles utilisateurs publics'

    def handle(self, *args, **kwargs):
        roles = [
            ("MEMBER", "Adhérent de l'association"),
            ("VOLUNTEER", "Volontaire actif"),
            ("SPONSOR", "Donateur ou mécène"),
            ("INSTITUTION", "Partenaire institutionnel"),
        ]
        for code, desc in roles:
            MembershipRole.objects.get_or_create(name=code, defaults={'description': desc})
        self.stdout.write(self.style.SUCCESS("Rôles utilisateurs créés."))
