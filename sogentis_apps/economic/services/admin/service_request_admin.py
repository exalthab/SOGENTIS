# economic/services/admin/service_request_admin.py
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from ..models import ServiceRequest


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "service",
        "user",
        "status",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = (
        "service__translations__title",
        "user__email",
        "full_name",
        "email",
    )
    # ⚠️ On évite autocomplete_fields sur CustomUser pour ne pas déclencher admin.E039
    # Si ton CustomUser est bien enregistré dans admin, tu pourras remettre:
    # autocomplete_fields = ("user",)

    readonly_fields = ("created_at", "updated_at")
