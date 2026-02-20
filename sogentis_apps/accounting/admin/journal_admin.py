# accounting/admin/journal_admin.py
from __future__ import annotations

from django.contrib import admin

from accounting.models import Journal


@admin.register(Journal)
class JournalAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "pole", "default_currency", "is_active", "is_system", "updated_at")
    list_filter = ("pole", "is_active", "is_system")
    search_fields = ("code", "name")
    ordering = ("code",)
    readonly_fields = ("created_at", "updated_at")
