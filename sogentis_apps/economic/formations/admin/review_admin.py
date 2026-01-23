# economic/formations/admin/review_admin.py
from __future__ import annotations

from django.contrib import admin

from ..models import CourseReview


@admin.register(CourseReview)
class CourseReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "course", "user", "rating", "is_public", "created_at")
    list_filter = ("rating", "is_public")
    search_fields = ("course__slug", "course__translations__title", "user__email", "user__username")
    autocomplete_fields = ("course", "user")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")
