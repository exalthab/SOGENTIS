from django.contrib import admin
from parler.admin import TranslatableAdmin
from about.models.organigram import Organigram

@admin.register(Organigram)
class OrganigramAdmin(TranslatableAdmin):
    list_display = ("title_translated",)

    def title_translated(self, obj):
        return obj.safe_translation_getter("title", any_language=True)
    title_translated.short_description = "Titre"
