# Generated manually (db-safe / idempotent) on 2026-02-02
from __future__ import annotations

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("prestations", "0006_alter_prestationfeature_options_and_more"),
    ]

    operations = [
        migrations.RunSQL(
            sql=r"""
DO $$
BEGIN
    -- 1) Rename colonne FK : service_id -> prestation_id
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name='prestations_quoteline'
          AND column_name='service_id'
    )
    AND NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name='prestations_quoteline'
          AND column_name='prestation_id'
    )
    THEN
        ALTER TABLE prestations_quoteline
            RENAME COLUMN service_id TO prestation_id;
    END IF;

    -- 2) Rename index éventuel généré sur service_id (si présent)
    IF EXISTS (
        SELECT 1
        FROM pg_class
        WHERE relkind='i'
          AND relname LIKE 'prestations_quoteline_service_id_%'
    )
    AND NOT EXISTS (
        SELECT 1
        FROM pg_class
        WHERE relkind='i'
          AND relname LIKE 'prestations_quoteline_prestation_id_%'
    )
    THEN
        EXECUTE (
            SELECT format(
                'ALTER INDEX %I RENAME TO %I',
                c.relname,
                replace(c.relname, 'service_id', 'prestation_id')
            )
            FROM pg_class c
            WHERE c.relkind='i'
              AND c.relname LIKE 'prestations_quoteline_service_id_%'
            LIMIT 1
        );
    END IF;

END $$;
""",
            reverse_sql=r"""
DO $$
BEGIN
    -- rollback : prestation_id -> service_id
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name='prestations_quoteline'
          AND column_name='prestation_id'
    )
    AND NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name='prestations_quoteline'
          AND column_name='service_id'
    )
    THEN
        ALTER TABLE prestations_quoteline
            RENAME COLUMN prestation_id TO service_id;
    END IF;
END $$;
""",
        )
    ]
