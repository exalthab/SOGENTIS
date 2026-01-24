# economic/ecommerce/admin/category_admin.py
from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from parler.admin import TranslatableAdmin

from economic.ecommerce.models import Category


@admin.register(Category)
class CategoryAdmin(TranslatableAdmin):
    list_display = ("id", "name_i18n", "parent", "is_active", "order")
    list_filter = ("is_active", "parent")
    search_fields = ("translations__name", "translations__slug")
    ordering = ("order", "id")
    list_editable = ("is_active", "order")
    autocomplete_fields = ("parent",)

    fieldsets = (
        (_("Structure"), {"fields": ("parent", "is_active", "order")}),
        (_("Traductions"), {"fields": ("name", "slug", "description", "seo_title", "seo_description")}),
        (_("Système"), {"fields": ("created_at", "updated_at")}),
    )
    readonly_fields = ("created_at", "updated_at")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("parent")

    @admin.display(description=_("Nom"))
    def name_i18n(self, obj):
        return obj.safe_translation_getter("name", any_language=True) or "-"




# # /economic/ecommerce/admin/category_admin.py

# from django.contrib import admin
# from django.utils.translation import gettext_lazy as _
# from parler.admin import TranslatableAdmin

# from economic.ecommerce.models import Category


# @admin.register(Category)
# class CategoryAdmin(TranslatableAdmin):
#     list_display = ("id", "name_i18n", "parent", "is_active", "order")
#     list_filter = ("is_active", "parent")
#     search_fields = ("translations__name", "translations__slug")
#     ordering = ("order", "id")
#     list_editable = ("is_active", "order")

#     fieldsets = (
#         (_("Structure"), {
#             "fields": ("parent", "is_active", "order"),
#         }),
#         (_("Traductions"), {
#             "fields": ("name", "slug", "description"),
#         }),
#     )

#     def name_i18n(self, obj):
#         return obj.safe_translation_getter("name", any_language=True) or "-"

#     name_i18n.short_description = _("Nom")
