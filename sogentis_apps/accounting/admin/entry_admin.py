# accounting/admin/entry_admin.py
from __future__ import annotations

from django.contrib import admin

from accounting.models import JournalEntry, JournalLine


class JournalLineInline(admin.TabularInline):
    model = JournalLine
    extra = 0
    fields = ("account", "label", "debit", "credit", "currency", "amount_fx")
    autocomplete_fields = ("account",)


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ("reference", "journal", "date", "kind", "status", "total_debit", "total_credit", "posted_at")
    list_filter = ("status", "kind", "journal")
    search_fields = ("reference", "memo", "object_id")
    date_hierarchy = "date"
    inlines = (JournalLineInline,)
    readonly_fields = ("uuid", "created_at", "updated_at", "posted_at")

    def total_debit(self, obj: JournalEntry):
        return obj.total_debit

    def total_credit(self, obj: JournalEntry):
        return obj.total_credit
