# economic/formations/admin/progress_admin.py
from __future__ import annotations

from django.contrib import admin

from ..models import LessonProgress


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ("id", "enrollment", "lesson", "progress_percent", "last_position_seconds", "updated_at")
    list_filter = ("progress_percent",)
    search_fields = ("enrollment__user__email", "enrollment__course__slug", "lesson__translations__title")
    autocomplete_fields = ("enrollment", "lesson")
    ordering = ("-updated_at",)
    readonly_fields = ("created_at", "updated_at")
