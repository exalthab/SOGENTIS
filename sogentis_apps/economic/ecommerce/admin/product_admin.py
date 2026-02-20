# economic/ecommerce/admin/product_admin.py
from __future__ import annotations

from django.contrib import admin, messages
from django.core.exceptions import FieldDoesNotExist
from django.db.models import Count
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from parler.admin import TranslatableAdmin

from economic.ecommerce.models import Product, ProductImage

# ------------------------------------------------------------
# Helpers: admin-safe (adaptation aux modèles optionnels)
# ------------------------------------------------------------
def _model_field_names(model) -> set[str]:
    try:
        return {f.name for f in model._meta.fields}
    except Exception:
        return set()


def _pick_fields(model, candidates: list[str]) -> list[str]:
    available = _model_field_names(model)
    return [f for f in candidates if f in available]


def _has_field(model, field_name: str) -> bool:
    try:
        model._meta.get_field(field_name)
        return True
    except FieldDoesNotExist:
        return False


# ✅ Optionnel : ProductPricing/BulkPrice (import direct module => pas dépendant de models/__init__.py)
try:
    from economic.ecommerce.models.product_pricing import ProductPricing  # type: ignore
except Exception:
    ProductPricing = None  # type: ignore

# BulkPrice existe peut-être, mais IMPORTANT: pas d'inline sous Product (FK vers ProductPricing, pas Product)
try:
    from economic.ecommerce.models.product_pricing import BulkPrice  # type: ignore
except Exception:
    BulkPrice = None  # type: ignore


# ------------------------------------------------------------
# Inlines
# ------------------------------------------------------------
_IMAGE_FIELDS = _pick_fields(
    ProductImage,
    ["image", "alt_text", "is_main", "is_primary", "sort_order", "order"],
)

# order fields preference
_IMAGE_ORDERING: list[str] = []
if "is_main" in _IMAGE_FIELDS:
    _IMAGE_ORDERING.append("-is_main")
elif "is_primary" in _IMAGE_FIELDS:
    _IMAGE_ORDERING.append("-is_primary")
if "sort_order" in _IMAGE_FIELDS:
    _IMAGE_ORDERING.append("sort_order")
elif "order" in _IMAGE_FIELDS:
    _IMAGE_ORDERING.append("order")
_IMAGE_ORDERING += ["id"]


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0
    fields = tuple(_IMAGE_FIELDS) if _IMAGE_FIELDS else ("image",)
    ordering = tuple(_IMAGE_ORDERING)


def _build_pricing_inlines():
    """
    ✅ PRODUCTION SAFE
    - Inline OK: ProductPricing (OneToOne vers Product)
    - ❌ PAS d'inline BulkPrice ici (BulkPrice -> FK ProductPricing, sinon admin.E202)
    """
    inlines = []

    if ProductPricing is None:
        return inlines

    pricing_fields = _pick_fields(
        ProductPricing,
        [
            "pricing_type",
            "is_active",
            "base_price",
            "promo_price",
            "promo_start",
            "promo_end",
            "currency",
            "created_at",
            "updated_at",
        ],
    )

    readonly = [f for f in ("created_at", "updated_at") if f in pricing_fields]
    # computed readonly
    readonly += ["effective_unit_price_display", "bulk_tiers_display"]

    # inject computed after currency if possible
    insert_after = "currency" if "currency" in pricing_fields else (pricing_fields[-1] if pricing_fields else None)

    computed = ["effective_unit_price_display", "bulk_tiers_display"]
    fields_order: list[str] = []
    for f in (pricing_fields or ["pricing_type", "is_active"]):
        fields_order.append(f)
        if insert_after and f == insert_after:
            fields_order.extend(computed)

    if not fields_order:
        fields_order = ["pricing_type", "is_active"] + computed

    class ProductPricingInline(admin.StackedInline):  # type: ignore
        model = ProductPricing
        extra = 0
        can_delete = True
        show_change_link = True  # ✅ ouvre la fiche ProductPricing (où BulkPriceInline existe)
        fields = tuple(fields_order)
        readonly_fields = tuple(readonly)

        @admin.display(description=_("Prix effectif"))
        def effective_unit_price_display(self, obj):
            if not obj:
                return "—"
            try:
                return obj.effective_unit_price
            except Exception:
                return "—"

        @admin.display(description=_("Paliers (BulkPrice)"))
        def bulk_tiers_display(self, obj) -> str:
            if not obj:
                return "—"
            mgr = getattr(obj, "bulk_prices", None)
            if mgr is None:
                return "—"
            try:
                return str(mgr.count())
            except Exception:
                return "—"

    inlines.append(ProductPricingInline)
    return inlines


# ------------------------------------------------------------
# Filters
# ------------------------------------------------------------
class SkuPresenceFilter(admin.SimpleListFilter):
    title = _("SKU")
    parameter_name = "sku_presence"

    def lookups(self, request, model_admin):
        return (
            ("with", _("Avec SKU")),
            ("without", _("Sans SKU")),
        )

    def queryset(self, request, queryset):
        v = self.value()
        if v == "with":
            return queryset.exclude(sku__isnull=True).exclude(sku__exact="")
        if v == "without":
            return queryset.filter(sku__isnull=True) | queryset.filter(sku__exact="")
        return queryset


# ------------------------------------------------------------
# Actions (prod-safe)
# ------------------------------------------------------------
@admin.action(description=_("Activer les produits sélectionnés"))
def action_activate_products(modeladmin, request, queryset):
    updated = queryset.update(is_active=True)
    modeladmin.message_user(
        request,
        _("%(n)s produit(s) activé(s).") % {"n": updated},
        level=messages.SUCCESS,
    )


@admin.action(description=_("Désactiver les produits (retire aussi la vedette)"))
def action_deactivate_products(modeladmin, request, queryset):
    updated = queryset.update(is_active=False, is_featured=False)
    modeladmin.message_user(
        request,
        _("%(n)s produit(s) désactivé(s) (vedette retirée si nécessaire).") % {"n": updated},
        level=messages.SUCCESS,
    )


@admin.action(description=_("Mettre en vedette (ignore les inactifs)"))
def action_feature_products(modeladmin, request, queryset):
    updated = 0
    skipped = 0
    for p in queryset.only("id", "is_active", "is_featured"):
        if not p.is_active:
            skipped += 1
            continue
        if p.is_featured:
            continue
        p.is_featured = True
        p.save(update_fields=["is_featured", "updated_at"])
        updated += 1

    if updated:
        modeladmin.message_user(
            request,
            _("%(n)s produit(s) mis en vedette.") % {"n": updated},
            level=messages.SUCCESS,
        )
    if skipped:
        modeladmin.message_user(
            request,
            _("%(n)s produit(s) ignoré(s) (inactif).") % {"n": skipped},
            level=messages.WARNING,
        )


@admin.action(description=_("Retirer la vedette (featured)"))
def action_unfeature_products(modeladmin, request, queryset):
    updated = queryset.update(is_featured=False)
    modeladmin.message_user(
        request,
        _("%(n)s produit(s) retiré(s) de la vedette.") % {"n": updated},
        level=messages.SUCCESS,
    )


@admin.action(description=_("Marquer comme Nouveau"))
def action_mark_new(modeladmin, request, queryset):
    updated = queryset.update(is_new=True)
    modeladmin.message_user(
        request,
        _("%(n)s produit(s) marqué(s) comme Nouveau.") % {"n": updated},
        level=messages.SUCCESS,
    )


@admin.action(description=_("Retirer le statut Nouveau"))
def action_unmark_new(modeladmin, request, queryset):
    updated = queryset.update(is_new=False)
    modeladmin.message_user(
        request,
        _("%(n)s produit(s) mis à jour.") % {"n": updated},
        level=messages.SUCCESS,
    )


@admin.action(description=_("Générer un SKU manquant (si possible)"))
def action_generate_missing_sku(modeladmin, request, queryset):
    updated = 0
    skipped = 0

    qs = queryset.select_related("vendor", "category").only("id", "sku", "vendor__code", "category__code")

    for p in qs:
        if p.sku and str(p.sku).strip():
            continue
        try:
            p.save()  # déclenche auto-génération SKU dans save()
            updated += 1
        except Exception:
            skipped += 1

    if updated:
        modeladmin.message_user(
            request,
            _("%(n)s SKU généré(s).") % {"n": updated},
            level=messages.SUCCESS,
        )
    if skipped:
        modeladmin.message_user(
            request,
            _("%(n)s produit(s) ignoré(s) (vendor/catcode manquant ou erreur).") % {"n": skipped},
            level=messages.WARNING,
        )


@admin.action(description=_("Régénérer slugs + SEO (traductions Parler)"))
def action_rebuild_seo(modeladmin, request, queryset):
    updated = 0
    for p in queryset.only("id"):
        try:
            p._ensure_translation_slugs_and_seo()
            updated += 1
        except Exception:
            pass
    modeladmin.message_user(
        request,
        _("%(n)s produit(s) traités (slugs/SEO).") % {"n": updated},
        level=messages.SUCCESS,
    )


# ------------------------------------------------------------
# Admin Product (aligné modèle Product)
# ------------------------------------------------------------
@admin.register(Product)
class ProductAdmin(TranslatableAdmin):
    inlines = [ProductImageInline] + _build_pricing_inlines()

    save_on_top = True
    actions_on_top = True
    actions_on_bottom = True
    list_per_page = 50
    date_hierarchy = "created_at"
    autocomplete_fields = ("category", "vendor")

    # ✅ inclure old_price si le champ existe (ton Product l'a)
    _price_fields = ("price", "old_price") if _has_field(Product, "old_price") else ("price",)

    list_display = (
        "id",
        "thumb",
        "name_i18n",
        "sku",
        "category",
        "category_code",
        "vendor",
        "vendor_code",
        "price",
        "stock",
        "track_stock",
        "is_new",
        "is_active",
        "is_featured",
        "purchasable_flag",
        "created_at",
    )
    list_display_links = ("id", "name_i18n")
    list_editable = ("price", "stock", "is_active", "is_featured", "is_new", "track_stock")
    ordering = ("-created_at", "id")

    list_filter = (
        "is_active",
        "is_featured",
        "is_new",
        "track_stock",
        SkuPresenceFilter,
        "category",
        "vendor",
        ("created_at", admin.DateFieldListFilter),
    )

    search_fields = (
        "sku",
        "category__code",
        "vendor__code",
        "vendor__company_name",
        "translations__name",
        "translations__slug",
    )

    readonly_fields = ("created_at", "updated_at", "thumb")

    fieldsets = (
        (_("Classification"), {"fields": ("category", "vendor", "is_active", "is_featured", "is_new")}),
        (_("Stock / Vente"), {"fields": ("track_stock", "stock")}),
        (_("Prix"), {"fields": _price_fields}),
        (_("SKU & Media"), {"fields": ("sku", "image", "thumb", "fiche_technique")}),
        (
            _("Traductions"),
            {"fields": ("name", "slug", "short_description", "description", "seo_title", "seo_description")},
        ),
        (_("Système"), {"fields": ("created_at", "updated_at")}),
    )

    actions = [
        action_activate_products,
        action_deactivate_products,
        action_feature_products,
        action_unfeature_products,
        action_mark_new,
        action_unmark_new,
        action_generate_missing_sku,
        action_rebuild_seo,
    ]

    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related("category", "vendor")
        # ✅ évite requêtes N+1 si le OneToOne pricing existe
        qs = qs.select_related("pricing") if _has_field(Product, "pricing") else qs
        return qs.annotate(_images_count=Count("images", distinct=True))

    @admin.display(description=_("Nom"))
    def name_i18n(self, obj: Product) -> str:
        return obj.safe_translation_getter("name", any_language=True) or "-"

    @admin.display(description=_("Code cat."))
    def category_code(self, obj: Product) -> str:
        c = getattr(obj.category, "code", None)
        return (c or "").strip().upper() or "—"

    @admin.display(description=_("Code vendeur"))
    def vendor_code(self, obj: Product) -> str:
        v = getattr(obj.vendor, "code", None) if obj.vendor_id else None
        return (v or "").strip().upper() or "—"

    @admin.display(description=_("Achat"), boolean=True)
    def purchasable_flag(self, obj: Product) -> bool:
        try:
            return bool(obj.purchasable)
        except Exception:
            return False

    @admin.display(description=_("Aperçu"))
    def thumb(self, obj: Product) -> str:
        url = None
        try:
            url = obj.main_image_url
        except Exception:
            url = None

        if not url:
            return "—"

        return format_html(
            '<img src="{}" style="height:38px;width:38px;object-fit:cover;border-radius:8px;border:1px solid rgba(0,0,0,.12);" />',
            url,
        )







# # economic/ecommerce/admin/product_admin.py
# from __future__ import annotations

# from django.contrib import admin, messages
# from django.db.models import Count
# from django.utils.translation import gettext_lazy as _
# from django.utils.html import format_html
# from parler.admin import TranslatableAdmin

# from economic.ecommerce.models import Product, ProductImage

# # ------------------------------------------------------------
# # Helpers: admin-safe (adaptation aux modèles optionnels)
# # ------------------------------------------------------------
# def _model_field_names(model) -> set[str]:
#     try:
#         return {f.name for f in model._meta.fields}
#     except Exception:
#         return set()


# def _pick_fields(model, candidates: list[str]) -> list[str]:
#     available = _model_field_names(model)
#     return [f for f in candidates if f in available]


# # ✅ Optionnel : ProductPricing/BulkPrice (import direct module => pas dépendant de models/__init__.py)
# try:
#     from economic.ecommerce.models.product_pricing import ProductPricing  # type: ignore
# except Exception:
#     ProductPricing = None  # type: ignore

# # BulkPrice existe peut-être, mais IMPORTANT: pas d'inline sous Product (FK vers ProductPricing, pas Product)
# try:
#     from economic.ecommerce.models.product_pricing import BulkPrice  # type: ignore
# except Exception:
#     BulkPrice = None  # type: ignore


# # ------------------------------------------------------------
# # Inlines
# # ------------------------------------------------------------
# _IMAGE_FIELDS = _pick_fields(
#     ProductImage,
#     ["image", "alt_text", "is_main", "is_primary", "sort_order", "order"],
# )

# # order fields preference
# _IMAGE_ORDERING: list[str] = []
# if "is_main" in _IMAGE_FIELDS:
#     _IMAGE_ORDERING.append("-is_main")
# elif "is_primary" in _IMAGE_FIELDS:
#     _IMAGE_ORDERING.append("-is_primary")
# if "sort_order" in _IMAGE_FIELDS:
#     _IMAGE_ORDERING.append("sort_order")
# elif "order" in _IMAGE_FIELDS:
#     _IMAGE_ORDERING.append("order")
# _IMAGE_ORDERING += ["id"]


# class ProductImageInline(admin.TabularInline):
#     model = ProductImage
#     extra = 0
#     fields = tuple(_IMAGE_FIELDS) if _IMAGE_FIELDS else ("image",)
#     ordering = tuple(_IMAGE_ORDERING)


# def _build_pricing_inlines():
#     """
#     ✅ PRODUCTION SAFE
#     - Inline OK: ProductPricing (OneToOne vers Product)
#     - ❌ PAS d'inline BulkPrice ici (BulkPrice -> FK ProductPricing, sinon admin.E202)
#     """
#     inlines = []

#     if ProductPricing is None:
#         return inlines

#     pricing_fields = _pick_fields(
#         ProductPricing,
#         [
#             "pricing_type",
#             "is_active",
#             "base_price",
#             "promo_price",
#             "promo_start",
#             "promo_end",
#             "currency",
#             "created_at",
#             "updated_at",
#         ],
#     )

#     readonly = [f for f in ("created_at", "updated_at") if f in pricing_fields]
#     # on ajoute des computed readonly (sans casser si BulkPrice pas importé)
#     readonly += ["effective_unit_price_display", "bulk_tiers_display"]

#     # on injecte les computed dans fields si possible
#     if "currency" in pricing_fields:
#         insert_after = "currency"
#     else:
#         insert_after = pricing_fields[-1] if pricing_fields else None

#     computed = ["effective_unit_price_display", "bulk_tiers_display"]
#     fields_order: list[str] = []
#     for f in (pricing_fields or ["pricing_type", "is_active"]):
#         fields_order.append(f)
#         if insert_after and f == insert_after:
#             fields_order.extend(computed)

#     if not fields_order:
#         fields_order = ["pricing_type", "is_active"] + computed

#     class ProductPricingInline(admin.StackedInline):  # type: ignore
#         model = ProductPricing
#         extra = 0
#         can_delete = True
#         show_change_link = True  # ✅ ouvre la fiche ProductPricing (où BulkPriceInline existe)
#         fields = tuple(fields_order)
#         readonly_fields = tuple(readonly)

#         @admin.display(description=_("Prix effectif"))
#         def effective_unit_price_display(self, obj):
#             if not obj:
#                 return "—"
#             try:
#                 return obj.effective_unit_price
#             except Exception:
#                 return "—"

#         @admin.display(description=_("Paliers (BulkPrice)"))
#         def bulk_tiers_display(self, obj) -> str:
#             if not obj:
#                 return "—"
#             # relation attendue: related_name="bulk_prices"
#             mgr = getattr(obj, "bulk_prices", None)
#             if mgr is None:
#                 return "—"
#             try:
#                 return str(mgr.count())
#             except Exception:
#                 return "—"

#     inlines.append(ProductPricingInline)
#     return inlines


# # ------------------------------------------------------------
# # Filters
# # ------------------------------------------------------------
# class SkuPresenceFilter(admin.SimpleListFilter):
#     title = _("SKU")
#     parameter_name = "sku_presence"

#     def lookups(self, request, model_admin):
#         return (
#             ("with", _("Avec SKU")),
#             ("without", _("Sans SKU")),
#         )

#     def queryset(self, request, queryset):
#         v = self.value()
#         if v == "with":
#             return queryset.exclude(sku__isnull=True).exclude(sku__exact="")
#         if v == "without":
#             return queryset.filter(sku__isnull=True) | queryset.filter(sku__exact="")
#         return queryset


# # ------------------------------------------------------------
# # Actions (prod-safe)
# # ------------------------------------------------------------
# @admin.action(description=_("Activer les produits sélectionnés"))
# def action_activate_products(modeladmin, request, queryset):
#     updated = queryset.update(is_active=True)
#     modeladmin.message_user(
#         request,
#         _("%(n)s produit(s) activé(s).") % {"n": updated},
#         level=messages.SUCCESS,
#     )


# @admin.action(description=_("Désactiver les produits (retire aussi la vedette)"))
# def action_deactivate_products(modeladmin, request, queryset):
#     updated = queryset.update(is_active=False, is_featured=False)
#     modeladmin.message_user(
#         request,
#         _("%(n)s produit(s) désactivé(s) (vedette retirée si nécessaire).") % {"n": updated},
#         level=messages.SUCCESS,
#     )


# @admin.action(description=_("Mettre en vedette (ignore les inactifs)"))
# def action_feature_products(modeladmin, request, queryset):
#     updated = 0
#     skipped = 0
#     for p in queryset.only("id", "is_active", "is_featured"):
#         if not p.is_active:
#             skipped += 1
#             continue
#         if p.is_featured:
#             continue
#         p.is_featured = True
#         p.save(update_fields=["is_featured", "updated_at"])
#         updated += 1

#     if updated:
#         modeladmin.message_user(
#             request,
#             _("%(n)s produit(s) mis en vedette.") % {"n": updated},
#             level=messages.SUCCESS,
#         )
#     if skipped:
#         modeladmin.message_user(
#             request,
#             _("%(n)s produit(s) ignoré(s) (inactif).") % {"n": skipped},
#             level=messages.WARNING,
#         )


# @admin.action(description=_("Retirer la vedette (featured)"))
# def action_unfeature_products(modeladmin, request, queryset):
#     updated = queryset.update(is_featured=False)
#     modeladmin.message_user(
#         request,
#         _("%(n)s produit(s) retiré(s) de la vedette.") % {"n": updated},
#         level=messages.SUCCESS,
#     )


# @admin.action(description=_("Marquer comme Nouveau"))
# def action_mark_new(modeladmin, request, queryset):
#     updated = queryset.update(is_new=True)
#     modeladmin.message_user(
#         request,
#         _("%(n)s produit(s) marqué(s) comme Nouveau.") % {"n": updated},
#         level=messages.SUCCESS,
#     )


# @admin.action(description=_("Retirer le statut Nouveau"))
# def action_unmark_new(modeladmin, request, queryset):
#     updated = queryset.update(is_new=False)
#     modeladmin.message_user(
#         request,
#         _("%(n)s produit(s) mis à jour.") % {"n": updated},
#         level=messages.SUCCESS,
#     )


# @admin.action(description=_("Générer un SKU manquant (si possible)"))
# def action_generate_missing_sku(modeladmin, request, queryset):
#     updated = 0
#     skipped = 0

#     qs = queryset.select_related("vendor", "category").only("id", "sku", "vendor__code", "category__code")

#     for p in qs:
#         if p.sku and str(p.sku).strip():
#             continue
#         try:
#             p.save()  # déclenche auto-génération SKU dans save()
#             updated += 1
#         except Exception:
#             skipped += 1

#     if updated:
#         modeladmin.message_user(
#             request,
#             _("%(n)s SKU généré(s).") % {"n": updated},
#             level=messages.SUCCESS,
#         )
#     if skipped:
#         modeladmin.message_user(
#             request,
#             _("%(n)s produit(s) ignoré(s) (vendor/catcode manquant ou erreur).") % {"n": skipped},
#             level=messages.WARNING,
#         )


# @admin.action(description=_("Régénérer slugs + SEO (traductions Parler)"))
# def action_rebuild_seo(modeladmin, request, queryset):
#     updated = 0
#     for p in queryset.only("id"):
#         try:
#             p._ensure_translation_slugs_and_seo()
#             updated += 1
#         except Exception:
#             pass
#     modeladmin.message_user(
#         request,
#         _("%(n)s produit(s) traités (slugs/SEO).") % {"n": updated},
#         level=messages.SUCCESS,
#     )


# # ------------------------------------------------------------
# # Admin Product (aligné modèle Product)
# # ------------------------------------------------------------
# @admin.register(Product)
# class ProductAdmin(TranslatableAdmin):
#     inlines = [ProductImageInline] + _build_pricing_inlines()

#     save_on_top = True
#     actions_on_top = True
#     actions_on_bottom = True
#     list_per_page = 50
#     date_hierarchy = "created_at"
#     autocomplete_fields = ("category", "vendor")

#     list_display = (
#         "id",
#         "thumb",
#         "name_i18n",
#         "sku",
#         "category",
#         "category_code",
#         "vendor",
#         "vendor_code",
#         "price",
#         "stock",
#         "track_stock",
#         "is_new",
#         "is_active",
#         "is_featured",
#         "purchasable_flag",
#         "created_at",
#     )
#     list_display_links = ("id", "name_i18n")
#     list_editable = ("price", "stock", "is_active", "is_featured", "is_new", "track_stock")
#     ordering = ("-created_at", "id")

#     list_filter = (
#         "is_active",
#         "is_featured",
#         "is_new",
#         "track_stock",
#         SkuPresenceFilter,
#         "category",
#         "vendor",
#         ("created_at", admin.DateFieldListFilter),
#     )

#     search_fields = (
#         "sku",
#         "category__code",
#         "vendor__code",
#         "vendor__company_name",
#         "translations__name",
#         "translations__slug",
#     )

#     readonly_fields = ("created_at", "updated_at", "thumb")

#     fieldsets = (
#         (_("Classification"), {"fields": ("category", "vendor", "is_active", "is_featured", "is_new")}),
#         (_("Stock / Vente"), {"fields": ("track_stock", "stock")}),
#         (_("Prix"), {"fields": ("price",)}),
#         (_("SKU & Media"), {"fields": ("sku", "image", "thumb", "fiche_technique")}),
#         (_("Traductions"), {"fields": ("name", "slug", "short_description", "description", "seo_title", "seo_description")}),
#         (_("Système"), {"fields": ("created_at", "updated_at")}),
#     )

#     actions = [
#         action_activate_products,
#         action_deactivate_products,
#         action_feature_products,
#         action_unfeature_products,
#         action_mark_new,
#         action_unmark_new,
#         action_generate_missing_sku,
#         action_rebuild_seo,
#     ]

#     def get_queryset(self, request):
#         qs = super().get_queryset(request).select_related("category", "vendor")
#         return qs.annotate(_images_count=Count("images", distinct=True))

#     @admin.display(description=_("Nom"))
#     def name_i18n(self, obj: Product) -> str:
#         return obj.safe_translation_getter("name", any_language=True) or "-"

#     @admin.display(description=_("Code cat."))
#     def category_code(self, obj: Product) -> str:
#         c = getattr(obj.category, "code", None)
#         return (c or "").strip().upper() or "—"

#     @admin.display(description=_("Code vendeur"))
#     def vendor_code(self, obj: Product) -> str:
#         v = getattr(obj.vendor, "code", None) if obj.vendor_id else None
#         return (v or "").strip().upper() or "—"

#     @admin.display(description=_("Achat"), boolean=True)
#     def purchasable_flag(self, obj: Product) -> bool:
#         try:
#             return bool(obj.purchasable)
#         except Exception:
#             return False

#     @admin.display(description=_("Aperçu"))
#     def thumb(self, obj: Product) -> str:
#         url = None
#         try:
#             url = obj.main_image_url
#         except Exception:
#             url = None

#         if not url:
#             return "—"

#         return format_html(
#             '<img src="{}" style="height:38px;width:38px;object-fit:cover;border-radius:8px;border:1px solid rgba(0,0,0,.12);" />',
#             url,
#         )






# # economic/ecommerce/admin/product_admin.py
# from __future__ import annotations

# from django.contrib import admin, messages
# from django.db.models import Count
# from django.utils.translation import gettext_lazy as _
# from django.utils.html import format_html
# from parler.admin import TranslatableAdmin

# from economic.ecommerce.models import Product, ProductImage

# # ------------------------------------------------------------
# # Helpers: admin-safe (adaptation aux modèles optionnels)
# # ------------------------------------------------------------
# def _model_field_names(model) -> set[str]:
#     try:
#         return {f.name for f in model._meta.fields}
#     except Exception:
#         return set()


# def _pick_fields(model, candidates: list[str]) -> list[str]:
#     available = _model_field_names(model)
#     return [f for f in candidates if f in available]


# # ✅ Optionnel : si ProductPricing/BulkPrice existent
# try:
#     from economic.ecommerce.models import ProductPricing  # type: ignore
# except Exception:
#     ProductPricing = None  # type: ignore

# try:
#     from economic.ecommerce.models import BulkPrice  # type: ignore
# except Exception:
#     BulkPrice = None  # type: ignore


# # ------------------------------------------------------------
# # Inlines
# # ------------------------------------------------------------
# _IMAGE_FIELDS = _pick_fields(
#     ProductImage,
#     ["image", "alt_text", "is_main", "is_primary", "sort_order", "order"],
# )

# # order fields preference
# _IMAGE_ORDERING = []
# if "is_main" in _IMAGE_FIELDS:
#     _IMAGE_ORDERING.append("-is_main")
# elif "is_primary" in _IMAGE_FIELDS:
#     _IMAGE_ORDERING.append("-is_primary")
# if "sort_order" in _IMAGE_FIELDS:
#     _IMAGE_ORDERING.append("sort_order")
# elif "order" in _IMAGE_FIELDS:
#     _IMAGE_ORDERING.append("order")
# _IMAGE_ORDERING += ["id"]


# class ProductImageInline(admin.TabularInline):
#     model = ProductImage
#     extra = 0
#     fields = tuple(_IMAGE_FIELDS) if _IMAGE_FIELDS else ("image",)
#     ordering = tuple(_IMAGE_ORDERING)


# def _build_pricing_inlines():
#     inlines = []

#     if ProductPricing is not None:
#         pricing_fields = _pick_fields(
#             ProductPricing,
#             [
#                 # le plus courant (selon ton design e-commerce)
#                 "pricing_type",
#                 "currency",
#                 "price",
#                 "amount",
#                 "unit_price",
#                 "is_active",
#                 # cas promo/advanced si présent
#                 "base_price",
#                 "promo_price",
#                 "promo_start",
#                 "promo_end",
#                 # meta
#                 "created_at",
#                 "updated_at",
#             ],
#         )
#         readonly = [f for f in ("created_at", "updated_at") if f in pricing_fields]

#         class ProductPricingInline(admin.StackedInline):  # type: ignore
#             model = ProductPricing
#             extra = 0
#             can_delete = True
#             show_change_link = True
#             fields = tuple(pricing_fields) if pricing_fields else ("pricing_type", "currency", "is_active")
#             readonly_fields = tuple(readonly)

#         inlines.append(ProductPricingInline)

#     if BulkPrice is not None:
#         bulk_fields = _pick_fields(
#             BulkPrice,
#             ["min_quantity", "unit_price", "price", "amount", "currency", "created_at"],
#         )
#         readonly = [f for f in ("created_at",) if f in bulk_fields]

#         class BulkPriceInline(admin.TabularInline):  # type: ignore
#             model = BulkPrice
#             extra = 0
#             fields = tuple(bulk_fields) if bulk_fields else ("min_quantity",)
#             readonly_fields = tuple(readonly)
#             ordering = ("min_quantity", "id")

#         inlines.append(BulkPriceInline)

#     return inlines


# # ------------------------------------------------------------
# # Filters
# # ------------------------------------------------------------
# class SkuPresenceFilter(admin.SimpleListFilter):
#     title = _("SKU")
#     parameter_name = "sku_presence"

#     def lookups(self, request, model_admin):
#         return (
#             ("with", _("Avec SKU")),
#             ("without", _("Sans SKU")),
#         )

#     def queryset(self, request, queryset):
#         v = self.value()
#         if v == "with":
#             return queryset.exclude(sku__isnull=True).exclude(sku__exact="")
#         if v == "without":
#             return queryset.filter(sku__isnull=True) | queryset.filter(sku__exact="")
#         return queryset


# # ------------------------------------------------------------
# # Actions (prod-safe)
# # ------------------------------------------------------------
# @admin.action(description=_("Activer les produits sélectionnés"))
# def action_activate_products(modeladmin, request, queryset):
#     updated = queryset.update(is_active=True)
#     modeladmin.message_user(
#         request,
#         _("%(n)s produit(s) activé(s).") % {"n": updated},
#         level=messages.SUCCESS,
#     )


# @admin.action(description=_("Désactiver les produits (retire aussi la vedette)"))
# def action_deactivate_products(modeladmin, request, queryset):
#     # règle métier: inactive => pas featured
#     updated = queryset.update(is_active=False, is_featured=False)
#     modeladmin.message_user(
#         request,
#         _("%(n)s produit(s) désactivé(s) (vedette retirée si nécessaire).") % {"n": updated},
#         level=messages.SUCCESS,
#     )


# @admin.action(description=_("Mettre en vedette (ignore les inactifs)"))
# def action_feature_products(modeladmin, request, queryset):
#     updated = 0
#     skipped = 0
#     for p in queryset.only("id", "is_active", "is_featured"):
#         if not p.is_active:
#             skipped += 1
#             continue
#         if p.is_featured:
#             continue
#         p.is_featured = True
#         # pas besoin de full_clean ici, on respecte la règle métier (actif)
#         p.save(update_fields=["is_featured", "updated_at"])
#         updated += 1

#     if updated:
#         modeladmin.message_user(
#             request,
#             _("%(n)s produit(s) mis en vedette.") % {"n": updated},
#             level=messages.SUCCESS,
#         )
#     if skipped:
#         modeladmin.message_user(
#             request,
#             _("%(n)s produit(s) ignoré(s) (inactif).") % {"n": skipped},
#             level=messages.WARNING,
#         )


# @admin.action(description=_("Retirer la vedette (featured)"))
# def action_unfeature_products(modeladmin, request, queryset):
#     updated = queryset.update(is_featured=False)
#     modeladmin.message_user(
#         request,
#         _("%(n)s produit(s) retiré(s) de la vedette.") % {"n": updated},
#         level=messages.SUCCESS,
#     )


# @admin.action(description=_("Marquer comme Nouveau"))
# def action_mark_new(modeladmin, request, queryset):
#     updated = queryset.update(is_new=True)
#     modeladmin.message_user(
#         request,
#         _("%(n)s produit(s) marqué(s) comme Nouveau.") % {"n": updated},
#         level=messages.SUCCESS,
#     )


# @admin.action(description=_("Retirer le statut Nouveau"))
# def action_unmark_new(modeladmin, request, queryset):
#     updated = queryset.update(is_new=False)
#     modeladmin.message_user(
#         request,
#         _("%(n)s produit(s) mis à jour.") % {"n": updated},
#         level=messages.SUCCESS,
#     )


# @admin.action(description=_("Générer un SKU manquant (si possible)"))
# def action_generate_missing_sku(modeladmin, request, queryset):
#     updated = 0
#     skipped = 0

#     qs = queryset.select_related("vendor", "category").only(
#         "id", "sku", "vendor__code", "category__code"
#     )

#     for p in qs:
#         if p.sku and str(p.sku).strip():
#             continue

#         # le modèle exigera vendor + codes via _generate_sku
#         try:
#             p.save()  # déclenche auto-génération SKU dans save()
#             updated += 1
#         except Exception:
#             skipped += 1

#     if updated:
#         modeladmin.message_user(
#             request,
#             _("%(n)s SKU généré(s).") % {"n": updated},
#             level=messages.SUCCESS,
#         )
#     if skipped:
#         modeladmin.message_user(
#             request,
#             _("%(n)s produit(s) ignoré(s) (vendor/catcode manquant ou erreur).") % {"n": skipped},
#             level=messages.WARNING,
#         )


# @admin.action(description=_("Régénérer slugs + SEO (traductions Parler)"))
# def action_rebuild_seo(modeladmin, request, queryset):
#     updated = 0
#     for p in queryset.only("id"):
#         try:
#             # méthode existante dans ton modèle
#             p._ensure_translation_slugs_and_seo()
#             updated += 1
#         except Exception:
#             pass
#     modeladmin.message_user(
#         request,
#         _("%(n)s produit(s) traités (slugs/SEO).") % {"n": updated},
#         level=messages.SUCCESS,
#     )


# # ------------------------------------------------------------
# # Admin Product (aligné modèle Product)
# # ------------------------------------------------------------
# @admin.register(Product)
# class ProductAdmin(TranslatableAdmin):
#     inlines = [ProductImageInline] + _build_pricing_inlines()

#     # UX / perf
#     save_on_top = True
#     actions_on_top = True
#     actions_on_bottom = True
#     list_per_page = 50
#     date_hierarchy = "created_at"
#     autocomplete_fields = ("category", "vendor")

#     # List
#     list_display = (
#         "id",
#         "thumb",
#         "name_i18n",
#         "sku",
#         "category",
#         "category_code",
#         "vendor",
#         "vendor_code",
#         "price",
#         "stock",
#         "track_stock",
#         "is_new",
#         "is_active",
#         "is_featured",
#         "purchasable_flag",
#         "created_at",
#     )
#     list_display_links = ("id", "name_i18n")
#     list_editable = ("price", "stock", "is_active", "is_featured", "is_new", "track_stock")
#     ordering = ("-created_at", "id")

#     list_filter = (
#         "is_active",
#         "is_featured",
#         "is_new",
#         "track_stock",
#         SkuPresenceFilter,
#         "category",
#         "vendor",
#         ("created_at", admin.DateFieldListFilter),
#     )

#     search_fields = (
#         "sku",
#         "category__code",
#         "vendor__code",
#         "vendor__company_name",
#         "translations__name",
#         "translations__slug",
#     )

#     readonly_fields = ("created_at", "updated_at", "thumb")

#     fieldsets = (
#         (_("Classification"), {"fields": ("category", "vendor", "is_active", "is_featured", "is_new")}),
#         (_("Stock / Vente"), {"fields": ("track_stock", "stock")}),
#         (_("Prix"), {"fields": ("price",)}),
#         (_("SKU & Media"), {"fields": ("sku", "image", "thumb", "fiche_technique")}),
#         (_("Traductions"), {"fields": ("name", "slug", "short_description", "description", "seo_title", "seo_description")}),
#         (_("Système"), {"fields": ("created_at", "updated_at")}),
#     )

#     actions = [
#         action_activate_products,
#         action_deactivate_products,
#         action_feature_products,
#         action_unfeature_products,
#         action_mark_new,
#         action_unmark_new,
#         action_generate_missing_sku,
#         action_rebuild_seo,
#     ]

#     def get_queryset(self, request):
#         qs = super().get_queryset(request).select_related("category", "vendor")
#         # (optionnel) count images pour diagnostic/tri
#         return qs.annotate(_images_count=Count("images", distinct=True))

#     # -------- Displays --------
#     @admin.display(description=_("Nom"))
#     def name_i18n(self, obj: Product) -> str:
#         return obj.safe_translation_getter("name", any_language=True) or "-"

#     @admin.display(description=_("Code cat."))
#     def category_code(self, obj: Product) -> str:
#         c = getattr(obj.category, "code", None)
#         return (c or "").strip().upper() or "—"

#     @admin.display(description=_("Code vendeur"))
#     def vendor_code(self, obj: Product) -> str:
#         v = getattr(obj.vendor, "code", None) if obj.vendor_id else None
#         return (v or "").strip().upper() or "—"

#     @admin.display(description=_("Achat"), boolean=True)
#     def purchasable_flag(self, obj: Product) -> bool:
#         try:
#             return bool(obj.purchasable)
#         except Exception:
#             return False

#     @admin.display(description=_("Aperçu"))
#     def thumb(self, obj: Product) -> str:
#         url = None
#         try:
#             url = obj.main_image_url
#         except Exception:
#             url = None

#         if not url:
#             return "—"

#         return format_html(
#             '<img src="{}" style="height:38px;width:38px;object-fit:cover;border-radius:8px;border:1px solid rgba(0,0,0,.12);" />',
#             url,
#         )






# # economic/ecommerce/admin/product_admin.py
# from __future__ import annotations

# from django.contrib import admin
# from django.utils.translation import gettext_lazy as _
# from parler.admin import TranslatableAdmin

# from economic.ecommerce.models import Product, ProductImage

# # ✅ Optionnel : si ProductPricing/BulkPrice existent
# try:
#     from economic.ecommerce.models import ProductPricing, BulkPrice
#     HAS_PRICING = True
# except Exception:
#     ProductPricing = None  # type: ignore
#     BulkPrice = None  # type: ignore
#     HAS_PRICING = False


# class ProductImageInline(admin.TabularInline):
#     model = ProductImage
#     extra = 1
#     fields = ("image", "alt_text", "is_main", "sort_order")
#     ordering = ("-is_main", "sort_order", "id")


# if HAS_PRICING:
#     class BulkPriceInline(admin.TabularInline):
#         model = BulkPrice
#         extra = 0
#         fields = ("min_quantity", "unit_price", "created_at")
#         readonly_fields = ("created_at",)
#         ordering = ("min_quantity",)

#     class ProductPricingInline(admin.StackedInline):
#         model = ProductPricing
#         extra = 0
#         can_delete = True
#         show_change_link = True
#         fields = (
#             "pricing_type",
#             "base_price",
#             ("promo_price", "currency"),
#             ("promo_start", "promo_end"),
#             ("created_at", "updated_at"),
#         )
#         readonly_fields = ("created_at", "updated_at")


# @admin.action(description=_("Activer les produits sélectionnés"))
# def activate_products(modeladmin, request, queryset):
#     queryset.update(is_active=True)


# @admin.action(description=_("Désactiver les produits sélectionnés"))
# def deactivate_products(modeladmin, request, queryset):
#     queryset.update(is_active=False)


# @admin.action(description=_("Mettre en vedette (featured)"))
# def feature_products(modeladmin, request, queryset):
#     queryset.update(is_featured=True)


# @admin.action(description=_("Retirer la vedette (featured)"))
# def unfeature_products(modeladmin, request, queryset):
#     queryset.update(is_featured=False)


# @admin.register(Product)
# class ProductAdmin(TranslatableAdmin):
#     inlines = [ProductImageInline] + ([ProductPricingInline, BulkPriceInline] if HAS_PRICING else [])

#     list_display = (
#         "id",
#         "name_i18n",
#         "sku",
#         "category",
#         "vendor",
#         "price",
#         "stock",
#         "is_active",
#         "is_featured",
#         "created_at",
#     )
#     list_filter = ("is_active", "is_featured", "category", "vendor")
#     search_fields = ("translations__name", "translations__slug", "sku")
#     ordering = ("-created_at",)
#     list_editable = ("price", "stock", "is_active", "is_featured")
#     autocomplete_fields = ("category", "vendor")
#     actions = [activate_products, deactivate_products, feature_products, unfeature_products]
#     readonly_fields = ("created_at", "updated_at")

#     fieldsets = (
#         (_("Classification"), {"fields": ("category", "vendor", "is_active", "is_featured")}),
#         (_("Commerce"), {"fields": ("sku", "price", "stock")}),
#         (_("Traductions"), {"fields": ("name", "slug", "short_description", "description", "seo_title", "seo_description")}),
#         (_("Système"), {"fields": ("created_at", "updated_at")}),
#     )

#     def get_queryset(self, request):
#         qs = super().get_queryset(request)
#         return qs.select_related("category", "vendor")

#     @admin.display(description=_("Nom"))
#     def name_i18n(self, obj):
#         return obj.safe_translation_getter("name", any_language=True) or "-"





# # /economic/ecommerce/admin/product_admin.py

# from django.contrib import admin
# from django.utils.translation import gettext_lazy as _
# from parler.admin import TranslatableAdmin

# from economic.ecommerce.models import Product, ProductImage


# class ProductImageInline(admin.TabularInline):
#     model = ProductImage
#     extra = 1
#     fields = ("image", "alt_text", "is_main")
#     ordering = ("-is_main", "id")


# @admin.action(description=_("Activer les produits sélectionnés"))
# def activate_products(modeladmin, request, queryset):
#     queryset.update(is_active=True)


# @admin.action(description=_("Désactiver les produits sélectionnés"))
# def deactivate_products(modeladmin, request, queryset):
#     queryset.update(is_active=False)


# @admin.action(description=_("Mettre en vedette (featured)"))
# def feature_products(modeladmin, request, queryset):
#     queryset.update(is_featured=True)


# @admin.action(description=_("Retirer la vedette (featured)"))
# def unfeature_products(modeladmin, request, queryset):
#     queryset.update(is_featured=False)


# @admin.register(Product)
# class ProductAdmin(TranslatableAdmin):
#     inlines = [ProductImageInline]

#     list_display = (
#         "id",
#         "name_i18n",
#         "sku",
#         "category",
#         "vendor",
#         "price",
#         "stock",
#         "is_active",
#         "is_featured",
#         "created_at",
#     )
#     list_filter = ("is_active", "is_featured", "category", "vendor")
#     search_fields = ("translations__name", "translations__slug", "sku")
#     ordering = ("-created_at",)
#     list_editable = ("price", "stock", "is_active", "is_featured")
#     autocomplete_fields = ("category", "vendor")
#     actions = [
#         activate_products,
#         deactivate_products,
#         feature_products,
#         unfeature_products,
#     ]

#     readonly_fields = ("created_at",)

#     fieldsets = (
#         (_("Classification"), {
#             "fields": ("category", "vendor", "is_active", "is_featured"),
#         }),
#         (_("Commerce"), {
#             "fields": ("sku", "price", "stock"),
#         }),
#         (_("Traductions"), {
#             "fields": ("name", "slug", "short_description", "description"),
#         }),
#         (_("Système"), {
#             "fields": ("created_at",),
#         }),
#     )

#     def name_i18n(self, obj):
#         return obj.safe_translation_getter("name", any_language=True) or "-"

#     name_i18n.short_description = _("Nom")
