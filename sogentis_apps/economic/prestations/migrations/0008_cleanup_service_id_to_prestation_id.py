# Generated manually (db-safe / idempotent) on 2026-02-02
from __future__ import annotations

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("prestations", "0007_fix_quoteline_service_id_to_prestation_id"),
    ]

    operations = [
        migrations.RunSQL(
            sql=r"""
DO $$
BEGIN
    -- ==========================================================
    -- 1) prestations_prestationfeature.service_id -> prestation_id
    -- ==========================================================
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='prestations_prestationfeature' AND column_name='service_id'
    )
    AND NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='prestations_prestationfeature' AND column_name='prestation_id'
    )
    THEN
        ALTER TABLE prestations_prestationfeature
            RENAME COLUMN service_id TO prestation_id;
    END IF;

    -- ==========================================================
    -- 2) prestations_prestationrequest.service_id -> prestation_id
    -- ==========================================================
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='prestations_prestationrequest' AND column_name='service_id'
    )
    AND NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='prestations_prestationrequest' AND column_name='prestation_id'
    )
    THEN
        ALTER TABLE prestations_prestationrequest
            RENAME COLUMN service_id TO prestation_id;
    END IF;

    -- ==========================================================
    -- 3) M2M table prestations_prestationpackage_prestations.service_id -> prestation_id
    --    (la table auto M2M garde le nom de colonne basé sur le FK field)
    -- ==========================================================
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='prestations_prestationpackage_prestations' AND column_name='service_id'
    )
    AND NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='prestations_prestationpackage_prestations' AND column_name='prestation_id'
    )
    THEN
        ALTER TABLE prestations_prestationpackage_prestations
            RENAME COLUMN service_id TO prestation_id;
    END IF;

    -- ==========================================================
    -- 4) Rename indexes éventuels (best-effort, non bloquant)
    -- ==========================================================

    -- prestationfeature
    IF EXISTS (
        SELECT 1 FROM pg_class
        WHERE relkind='i' AND relname LIKE 'prestations_prestationfeature_service_id_%'
    )
    AND NOT EXISTS (
        SELECT 1 FROM pg_class
        WHERE relkind='i' AND relname LIKE 'prestations_prestationfeature_prestation_id_%'
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
              AND c.relname LIKE 'prestations_prestationfeature_service_id_%'
            LIMIT 1
        );
    END IF;

    -- prestationrequest
    IF EXISTS (
        SELECT 1 FROM pg_class
        WHERE relkind='i' AND relname LIKE 'prestations_prestationrequest_service_id_%'
    )
    AND NOT EXISTS (
        SELECT 1 FROM pg_class
        WHERE relkind='i' AND relname LIKE 'prestations_prestationrequest_prestation_id_%'
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
              AND c.relname LIKE 'prestations_prestationrequest_service_id_%'
            LIMIT 1
        );
    END IF;

    -- m2m
    IF EXISTS (
        SELECT 1 FROM pg_class
        WHERE relkind='i' AND relname LIKE 'prestations_prestationpackage_prestations_service_id_%'
    )
    AND NOT EXISTS (
        SELECT 1 FROM pg_class
        WHERE relkind='i' AND relname LIKE 'prestations_prestationpackage_prestations_prestation_id_%'
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
              AND c.relname LIKE 'prestations_prestationpackage_prestations_service_id_%'
            LIMIT 1
        );
    END IF;

END $$;
""",
            reverse_sql=r"""
DO $$
BEGIN
    -- rollback best-effort (symétrique)

    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='prestations_prestationfeature' AND column_name='prestation_id'
    )
    AND NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='prestations_prestationfeature' AND column_name='service_id'
    )
    THEN
        ALTER TABLE prestations_prestationfeature
            RENAME COLUMN prestation_id TO service_id;
    END IF;

    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='prestations_prestationrequest' AND column_name='prestation_id'
    )
    AND NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='prestations_prestationrequest' AND column_name='service_id'
    )
    THEN
        ALTER TABLE prestations_prestationrequest
            RENAME COLUMN prestation_id TO service_id;
    END IF;

    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='prestations_prestationpackage_prestations' AND column_name='prestation_id'
    )
    AND NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='prestations_prestationpackage_prestations' AND column_name='service_id'
    )
    THEN
        ALTER TABLE prestations_prestationpackage_prestations
            RENAME COLUMN prestation_id TO service_id;
    END IF;

END $$;
""",
        )
    ]
