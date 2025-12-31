# accounts_users/admin/admin_profile_admin.py

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from accounts_users.models.users_profile import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Admin du profil SOCIAL (identité de base uniquement).
    ⚠️ Aucun workflow ici : pas de status, pas de validation, pas de codes.
    """

    list_display = (
        "user",
        "get_full_identity",
        "phone_number",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "created_at",
    )

    search_fields = (
        "user__email",
        "user__username",
        "last_name",
        "first_name",
        "middle_names",
        "nickname",
        "phone_number",
    )

    ordering = ("-created_at",)

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (_("Utilisateur"), {"fields": ("user",)}),
        (_("Identité"), {"fields": ("last_name", "first_name", "middle_names", "nickname")}),
        (_("Contact"), {"fields": ("phone_number", "message")}),
        (_("Dates"), {"fields": ("created_at", "updated_at")}),
    )

    @admin.display(description=_("Identité"), ordering="last_name")
    def get_full_identity(self, obj: UserProfile):
        full_name = " ".join(filter(None, [obj.last_name, obj.first_name, obj.middle_names]))
        return full_name.strip() or obj.user.get_username()





# # accounts_users/admin/admin_profile_admin.py 24/12/2025
# from django.contrib import admin
# from django.utils.translation import gettext_lazy as _

# from accounts_users.models.users_profile import UserProfile


# @admin.register(UserProfile)
# class UserProfileAdmin(admin.ModelAdmin):

#     list_display = (
#         "user",
#         "get_full_identity",
#         "membership_role",
#         "status",
#         "created_at",
#     )

#     list_filter = (
#         "membership_role",
#         "status",
#     )

#     search_fields = (
#         "user__email",
#         "last_name",
#         "first_name",
#         "nickname",
#         "phone",
#     )

#     ordering = ("-created_at",)

#     readonly_fields = (
#         "social_registration_code",
#         "created_at",
#         "updated_at",
#     )

#     fieldsets = (
#         (_("Utilisateur"), {"fields": ("user", "status")}),
#         (_("Identité"), {"fields": ("last_name", "first_name", "middle_names", "nickname")}),
#         (_("Contact"), {"fields": ("phone", "message")}),
#         (_("Rôle social"), {"fields": ("membership_role",)}),
#         (_("Code système"), {"fields": ("social_registration_code",)}),
#         (_("Dates"), {"fields": ("created_at", "updated_at")}),
#     )

#     @admin.display(description=_("Identité"), ordering="last_name")
#     def get_full_identity(self, obj):
#         return f"{obj.last_name} {obj.first_name}".strip() or str(obj.user)





# # accounts_users/admin/profile_admin.py 21/12/2025 error

# from django.contrib import admin
# from django.utils.translation import gettext_lazy as _

# from accounts_users.models.users_economic_profile import UserProfile


# @admin.register(UserProfile)
# class UserProfileAdmin(admin.ModelAdmin):
#     # ======================================================
#     # LISTE
#     # ======================================================
#     list_display = (
#         "user",
#         "get_full_identity",
#         "phone",
#         "membership_role",
#         "economic_role",
#         "status",
#         "created_at",
#     )

#     list_filter = (
#         "membership_role",
#         "economic_role",
#         "status",
#         "country_of_residence",
#     )

#     search_fields = (
#         "user__email",
#         "last_name",
#         "first_name",
#         "middle_names",
#         "nickname",
#         "phone",
#     )

#     ordering = ("-created_at",)

#     readonly_fields = (
#         "social_registration_code",
#         "economic_registration_code",
#         "created_at",
#         "updated_at",
#     )

#     # ======================================================
#     # FIELDSETS (ADMIN PRO)
#     # ======================================================
#     fieldsets = (
#         (_("Utilisateur"), {
#             "fields": ("user", "status"),
#         }),
#         (_("Identité"), {
#             "fields": (
#                 "last_name",
#                 "first_name",
#                 "middle_names",
#                 "nickname",
#             ),
#         }),
#         (_("Naissance"), {
#             "fields": (
#                 "date_of_birth",
#                 "place_of_birth",
#                 "country_of_birth",
#             ),
#         }),
#         (_("Résidence"), {
#             "fields": (
#                 "country_of_residence",
#                 "city_of_residence",
#                 "address",
#             ),
#         }),
#         (_("Contact & message"), {
#             "fields": (
#                 "phone",
#                 "message",
#             ),
#         }),
#         (_("Rôles"), {
#             "fields": (
#                 "membership_role",
#                 "economic_role",
#                 "role",
#             ),
#         }),
#         (_("Documents"), {
#             "fields": (
#                 "profile_picture",
#                 "judicial_record",
#             ),
#         }),
#         (_("Codes système"), {
#             "fields": (
#                 "social_registration_code",
#                 "economic_registration_code",
#             ),
#         }),
#         (_("Métadonnées"), {
#             "fields": (
#                 "created_at",
#                 "updated_at",
#             ),
#         }),
#     )

#     # ======================================================
#     # MÉTHODES
#     # ======================================================
#     @admin.display(
#         description=_("Identité"),
#         ordering="last_name",
#     )
#     def get_full_identity(self, obj: UserProfile):
#         """
#         Affichage lisible du nom complet.
#         """
#         parts = filter(None, [
#             obj.last_name,
#             obj.first_name,
#             obj.middle_names,
#         ])
#         return " ".join(parts) or obj.nickname or str(obj.user)







# # accounts_users/admin/profile_admin.py November 2025

# from django.contrib import admin
# from accounts_users.models.users_profile import UserProfile

# @admin.register(UserProfile)
# class UserProfileAdmin(admin.ModelAdmin):
#     list_display = (
#         "user", 
#         "full_name", 
#         "phone", 
#         # "country", 
#         "created", 
#         "updated",
        
#     )
#     search_fields = ("full_name", "phone", "user__email")
#     list_filter = ( "membership_role", "phone")
#     readonly_fields = ("created", "updated")

#     def created(self, obj):
#         return obj.created_at
#     created.admin_order_field = "created_at"
#     created.short_description = "Créé le"

#     def updated(self, obj):
#         return obj.updated_at
#     updated.admin_order_field = "updated_at"
#     updated.short_description = "Mis à jour le"





