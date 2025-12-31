from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from economic.support.models import SupportTicket, TicketMessage


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ("subject", "user", "status", "priority", "order_ref", "created_at")
    list_filter = ("status", "priority", "created_at")
    search_fields = ("subject", "description", "order_ref", "user__email", "user__username")
    readonly_fields = ("created_at", "updated_at", "closed_at")
    ordering = ("-created_at",)

    fieldsets = (
        (_("Ticket"), {"fields": ("user", "subject", "description", "order_ref")}),
        (_("Statut"), {"fields": ("status", "priority", "closed_at")}),
        (_("Dates"), {"fields": ("created_at", "updated_at")}),
    )


@admin.register(TicketMessage)
class TicketMessageAdmin(admin.ModelAdmin):
    list_display = ("ticket", "author", "is_staff_reply", "created_at")
    list_filter = ("is_staff_reply", "created_at")
    search_fields = ("ticket__subject", "message", "author__email", "author__username")
    readonly_fields = ("created_at",)
