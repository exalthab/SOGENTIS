# accounts_users/management/commands/activate_admin_profiles.py
from __future__ import annotations

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from accounts_users.services.admin_profile_activation_service import (
    activate_admin_user,
    activate_all_admins,
)


class Command(BaseCommand):
    help = "Active le profil admin/superuser (status approuvé + flags) pour tester et paramétrer l’application."

    def add_arguments(self, parser):
        parser.add_argument("--all", action="store_true", help="Activer tous les superusers (+ staff si --also-staff).")
        parser.add_argument("--also-staff", action="store_true", help="Inclure les comptes staff (is_staff=True).")
        parser.add_argument("--username", type=str, help="Activer un compte spécifique par username.")
        parser.add_argument("--email", type=str, help="Activer un compte spécifique par email.")

    def handle(self, *args, **options):
        username = options.get("username")
        email = options.get("email")

        if options.get("all"):
            data = activate_all_admins(also_staff=bool(options.get("also_staff")))
            self.stdout.write(self.style.SUCCESS(f"OK: {data['count']} compte(s) activé(s)."))
            return

        if not username and not email:
            self.stdout.write(self.style.ERROR("Utilise --all OU --username=... OU --email=..."))
            return

        User = get_user_model()
        qs = User.objects.all()
        if username:
            qs = qs.filter(username=username)
        if email:
            qs = qs.filter(email=email)

        u = qs.first()
        if not u:
            self.stdout.write(self.style.ERROR("Utilisateur introuvable."))
            return

        data = activate_admin_user(u, ensure_is_active=True)
        self.stdout.write(self.style.SUCCESS(f"OK: activé -> {data.get('username') or data.get('email')}"))
