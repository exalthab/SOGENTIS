# sogentis_apps/economic/ecommerce/admin/category_admin.py

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

    fieldsets = (
        (_("Structure"), {
            "fields": ("parent", "is_active", "order"),
        }),
        (_("Traductions"), {
            "fields": ("name", "slug", "description"),
        }),
    )

    def name_i18n(self, obj):
        return obj.safe_translation_getter("name", any_language=True) or "-"

    name_i18n.short_description = _("Nom")
