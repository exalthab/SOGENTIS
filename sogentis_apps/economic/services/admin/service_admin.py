# economic/services/admin/service_admin.py
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from parler.admin import TranslatableAdmin

from economic.services.models import Service


@admin.register(Service)
class ServiceAdmin(TranslatableAdmin):
    list_display = ("title_col", "category", "base_price", "is_active", "is_featured", "created_at")
    list_filter = ("is_active", "is_featured", "category")
    search_fields = ("translations__title", "slug")
    autocomplete_fields = ("category",)
    ordering = ("-created_at", "-id")

    def title_col(self, obj):
        return obj.safe_translation_getter("title", any_language=True)

    title_col.short_description = _("Titre")







# # economic/services/admin/service_admin.py
# from django.contrib import admin
# from django.utils.translation import gettext_lazy as _
# from parler.admin import TranslatableAdmin

# from ..models import Service


# @admin.register(Service)
# class ServiceAdmin(TranslatableAdmin):
#     list_display = (
#         "title_col",
#         "category",
#         "base_price",
#         "is_active",
#         "is_featured",
#         "created_at",
#     )
#     list_filter = ("is_active", "is_featured", "category")
#     search_fields = ("translations__title", "slug")

#     def title_col(self, obj):
#         return obj.safe_translation_getter("title", any_language=True)

#     title_col.short_description = _("Titre")
