#admin hero_admin.py
from django.contrib import admin
from parler.admin import TranslatableAdmin
from about.models import HeroBlock

@admin.register(HeroBlock)
class HeroBlockAdmin(TranslatableAdmin):
    list_display = ("title_translated",)

    def title_translated(self, obj):
        return obj.safe_translation_getter("title", any_language=True)
