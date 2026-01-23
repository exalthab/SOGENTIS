# economic/services/admin/service_category_admin.py
from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from parler.admin import TranslatableAdmin

from economic.services.models import ServiceCategory


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(TranslatableAdmin):
    list_display = ("name_col", "slug", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("translations__name", "slug")
    ordering = ("-created_at", "-id")

    @admin.display(description=_("Nom"))
    def name_col(self, obj: ServiceCategory) -> str:
        return obj.safe_translation_getter("name", any_language=True) or f"Category #{obj.pk}"






# # economic/services/admin/service_category_admin.py
# from django.contrib import admin
# from django.utils.translation import gettext_lazy as _
# from parler.admin import TranslatableAdmin

# from economic.services.models import ServiceCategory


# @admin.register(ServiceCategory)
# class ServiceCategoryAdmin(TranslatableAdmin):
#     list_display = ("name_col", "slug", "is_active", "created_at")
#     list_filter = ("is_active",)
#     search_fields = ("translations__name", "slug")
#     ordering = ("-created_at", "-id")

#     def name_col(self, obj):
#         return obj.safe_translation_getter("name", any_language=True)

#     name_col.short_description = _("Nom")







# # economic/services/admin/service_category_admin.py
# from django.contrib import admin
# from django.utils.translation import gettext_lazy as _
# from parler.admin import TranslatableAdmin

# from ..models import ServiceCategory


# @admin.register(ServiceCategory)
# class ServiceCategoryAdmin(TranslatableAdmin):
#     list_display = ("name_col", "slug", "is_active", "created_at")
#     list_filter = ("is_active",)
#     search_fields = ("translations__name", "slug")

#     def name_col(self, obj):
#         return obj.safe_translation_getter("name", any_language=True)

#     name_col.short_description = _("Nom")
