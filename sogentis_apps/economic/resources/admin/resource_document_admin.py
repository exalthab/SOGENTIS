from django.contrib import admin
from ..models import ResourceDocument


@admin.register(ResourceDocument)
class ResourceDocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "resource", "is_public", "created_at")
    list_filter = ("is_public", "created_at")
    search_fields = ("title", "resource__translations__title")
    ordering = ("-created_at",)
