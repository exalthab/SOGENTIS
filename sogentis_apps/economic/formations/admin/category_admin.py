from django.contrib import admin
from ._base import TranslatableAdmin
from ..models import CourseCategory


@admin.register(CourseCategory)
class CourseCategoryAdmin(TranslatableAdmin):
    list_display = ("__str__", "slug", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("translations__name", "slug")
    ordering = ("translations__name",)

    fieldsets = (
        (None, {"fields": ("is_active", "slug")}),
        ("Traductions", {"fields": ("name", "short_description")}),
    )
