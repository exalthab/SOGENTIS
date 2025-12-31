# economic/resources/admin/resource_category_admin.py
from django.contrib import admin
from parler.admin import TranslatableAdmin

from ..models import ResourceCategory


@admin.register(ResourceCategory)
class ResourceCategoryAdmin(TranslatableAdmin):
    list_display = ("_name", "slug", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("translations__name", "slug")
    ordering = ("-created_at",)

    def _name(self, obj):
        return obj.safe_translation_getter("name", any_language=True)
    _name.short_description = "Nom"
