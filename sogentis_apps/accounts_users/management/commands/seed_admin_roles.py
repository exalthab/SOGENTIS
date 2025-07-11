from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = 'Crée les rôles administrateurs (Group) pour le dashboard'

    def handle(self, *args, **kwargs):
        roles = ['SuperAdmin', 'MembresManager', 'DonsManager']
        for name in roles:
            Group.objects.get_or_create(name=name)
        self.stdout.write(self.style.SUCCESS("Rôles dashboard créés."))
