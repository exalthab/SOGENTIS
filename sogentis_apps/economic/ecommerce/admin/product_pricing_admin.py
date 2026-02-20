# economic/ecommerce/admin/product_pricing_admin.py
from __future__ import annotations

from decimal import Decimal

from django.contrib import admin, messages
from django.db import models, transaction
from django.db.models import Count, Min
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now as tz_now

from economic.ecommerce.models import BulkPrice, ProductPricing


# ------------------------------------------------------------
# Actions (prod)
# ------------------------------------------------------------
@admin.action(description=_("Synchroniser Product.price = prix effectif (promo/base) + old_price (sélection)"))
def action_sync_product_effective_price(modeladmin, request, queryset):
    """
    ✅ Recalcule Product.price = pricing.effective_unit_price
    ✅ old_price = base_price si promo active, sinon NULL
    """
    updated = 0
    with transaction.atomic():
        qs = queryset.select_related("product").select_for_update()
        for pr in qs:
            try:
                Product = pr.product.__class__

                eff = pr.effective_unit_price
                updates = {"price": eff}

                if pr.has_promo():
                    updates["old_price"] = Decimal(pr.base_price).quantize(Decimal("0.01"))
                else:
                    updates["old_price"] = None

                Product.objects.filter(pk=pr.product_id).update(**updates)
                updated += 1
            except Exception:
                continue

    modeladmin.message_user(
        request,
        _("%(n)s produit(s) synchronisé(s).") % {"n": updated},
        messages.SUCCESS,
    )


@admin.action(description=_("Synchroniser Product.price = base_price (sélection)"))
def action_sync_product_price_from_base(modeladmin, request, queryset):
    updated = 0
    with transaction.atomic():
        qs = queryset.select_related("product").select_for_update()
        for pr in qs:
            try:
                Product = pr.product.__class__
                n = Product.objects.filter(pk=pr.product_id).exclude(price=pr.base_price).update(
                    price=pr.base_price
                )
                updated += int(n or 0)
            except Exception:
                continue
    modeladmin.message_user(request, _("%(n)s produit(s) synchronisé(s).") % {"n": updated}, messages.SUCCESS)


@admin.action(description=_("Activer la tarification (is_active=True)"))
def action_activate_pricing(modeladmin, request, queryset):
    n = queryset.update(is_active=True, updated_at=models.functions.Now())
    modeladmin.message_user(request, _("%(n)s tarification(s) activée(s).") % {"n": n}, messages.SUCCESS)


@admin.action(description=_("Désactiver la tarification (is_active=False)"))
def action_deactivate_pricing(modeladmin, request, queryset):
    n = queryset.update(is_active=False, updated_at=models.functions.Now())
    modeladmin.message_user(request, _("%(n)s tarification(s) désactivée(s).") % {"n": n}, messages.SUCCESS)


@admin.action(description=_("Nettoyer promo expirée (promo_* à NULL)"))
def action_clear_expired_promo(modeladmin, request, queryset):
    now_ts = tz_now()
    n = 0
    with transaction.atomic():
        qs = queryset.select_for_update()
        for pr in qs:
            try:
                if pr.promo_end and pr.promo_end < now_ts:
                    ProductPricing.objects.filter(pk=pr.pk).update(
                        promo_price=None,
                        promo_start=None,
                        promo_end=None,
                        updated_at=models.functions.Now(),
                    )
                    n += 1
            except Exception:
                continue
    modeladmin.message_user(request, _("%(n)s promo(s) expirée(s) nettoyée(s).") % {"n": n}, messages.SUCCESS)


@admin.action(description=_("Touch updated_at (marquer comme modifié)"))
def action_touch_pricing(modeladmin, request, queryset):
    n = queryset.update(updated_at=models.functions.Now())
    modeladmin.message_user(request, _("%(n)s tarification(s) mise(s) à jour (updated_at).") % {"n": n}, messages.SUCCESS)


# ------------------------------------------------------------
# Inlines (BulkPrice)
# ------------------------------------------------------------
class BulkPriceInline(admin.TabularInline):
    model = BulkPrice
    extra = 0
    show_change_link = True

    fields = ("min_quantity", "unit_price", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("min_quantity",)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("pricing", "pricing__product")


# ------------------------------------------------------------
# ProductPricingAdmin (production)
# ------------------------------------------------------------
@admin.register(ProductPricing)
class ProductPricingAdmin(admin.ModelAdmin):
    save_on_top = True
    actions_on_top = True
    actions_on_bottom = True
    list_per_page = 50

    inlines = [BulkPriceInline]

    autocomplete_fields = ("product",)

    list_display = (
        "id",
        "product",
        "product_sku",
        "pricing_type",
        "is_active",
        "base_price",
        "promo_price",
        "currency",
        "promo_window",
        "has_promo_now",
        "effective_unit_price_display",
        "bulk_tiers",
        "best_b2b_price_hint",
        "updated_at",
        "created_at",
    )
    list_display_links = ("id", "product")
    ordering = ("-updated_at", "-created_at", "id")

    list_filter = (
        "pricing_type",
        "is_active",
        ("currency", admin.AllValuesFieldListFilter),
        ("created_at", admin.DateFieldListFilter),
        ("updated_at", admin.DateFieldListFilter),
        ("promo_start", admin.DateFieldListFilter),
        ("promo_end", admin.DateFieldListFilter),
    )

    search_fields = (
        "product__sku",
        "product__translations__name",
    )

    list_editable = ("is_active", "base_price", "promo_price")

    readonly_fields = (
        "created_at",
        "updated_at",
        "has_promo_now",
        "effective_unit_price_display",
        "bulk_tiers",
        "best_b2b_price_hint",
    )

    fieldsets = (
        (_("Produit"), {"fields": ("product",)}),
        (_("Statut & type"), {"fields": ("pricing_type", "is_active")}),
        (_("Prix"), {"fields": (("base_price", "currency"), "promo_price", ("promo_start", "promo_end"))}),
        (
            _("Calculs (lecture seule)"),
            {"fields": ("has_promo_now", "effective_unit_price_display", "bulk_tiers", "best_b2b_price_hint")},
        ),
        (_("Système"), {"fields": ("created_at", "updated_at")}),
    )

    actions = (
        action_sync_product_effective_price,
        action_sync_product_price_from_base,
        action_activate_pricing,
        action_deactivate_pricing,
        action_clear_expired_promo,
        action_touch_pricing,
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("product")
            .annotate(
                _bulk_count=Count("bulk_prices", distinct=True),
                _bulk_min=Min("bulk_prices__unit_price"),
            )
        )

    @admin.display(description=_("SKU"))
    def product_sku(self, obj: ProductPricing) -> str:
        p = getattr(obj, "product", None)
        return (getattr(p, "sku", "") or "—")

    @admin.display(description=_("Fenêtre promo"))
    def promo_window(self, obj: ProductPricing) -> str:
        s = getattr(obj, "promo_start", None)
        e = getattr(obj, "promo_end", None)
        if not s and not e:
            return "—"
        if s and e:
            return f"{s:%Y-%m-%d %H:%M} → {e:%Y-%m-%d %H:%M}"
        if s:
            return f"{s:%Y-%m-%d %H:%M} → …"
        return f"… → {e:%Y-%m-%d %H:%M}"

    @admin.display(description=_("Promo active"), boolean=True)
    def has_promo_now(self, obj: ProductPricing) -> bool:
        try:
            return bool(obj.has_promo())
        except Exception:
            return False

    @admin.display(description=_("Prix effectif"))
    def effective_unit_price_display(self, obj: ProductPricing):
        try:
            return obj.effective_unit_price
        except Exception:
            try:
                return Decimal(obj.base_price).quantize(Decimal("0.01"))
            except Exception:
                return Decimal("0.00")

    @admin.display(description=_("Paliers"), ordering="_bulk_count")
    def bulk_tiers(self, obj: ProductPricing) -> int:
        return int(getattr(obj, "_bulk_count", 0) or 0)

    @admin.display(description=_("Meilleur prix (min palier)"), ordering="_bulk_min")
    def best_b2b_price_hint(self, obj: ProductPricing):
        v = getattr(obj, "_bulk_min", None)
        if v is None:
            return "—"
        try:
            return Decimal(v).quantize(Decimal("0.01"))
        except Exception:
            return v


# ------------------------------------------------------------
# BulkPriceAdmin (prod) — utile pour exploitation / audit
# ------------------------------------------------------------
@admin.register(BulkPrice)
class BulkPriceAdmin(admin.ModelAdmin):
    save_on_top = True
    actions_on_top = True
    actions_on_bottom = True
    list_per_page = 50

    autocomplete_fields = ("pricing",)

    list_display = (
        "id",
        "pricing",
        "product",
        "pricing_type",
        "min_quantity",
        "unit_price",
        "created_at",
        "updated_at",
    )
    ordering = ("pricing__id", "min_quantity", "id")

    list_filter = (
        "pricing__pricing_type",
        ("created_at", admin.DateFieldListFilter),
        ("updated_at", admin.DateFieldListFilter),
    )

    search_fields = (
        "pricing__product__sku",
        "pricing__product__translations__name",
    )

    readonly_fields = ("created_at", "updated_at")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("pricing", "pricing__product")

    @admin.display(description=_("Produit"))
    def product(self, obj: BulkPrice):
        return getattr(getattr(obj, "pricing", None), "product", None)

    @admin.display(description=_("Type"))
    def pricing_type(self, obj: BulkPrice):
        return getattr(getattr(obj, "pricing", None), "pricing_type", None)






# # economic/ecommerce/admin/product_pricing_admin.py
# from __future__ import annotations

# from decimal import Decimal

# from django.contrib import admin, messages
# from django.db import models, transaction
# from django.db.models import Count, Min
# from django.utils.translation import gettext_lazy as _

# from economic.ecommerce.models import BulkPrice, ProductPricing


# # ------------------------------------------------------------
# # Actions (prod)
# # ------------------------------------------------------------
# @admin.action(description=_("Synchroniser Product.price = base_price (sélection)"))
# def action_sync_product_price_from_base(modeladmin, request, queryset):
#     updated = 0
#     with transaction.atomic():
#         qs = queryset.select_related("product").select_for_update()
#         for pr in qs:
#             try:
#                 Product = pr.product.__class__
#                 n = Product.objects.filter(pk=pr.product_id).exclude(price=pr.base_price).update(
#                     price=pr.base_price
#                 )
#                 updated += int(n or 0)
#             except Exception:
#                 continue
#     modeladmin.message_user(request, _("%(n)s produit(s) synchronisé(s).") % {"n": updated}, messages.SUCCESS)


# @admin.action(description=_("Activer la tarification (is_active=True)"))
# def action_activate_pricing(modeladmin, request, queryset):
#     n = queryset.update(is_active=True, updated_at=models.functions.Now())
#     modeladmin.message_user(request, _("%(n)s tarification(s) activée(s).") % {"n": n}, messages.SUCCESS)


# @admin.action(description=_("Désactiver la tarification (is_active=False)"))
# def action_deactivate_pricing(modeladmin, request, queryset):
#     n = queryset.update(is_active=False, updated_at=models.functions.Now())
#     modeladmin.message_user(request, _("%(n)s tarification(s) désactivée(s).") % {"n": n}, messages.SUCCESS)


# @admin.action(description=_("Nettoyer promo expirée (promo_* à NULL)"))
# def action_clear_expired_promo(modeladmin, request, queryset):
#     from django.utils.timezone import now as tz_now

#     now_ts = tz_now()
#     n = 0
#     with transaction.atomic():
#         qs = queryset.select_for_update()
#         for pr in qs:
#             try:
#                 if pr.promo_end and pr.promo_end < now_ts:
#                     ProductPricing.objects.filter(pk=pr.pk).update(
#                         promo_price=None,
#                         promo_start=None,
#                         promo_end=None,
#                         updated_at=models.functions.Now(),
#                     )
#                     n += 1
#             except Exception:
#                 continue
#     modeladmin.message_user(request, _("%(n)s promo(s) expirée(s) nettoyée(s).") % {"n": n}, messages.SUCCESS)


# @admin.action(description=_("Touch updated_at (marquer comme modifié)"))
# def action_touch_pricing(modeladmin, request, queryset):
#     n = queryset.update(updated_at=models.functions.Now())
#     modeladmin.message_user(request, _("%(n)s tarification(s) mise(s) à jour (updated_at).") % {"n": n}, messages.SUCCESS)


# # ------------------------------------------------------------
# # Inlines (BulkPrice)
# # ------------------------------------------------------------
# class BulkPriceInline(admin.TabularInline):
#     model = BulkPrice
#     extra = 0
#     show_change_link = True

#     fields = ("min_quantity", "unit_price", "created_at", "updated_at")
#     readonly_fields = ("created_at", "updated_at")
#     ordering = ("min_quantity",)

#     def get_queryset(self, request):
#         return super().get_queryset(request).select_related("pricing", "pricing__product")


# # ------------------------------------------------------------
# # ProductPricingAdmin (production)
# # ------------------------------------------------------------
# @admin.register(ProductPricing)
# class ProductPricingAdmin(admin.ModelAdmin):
#     save_on_top = True
#     actions_on_top = True
#     actions_on_bottom = True
#     list_per_page = 50

#     inlines = [BulkPriceInline]

#     autocomplete_fields = ("product",)

#     list_display = (
#         "id",
#         "product",
#         "product_sku",
#         "pricing_type",
#         "is_active",
#         "base_price",
#         "promo_price",
#         "currency",
#         "promo_window",
#         "has_promo_now",
#         "effective_unit_price_display",
#         "bulk_tiers",
#         "best_b2b_price_hint",
#         "updated_at",
#         "created_at",
#     )
#     list_display_links = ("id", "product")
#     ordering = ("-updated_at", "-created_at", "id")

#     list_filter = (
#         "pricing_type",
#         "is_active",
#         ("currency", admin.AllValuesFieldListFilter),
#         ("created_at", admin.DateFieldListFilter),
#         ("updated_at", admin.DateFieldListFilter),
#         ("promo_start", admin.DateFieldListFilter),
#         ("promo_end", admin.DateFieldListFilter),
#     )

#     search_fields = (
#         "product__sku",
#         "product__translations__name",
#     )

#     list_editable = ("is_active", "base_price", "promo_price")

#     readonly_fields = (
#         "created_at",
#         "updated_at",
#         "has_promo_now",
#         "effective_unit_price_display",
#         "bulk_tiers",
#         "best_b2b_price_hint",
#     )

#     fieldsets = (
#         (_("Produit"), {"fields": ("product",)}),
#         (_("Statut & type"), {"fields": ("pricing_type", "is_active")}),
#         (_("Prix"), {"fields": (("base_price", "currency"), "promo_price", ("promo_start", "promo_end"))}),
#         (_("Calculs (lecture seule)"), {"fields": ("has_promo_now", "effective_unit_price_display", "bulk_tiers", "best_b2b_price_hint")}),
#         (_("Système"), {"fields": ("created_at", "updated_at")}),
#     )

#     actions = (
#         action_sync_product_price_from_base,
#         action_activate_pricing,
#         action_deactivate_pricing,
#         action_clear_expired_promo,
#         action_touch_pricing,
#     )

#     def get_queryset(self, request):
#         return (
#             super()
#             .get_queryset(request)
#             .select_related("product")
#             .annotate(
#                 _bulk_count=Count("bulk_prices", distinct=True),
#                 _bulk_min=Min("bulk_prices__unit_price"),
#             )
#         )

#     @admin.display(description=_("SKU"))
#     def product_sku(self, obj: ProductPricing) -> str:
#         p = getattr(obj, "product", None)
#         return (getattr(p, "sku", "") or "—")

#     @admin.display(description=_("Fenêtre promo"))
#     def promo_window(self, obj: ProductPricing) -> str:
#         s = getattr(obj, "promo_start", None)
#         e = getattr(obj, "promo_end", None)
#         if not s and not e:
#             return "—"
#         if s and e:
#             return f"{s:%Y-%m-%d %H:%M} → {e:%Y-%m-%d %H:%M}"
#         if s:
#             return f"{s:%Y-%m-%d %H:%M} → …"
#         return f"… → {e:%Y-%m-%d %H:%M}"

#     @admin.display(description=_("Promo active"), boolean=True)
#     def has_promo_now(self, obj: ProductPricing) -> bool:
#         try:
#             return bool(obj.has_promo())
#         except Exception:
#             return False

#     @admin.display(description=_("Prix effectif"))
#     def effective_unit_price_display(self, obj: ProductPricing):
#         try:
#             return obj.effective_unit_price
#         except Exception:
#             try:
#                 return Decimal(obj.base_price).quantize(Decimal("0.01"))
#             except Exception:
#                 return Decimal("0.00")

#     @admin.display(description=_("Paliers"), ordering="_bulk_count")
#     def bulk_tiers(self, obj: ProductPricing) -> int:
#         return int(getattr(obj, "_bulk_count", 0) or 0)

#     @admin.display(description=_("Meilleur prix (min palier)"), ordering="_bulk_min")
#     def best_b2b_price_hint(self, obj: ProductPricing):
#         v = getattr(obj, "_bulk_min", None)
#         if v is None:
#             return "—"
#         try:
#             return Decimal(v).quantize(Decimal("0.01"))
#         except Exception:
#             return v


# # ------------------------------------------------------------
# # BulkPriceAdmin (prod) — utile pour exploitation / audit
# # ------------------------------------------------------------
# @admin.register(BulkPrice)
# class BulkPriceAdmin(admin.ModelAdmin):
#     save_on_top = True
#     actions_on_top = True
#     actions_on_bottom = True
#     list_per_page = 50

#     autocomplete_fields = ("pricing",)

#     list_display = (
#         "id",
#         "pricing",
#         "product",
#         "pricing_type",
#         "min_quantity",
#         "unit_price",
#         "created_at",
#         "updated_at",
#     )
#     ordering = ("pricing__id", "min_quantity", "id")

#     list_filter = (
#         "pricing__pricing_type",
#         ("created_at", admin.DateFieldListFilter),
#         ("updated_at", admin.DateFieldListFilter),
#     )

#     search_fields = (
#         "pricing__product__sku",
#         "pricing__product__translations__name",
#     )

#     readonly_fields = ("created_at", "updated_at")

#     def get_queryset(self, request):
#         return super().get_queryset(request).select_related("pricing", "pricing__product")

#     @admin.display(description=_("Produit"))
#     def product(self, obj: BulkPrice):
#         return getattr(getattr(obj, "pricing", None), "product", None)

#     @admin.display(description=_("Type"))
#     def pricing_type(self, obj: BulkPrice):
#         return getattr(getattr(obj, "pricing", None), "pricing_type", None)
