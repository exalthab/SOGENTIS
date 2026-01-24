# economic/ecommerce/admin/product_admin.py
from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from parler.admin import TranslatableAdmin

from economic.ecommerce.models import Product, ProductImage

# ✅ Optionnel : si ProductPricing/BulkPrice existent
try:
    from economic.ecommerce.models import ProductPricing, BulkPrice
    HAS_PRICING = True
except Exception:
    ProductPricing = None  # type: ignore
    BulkPrice = None  # type: ignore
    HAS_PRICING = False


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image", "alt_text", "is_main", "sort_order")
    ordering = ("-is_main", "sort_order", "id")


if HAS_PRICING:
    class BulkPriceInline(admin.TabularInline):
        model = BulkPrice
        extra = 0
        fields = ("min_quantity", "unit_price", "created_at")
        readonly_fields = ("created_at",)
        ordering = ("min_quantity",)

    class ProductPricingInline(admin.StackedInline):
        model = ProductPricing
        extra = 0
        can_delete = True
        show_change_link = True
        fields = (
            "pricing_type",
            "base_price",
            ("promo_price", "currency"),
            ("promo_start", "promo_end"),
            ("created_at", "updated_at"),
        )
        readonly_fields = ("created_at", "updated_at")


@admin.action(description=_("Activer les produits sélectionnés"))
def activate_products(modeladmin, request, queryset):
    queryset.update(is_active=True)


@admin.action(description=_("Désactiver les produits sélectionnés"))
def deactivate_products(modeladmin, request, queryset):
    queryset.update(is_active=False)


@admin.action(description=_("Mettre en vedette (featured)"))
def feature_products(modeladmin, request, queryset):
    queryset.update(is_featured=True)


@admin.action(description=_("Retirer la vedette (featured)"))
def unfeature_products(modeladmin, request, queryset):
    queryset.update(is_featured=False)


@admin.register(Product)
class ProductAdmin(TranslatableAdmin):
    inlines = [ProductImageInline] + ([ProductPricingInline, BulkPriceInline] if HAS_PRICING else [])

    list_display = (
        "id",
        "name_i18n",
        "sku",
        "category",
        "vendor",
        "price",
        "stock",
        "is_active",
        "is_featured",
        "created_at",
    )
    list_filter = ("is_active", "is_featured", "category", "vendor")
    search_fields = ("translations__name", "translations__slug", "sku")
    ordering = ("-created_at",)
    list_editable = ("price", "stock", "is_active", "is_featured")
    autocomplete_fields = ("category", "vendor")
    actions = [activate_products, deactivate_products, feature_products, unfeature_products]
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (_("Classification"), {"fields": ("category", "vendor", "is_active", "is_featured")}),
        (_("Commerce"), {"fields": ("sku", "price", "stock")}),
        (_("Traductions"), {"fields": ("name", "slug", "short_description", "description", "seo_title", "seo_description")}),
        (_("Système"), {"fields": ("created_at", "updated_at")}),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("category", "vendor")

    @admin.display(description=_("Nom"))
    def name_i18n(self, obj):
        return obj.safe_translation_getter("name", any_language=True) or "-"





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
