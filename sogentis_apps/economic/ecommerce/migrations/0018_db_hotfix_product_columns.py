# Generated manually for production hotfix (PostgreSQL)

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("ecommerce", "0017_alter_productimage_options_product_updated_at_and_more"),
    ]

    operations = [
        # --- ecommerce_product: colonnes manquantes (safe IF NOT EXISTS) ---
        migrations.RunSQL(
            sql="""
            ALTER TABLE ecommerce_product
              ADD COLUMN IF NOT EXISTS category_id bigint NULL;
            ALTER TABLE ecommerce_product
              ADD COLUMN IF NOT EXISTS vendor_id bigint NULL;
            ALTER TABLE ecommerce_product
              ADD COLUMN IF NOT EXISTS stock integer NOT NULL DEFAULT 0;
            ALTER TABLE ecommerce_product
              ADD COLUMN IF NOT EXISTS is_active boolean NOT NULL DEFAULT true;
            ALTER TABLE ecommerce_product
              ADD COLUMN IF NOT EXISTS is_featured boolean NOT NULL DEFAULT false;
            ALTER TABLE ecommerce_product
              ADD COLUMN IF NOT EXISTS created_at timestamp with time zone NOT NULL DEFAULT now();
            ALTER TABLE ecommerce_product
              ADD COLUMN IF NOT EXISTS updated_at timestamp with time zone NOT NULL DEFAULT now();
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),

        # Indexes utiles (ne cassent pas si déjà existants)
        migrations.RunSQL(
            sql="""
            CREATE INDEX IF NOT EXISTS ecommerce_product_is_active_idx
              ON ecommerce_product (is_active);

            CREATE INDEX IF NOT EXISTS ecommerce_product_is_featured_idx
              ON ecommerce_product (is_featured);

            CREATE INDEX IF NOT EXISTS ecommerce_product_category_active_idx
              ON ecommerce_product (category_id, is_active);

            CREATE INDEX IF NOT EXISTS ecommerce_product_vendor_active_idx
              ON ecommerce_product (vendor_id, is_active);
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
