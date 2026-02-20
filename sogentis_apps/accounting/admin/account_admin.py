# accounting/admin/account_admin.py
from __future__ import annotations

from django.contrib import admin

from accounting.models import Account


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "type", "pole", "is_active", "is_system", "updated_at")
    list_filter = ("type", "pole", "is_active", "is_system")
    search_fields = ("code", "name")
    ordering = ("code",)
    readonly_fields = ("created_at", "updated_at")
