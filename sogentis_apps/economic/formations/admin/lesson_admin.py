# economic/formations/admin/lesson_admin.py
from __future__ import annotations

from django.contrib import admin
from parler.admin import TranslatableAdmin

from ..models import Lesson


@admin.register(Lesson)
class LessonAdmin(TranslatableAdmin):
    list_display = ("get_title", "module", "get_course", "type", "order", "is_preview", "is_active", "released_at")
    list_filter = ("type", "is_preview", "is_active", "module__course")
    search_fields = ("translations__title", "module__translations__title", "module__course__translations__title")
    ordering = ("module_id", "order", "id")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (None, {"fields": ("module", "type", "order", "is_preview", "is_active", "released_at")}),
        ("Média", {"fields": ("video_url", "video_file", "duration_seconds", "attachment")}),
        ("Contenu", {"fields": ("title", "content")}),
        ("Audit", {"fields": ("created_at", "updated_at")}),
    )

    def get_title(self, obj: Lesson):
        return obj.safe_translation_getter("title", any_language=True)

    get_title.short_description = "Titre"

    def get_course(self, obj: Lesson):
        try:
            return obj.module.course
        except Exception:
            return "—"

    get_course.short_description = "Course"






# # economic/formations/admin/lesson_admin.py
# from django.contrib import admin
# from ._base import TranslatableAdmin
# from ..models import Lesson


# @admin.register(Lesson)
# class LessonAdmin(TranslatableAdmin):
#     list_display = ("__str__", "title", "module", "order", "video_url")
#     list_filter = ("module", "module__course")
#     search_fields = ("translations__title", "module__translations__title", "module__course__translations__title")
#     ordering = ("module__course", "module", "order")




# from django.contrib import admin
# from parler.admin import TranslatableAdmin

# from ..models import Lesson


# @admin.register(Lesson)
# class LessonAdmin(TranslatableAdmin):
#     list_display = ("title", "module", "order")
#     list_filter = ("module",)
