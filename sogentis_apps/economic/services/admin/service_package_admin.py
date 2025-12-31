# economic/services/admin/service_package_admin.py
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from parler.admin import TranslatableAdmin

from ..models import ServicePackage


@admin.register(ServicePackage)
class ServicePackageAdmin(TranslatableAdmin):
    list_display = ("name_col", "total_price", "is_active", "created_at")
    list_filter = ("is_active",)
    filter_horizontal = ("services",)
    search_fields = ("translations__name", "slug")

    def name_col(self, obj):
        return obj.safe_translation_getter("name", any_language=True)

    name_col.short_description = _("Nom du pack")
