from django.contrib import admin

try:
    from parler.admin import TranslatableAdmin, TranslatableTabularInline
except Exception:
    TranslatableAdmin = admin.ModelAdmin
    TranslatableTabularInline = admin.TabularInline

__all__ = ["TranslatableAdmin", "TranslatableTabularInline"]
