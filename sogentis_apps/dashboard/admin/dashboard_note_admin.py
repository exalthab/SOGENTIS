# dashboard/admin/notes_admin.py

from django.contrib import admin
from dashboard.models.dashboard_note import DashboardNote
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

@admin.register(DashboardNote)
class DashboardNoteAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "preview_content", "is_public", "created_at")
    list_filter = ("is_public", "created_at")
    search_fields = ("title", "content", "author__email", "author__first_name", "author__last_name")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (None, {
            "fields": ("title", "author", "is_public", "content")
        }),
        (_("Métadonnées"), {
            "fields": ("created_at", "updated_at"),
        }),
    )

    def preview_content(self, obj):
        return format_html(
            "<div style='max-width: 400px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;'>{}</div>",
            obj.content[:100]
        )
    preview_content.short_description = _("Aperçu")
