# Generated manually (db-safe / idempotent) on 2026-02-02
from __future__ import annotations

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("prestations", "0008_cleanup_service_id_to_prestation_id"),
    ]

    operations = [
        migrations.RunSQL(
            sql=r"""
DO $$
BEGIN
    -- Table M2M: prestations_prestationpackage_prestations
    -- Fix: servicepackage_id -> prestationpackage_id

    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name='prestations_prestationpackage_prestations'
          AND column_name='servicepackage_id'
    )
    AND NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name='prestations_prestationpackage_prestations'
          AND column_name='prestationpackage_id'
    )
    THEN
        ALTER TABLE prestations_prestationpackage_prestations
            RENAME COLUMN servicepackage_id TO prestationpackage_id;
    END IF;

    -- Rename index (best effort) if it exists
    IF EXISTS (
        SELECT 1 FROM pg_class
        WHERE relkind='i'
          AND relname LIKE 'prestations_prestationpackage_prestations_servicepackage_id_%'
    )
    AND NOT EXISTS (
        SELECT 1 FROM pg_class
        WHERE relkind='i'
          AND relname LIKE 'prestations_prestationpackage_prestations_prestationpackage_id_%'
    )
    THEN
        EXECUTE (
            SELECT format(
                'ALTER INDEX %I RENAME TO %I',
                c.relname,
                replace(c.relname, 'servicepackage_id', 'prestationpackage_id')
            )
            FROM pg_class c
            WHERE c.relkind='i'
              AND c.relname LIKE 'prestations_prestationpackage_prestations_servicepackage_id_%'
            LIMIT 1
        );
    END IF;

END $$;
""",
            reverse_sql=r"""
DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name='prestations_prestationpackage_prestations'
          AND column_name='prestationpackage_id'
    )
    AND NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name='prestations_prestationpackage_prestations'
          AND column_name='servicepackage_id'
    )
    THEN
        ALTER TABLE prestations_prestationpackage_prestations
            RENAME COLUMN prestationpackage_id TO servicepackage_id;
    END IF;
END $$;
""",
        )
    ]
