#  about/admin/partner_admin.py
from django.contrib import admin
from parler.admin import TranslatableAdmin
from about.models.partner import Partner

@admin.register(Partner)
class PartnerAdmin(TranslatableAdmin):
    list_display = ['name', 'website']
    search_fields = ['translations__name']

    def name_translated(self, obj):
        return obj.safe_translation_getter("name", any_language=True)