# accounts_users/admin/vendor_profile_admin.py
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from accounts_users.models.economic.vendor_profile import VendorProfile


@admin.register(VendorProfile)
class VendorProfileAdmin(admin.ModelAdmin):
    """
    Admin Profil Vendeur
    """

    list_display = (
        "id",
        "profile",
        "business_name",
        "ninea",
        "postal_code",
        "verified",
        "created_at",
    )

    list_filter = (
        "verified",
        "created_at",
    )

    search_fields = (
        "business_name",
        "ninea",
        "profile__user__email",
    )

    ordering = ("-created_at",)

    readonly_fields = (
        "created_at",
    )

    fieldsets = (
        (
            _("Profil utilisateur"),
            {
                "fields": ("profile",)
            },
        ),
        (
            _("Informations commerciales"),
            {
                "fields": (
                    "business_name",
                    "ninea",
                    "business_address",
                    "postal_code",
                    "verified",
                )
            },
        ),
        (
            _("Documents"),
            {
                "fields": ("trade_register_document",)
            },
        ),
        (
            _("Dates"),
            {
                "fields": ("created_at",)
            },
        ),
    )





# # accounts_users/admin/vendor_profile_admin.py
# from django.contrib import admin
# from django.utils.translation import gettext_lazy as _

# from accounts_users.models.economic.vendor_profile import VendorProfile


# @admin.register(VendorProfile)
# class VendorProfileAdmin(admin.ModelAdmin):
#     """
#     Admin Profil Vendeur
#     """

#     list_display = (
#         "id",
#         "profile",
#         "business_name",
#         "ninea",
#         "postal_code",
#         "created_at",
#     )

#     list_filter = (
#         "created_at",
#     )

#     search_fields = (
#         "business_name",
#         "ninea",
#         "profile__user__email",
#     )

#     ordering = ("-created_at",)

#     readonly_fields = (
#         "created_at",
#         "updated_at",
#     )

#     fieldsets = (
#         (
#             _("Profil utilisateur"),
#             {
#                 "fields": (
#                     "profile",
#                 )
#             },
#         ),
#         (
#             _("Informations commerciales"),
#             {
#                 "fields": (
#                     "business_name",
#                     "ninea",
#                     "business_address",
#                     "postal_code",
#                 )
#             },
#         ),
#         (
#             _("Documents"),
#             {
#                 "fields": (
#                     "trade_register_document",
#                 )
#             },
#         ),
#         (
#             _("Dates"),
#             {
#                 "fields": (
#                     "created_at",
#                     "updated_at",
#                 )
#             },
#         ),
#     )
