# Generated manually
from django.db import migrations

COLUMNS = ("name", "slug")

# Build SQL literal: ARRAY['name','slug']
ARRAY_LITERAL = "ARRAY[" + ",".join(f"'{c}'" for c in COLUMNS) + "]"

SQL = f"""
DO $$
DECLARE
    col_name text;
BEGIN
    FOREACH col_name IN ARRAY {ARRAY_LITERAL} LOOP
        IF EXISTS (
            SELECT 1
            FROM information_schema.columns
            WHERE table_schema='public'
              AND table_name='ecommerce_category'
              AND column_name=col_name
        ) THEN
            EXECUTE format(
                'ALTER TABLE public.ecommerce_category ALTER COLUMN %I DROP NOT NULL',
                col_name
            );
        END IF;
    END LOOP;
END $$;
"""

REVERSE_SQL = f"""
DO $$
DECLARE
    col_name text;
BEGIN
    FOREACH col_name IN ARRAY {ARRAY_LITERAL} LOOP
        IF EXISTS (
            SELECT 1
            FROM information_schema.columns
            WHERE table_schema='public'
              AND table_name='ecommerce_category'
              AND column_name=col_name
        ) THEN
            EXECUTE format(
                'UPDATE public.ecommerce_category SET %I = '''' WHERE %I IS NULL',
                col_name, col_name
            );
            EXECUTE format(
                'ALTER TABLE public.ecommerce_category ALTER COLUMN %I SET NOT NULL',
                col_name
            );
        END IF;
    END LOOP;
END $$;
"""

class Migration(migrations.Migration):
    dependencies = [
        ("ecommerce", "0023_pg_hardening_invoice_review_constraints"),
    ]

    operations = [
        migrations.RunSQL(SQL, reverse_sql=REVERSE_SQL),
    ]
