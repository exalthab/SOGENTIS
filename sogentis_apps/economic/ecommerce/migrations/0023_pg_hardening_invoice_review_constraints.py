# Generated manually (prod-safe / idempotent) on 2026-01-25
from __future__ import annotations

from django.db import migrations, models


# ============================================================
# Postgres helpers (idempotent)
# ============================================================
def _pg_fix_category_bigautofield_and_code(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return

    schema_editor.execute(
        """
DO $$
DECLARE
  coldef text;
  max_id bigint;
BEGIN
  IF to_regclass('public.ecommerce_category') IS NULL THEN
    RETURN;
  END IF;

  -- 1) Ensure sequence exists
  IF to_regclass('public.ecommerce_category_id_seq') IS NULL THEN
    CREATE SEQUENCE public.ecommerce_category_id_seq;
  END IF;

  -- 2) Ensure owned-by
  BEGIN
    ALTER SEQUENCE public.ecommerce_category_id_seq OWNED BY public.ecommerce_category.id;
  EXCEPTION WHEN others THEN
    NULL;
  END;

  -- 3) Ensure default nextval
  SELECT column_default INTO coldef
  FROM information_schema.columns
  WHERE table_schema='public'
    AND table_name='ecommerce_category'
    AND column_name='id';

  IF coldef IS NULL OR coldef = '' OR position('nextval' in coldef) = 0 THEN
    BEGIN
      ALTER TABLE public.ecommerce_category
        ALTER COLUMN id SET DEFAULT nextval('public.ecommerce_category_id_seq'::regclass);
    EXCEPTION WHEN others THEN
      NULL;
    END;
  END IF;

  -- 4) Sync sequence with MAX(id)
  SELECT COALESCE(MAX(id), 0) INTO max_id FROM public.ecommerce_category;
  IF max_id <= 0 THEN
    PERFORM setval('public.ecommerce_category_id_seq', 1, false);
  ELSE
    PERFORM setval('public.ecommerce_category_id_seq', max_id, true);
  END IF;

  -- 5) Normalize code column
  IF EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema='public' AND table_name='ecommerce_category' AND column_name='code'
  ) THEN
    BEGIN
      UPDATE public.ecommerce_category
      SET code = NULL
      WHERE code IS NOT NULL AND btrim(code) = '';
    EXCEPTION WHEN others THEN
      NULL;
    END;

    BEGIN
      ALTER TABLE public.ecommerce_category ALTER COLUMN code DROP NOT NULL;
    EXCEPTION WHEN others THEN
      NULL;
    END;

    BEGIN
      ALTER TABLE public.ecommerce_category ALTER COLUMN code DROP DEFAULT;
    EXCEPTION WHEN others THEN
      NULL;
    END;
  END IF;

END $$;
"""
    )


def _pg_cleanup_invoice_number_legacy(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return

    schema_editor.execute(
        """
DO $$
DECLARE
  r record;
BEGIN
  IF to_regclass('public.ecommerce_invoice') IS NULL THEN
    RETURN;
  END IF;

  -- Convert ''/spaces -> NULL
  BEGIN
    UPDATE public.ecommerce_invoice
    SET invoice_number = NULL
    WHERE invoice_number IS NOT NULL AND btrim(invoice_number) = '';
  EXCEPTION WHEN others THEN
    NULL;
  END;

  -- Drop DEFAULT/NOT NULL
  BEGIN
    ALTER TABLE public.ecommerce_invoice ALTER COLUMN invoice_number DROP DEFAULT;
  EXCEPTION WHEN others THEN
    NULL;
  END;

  BEGIN
    ALTER TABLE public.ecommerce_invoice ALTER COLUMN invoice_number DROP NOT NULL;
  EXCEPTION WHEN others THEN
    NULL;
  END;

  -- Drop legacy single-column unique constraints
  FOR r IN
    SELECT c.conname
    FROM pg_constraint c
    JOIN pg_attribute a
      ON a.attrelid = c.conrelid
     AND a.attnum = ANY (c.conkey)
    WHERE c.conrelid = 'public.ecommerce_invoice'::regclass
      AND c.contype = 'u'
      AND array_length(c.conkey, 1) = 1
      AND a.attname = 'invoice_number'
      AND c.conname <> 'uniq_invoice_number_not_empty'
  LOOP
    BEGIN
      EXECUTE 'ALTER TABLE public.ecommerce_invoice DROP CONSTRAINT IF EXISTS ' || quote_ident(r.conname);
    EXCEPTION WHEN others THEN
      NULL;
    END;
  END LOOP;

END $$;
"""
    )


def _pg_fix_review_constraints(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return

    schema_editor.execute(
        """
DO $$
BEGIN
  IF to_regclass('public.ecommerce_review') IS NULL THEN
    RETURN;
  END IF;

  -- Drop legacy unique constraint/index
  BEGIN
    ALTER TABLE public.ecommerce_review DROP CONSTRAINT IF EXISTS unique_review_per_user_product;
  EXCEPTION WHEN others THEN
    NULL;
  END;

  BEGIN
    DROP INDEX IF EXISTS public.unique_review_per_user_product;
  EXCEPTION WHEN others THEN
    NULL;
  END;

  -- Add rating check
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'chk_review_rating_1_5'
  ) THEN
    BEGIN
      ALTER TABLE public.ecommerce_review
        ADD CONSTRAINT chk_review_rating_1_5 CHECK (rating >= 1 AND rating <= 5);
    EXCEPTION WHEN others THEN
      NULL;
    END;
  END IF;

  -- Partial unique index for active reviews
  IF NOT EXISTS (
    SELECT 1 FROM pg_indexes
    WHERE schemaname='public' AND indexname='unique_active_review_per_user_product'
  ) THEN
    BEGIN
      CREATE UNIQUE INDEX unique_active_review_per_user_product
      ON public.ecommerce_review (product_id, user_id)
      WHERE is_active IS TRUE;
    EXCEPTION WHEN others THEN
      NULL;
    END;
  END IF;

END $$;
"""
    )


# ============================================================
# Migration
# ============================================================
class Migration(migrations.Migration):

    dependencies = [
        ("ecommerce", "0022_alter_category_id_alter_favorite_created_at_and_more"),
    ]

    operations = [
        # A) Hardening DB legacy
        migrations.RunPython(_pg_fix_category_bigautofield_and_code, migrations.RunPython.noop),
        migrations.RunPython(_pg_cleanup_invoice_number_legacy, migrations.RunPython.noop),

        # B) Invoice: nullable + unique only when non-empty
        migrations.AlterField(
            model_name="invoice",
            name="invoice_number",
            field=models.CharField(
                max_length=24,
                null=True,
                blank=True,
                db_index=True,
                verbose_name="Numéro de facture",
                help_text="Auto-généré. Ex: INV-20260124-0001",
            ),
        ),
        migrations.AddConstraint(
            model_name="invoice",
            constraint=models.UniqueConstraint(
                fields=("invoice_number",),
                condition=models.Q(invoice_number__isnull=False) & ~models.Q(invoice_number=""),
                name="uniq_invoice_number_not_empty",
            ),
        ),

        # C) Review constraints: prod-safe + soft-delete compatible
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(_pg_fix_review_constraints, migrations.RunPython.noop),
            ],
            state_operations=[
                migrations.RemoveConstraint(
                    model_name="review",
                    name="unique_review_per_user_product",
                ),
                migrations.AddConstraint(
                    model_name="review",
                    constraint=models.CheckConstraint(
                        condition=models.Q(rating__gte=1, rating__lte=5),
                        name="chk_review_rating_1_5",
                    ),
                ),
                migrations.AddConstraint(
                    model_name="review",
                    constraint=models.UniqueConstraint(
                        fields=("product", "user"),
                        condition=models.Q(is_active=True),
                        name="unique_active_review_per_user_product",
                    ),
                ),
            ],
        ),
    ]
