# economic/formations/admin/instructor_admin.py
from __future__ import annotations

from django.contrib import admin

from ..models import CourseInstructor


@admin.register(CourseInstructor)
class CourseInstructorAdmin(admin.ModelAdmin):
    list_display = ("course", "user", "role", "display_order", "is_active", "created_at")
    list_filter = ("role", "is_active")
    search_fields = ("course__slug", "course__translations__title", "user__email", "user__username")
    autocomplete_fields = ("course", "user")
    ordering = ("course_id", "display_order", "id")
    readonly_fields = ("created_at", "updated_at")
