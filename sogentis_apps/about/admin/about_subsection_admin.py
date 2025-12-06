# about/admin.py
from django.contrib import admin
from parler.admin import TranslatableAdmin
from about.models import AboutSubsection

@admin.register(AboutSubsection)
class AboutSubsectionAdmin(TranslatableAdmin):
    list_display = ("key", "slug", "is_active", "order")
    list_editable = ("is_active", "order")
    search_fields = ("translations__title",)
    ordering = ("order",)

