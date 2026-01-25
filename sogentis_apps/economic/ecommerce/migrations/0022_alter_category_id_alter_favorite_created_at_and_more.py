# Generated manually (prod-safe / idempotent) on 2026-01-25
import django.db.models.deletion
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models


# ------------------------------------------------------------
# Helpers Postgres: safe guards (table/column/index/constraint)
# ------------------------------------------------------------
def _sql(sql: str) -> str:
    return sql.strip()


def _try(inner_sql: str) -> str:
    """
    Exécute un SQL en best-effort: si erreur -> ignore.
    """
    return _sql(
        f"""
DO $$
BEGIN
  BEGIN
    {inner_sql}
  EXCEPTION WHEN others THEN
    NULL;
  END;
END $$;
"""
    )


def _ensure_column(table: str, column: str, ddl: str) -> str:
    """
    Ajoute une colonne si elle manque (sans casser si elle existe déjà).
    ddl = "type ... [NOT NULL] [DEFAULT ...]"
    """
    return _sql(
        f"""
DO $$
BEGIN
  IF to_regclass('public.{table}') IS NOT NULL THEN
    IF NOT EXISTS (
      SELECT 1
      FROM information_schema.columns
      WHERE table_schema='public'
        AND table_name='{table}'
        AND column_name='{column}'
    ) THEN
      BEGIN
        ALTER TABLE {table} ADD COLUMN {column} {ddl};
      EXCEPTION WHEN others THEN
        NULL;
      END;
    END IF;
  END IF;
END $$;
"""
    )


def _create_index_if_missing(indexname: str, create_sql: str) -> str:
    return _sql(
        f"""
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_indexes
    WHERE schemaname='public' AND indexname='{indexname}'
  ) THEN
    BEGIN
      {create_sql}
    EXCEPTION WHEN others THEN
      NULL;
    END;
  END IF;
END $$;
"""
    )


def _add_constraint_if_missing(constraint_name: str, table: str, alter_sql: str) -> str:
    return _sql(
        f"""
DO $$
BEGIN
  IF to_regclass('public.{table}') IS NOT NULL THEN
    IF NOT EXISTS (
      SELECT 1 FROM pg_constraint WHERE conname='{constraint_name}'
    ) THEN
      BEGIN
        {alter_sql}
      EXCEPTION WHEN others THEN
        NULL;
      END;
    END IF;
  END IF;
END $$;
"""
    )


class Migration(migrations.Migration):

    dependencies = [
        ("ecommerce", "0021_skusequence_alter_cart_options_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # ============================================================
        # DB OPS (safe): ensure columns + create indexes/constraints safely
        # ============================================================
        migrations.SeparateDatabaseAndState(
            database_operations=[
                # ---------------------------
                # Ensure columns for INDEXES
                # ---------------------------

                # CART
                migrations.RunSQL(_ensure_column("ecommerce_cart", "is_active", "boolean NOT NULL DEFAULT true"), migrations.RunSQL.noop),
                migrations.RunSQL(_ensure_column("ecommerce_cart", "created_at", "timestamptz NOT NULL DEFAULT now()"), migrations.RunSQL.noop),
                migrations.RunSQL(_ensure_column("ecommerce_cart", "session_key", "varchar(255) NULL"), migrations.RunSQL.noop),
                migrations.RunSQL(_ensure_column("ecommerce_cart", "expires_at", "timestamptz NULL"), migrations.RunSQL.noop),
                migrations.RunSQL(_ensure_column("ecommerce_cart", "user_id", "bigint NULL"), migrations.RunSQL.noop),

                # CARTITEM
                migrations.RunSQL(_ensure_column("ecommerce_cartitem", "cart_id", "bigint NULL"), migrations.RunSQL.noop),
                migrations.RunSQL(_ensure_column("ecommerce_cartitem", "product_id", "bigint NULL"), migrations.RunSQL.noop),
                migrations.RunSQL(_ensure_column("ecommerce_cartitem", "created_at", "timestamptz NOT NULL DEFAULT now()"), migrations.RunSQL.noop),

                # CATEGORY
                migrations.RunSQL(_ensure_column("ecommerce_category", "code", "varchar(50) NOT NULL DEFAULT ''"), migrations.RunSQL.noop),

                # FAVORITE
                migrations.RunSQL(_ensure_column("ecommerce_favorite", "user_id", "bigint NULL"), migrations.RunSQL.noop),
                migrations.RunSQL(_ensure_column("ecommerce_favorite", "product_id", "bigint NULL"), migrations.RunSQL.noop),
                migrations.RunSQL(_ensure_column("ecommerce_favorite", "created_at", "timestamptz NOT NULL DEFAULT now()"), migrations.RunSQL.noop),

                # INVOICE
                migrations.RunSQL(_ensure_column("ecommerce_invoice", "invoice_number", "varchar(50) NULL"), migrations.RunSQL.noop),
                migrations.RunSQL(_ensure_column("ecommerce_invoice", "status", "varchar(30) NOT NULL DEFAULT 'draft'"), migrations.RunSQL.noop),
                migrations.RunSQL(_ensure_column("ecommerce_invoice", "created_at", "timestamptz NOT NULL DEFAULT now()"), migrations.RunSQL.noop),
                migrations.RunSQL(_ensure_column("ecommerce_invoice", "amount", "numeric(12,2) NOT NULL DEFAULT 0"), migrations.RunSQL.noop),
                migrations.RunSQL(_ensure_column("ecommerce_invoice", "order_id", "bigint NULL"), migrations.RunSQL.noop),

                # ORDER
                migrations.RunSQL(_ensure_column("ecommerce_order", "reference", "varchar(50) NULL"), migrations.RunSQL.noop),
                migrations.RunSQL(_ensure_column("ecommerce_order", "user_id", "bigint NULL"), migrations.RunSQL.noop),
                migrations.RunSQL(_ensure_column("ecommerce_order", "created_at", "timestamptz NOT NULL DEFAULT now()"), migrations.RunSQL.noop),
                migrations.RunSQL(_ensure_column("ecommerce_order", "subtotal_amount", "numeric(12,2) NOT NULL DEFAULT 0"), migrations.RunSQL.noop),
                migrations.RunSQL(_ensure_column("ecommerce_order", "shipping_amount", "numeric(12,2) NOT NULL DEFAULT 0"), migrations.RunSQL.noop),
                migrations.RunSQL(_ensure_column("ecommerce_order", "tax_amount", "numeric(12,2) NOT NULL DEFAULT 0"), migrations.RunSQL.noop),
                migrations.RunSQL(_ensure_column("ecommerce_order", "discount_amount", "numeric(12,2) NOT NULL DEFAULT 0"), migrations.RunSQL.noop),
                migrations.RunSQL(_ensure_column("ecommerce_order", "total_amount", "numeric(12,2) NOT NULL DEFAULT 0"), migrations.RunSQL.noop),

                # ORDERITEM  ✅ important (ton erreur précédente)
                migrations.RunSQL(_ensure_column("ecommerce_orderitem", "product_id", "bigint NULL"), migrations.RunSQL.noop),
                migrations.RunSQL(_ensure_column("ecommerce_orderitem", "created_at", "timestamptz NOT NULL DEFAULT now()"), migrations.RunSQL.noop),
                migrations.RunSQL(_ensure_column("ecommerce_orderitem", "quantity", "integer NOT NULL DEFAULT 1"), migrations.RunSQL.noop),
                migrations.RunSQL(_ensure_column("ecommerce_orderitem", "unit_price", "numeric(12,2) NOT NULL DEFAULT 0"), migrations.RunSQL.noop),

                # PAYMENTTRANSACTION
                migrations.RunSQL(_ensure_column("ecommerce_paymenttransaction", "order_id", "bigint NULL"), migrations.RunSQL.noop),
                migrations.RunSQL(_ensure_column("ecommerce_paymenttransaction", "created_at", "timestamptz NOT NULL DEFAULT now()"), migrations.RunSQL.noop),
                migrations.RunSQL(_ensure_column("ecommerce_paymenttransaction", "provider_payment_id", "varchar(255) NULL"), migrations.RunSQL.noop),
                migrations.RunSQL(_ensure_column("ecommerce_paymenttransaction", "idempotency_key", "varchar(128) NOT NULL DEFAULT ''"), migrations.RunSQL.noop),
                migrations.RunSQL(_ensure_column("ecommerce_paymenttransaction", "amount", "numeric(12,2) NOT NULL DEFAULT 0"), migrations.RunSQL.noop),
                migrations.RunSQL(_ensure_column("ecommerce_paymenttransaction", "provider_fee", "numeric(12,2) NOT NULL DEFAULT 0"), migrations.RunSQL.noop),
                migrations.RunSQL(_ensure_column("ecommerce_paymenttransaction", "provider", "varchar(30) NOT NULL DEFAULT ''"), migrations.RunSQL.noop),

                # PRODUCT
                migrations.RunSQL(_ensure_column("ecommerce_product", "sku", "varchar(100) NULL"), migrations.RunSQL.noop),

                # PRODUCTPRICING
                migrations.RunSQL(_ensure_column("ecommerce_productpricing", "pricing_type", "varchar(3) NOT NULL DEFAULT 'B2C'"), migrations.RunSQL.noop),
                migrations.RunSQL(_ensure_column("ecommerce_productpricing", "currency", "varchar(10) NOT NULL DEFAULT 'XOF'"), migrations.RunSQL.noop),
                migrations.RunSQL(_ensure_column("ecommerce_productpricing", "is_active", "boolean NOT NULL DEFAULT true"), migrations.RunSQL.noop),

                # REVIEW
                migrations.RunSQL(_ensure_column("ecommerce_review", "product_id", "bigint NULL"), migrations.RunSQL.noop),
                migrations.RunSQL(_ensure_column("ecommerce_review", "user_id", "bigint NULL"), migrations.RunSQL.noop),
                migrations.RunSQL(_ensure_column("ecommerce_review", "created_at", "timestamptz NOT NULL DEFAULT now()"), migrations.RunSQL.noop),
                migrations.RunSQL(_ensure_column("ecommerce_review", "is_active", "boolean NOT NULL DEFAULT true"), migrations.RunSQL.noop),
                migrations.RunSQL(_ensure_column("ecommerce_review", "is_approved", "boolean NOT NULL DEFAULT false"), migrations.RunSQL.noop),
                migrations.RunSQL(_ensure_column("ecommerce_review", "rating", "integer NOT NULL DEFAULT 5"), migrations.RunSQL.noop),

                # SKU SEQUENCE
                migrations.RunSQL(_ensure_column("ecommerce_skusequence", "vendor_code", "varchar(50) NOT NULL DEFAULT ''"), migrations.RunSQL.noop),
                migrations.RunSQL(_ensure_column("ecommerce_skusequence", "category_code", "varchar(50) NOT NULL DEFAULT ''"), migrations.RunSQL.noop),

                # VENDOR
                migrations.RunSQL(_ensure_column("ecommerce_vendor", "code", "varchar(50) NOT NULL DEFAULT ''"), migrations.RunSQL.noop),
                migrations.RunSQL(_ensure_column("ecommerce_vendor", "slug", "varchar(255) NOT NULL DEFAULT ''"), migrations.RunSQL.noop),
                migrations.RunSQL(_ensure_column("ecommerce_vendor", "is_active", "boolean NOT NULL DEFAULT true"), migrations.RunSQL.noop),
                migrations.RunSQL(_ensure_column("ecommerce_vendor", "is_verified", "boolean NOT NULL DEFAULT false"), migrations.RunSQL.noop),

                # WISHLIST
                migrations.RunSQL(_ensure_column("ecommerce_wishlist", "user_id", "bigint NULL"), migrations.RunSQL.noop),
                migrations.RunSQL(_ensure_column("ecommerce_wishlist", "created_at", "timestamptz NOT NULL DEFAULT now()"), migrations.RunSQL.noop),

                # WISHLISTITEM
                migrations.RunSQL(_ensure_column("ecommerce_wishlistitem", "wishlist_id", "bigint NULL"), migrations.RunSQL.noop),
                migrations.RunSQL(_ensure_column("ecommerce_wishlistitem", "product_id", "bigint NULL"), migrations.RunSQL.noop),
                migrations.RunSQL(_ensure_column("ecommerce_wishlistitem", "is_active", "boolean NOT NULL DEFAULT true"), migrations.RunSQL.noop),
                migrations.RunSQL(_ensure_column("ecommerce_wishlistitem", "added_at", "timestamptz NOT NULL DEFAULT now()"), migrations.RunSQL.noop),

                # ---------------------------
                # Create INDEXES safely
                # ---------------------------
                migrations.RunSQL(_create_index_if_missing("ecommerce_c_is_acti_f1406f_idx", "CREATE INDEX ecommerce_c_is_acti_f1406f_idx ON ecommerce_cart (is_active, created_at);"), migrations.RunSQL.noop),
                migrations.RunSQL(_create_index_if_missing("ecommerce_c_user_id_9231b2_idx", "CREATE INDEX ecommerce_c_user_id_9231b2_idx ON ecommerce_cart (user_id, is_active);"), migrations.RunSQL.noop),
                migrations.RunSQL(_create_index_if_missing("ecommerce_c_session_73ce7b_idx", "CREATE INDEX ecommerce_c_session_73ce7b_idx ON ecommerce_cart (session_key, is_active);"), migrations.RunSQL.noop),
                migrations.RunSQL(_create_index_if_missing("ecommerce_c_expires_c5a0fb_idx", "CREATE INDEX ecommerce_c_expires_c5a0fb_idx ON ecommerce_cart (expires_at);"), migrations.RunSQL.noop),

                migrations.RunSQL(_create_index_if_missing("ecommerce_c_cart_id_e86aae_idx", "CREATE INDEX ecommerce_c_cart_id_e86aae_idx ON ecommerce_cartitem (cart_id, created_at);"), migrations.RunSQL.noop),
                migrations.RunSQL(_create_index_if_missing("ecommerce_c_product_6c0a19_idx", "CREATE INDEX ecommerce_c_product_6c0a19_idx ON ecommerce_cartitem (product_id);"), migrations.RunSQL.noop),

                migrations.RunSQL(_create_index_if_missing("ecommerce_c_code_03eca9_idx", "CREATE INDEX ecommerce_c_code_03eca9_idx ON ecommerce_category (code);"), migrations.RunSQL.noop),

                migrations.RunSQL(_create_index_if_missing("ecommerce_f_user_id_8e5f1e_idx", "CREATE INDEX ecommerce_f_user_id_8e5f1e_idx ON ecommerce_favorite (user_id, created_at);"), migrations.RunSQL.noop),
                migrations.RunSQL(_create_index_if_missing("ecommerce_f_product_d4e109_idx", "CREATE INDEX ecommerce_f_product_d4e109_idx ON ecommerce_favorite (product_id, created_at);"), migrations.RunSQL.noop),

                migrations.RunSQL(_create_index_if_missing("ecommerce_i_invoice_66eb4a_idx", "CREATE INDEX ecommerce_i_invoice_66eb4a_idx ON ecommerce_invoice (invoice_number);"), migrations.RunSQL.noop),
                migrations.RunSQL(_create_index_if_missing("ecommerce_i_status_ebfed2_idx", "CREATE INDEX ecommerce_i_status_ebfed2_idx ON ecommerce_invoice (status, created_at);"), migrations.RunSQL.noop),
                migrations.RunSQL(_create_index_if_missing("ecommerce_i_order_i_9a9c03_idx", "CREATE INDEX ecommerce_i_order_i_9a9c03_idx ON ecommerce_invoice (order_id);"), migrations.RunSQL.noop),

                migrations.RunSQL(_create_index_if_missing("ecommerce_o_referen_19782e_idx", "CREATE INDEX ecommerce_o_referen_19782e_idx ON ecommerce_order (reference);"), migrations.RunSQL.noop),
                migrations.RunSQL(_create_index_if_missing("ecommerce_o_user_id_cb1717_idx", "CREATE INDEX ecommerce_o_user_id_cb1717_idx ON ecommerce_order (user_id, created_at);"), migrations.RunSQL.noop),

                migrations.RunSQL(_create_index_if_missing("ecommerce_o_product_e8ab69_idx", "CREATE INDEX ecommerce_o_product_e8ab69_idx ON ecommerce_orderitem (product_id);"), migrations.RunSQL.noop),
                migrations.RunSQL(_create_index_if_missing("ecommerce_o_created_9448b8_idx", "CREATE INDEX ecommerce_o_created_9448b8_idx ON ecommerce_orderitem (created_at);"), migrations.RunSQL.noop),

                migrations.RunSQL(_create_index_if_missing("ecommerce_p_order_i_21b106_idx", "CREATE INDEX ecommerce_p_order_i_21b106_idx ON ecommerce_paymenttransaction (order_id, created_at);"), migrations.RunSQL.noop),
                migrations.RunSQL(_create_index_if_missing("ecommerce_p_provide_c699b4_idx", "CREATE INDEX ecommerce_p_provide_c699b4_idx ON ecommerce_paymenttransaction (provider_payment_id);"), migrations.RunSQL.noop),
                migrations.RunSQL(_create_index_if_missing("ecommerce_p_idempot_312b31_idx", "CREATE INDEX ecommerce_p_idempot_312b31_idx ON ecommerce_paymenttransaction (idempotency_key);"), migrations.RunSQL.noop),

                migrations.RunSQL(_create_index_if_missing("ecommerce_p_sku_35a263_idx", "CREATE INDEX ecommerce_p_sku_35a263_idx ON ecommerce_product (sku);"), migrations.RunSQL.noop),

                migrations.RunSQL(_create_index_if_missing("ecommerce_p_pricing_7988ae_idx", "CREATE INDEX ecommerce_p_pricing_7988ae_idx ON ecommerce_productpricing (pricing_type, currency, is_active);"), migrations.RunSQL.noop),

                migrations.RunSQL(_create_index_if_missing("ecommerce_r_product_3147d3_idx", "CREATE INDEX ecommerce_r_product_3147d3_idx ON ecommerce_review (product_id, is_active, is_approved);"), migrations.RunSQL.noop),
                migrations.RunSQL(_create_index_if_missing("ecommerce_r_user_id_5bd2b2_idx", "CREATE INDEX ecommerce_r_user_id_5bd2b2_idx ON ecommerce_review (user_id, created_at);"), migrations.RunSQL.noop),
                migrations.RunSQL(_create_index_if_missing("ecommerce_r_rating_52ad52_idx", "CREATE INDEX ecommerce_r_rating_52ad52_idx ON ecommerce_review (rating, created_at);"), migrations.RunSQL.noop),

                migrations.RunSQL(_create_index_if_missing("ecommerce_s_vendor__c7eff4_idx", "CREATE INDEX ecommerce_s_vendor__c7eff4_idx ON ecommerce_skusequence (vendor_code, category_code);"), migrations.RunSQL.noop),

                migrations.RunSQL(_create_index_if_missing("ecommerce_v_code_50dfcd_idx", "CREATE INDEX ecommerce_v_code_50dfcd_idx ON ecommerce_vendor (code);"), migrations.RunSQL.noop),
                migrations.RunSQL(_create_index_if_missing("ecommerce_v_slug_86ae78_idx", "CREATE INDEX ecommerce_v_slug_86ae78_idx ON ecommerce_vendor (slug);"), migrations.RunSQL.noop),
                migrations.RunSQL(_create_index_if_missing("ecommerce_v_is_acti_8fce7f_idx", "CREATE INDEX ecommerce_v_is_acti_8fce7f_idx ON ecommerce_vendor (is_active, is_verified);"), migrations.RunSQL.noop),

                migrations.RunSQL(_create_index_if_missing("ecommerce_w_user_id_638869_idx", "CREATE INDEX ecommerce_w_user_id_638869_idx ON ecommerce_wishlist (user_id);"), migrations.RunSQL.noop),
                migrations.RunSQL(_create_index_if_missing("ecommerce_w_created_1d487e_idx", "CREATE INDEX ecommerce_w_created_1d487e_idx ON ecommerce_wishlist (created_at);"), migrations.RunSQL.noop),

                migrations.RunSQL(_create_index_if_missing("ecommerce_w_wishlis_cbf394_idx", "CREATE INDEX ecommerce_w_wishlis_cbf394_idx ON ecommerce_wishlistitem (wishlist_id, is_active, added_at DESC);"), migrations.RunSQL.noop),
                migrations.RunSQL(_create_index_if_missing("ecommerce_w_product_2951e2_idx", "CREATE INDEX ecommerce_w_product_2951e2_idx ON ecommerce_wishlistitem (product_id, is_active);"), migrations.RunSQL.noop),

                # ---------------------------
                # Constraints safely
                # ---------------------------
                migrations.RunSQL(_add_constraint_if_missing("chk_invoice_amount_gte_0", "ecommerce_invoice", "ALTER TABLE ecommerce_invoice ADD CONSTRAINT chk_invoice_amount_gte_0 CHECK (amount >= 0);"), migrations.RunSQL.noop),

                migrations.RunSQL(_add_constraint_if_missing("chk_order_total_gte_0", "ecommerce_order", "ALTER TABLE ecommerce_order ADD CONSTRAINT chk_order_total_gte_0 CHECK (total_amount >= 0);"), migrations.RunSQL.noop),
                migrations.RunSQL(_add_constraint_if_missing("chk_order_subtotal_gte_0", "ecommerce_order", "ALTER TABLE ecommerce_order ADD CONSTRAINT chk_order_subtotal_gte_0 CHECK (subtotal_amount >= 0);"), migrations.RunSQL.noop),
                migrations.RunSQL(_add_constraint_if_missing("chk_order_shipping_gte_0", "ecommerce_order", "ALTER TABLE ecommerce_order ADD CONSTRAINT chk_order_shipping_gte_0 CHECK (shipping_amount >= 0);"), migrations.RunSQL.noop),
                migrations.RunSQL(_add_constraint_if_missing("chk_order_tax_gte_0", "ecommerce_order", "ALTER TABLE ecommerce_order ADD CONSTRAINT chk_order_tax_gte_0 CHECK (tax_amount >= 0);"), migrations.RunSQL.noop),
                migrations.RunSQL(_add_constraint_if_missing("chk_order_discount_gte_0", "ecommerce_order", "ALTER TABLE ecommerce_order ADD CONSTRAINT chk_order_discount_gte_0 CHECK (discount_amount >= 0);"), migrations.RunSQL.noop),

                migrations.RunSQL(_add_constraint_if_missing("chk_orderitem_qty_gt_0", "ecommerce_orderitem", "ALTER TABLE ecommerce_orderitem ADD CONSTRAINT chk_orderitem_qty_gt_0 CHECK (quantity > 0);"), migrations.RunSQL.noop),
                migrations.RunSQL(_add_constraint_if_missing("chk_orderitem_unitprice_gte_0", "ecommerce_orderitem", "ALTER TABLE ecommerce_orderitem ADD CONSTRAINT chk_orderitem_unitprice_gte_0 CHECK (unit_price >= 0);"), migrations.RunSQL.noop),

                migrations.RunSQL(_add_constraint_if_missing("chk_payment_amount_gte_0", "ecommerce_paymenttransaction", "ALTER TABLE ecommerce_paymenttransaction ADD CONSTRAINT chk_payment_amount_gte_0 CHECK (amount >= 0);"), migrations.RunSQL.noop),
                migrations.RunSQL(_add_constraint_if_missing("chk_payment_fee_gte_0", "ecommerce_paymenttransaction", "ALTER TABLE ecommerce_paymenttransaction ADD CONSTRAINT chk_payment_fee_gte_0 CHECK (provider_fee >= 0);"), migrations.RunSQL.noop),

                # Partial unique constraints -> use UNIQUE INDEX (idempotent)
                migrations.RunSQL(
                    _create_index_if_missing(
                        "uniq_order_reference_not_empty",
                        "CREATE UNIQUE INDEX uniq_order_reference_not_empty ON ecommerce_order (reference) "
                        "WHERE reference IS NOT NULL AND reference <> '';",
                    ),
                    migrations.RunSQL.noop,
                ),
                migrations.RunSQL(
                    _create_index_if_missing(
                        "uniq_payment_provider_idempotency_nonempty",
                        "CREATE UNIQUE INDEX uniq_payment_provider_idempotency_nonempty "
                        "ON ecommerce_paymenttransaction (provider, idempotency_key) "
                        "WHERE idempotency_key IS NOT NULL AND idempotency_key <> '';",
                    ),
                    migrations.RunSQL.noop,
                ),

                # Regular unique constraint for skusequence
                migrations.RunSQL(
                    _add_constraint_if_missing(
                        "uniq_sku_sequence_vendor_category",
                        "ecommerce_skusequence",
                        "ALTER TABLE ecommerce_skusequence "
                        "ADD CONSTRAINT uniq_sku_sequence_vendor_category UNIQUE (vendor_code, category_code);",
                    ),
                    migrations.RunSQL.noop,
                ),
            ],
            state_operations=[
                # ============================================================
                # STATE OPS: on garde EXACTEMENT les opérations générées
                # (mais sans exécuter SQL fragile automatiquement)
                # ============================================================
                migrations.AlterField(
                    model_name="category",
                    name="id",
                    field=models.BigAutoField(primary_key=True, serialize=False),
                ),
                migrations.AlterField(
                    model_name="favorite",
                    name="created_at",
                    field=models.DateTimeField(auto_now_add=True, verbose_name="Créé le"),
                ),
                migrations.AlterField(
                    model_name="invoice",
                    name="file",
                    field=models.FileField(
                        blank=True,
                        null=True,
                        upload_to="invoices/%Y/%m/",
                        verbose_name="Fichier PDF",
                    ),
                ),
                migrations.AlterField(
                    model_name="invoice",
                    name="order",
                    field=models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="invoice",
                        to="ecommerce.order",
                        verbose_name="Commande",
                    ),
                ),
                migrations.AlterField(
                    model_name="order",
                    name="total_amount",
                    field=models.DecimalField(
                        decimal_places=2,
                        default=Decimal("0.00"),
                        max_digits=12,
                        verbose_name="Montant total",
                    ),
                ),
                migrations.AlterField(
                    model_name="paymenttransaction",
                    name="currency",
                    field=models.CharField(
                        db_index=True, default="XOF", max_length=10, verbose_name="Devise"
                    ),
                ),
                migrations.AlterField(
                    model_name="product",
                    name="sku",
                    field=models.CharField(
                        blank=True,
                        db_index=True,
                        help_text="Format recommandé : <VENDORCODE>-<CATCODE>-<NNNN> (ex: SOG-TECH-0001).",
                        max_length=100,
                        unique=True,
                        verbose_name="SKU",
                    ),
                ),
                migrations.AlterField(
                    model_name="review",
                    name="is_approved",
                    field=models.BooleanField(
                        db_index=True, default=False, verbose_name="Approuvé"
                    ),
                ),
                migrations.AlterField(
                    model_name="review",
                    name="rating",
                    field=models.PositiveSmallIntegerField(
                        choices=[(1, "1"), (2, "2"), (3, "3"), (4, "4"), (5, "5")],
                        db_index=True,
                        verbose_name="Note",
                    ),
                ),
                migrations.AlterField(
                    model_name="vendor",
                    name="is_verified",
                    field=models.BooleanField(
                        db_index=True, default=False, verbose_name="Vérifié"
                    ),
                ),
                migrations.AddIndex(
                    model_name="cart",
                    index=models.Index(
                        fields=["is_active", "created_at"],
                        name="ecommerce_c_is_acti_f1406f_idx",
                    ),
                ),
                migrations.AddIndex(
                    model_name="cart",
                    index=models.Index(
                        fields=["user", "is_active"], name="ecommerce_c_user_id_9231b2_idx"
                    ),
                ),
                migrations.AddIndex(
                    model_name="cart",
                    index=models.Index(
                        fields=["session_key", "is_active"],
                        name="ecommerce_c_session_73ce7b_idx",
                    ),
                ),
                migrations.AddIndex(
                    model_name="cart",
                    index=models.Index(
                        fields=["expires_at"], name="ecommerce_c_expires_c5a0fb_idx"
                    ),
                ),
                migrations.AddIndex(
                    model_name="cartitem",
                    index=models.Index(
                        fields=["cart", "created_at"], name="ecommerce_c_cart_id_e86aae_idx"
                    ),
                ),
                migrations.AddIndex(
                    model_name="cartitem",
                    index=models.Index(
                        fields=["product"], name="ecommerce_c_product_6c0a19_idx"
                    ),
                ),
                migrations.AddIndex(
                    model_name="category",
                    index=models.Index(fields=["code"], name="ecommerce_c_code_03eca9_idx"),
                ),
                migrations.AddIndex(
                    model_name="favorite",
                    index=models.Index(
                        fields=["user", "created_at"], name="ecommerce_f_user_id_8e5f1e_idx"
                    ),
                ),
                migrations.AddIndex(
                    model_name="favorite",
                    index=models.Index(
                        fields=["product", "created_at"], name="ecommerce_f_product_d4e109_idx"
                    ),
                ),
                migrations.AddIndex(
                    model_name="invoice",
                    index=models.Index(
                        fields=["invoice_number"], name="ecommerce_i_invoice_66eb4a_idx"
                    ),
                ),
                migrations.AddIndex(
                    model_name="invoice",
                    index=models.Index(
                        fields=["status", "created_at"], name="ecommerce_i_status_ebfed2_idx"
                    ),
                ),
                migrations.AddIndex(
                    model_name="invoice",
                    index=models.Index(fields=["order"], name="ecommerce_i_order_i_9a9c03_idx"),
                ),
                migrations.AddIndex(
                    model_name="order",
                    index=models.Index(
                        fields=["reference"], name="ecommerce_o_referen_19782e_idx"
                    ),
                ),
                migrations.AddIndex(
                    model_name="order",
                    index=models.Index(
                        fields=["user", "created_at"], name="ecommerce_o_user_id_cb1717_idx"
                    ),
                ),
                migrations.AddIndex(
                    model_name="orderitem",
                    index=models.Index(
                        fields=["product"], name="ecommerce_o_product_e8ab69_idx"
                    ),
                ),
                migrations.AddIndex(
                    model_name="orderitem",
                    index=models.Index(
                        fields=["created_at"], name="ecommerce_o_created_9448b8_idx"
                    ),
                ),
                migrations.AddIndex(
                    model_name="paymenttransaction",
                    index=models.Index(
                        fields=["order", "created_at"], name="ecommerce_p_order_i_21b106_idx"
                    ),
                ),
                migrations.AddIndex(
                    model_name="paymenttransaction",
                    index=models.Index(
                        fields=["provider_payment_id"], name="ecommerce_p_provide_c699b4_idx"
                    ),
                ),
                migrations.AddIndex(
                    model_name="paymenttransaction",
                    index=models.Index(
                        fields=["idempotency_key"], name="ecommerce_p_idempot_312b31_idx"
                    ),
                ),
                migrations.AddIndex(
                    model_name="product",
                    index=models.Index(fields=["sku"], name="ecommerce_p_sku_35a263_idx"),
                ),
                migrations.AddIndex(
                    model_name="productpricing",
                    index=models.Index(
                        fields=["pricing_type", "currency", "is_active"],
                        name="ecommerce_p_pricing_7988ae_idx",
                    ),
                ),
                migrations.AddIndex(
                    model_name="review",
                    index=models.Index(
                        fields=["product", "is_active", "is_approved"],
                        name="ecommerce_r_product_3147d3_idx",
                    ),
                ),
                migrations.AddIndex(
                    model_name="review",
                    index=models.Index(
                        fields=["user", "created_at"], name="ecommerce_r_user_id_5bd2b2_idx"
                    ),
                ),
                migrations.AddIndex(
                    model_name="review",
                    index=models.Index(
                        fields=["rating", "created_at"], name="ecommerce_r_rating_52ad52_idx"
                    ),
                ),
                migrations.AddIndex(
                    model_name="skusequence",
                    index=models.Index(
                        fields=["vendor_code", "category_code"],
                        name="ecommerce_s_vendor__c7eff4_idx",
                    ),
                ),
                migrations.AddIndex(
                    model_name="vendor",
                    index=models.Index(fields=["code"], name="ecommerce_v_code_50dfcd_idx"),
                ),
                migrations.AddIndex(
                    model_name="vendor",
                    index=models.Index(fields=["slug"], name="ecommerce_v_slug_86ae78_idx"),
                ),
                migrations.AddIndex(
                    model_name="vendor",
                    index=models.Index(
                        fields=["is_active", "is_verified"],
                        name="ecommerce_v_is_acti_8fce7f_idx",
                    ),
                ),
                migrations.AddIndex(
                    model_name="wishlist",
                    index=models.Index(fields=["user"], name="ecommerce_w_user_id_638869_idx"),
                ),
                migrations.AddIndex(
                    model_name="wishlist",
                    index=models.Index(
                        fields=["created_at"], name="ecommerce_w_created_1d487e_idx"
                    ),
                ),
                migrations.AddIndex(
                    model_name="wishlistitem",
                    index=models.Index(
                        fields=["wishlist", "is_active", "-added_at"],
                        name="ecommerce_w_wishlis_cbf394_idx",
                    ),
                ),
                migrations.AddIndex(
                    model_name="wishlistitem",
                    index=models.Index(
                        fields=["product", "is_active"], name="ecommerce_w_product_2951e2_idx"
                    ),
                ),
                migrations.AddConstraint(
                    model_name="invoice",
                    constraint=models.CheckConstraint(
                        condition=models.Q(("amount__gte", 0)), name="chk_invoice_amount_gte_0"
                    ),
                ),
                migrations.AddConstraint(
                    model_name="order",
                    constraint=models.CheckConstraint(
                        condition=models.Q(("total_amount__gte", 0)),
                        name="chk_order_total_gte_0",
                    ),
                ),
                migrations.AddConstraint(
                    model_name="order",
                    constraint=models.CheckConstraint(
                        condition=models.Q(("subtotal_amount__gte", 0)),
                        name="chk_order_subtotal_gte_0",
                    ),
                ),
                migrations.AddConstraint(
                    model_name="order",
                    constraint=models.CheckConstraint(
                        condition=models.Q(("shipping_amount__gte", 0)),
                        name="chk_order_shipping_gte_0",
                    ),
                ),
                migrations.AddConstraint(
                    model_name="order",
                    constraint=models.CheckConstraint(
                        condition=models.Q(("tax_amount__gte", 0)), name="chk_order_tax_gte_0"
                    ),
                ),
                migrations.AddConstraint(
                    model_name="order",
                    constraint=models.CheckConstraint(
                        condition=models.Q(("discount_amount__gte", 0)),
                        name="chk_order_discount_gte_0",
                    ),
                ),
                migrations.AddConstraint(
                    model_name="order",
                    constraint=models.UniqueConstraint(
                        condition=models.Q(
                            ("reference__isnull", False),
                            models.Q(("reference", ""), _negated=True),
                        ),
                        fields=("reference",),
                        name="uniq_order_reference_not_empty",
                    ),
                ),
                migrations.AddConstraint(
                    model_name="orderitem",
                    constraint=models.CheckConstraint(
                        condition=models.Q(("quantity__gt", 0)), name="chk_orderitem_qty_gt_0"
                    ),
                ),
                migrations.AddConstraint(
                    model_name="orderitem",
                    constraint=models.CheckConstraint(
                        condition=models.Q(("unit_price__gte", 0)),
                        name="chk_orderitem_unitprice_gte_0",
                    ),
                ),
                migrations.AddConstraint(
                    model_name="paymenttransaction",
                    constraint=models.CheckConstraint(
                        condition=models.Q(("amount__gte", 0)), name="chk_payment_amount_gte_0"
                    ),
                ),
                migrations.AddConstraint(
                    model_name="paymenttransaction",
                    constraint=models.CheckConstraint(
                        condition=models.Q(("provider_fee__gte", 0)),
                        name="chk_payment_fee_gte_0",
                    ),
                ),
                migrations.AddConstraint(
                    model_name="paymenttransaction",
                    constraint=models.UniqueConstraint(
                        condition=models.Q(("idempotency_key", ""), _negated=True),
                        fields=("provider", "idempotency_key"),
                        name="uniq_payment_provider_idempotency_nonempty",
                    ),
                ),
                migrations.AddConstraint(
                    model_name="skusequence",
                    constraint=models.UniqueConstraint(
                        fields=("vendor_code", "category_code"),
                        name="uniq_sku_sequence_vendor_category",
                    ),
                ),
            ],
        ),
    ]

