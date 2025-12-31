# admin_modules/product_admin.py
from django.contrib import admin
from parler.admin import TranslatableAdmin
from economic.ecommerce.models import Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image", "alt_text", "is_primary", "created_at")
    readonly_fields = ("created_at",)
    show_change_link = True


@admin.register(Product)
class ProductAdmin(TranslatableAdmin):
    list_display = (
        "name",
        "category",
        "price",
        "promo_percent",
        "discounted_price_display",
        "stock",
        "sold_count",
        "badge",
        "is_new",
        "is_featured",
        "is_flash_sale",
        "is_active",
        "created_at",
    )

    list_filter = (
        "category",
        "is_active",
        "is_new",
        "is_featured",
        "is_flash_sale",
        "badge",
        "created_at",
    )

    search_fields = (
        "translations__name",
        "translations__short_description",
        "slug",
    )

    ordering = ("-created_at",)

    readonly_fields = (
        "sold_count",
        "created_at",
        "reviews_count_cached",
    )

    # prepopulated_fields = {"slug": ("name",)}

    inlines = [ProductImageInline]

    fieldsets = (
        ("📦 Informations générales", {
            "fields": (
                "category",
                "name",
                "slug",
                "short_description",
                "description",
                "specifications",
            )
        }),
        ("💰 Prix & Promotions", {
            "fields": (
                "price",
                "old_price",
                "promo_percent",
            )
        }),
        ("📊 Stock & Statistiques", {
            "fields": (
                "stock",
                "sold_count",
                "rating",
                "reviews_count_cached",
            )
        }),
        ("🏷️ Badges & Mise en avant", {
            "fields": (
                "badge",
                "badge_text",
                "is_new",
                "is_featured",
                "is_flash_sale",
                "flash_ends_at",
            )
        }),
        ("⚙️ Statut & visibilité", {
            "fields": ("is_active",)
        }),
        ("🕒 Dates", {
            "fields": ("created_at",)
        }),
    )

    def discounted_price_display(self, obj):
        return f"{obj.discounted_price:.0f} XOF"
    discounted_price_display.short_description = "Prix après promo"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("category").prefetch_related("translations")






# # admin_modules/product_admin.py
# from django.contrib import admin
# from parler.admin import TranslatableAdmin

# from economic.ecommerce.models import Product, ProductImage


# class ProductImageInline(admin.TabularInline):
#     model = ProductImage
#     extra = 1
#     fields = ("image", "alt_text", "is_primary")
#     show_change_link = True


# @admin.register(Product)
# class ProductAdmin(TranslatableAdmin):
#     list_display = (
#         "name",
#         "category",
#         "price",
#         "promo_percent",
#         "stock",
#         "badge",
#         "is_featured",
#         "is_flash_sale",
#         "is_active",
#         "created_at",
#     )

#     list_filter = (
#         "category",
#         "is_active",
#         "is_featured",
#         "is_flash_sale",
#         "badge",
#         "created_at",
#     )

#     search_fields = (
#         "translations__name",
#         "translations__short_description",
#         "slug",
#     )

#     ordering = ("-created_at",)

#     # Parler supports using translated fields here
#     # prepopulated_fields = {"slug": ("name",)}

#     inlines = [ProductImageInline]

#     readonly_fields = ("created_at",)

#     fieldsets = (
#         ("📦 Informations générales", {
#             "fields": (
#                 "category",
#                 "name",
#                 "slug",
#                 "short_description",
#                 "description",
#                 "specifications",
#             )
#         }),
#         ("💰 Prix & Promotions", {
#             "fields": (
#                 "price",
#                 "old_price",
#                 "promo_percent",
#             )
#         }),
#         ("📊 Stock & Statistiques", {
#             "fields": (
#                 "stock",
#                 "sold_count",
#                 "rating",
#                 "reviews_count_cached",
#             )
#         }),
#         ("🏷️ Affichage Marketplace", {
#             "fields": (
#                 "badge",
#                 "badge_text",
#                 "is_new",
#                 "is_featured",
#                 "is_flash_sale",
#                 "flash_ends_at",
#             )
#         }),
#         ("⚙️ Statut", {
#             "fields": ("is_active",)
#         }),
#         ("🕒 Dates", {
#             "fields": ("created_at",)
#         }),
#     )

#     def get_queryset(self, request):
#         qs = super().get_queryset(request)
#         return (
#             qs.select_related("category")
#               .prefetch_related("translations")  # IMPORTANT for performance with Parler
#         )
