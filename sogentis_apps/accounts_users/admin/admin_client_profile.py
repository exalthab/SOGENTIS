# accounts_users/admin/client_profile_admin.py
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from accounts_users.models.economic.client_profile import ClientProfile


@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    """
    Admin Profil Client (B2C)
    """

    list_display = (
        "id",
        "profile",
        "city",
        "postal_code",
        "created_at",
    )

    search_fields = (
        "profile__user__email",
        "profile__first_name",
        "profile__last_name",
    )

    list_filter = (
        "city",
        "created_at",
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
            _("Informations client"),
            {
                "fields": (
                    "address",
                    "city",
                    "postal_code",
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





# # accounts_users/admin/client_profile_admin.py
# from django.contrib import admin
# from django.utils.translation import gettext_lazy as _

# from accounts_users.models.economic.client_profile import ClientProfile


# @admin.register(ClientProfile)
# class ClientProfileAdmin(admin.ModelAdmin):
#     """
#     Admin Profil Client (B2C)
#     """

#     list_display = (
#         "id",
#         "profile",
#         "city",
#         "postal_code",
#         "created_at",
#     )

#     search_fields = (
#         "profile__user__email",
#         "profile__first_name",
#         "profile__last_name",
#     )

#     list_filter = (
#         "city",
#         "created_at",
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
#             _("Informations client"),
#             {
#                 "fields": (
#                     "address",
#                     "city",
#                     "postal_code",
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
