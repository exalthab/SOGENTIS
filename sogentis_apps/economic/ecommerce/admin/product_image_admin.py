# economic/ecommerce/admin/product_image_admin.py
from __future__ import annotations

from collections import defaultdict

from django.contrib import admin, messages
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html

from economic.ecommerce.models import ProductImage


# ------------------------------------------------------------
# Actions (prod)
# ------------------------------------------------------------
@admin.action(description=_("Définir comme image principale (1 par produit)"))
def action_set_as_main(modeladmin, request, queryset):
    """
    Prod-safe: pour chaque produit, on garde 1 seule image principale.
    Si plusieurs images d'un même produit sont sélectionnées,
    on prend la plus récente (id max) comme "main".
    """
    qs = queryset.select_related("product").only("id", "product_id", "is_main", "sort_order")
    by_product: dict[int, list[ProductImage]] = defaultdict(list)
    for img in qs:
        if img.product_id:
            by_product[img.product_id].append(img)

    updated = 0
    with transaction.atomic():
        for product_id, images in by_product.items():
            # choisir 1 image "main" (ici id max = plus récente)
            chosen = max(images, key=lambda x: x.pk or 0)

            # 1) unset all mains for that product (idempotent)
            ProductImage.objects.filter(product_id=product_id, is_main=True).exclude(pk=chosen.pk).update(
                is_main=False,
                updated_at=models.functions.Now(),
            )

            # 2) set chosen main + sort_order=0
            ProductImage.objects.filter(pk=chosen.pk).update(
                is_main=True,
                sort_order=0,
                updated_at=models.functions.Now(),
            )
            updated += 1

    modeladmin.message_user(
        request,
        _("Image principale définie pour %(n)s produit(s).") % {"n": updated},
        level=messages.SUCCESS,
    )


@admin.action(description=_("Retirer le statut principal (is_main=False)"))
def action_unset_main(modeladmin, request, queryset):
    n = queryset.filter(is_main=True).update(is_main=False, updated_at=models.functions.Now())
    modeladmin.message_user(
        request,
        _("%(n)s image(s) ne sont plus principales.") % {"n": n},
        level=messages.SUCCESS,
    )


@admin.action(description=_("Auto-remplir alt_text (si vide)"))
def action_fill_alt_text(modeladmin, request, queryset):
    """
    Remplit alt_text uniquement quand vide, avec le nom produit i18n.
    (Le modèle le fait déjà, mais utile en rattrapage legacy.)
    """
    qs = queryset.select_related("product")
    done = 0
    for img in qs:
        if img.alt_text:
            continue
        try:
            p = img.product
            name = p.safe_translation_getter("name", any_language=True) or ""
            if name:
                ProductImage.objects.filter(pk=img.pk).update(
                    alt_text=name[:255],
                    updated_at=models.functions.Now(),
                )
                done += 1
        except Exception:
            continue

    modeladmin.message_user(
        request,
        _("%(n)s image(s) mises à jour (alt_text).") % {"n": done},
        level=messages.SUCCESS,
    )


@admin.action(description=_("Normaliser sort_order (0..n) par produit"))
def action_normalize_sort_order(modeladmin, request, queryset):
    """
    Recalcule sort_order pour les produits concernés:
    - main image en 0 si présente
    - puis sort_order croissant par id
    """
    product_ids = list(queryset.values_list("product_id", flat=True).distinct())
    product_ids = [pid for pid in product_ids if pid]

    if not product_ids:
        modeladmin.message_user(request, _("Aucun produit détecté."), level=messages.INFO)
        return

    touched = 0
    with transaction.atomic():
        for pid in product_ids:
            imgs = list(
                ProductImage.objects.filter(product_id=pid).only("id", "is_main", "sort_order").order_by(
                    "-is_main", "sort_order", "id"
                )
            )
            if not imgs:
                continue

            # main -> 0 ; autres -> 1..n
            next_order = 0
            for img in imgs:
                desired = 0 if img.is_main else next_order
                if img.is_main:
                    desired = 0
                else:
                    next_order += 1

                if img.sort_order != desired:
                    ProductImage.objects.filter(pk=img.pk).update(
                        sort_order=desired,
                        updated_at=models.functions.Now(),
                    )

            touched += 1

    modeladmin.message_user(
        request,
        _("Ordre normalisé pour %(n)s produit(s).") % {"n": touched},
        level=messages.SUCCESS,
    )


# ------------------------------------------------------------
# Admin
# ------------------------------------------------------------
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    save_on_top = True
    actions_on_top = True
    actions_on_bottom = True
    list_per_page = 50
    date_hierarchy = "created_at"

    ordering = ("-is_main", "sort_order", "id")

    list_display = (
        "id",
        "preview",
        "product",
        "product_sku",
        "product_name_i18n",
        "is_main",
        "sort_order",
        "created_at",
        "updated_at",
    )
    list_display_links = ("id", "preview", "product")
    list_filter = (
        "is_main",
        ("created_at", admin.DateFieldListFilter),
        ("updated_at", admin.DateFieldListFilter),
        "product__category",
        "product__vendor",
    )
    search_fields = (
        "alt_text",
        "product__sku",
        "product__translations__name",
        "product__translations__slug",
    )

    autocomplete_fields = ("product",)
    readonly_fields = ("preview_large", "created_at", "updated_at")

    # ⚠️ éviter list_editable sur is_main (risque contrainte 1 main / produit)
    list_editable = ("sort_order",)

    fieldsets = (
        (_("Produit"), {"fields": ("product",)}),
        (_("Image"), {"fields": ("image", "preview_large", "alt_text")}),
        (_("Affichage"), {"fields": ("is_main", "sort_order")}),
        (_("Système"), {"fields": ("created_at", "updated_at")}),
    )

    actions = (
        action_set_as_main,
        action_unset_main,
        action_fill_alt_text,
        action_normalize_sort_order,
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("product", "product__category", "product__vendor")
        )

    # -------------------------
    # Helpers affichage
    # -------------------------
    @admin.display(description=_("Aperçu"))
    def preview(self, obj: ProductImage):
        if not obj.image:
            return "—"
        try:
            return format_html(
                '<img src="{}" style="height:42px;width:42px;object-fit:cover;border-radius:8px;border:1px solid rgba(0,0,0,.1)"/>',
                obj.image.url,
            )
        except Exception:
            return "—"

    @admin.display(description=_("Aperçu (grand)"))
    def preview_large(self, obj: ProductImage):
        if not obj.image:
            return "—"
        try:
            return format_html(
                '<img src="{}" style="max-height:260px;max-width:100%;object-fit:contain;border-radius:12px;border:1px solid rgba(0,0,0,.1)"/>',
                obj.image.url,
            )
        except Exception:
            return "—"

    @admin.display(description=_("SKU"))
    def product_sku(self, obj: ProductImage) -> str:
        p = getattr(obj, "product", None)
        return getattr(p, "sku", "") or "—"

    @admin.display(description=_("Nom (i18n)"))
    def product_name_i18n(self, obj: ProductImage) -> str:
        p = getattr(obj, "product", None)
        if not p:
            return "—"
        try:
            return p.safe_translation_getter("name", any_language=True) or "—"
        except Exception:
            return str(p)

    # -------------------------
    # Sécurité prod: si is_main True => sort_order 0
    # -------------------------
    def save_model(self, request, obj, form, change):
        if getattr(obj, "is_main", False):
            obj.sort_order = 0
        super().save_model(request, obj, form, change)
