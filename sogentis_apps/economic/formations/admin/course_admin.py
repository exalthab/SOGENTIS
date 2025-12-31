# economic/formations/admin/course_admin.py
from django.contrib import admin
from parler.admin import TranslatableAdmin

from ..models import Course


@admin.register(Course)
class CourseAdmin(TranslatableAdmin):
    list_display = ("get_title", "slug", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("translations__title",)
    ordering = ("-created_at",)

    fieldsets = (
        (None, {
            "fields": ("slug", "is_active"),
        }),
        ("Contenu", {
            "fields": ("title", "description"),
        }),
        ("Système", {
            "fields": ("created_at",),
        }),
    )

    readonly_fields = ("created_at",)

    def get_title(self, obj):
        return obj.safe_translation_getter("title", any_language=True)

    get_title.short_description = "Titre"
