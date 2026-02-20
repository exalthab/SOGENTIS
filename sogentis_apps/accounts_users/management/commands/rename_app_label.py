# core/management/commands/rename_app_label.py
from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction


class Command(BaseCommand):
    help = "Rename a Django app label in django_migrations and django_content_type (and related permissions)."

    def add_arguments(self, parser):
        parser.add_argument("--from", dest="from_label", required=True)
        parser.add_argument("--to", dest="to_label", required=True)

    @transaction.atomic
    def handle(self, *args, **options):
        from_label = options["from_label"].strip()
        to_label = options["to_label"].strip()

        if not from_label or not to_label or from_label == to_label:
            raise CommandError("Invalid labels.")

        with connection.cursor() as c:
            # --- 1) Safety: if target already exists in migrations, refuse
            c.execute("SELECT COUNT(*) FROM django_migrations WHERE app=%s", [to_label])
            if c.fetchone()[0] > 0:
                raise CommandError(
                    f"Target label '{to_label}' already exists in django_migrations. "
                    f"Stop: you likely already renamed or have mixed states."
                )

            # --- 2) If target contenttypes already exist, delete them to avoid duplicates
            c.execute("SELECT COUNT(*) FROM django_content_type WHERE app_label=%s", [to_label])
            existing_ct = c.fetchone()[0]
            if existing_ct > 0:
                self.stdout.write(self.style.WARNING(
                    f"Deleting {existing_ct} contenttypes for '{to_label}' to avoid duplicates."
                ))
                c.execute("DELETE FROM django_content_type WHERE app_label=%s", [to_label])

            # --- 3) Rename migrations history
            c.execute("UPDATE django_migrations SET app=%s WHERE app=%s", [to_label, from_label])
            mig_updated = c.rowcount

            # --- 4) Rename contenttypes
            c.execute("UPDATE django_content_type SET app_label=%s WHERE app_label=%s", [to_label, from_label])
            ct_updated = c.rowcount

            # --- 5) Re-attach permissions to renamed contenttypes (best-effort)
            # If permissions were linked to contenttype rows that were updated, they remain valid.
            # But if there are orphaned perms pointing to deleted CTs, cleanup:
            c.execute("""
                DELETE FROM auth_permission p
                WHERE NOT EXISTS (
                    SELECT 1 FROM django_content_type ct WHERE ct.id = p.content_type_id
                )
            """)
            perms_cleaned = c.rowcount

        self.stdout.write(self.style.SUCCESS(
            f"Done. migrations updated={mig_updated}, contenttypes updated={ct_updated}, orphan perms cleaned={perms_cleaned}"
        ))
