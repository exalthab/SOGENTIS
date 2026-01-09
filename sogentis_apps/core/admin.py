# core/admin.py
from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from core.models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("created_at", "name", "email", "status", "verified_at", "sent_at")
    list_filter = ("status", "created_at")
    search_fields = ("name", "email", "message")
    ordering = ("-created_at",)

    readonly_fields = (
        "verify_token",
        "token_expires_at",
        "verified_at",
        "sent_at",
        "created_at",
        "sender_ip",
        "user_agent",
    )

    actions = ("mark_as_verified", "mark_as_sent", "mark_as_rejected", "rotate_verification_token")

    @admin.action(description=_("Marquer comme vérifié (VERIFIED)"))
    def mark_as_verified(self, request, queryset):
        for obj in queryset:
            obj.mark_verified(save=True)

    @admin.action(description=_("Marquer comme transmis (SENT)"))
    def mark_as_sent(self, request, queryset):
        for obj in queryset:
            obj.mark_sent(save=True)

    @admin.action(description=_("Marquer comme rejeté (REJECTED)"))
    def mark_as_rejected(self, request, queryset):
        for obj in queryset:
            obj.mark_rejected(save=True)

    @admin.action(description=_("Régénérer le token + remettre PENDING"))
    def rotate_verification_token(self, request, queryset):
        for obj in queryset:
            obj.rotate_token(hours=24, save=True)





# # core/admin.py
# from django.contrib import admin
# from django.utils.translation import gettext_lazy as _

# from core.models import ContactMessage


# @admin.register(ContactMessage)
# class ContactMessageAdmin(admin.ModelAdmin):
#     list_display = ("created_at", "name", "email", "status", "verified_at", "sent_at")
#     list_filter = ("status", "created_at")
#     search_fields = ("name", "email", "message")
#     readonly_fields = ("verify_token", "token_expires_at", "verified_at", "sent_at", "created_at", "sender_ip", "user_agent")
#     ordering = ("-created_at",)

#     actions = ("mark_as_sent", "mark_as_rejected")

#     @admin.action(description=_("Marquer comme transmis (SENT)"))
#     def mark_as_sent(self, request, queryset):
#         for obj in queryset:
#             obj.mark_sent(save=True)

#     @admin.action(description=_("Marquer comme rejeté (REJECTED)"))
#     def mark_as_rejected(self, request, queryset):
#         for obj in queryset:
#             obj.mark_rejected(save=True)
