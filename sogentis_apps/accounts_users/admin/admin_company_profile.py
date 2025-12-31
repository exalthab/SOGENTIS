# accounts_users/admin/company_profile_admin.py
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from accounts_users.models.economic.company_profile import CompanyProfile


@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    """
    Admin Profil Entreprise (B2B)
    """

    list_display = (
        "id",
        "profile",
        "company_name",
        "owner_name",
        "postal_code",
        "verified",
        "created_at",
    )

    list_filter = (
        "verified",
        "created_at",
    )

    search_fields = (
        "company_name",
        "owner_name",
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
            _("Informations entreprise"),
            {
                "fields": (
                    "company_name",
                    "owner_name",
                    "company_address",
                    "postal_code",
                    "verified",
                )
            },
        ),
        (
            _("Documents légaux"),
            {
                "fields": (
                    "registration_document",
                    "financial_document",
                )
            },
        ),
        (
            _("Dates"),
            {
                "fields": ("created_at",)
            },
        ),
    )







# # accounts_users/admin/company_profile_admin.py
# from django.contrib import admin
# from django.utils.translation import gettext_lazy as _

# from accounts_users.models.economic.company_profile import CompanyProfile


# @admin.register(CompanyProfile)
# class CompanyProfileAdmin(admin.ModelAdmin):
#     """
#     Admin Profil Entreprise (B2B)
#     """

#     list_display = (
#         "id",
#         "profile",
#         "company_name",
#         "owner_name",
#         "postal_code",
#         "created_at",
#     )

#     list_filter = (
#         "created_at",
#     )

#     search_fields = (
#         "company_name",
#         "owner_name",
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
#             _("Informations entreprise"),
#             {
#                 "fields": (
#                     "company_name",
#                     "owner_name",
#                     "company_address",
#                     "postal_code",
#                 )
#             },
#         ),
#         (
#             _("Documents légaux"),
#             {
#                 "fields": (
#                     "registration_document",
#                     "financial_document",
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
