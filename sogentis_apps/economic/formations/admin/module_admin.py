from django.contrib import admin
from parler.admin import TranslatableAdmin

from ..models import Module


@admin.register(Module)
class ModuleAdmin(TranslatableAdmin):
    list_display = ("title", "course", "order")
    list_filter = ("course",)
