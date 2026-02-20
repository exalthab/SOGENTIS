# accounting/management/commands/seed_accounting.py
from __future__ import annotations

from django.core.management.base import BaseCommand

from accounting.models import Account, Journal
from accounting.services.posting import DEFAULT_ACCOUNTS, DEFAULT_JOURNALS


class Command(BaseCommand):
    help = "Seed system journals and accounts for Accounting."

    def handle(self, *args, **options):
        created_j = 0
        created_a = 0

        for code, name in DEFAULT_JOURNALS.values():
            obj, was = Journal.objects.get_or_create(
                code=code,
                defaults={
                    "name": name,
                    "default_currency": "XOF",
                    "is_active": True,
                    "is_system": True,
                },
            )
            created_j += 1 if was else 0

        for key, (code, name, typ) in DEFAULT_ACCOUNTS.items():
            obj, was = Account.objects.get_or_create(
                code=code,
                defaults={
                    "name": name,
                    "type": typ,
                    "is_active": True,
                    "is_system": True,
                },
            )
            created_a += 1 if was else 0

        self.stdout.write(self.style.SUCCESS(f"Journaux créés: {created_j} | Comptes créés: {created_a}"))
