# economic/formations/admin/module_admin.py
from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from parler.admin import TranslatableAdmin

from ..models import Module

try:
    from ..models import Lesson
except Exception:
    Lesson = None


if Lesson:
    class LessonInline(admin.TabularInline):
        model = Lesson
        extra = 0
        fields = ("order", "type", "is_preview", "is_active", "released_at")
        ordering = ("order",)
        show_change_link = True


@admin.register(Module)
class ModuleAdmin(TranslatableAdmin):
    list_display = ("get_title", "course", "order", "is_active", "created_at")
    list_filter = ("is_active", "course")
    search_fields = ("translations__title", "course__slug", "course__translations__title")
    ordering = ("course_id", "order", "id")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (None, {"fields": ("course", "order", "is_active")}),
        (_("Contenu"), {"fields": ("title", "description")}),
        (_("Audit"), {"fields": ("created_at", "updated_at")}),
    )

    if Lesson:
        inlines = [LessonInline]

    def get_title(self, obj: Module):
        return obj.safe_translation_getter("title", any_language=True)

    get_title.short_description = _("Titre")





# # economic/formations/admin/module_admin.py (inline Lessons)
# from django.contrib import admin
# from ._base import TranslatableAdmin, TranslatableTabularInline
# from ..models import Module, Lesson


# class LessonInline(TranslatableTabularInline):
#     model = Lesson
#     extra = 0
#     fields = ("title", "order", "video_url")
#     ordering = ("order",)
#     show_change_link = True


# @admin.register(Module)
# class ModuleAdmin(TranslatableAdmin):
#     list_display = ("__str__", "title", "course", "order")
#     list_filter = ("course",)
#     search_fields = ("translations__title", "course__translations__title")
#     ordering = ("course", "order")
#     inlines = [LessonInline]



# from django.contrib import admin
# from parler.admin import TranslatableAdmin

# from ..models import Module


# @admin.register(Module)
# class ModuleAdmin(TranslatableAdmin):
#     list_display = ("title", "course", "order")
#     list_filter = ("course",)