from django.contrib import admin
from parler.admin import TranslatableAdmin

from ..models import Lesson


@admin.register(Lesson)
class LessonAdmin(TranslatableAdmin):
    list_display = ("title", "module", "order")
    list_filter = ("module",)
