# core/admin.py
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from core.models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("created_at", "name", "email", "status")
    list_filter = ("status", "created_at")
    search_fields = ("name", "email", "message")
    ordering = ("-created_at",)

    readonly_fields = (
        "created_at", "verify_token", "token_expires_at", "verified_at", "sent_at",
        "sender_ip", "user_agent",
    )

    fieldsets = (
        (_("Contenu"), {"fields": ("name", "email", "message")}),
        (_("Statut"), {"fields": ("status", "verified_at", "sent_at")}),
        (_("Vérification"), {"fields": ("verify_token", "token_expires_at")}),
        (_("Technique"), {"fields": ("sender_ip", "user_agent", "created_at")}),
    )
