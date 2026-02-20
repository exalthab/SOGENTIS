# economic/prestations/admin/projects_admin.py
from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from ..models import ProjectAttachment, ProjectBid, ProjectCall


class ProjectAttachmentInline(admin.TabularInline):
    model = ProjectAttachment
    extra = 0


class ProjectBidInline(admin.TabularInline):
    model = ProjectBid
    extra = 0
    autocomplete_fields = ("bidder",)
    fields = ("bidder", "amount", "currency", "status", "created_at")
    readonly_fields = ("created_at",)


@admin.register(ProjectCall)
class ProjectCallAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "status", "is_public", "created_by", "deadline", "created_at")
    list_filter = ("status", "is_public")
    search_fields = ("title", "slug", "created_by__email", "created_by__username")
    prepopulated_fields = {"slug": ("title",)}
    autocomplete_fields = ("created_by",)
    inlines = (ProjectAttachmentInline, ProjectBidInline)
    ordering = ("-created_at", "-id")

    fieldsets = (
        (_("Auteur"), {"fields": ("created_by",)}),
        (_("Contenu"), {"fields": ("title", "slug", "summary", "description")}),
        (_("Budget"), {"fields": ("currency", "budget_min", "budget_max")}),
        (_("Publication"), {"fields": ("status", "is_public", "deadline")}),
        (_("Dates"), {"fields": ("created_at", "updated_at")}),
    )
    readonly_fields = ("created_at", "updated_at")


@admin.register(ProjectBid)
class ProjectBidAdmin(admin.ModelAdmin):
    list_display = ("id", "project", "bidder", "amount", "currency", "status", "created_at")
    list_filter = ("status", "currency")
    search_fields = ("project__slug", "project__title", "bidder__email", "bidder__username")
    autocomplete_fields = ("project", "bidder")
    ordering = ("-created_at", "-id")
    readonly_fields = ("created_at",)


@admin.register(ProjectAttachment)
class ProjectAttachmentAdmin(admin.ModelAdmin):
    list_display = ("id", "project", "label", "file", "created_at")
    search_fields = ("project__slug", "project__title", "label", "file")
    autocomplete_fields = ("project",)
    ordering = ("-created_at", "-id")
    readonly_fields = ("created_at",)
