#about/admin_modules/donation_admin.py
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from z_about_old.models import Donation


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    """
    Administration des dons effectués par les sponsors.
    """
    list_display = ("sponsor_name", "amount_display", "recurring", "date", "is_active")
    list_editable = ("is_active",)
    list_filter = ("recurring", "date", "is_active")
    search_fields = ("sponsor__name", "message")
    ordering = ("-date",)
    readonly_fields = ("date", "created_at", "updated_at")

    fieldsets = (
        (_("Informations générales"), {
            "fields": ("sponsor", "amount", "recurring", "message"),
        }),
        (_("Statut et suivi"), {
            "fields": ("is_active",),
        }),
        (_("Métadonnées"), {
            "fields": ("date", "created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )

    def sponsor_name(self, obj):
        """Affiche le nom du sponsor."""
        return obj.sponsor.name if obj.sponsor else "—"
    sponsor_name.short_description = _("Sponsor")

    def amount_display(self, obj):
        """Formatage du montant avec la devise FCFA."""
        return f"{obj.amount:,.2f} FCFA"
    amount_display.short_description = _("Montant")








# #about/admin_modules/donation_admin.py
# from django.contrib import admin
# from django.utils.translation import gettext_lazy as _
# from ..models import ChildDonation

# @admin.register(ChildDonation)
# class ChildDonationAdmin(admin.ModelAdmin):
#     list_display = ("child", "sponsor_name", "amount", "date")
#     list_filter = ("date",)
#     search_fields = ("child__name", "sponsor__name")
#     ordering = ("-date",)

#     def sponsor_name(self, obj):
#         return obj.sponsor.name if obj.sponsor else _("Anonyme")
#     sponsor_name.short_description = _("Sponsor")




# from django.contrib import admin
# from django.utils.translation import gettext_lazy as _
# from parler.admin import TranslatableAdmin
# from about.models.donation import Donation


# @admin.register(Donation)
# class DonationAdmin(TranslatableAdmin):
#     list_display = ("get_title", "amount", "is_active")
#     search_fields = ("translations__title",)
#     ordering = ("-created_at",)

#     def get_title(self, obj):
#         return obj.safe_translation_getter("title", any_language=True)
#     get_title.short_description = _("Titre")
