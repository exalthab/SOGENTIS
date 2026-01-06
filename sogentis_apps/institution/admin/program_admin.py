from django.contrib import admin

from institution.models.program import Program


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ("title", "facility", "start_date", "end_date", "is_active", "created_at")
    list_filter = ("is_active", "start_date")
    search_fields = ("title", "summary", "content", "facility__name")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("-created_at",)
