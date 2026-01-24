# Generated manually (prod-safe) on 2026-01-24
from django.db import migrations, models


def _try(sql: str) -> str:
    """
    Exécute un SQL en best-effort (si erreur -> ignore).
    Utile pour DROP NOT NULL / SET DEFAULT sur schéma ancien.
    """
    return f"""
DO $$
BEGIN
  BEGIN
    {sql};
  EXCEPTION WHEN others THEN
    NULL;
  END;
END $$;
""".strip()


class Migration(migrations.Migration):

    dependencies = [
        ("ecommerce", "0018_db_hotfix_product_columns"),
    ]

    operations = [
        # ------------------------------------------------------------------
        # DB: ajoute les colonnes seulement si elles n'existent pas déjà
        # ------------------------------------------------------------------
        migrations.RunSQL(
            sql="""
            ALTER TABLE ecommerce_product
              ADD COLUMN IF NOT EXISTS fiche_technique text NOT NULL DEFAULT '';
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),

        migrations.RunSQL(
            sql="""
            ALTER TABLE ecommerce_product
              ADD COLUMN IF NOT EXISTS is_new boolean NOT NULL DEFAULT false;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),

        # ImageField => varchar en DB
        migrations.RunSQL(
            sql="""
            ALTER TABLE ecommerce_product
              ADD COLUMN IF NOT EXISTS image varchar(100) NULL;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        # Si ta colonne image existe déjà en NOT NULL (ancien schéma), on la rend nullable (ton modèle: null=True)
        migrations.RunSQL(
            sql=_try("ALTER TABLE ecommerce_product ALTER COLUMN image DROP NOT NULL"),
            reverse_sql=migrations.RunSQL.noop,
        ),

        # Index safe (évite "already exists")
        migrations.RunSQL(
            sql="""
            CREATE INDEX IF NOT EXISTS ecommerce_p_is_new_3bcaab_idx
            ON ecommerce_product (is_new, is_active);
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),

        # ------------------------------------------------------------------
        # STATE: met l'état Django à jour (sans refaire SQL dangereux)
        # ------------------------------------------------------------------
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AddField(
                    model_name="product",
                    name="fiche_technique",
                    field=models.TextField(blank=True, verbose_name="Fiche technique"),
                ),
                migrations.AddField(
                    model_name="product",
                    name="image",
                    field=models.ImageField(
                        blank=True,
                        null=True,
                        upload_to="products/main/%Y/%m/",
                        verbose_name="Image principale",
                    ),
                ),
                migrations.AddField(
                    model_name="product",
                    name="is_new",
                    field=models.BooleanField(db_index=True, default=False, verbose_name="Nouveau"),
                ),
                migrations.AddIndex(
                    model_name="product",
                    index=models.Index(
                        fields=["is_new", "is_active"],
                        name="ecommerce_p_is_new_3bcaab_idx",
                    ),
                ),
            ],
        ),
    ]
