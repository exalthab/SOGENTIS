# accounts_users/admin/admin_base.py

from django.contrib import admin
from django.utils.translation import gettext_lazy as _


class BaseAdmin(admin.ModelAdmin):
    """
    Admin de base commun à tous les modèles :
    - champs en lecture seule
    - ordering cohérent
    - pagination
    """

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )

    list_per_page = 25

    def created_at_display(self, obj):
        return obj.created_at
    created_at_display.short_description = _("Créé le")
    created_at_display.admin_order_field = "created_at"

    def updated_at_display(self, obj):
        return obj.updated_at
    updated_at_display.short_description = _("Mis à jour le")
    updated_at_display.admin_order_field = "updated_at"





# # accounts_users/admin/base_admin.py
# from django.contrib import admin

# class BaseAdmin(admin.ModelAdmin):
#     readonly_fields = ["created_at", "updated_at"]
#     ordering = ["-created_at"]
#     list_per_page = 25
