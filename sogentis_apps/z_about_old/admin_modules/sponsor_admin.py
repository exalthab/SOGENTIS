#about/admin_modules/sponsor_admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from z_about_old.models import Sponsor


@admin.register(Sponsor)
class SponsorAdmin(admin.ModelAdmin):
    """
    Administration des sponsors et donateurs.
    """
    list_display = ("name", "email", "photo_preview", "message", "created_at")
    search_fields = ("name", "email", "message")
    readonly_fields = ("photo_preview", "created_at")
    ordering = ("-created_at",)

    fieldsets = (
        (_("Informations générales"), {
            "fields": ("name", "email", "message"),
        }),
        (_("Image / Logo"), {
            "fields": ("photo", "photo_preview"),
        }),
        (_("Métadonnées"), {
            "fields": ("created_at",),
            "classes": ("collapse",)
        }),
    )

    def photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="80" height="80" style="object-fit:cover;border-radius:8px;">', obj.photo.url)
        return "—"
    photo_preview.short_description = _("Aperçu photo / logo")






# #about/admin_modules/sponsor_admin.py
# from django.contrib import admin
# from django.utils.translation import gettext_lazy as _
# from about.models.sponsor import Sponsor


# @admin.register(Sponsor)
# class SponsorAdmin(admin.ModelAdmin):
#     list_display = ("name", "email")
#     search_fields = ("name", "email")
