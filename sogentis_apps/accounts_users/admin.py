# accounts_users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from accounts_users.models.custom_users import CustomUser
from accounts_users.forms.auth_forms import (
    CustomUserCreationForm,
    CustomUserChangeForm,
)

from accounts_users.models.users_economic_profile import UserProfile
from accounts_users.models.membership_role import MembershipRole
from accounts_users.models.user_role import UserRole
from accounts_users.models.admin_roles import AdminRole
from accounts_users.models import DashboardNote

# ⚠️ Forcer le chargement des sous-admins
from accounts_users.admin.admin_social_profile import SocialProfileAdmin  # noqa
from accounts_users.admin.admin_client_profile import ClientProfileAdmin  # noqa
from accounts_users.admin.admin_vendor_profile import VendorProfileAdmin  # noqa
from accounts_users.admin.admin_company_profile import CompanyProfileAdmin  # noqa


# =====================================================
# CUSTOM USER ADMIN
# =====================================================
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser

    list_display = (
        "email",
        "is_active",
        "is_staff",
        "is_superuser",
        "date_joined",
    )

    list_filter = ("is_active", "is_staff", "is_superuser")
    search_fields = ("email",)
    ordering = ("-date_joined",)
    readonly_fields = ("date_joined", "last_login")

    fieldsets = (
        (None, {"fields": ("email", "password")}),

        (
            _("Permissions"),
            {
                "fields": (
                    "is_staff",
                    "is_active",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),

        (_("Dates"), {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                    "is_superuser",
                ),
            },
        ),
    )


# =====================================================
# USER PROFILE ADMIN (PLATEFORME / ÉCONOMIQUE)
# =====================================================
STATUS_COLORS = {
    "pending": "secondary",
    "approved": "success",
    "rejected": "danger",
}


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Profil utilisateur CENTRAL
    - Client / Vendeur / Entreprise
    - AUCUNE donnée sociale ici
    """

    list_display = (
        "user",
        "display_full_name",
        "phone",
        "economic_role",
        "colored_status",
        "created_at",
        "thumbnail",
    )

    search_fields = (
        "user__email",
        "first_name",
        "last_name",
        "phone",
    )

    list_filter = (
        "status",
        "economic_role",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "thumbnail",
        "economic_registration_code",
        "social_registration_code",
    )

    fieldsets = (
        (_("Utilisateur"), {
            "fields": ("user",)
        }),

        (_("Identité"), {
            "fields": (
                "first_name",
                "last_name",
                "middle_names",
                "nickname",
                "date_of_birth",
                "place_of_birth",
            )
        }),

        (_("Résidence"), {
            "fields": (
                "country_of_residence",
                "city_of_residence",
                "address",
            )
        }),

        (_("Contact / Profession"), {
            "fields": (
                "phone",
                "profession",
                "function",
            )
        }),

        (_("Rôle économique"), {
            "fields": (
                "economic_role",
            )
        }),

        (_("Statut"), {
            "fields": (
                "status",
            )
        }),

        (_("Codes"), {
            "fields": (
                "economic_registration_code",
                "social_registration_code",
            )
        }),

        (_("Dates"), {
            "fields": (
                "created_at",
                "updated_at",
            )
        }),
    )

    # ---------- HELPERS ----------

    def display_full_name(self, obj):
        return f"{obj.last_name or ''} {obj.first_name or ''}".strip()

    display_full_name.short_description = _("Nom complet")

    def thumbnail(self, obj):
        if obj.profile_picture:
            return format_html(
                '<img src="{}" style="height:50px; border-radius:6px;" />',
                obj.profile_picture.url,
            )
        return "—"

    thumbnail.short_description = _("Photo")

    def colored_status(self, obj):
        color = STATUS_COLORS.get(obj.status, "secondary")
        return mark_safe(
            f'<span class="badge bg-{color}">{obj.get_status_display()}</span>'
        )

    colored_status.short_description = _("Statut")


# =====================================================
# ROLES & CONFIGURATION
# =====================================================
@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)


@admin.register(MembershipRole)
class MembershipRoleAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)


@admin.register(AdminRole)
class AdminRoleAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "created_at")
    readonly_fields = ("created_at", "updated_at")
    list_filter = ("is_active",)
    ordering = ("-created_at",)


# =====================================================
# DASHBOARD NOTES
# =====================================================
@admin.register(DashboardNote)
class DashboardNoteAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "created_at")
    search_fields = ("title", "user__email")
    ordering = ("-created_at",)
    
    
    
    
    
    
    
    
    
# # accounts_users/admin.py 23/12/2025
# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin
# from django.utils.html import format_html
# from django.utils.safestring import mark_safe
# from django.core.mail import send_mail
# from django.conf import settings
# from django.utils.translation import gettext_lazy as _

# from accounts_users.models.users import CustomUser
# from accounts_users.forms.auth_forms import (
#     CustomUserCreationForm,
#     CustomUserChangeForm,
# )
# from accounts_users.models.users_profile import UserProfile
# from accounts_users.models.membership_role import MembershipRole
# from accounts_users.models.role import UserRole
# from accounts_users.models.admin_roles import AdminRole
# from accounts_users.models.user_role import UserRole as UserUserRole
# from accounts_users.models import DashboardNote

# # IMPORTANT: force loading SocialProfile admin
# from accounts_users.admin.social_profile_admin import SocialProfileAdmin
# from accounts_users.admin.client_profile_admin import ClientProfileAdmin
# from accounts_users.admin.vendor_profile_admin import VendorProfileAdmin
# from accounts_users.admin.company_profile_admin import CompanyProfileAdmin


# # =====================================================
# # CUSTOM USER ADMIN
# # =====================================================
# @admin.register(CustomUser)
# class CustomUserAdmin(UserAdmin):
#     add_form = CustomUserCreationForm
#     form = CustomUserChangeForm
#     model = CustomUser

#     list_display = (
#         "email",
#         "is_active",
#         "is_staff",
#         "is_superuser",
#         "date_joined",
#     )

#     list_filter = ("is_active", "is_staff", "is_superuser")
#     search_fields = ("email",)
#     ordering = ("-date_joined",)
#     readonly_fields = ("date_joined", "last_login")

#     fieldsets = (
#         (None, {"fields": ("email", "password")}),
#         (
#             _("Permissions"),
#             {
#                 "fields": (
#                     "is_staff",
#                     "is_active",
#                     "is_superuser",
#                     "groups",
#                     "user_permissions",
#                 )
#             },
#         ),
#         (_("Dates"), {"fields": ("last_login", "date_joined")}),
#     )

#     add_fieldsets = (
#         (
#             None,
#             {
#                 "classes": ("wide",),
#                 "fields": (
#                     "email",
#                     "password1",
#                     "password2",
#                     "is_staff",
#                     "is_active",
#                     "is_superuser",
#                 ),
#             },
#         ),
#     )


# # =====================================================
# # USER PROFILE ADMIN
# # =====================================================
# STATUS_COLORS = {
#     "pending": "secondary",
#     "approved": "success",
#     "rejected": "danger",
# }


# @admin.register(UserProfile)
# class UserProfileAdmin(admin.ModelAdmin):
#     list_display = (
#         "user",
#         "display_full_name",
#         "phone",
#         "membership_role",
#         "colored_status",
#         "created_at",
#         "thumbnail",
#     )

#     search_fields = (
#         "user__email",
#         "first_name",
#         "last_name",
#         "phone",
#     )

#     list_filter = (
#         "status",
#         "membership_role",
#     )

#     readonly_fields = (
#         "created_at",
#         "updated_at",
#         "thumbnail",
#         "social_registration_code",
#         "economic_registration_code",
#     )

#     actions = ("valider_profils", "refuser_profils")

#     # ---------- HELPERS ----------

#     def display_full_name(self, obj):
#         return f"{obj.last_name or ''} {obj.first_name or ''}".strip()

#     display_full_name.short_description = _("Nom complet")

#     def thumbnail(self, obj):
#         if obj.profile_picture:
#             return format_html(
#                 '<img src="{}" style="height:50px; border-radius:6px;" />',
#                 obj.profile_picture.url,
#             )
#         return "—"

#     thumbnail.short_description = _("Photo")

#     def colored_status(self, obj):
#         color = STATUS_COLORS.get(obj.status, "secondary")
#         return mark_safe(
#             f'<span class="badge bg-{color}">{obj.get_status_display()}</span>'
#         )

#     colored_status.short_description = _("Statut")

#     # ---------- ACTIONS ----------

#     @admin.action(description=_("Valider les profils sélectionnés"))
#     def valider_profils(self, request, queryset):
#         updated = queryset.update(status=UserProfile.Status.APPROVED)
#         self.message_user(
#             request,
#             _("%(count)d profil(s) validé(s).") % {"count": updated},
#         )

#     @admin.action(description=_("Refuser les profils sélectionnés"))
#     def refuser_profils(self, request, queryset):
#         for profile in queryset:
#             profile.status = UserProfile.Status.REJECTED
#             profile.save(update_fields=["status"])

#             send_mail(
#                 subject=_("Votre profil a été refusé"),
#                 message=_(
#                     "Bonjour {name},\n\n"
#                     "Votre profil a été refusé. "
#                     "Merci de contacter l’administrateur pour plus de détails."
#                 ).format(name=self.display_full_name(profile)),
#                 from_email=settings.DEFAULT_FROM_EMAIL,
#                 recipient_list=[profile.user.email],
#                 fail_silently=True,
#             )

#         self.message_user(
#             request,
#             _("%(count)d profil(s) refusé(s) et notifié(s).")
#             % {"count": queryset.count()},
#         )


# # =====================================================
# # ROLES ADMINS
# # =====================================================
# @admin.register(UserRole)
# class UserRoleAdmin(admin.ModelAdmin):
#     list_display = ("name", "description")
#     search_fields = ("name",)


# @admin.register(MembershipRole)
# class MembershipRoleAdmin(admin.ModelAdmin):
#     list_display = ("name", "description")
#     search_fields = ("name",)


# @admin.register(AdminRole)
# class AdminRoleAdmin(admin.ModelAdmin):
#     list_display = ("name", "is_active", "created_at")
#     readonly_fields = ("created_at", "updated_at")
#     list_filter = ("is_active",)
#     ordering = ("-created_at",)


# @admin.register(UserUserRole)
# class UserUserRoleAdmin(admin.ModelAdmin):
#     list_display = ("user", "role", "is_active", "created_at")
#     readonly_fields = ("created_at", "updated_at")
#     list_filter = ("role", "is_active")
#     ordering = ("-created_at",)


# # =====================================================
# # DASHBOARD NOTES ADMIN
# # =====================================================
# @admin.register(DashboardNote)
# class DashboardNoteAdmin(admin.ModelAdmin):
#     list_display = ("title", "user", "created_at")
#     search_fields = ("title", "user__email")
#     ordering = ("-created_at",)




# accounts_users/admin.py/ 22/12/2025
# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin
# from django.utils.html import format_html
# from django.utils.safestring import mark_safe
# from django.core.mail import send_mail
# from django.conf import settings

# from accounts_users.models.users import CustomUser
# from accounts_users.forms.auth_forms import (
#     CustomUserCreationForm,
#     CustomUserChangeForm,
# )
# from accounts_users.models.users_profile import UserProfile
# from accounts_users.models.membership_role import MembershipRole
# from accounts_users.models.role import UserRole
# from accounts_users.models.admin_roles import AdminRole
# from accounts_users.models.user_role import UserRole as UserUserRole
# from accounts_users.models import DashboardNote


# # =====================================================
# # CUSTOM USER ADMIN
# # =====================================================

# @admin.register(CustomUser)
# class CustomUserAdmin(UserAdmin):
#     add_form = CustomUserCreationForm
#     form = CustomUserChangeForm
#     model = CustomUser

#     list_display = (
#         "email",
#         "is_active",
#         "is_staff",
#         "is_superuser",
#         "date_joined",
#     )
#     list_filter = ("is_active", "is_staff", "is_superuser")
#     search_fields = ("email",)
#     ordering = ("-date_joined",)
#     readonly_fields = ("date_joined", "last_login")

#     fieldsets = (
#         (None, {"fields": ("email", "password")}),
#         (
#             "Permissions",
#             {
#                 "fields": (
#                     "is_staff",
#                     "is_active",
#                     "is_superuser",
#                     "groups",
#                     "user_permissions",
#                 )
#             },
#         ),
#         ("Dates", {"fields": ("last_login", "date_joined")}),
#     )

#     add_fieldsets = (
#         (
#             None,
#             {
#                 "classes": ("wide",),
#                 "fields": (
#                     "email",
#                     "password1",
#                     "password2",
#                     "is_staff",
#                     "is_active",
#                     "is_superuser",
#                 ),
#             },
#         ),
#     )


# # =====================================================
# # USER PROFILE ADMIN
# # =====================================================

# STATUS_COLORS = {
#     "pending": "secondary",
#     "approved": "success",
#     "rejected": "danger",
# }


# @admin.register(UserProfile)
# class UserProfileAdmin(admin.ModelAdmin):
#     list_display = (
#         "user",
#         "display_last_name",
#         "phone",
#         # "country_of_residence",
#         "membership_role",
#         "colored_status",
#         "created_at",
#         "thumbnail",
#     )

#     search_fields = (
#         "user__email",
#         "first_name",
#         "last_name",
#         "phone",
#     )

#     list_filter = (
#         "status",
#         "membership_role",
#         # "country_of_residence",
#     )

#     readonly_fields = (
#         "created_at",
#         "updated_at",
#         "thumbnail",
#         "social_registration_code",
#         "economic_registration_code",
#     )

#     actions = ("valider_profils", "refuser_profils")

#     # ---------- HELPERS ----------

#     def display_full_name(self, obj):
#         return f"{obj.last_name or ''} {obj.first_name or ''}".strip()

#     display_full_name.short_description = "Nom complet"

#     def thumbnail(self, obj):
#         if obj.profile_picture:
#             return format_html(
#                 '<img src="{}" style="height:50px; border-radius:6px;" />',
#                 obj.profile_picture.url,
#             )
#         return "—"

#     thumbnail.short_description = "Photo"

#     def colored_status(self, obj):
#         color = STATUS_COLORS.get(obj.status, "secondary")
#         return mark_safe(
#             f'<span class="badge bg-{color}">{obj.get_status_display()}</span>'
#         )

#     colored_status.short_description = "Statut"

#     # ---------- ACTIONS ----------

#     @admin.action(description="✅ Valider les profils sélectionnés")
#     def valider_profils(self, request, queryset):
#         updated = queryset.update(status=UserProfile.Status.APPROVED)
#         self.message_user(request, f"{updated} profil(s) validé(s).")

#     @admin.action(description="❌ Refuser les profils sélectionnés")
#     def refuser_profils(self, request, queryset):
#         for profile in queryset:
#             profile.status = UserProfile.Status.REJECTED
#             profile.save(update_fields=["status"])

#             send_mail(
#                 subject=_("Votre profil a été refusé"),
#                 message=_(
#                     "Bonjour {name},\n\n"
#                     "Votre profil a été refusé. "
#                     "Merci de contacter l’administrateur pour plus de détails."
#                 ).format(name=self.display_full_name(profile)),
#                 from_email=settings.DEFAULT_FROM_EMAIL,
#                 recipient_list=[profile.user.email],
#                 fail_silently=True,
#             )

#         self.message_user(
#             request,
#             f"{queryset.count()} profil(s) refusé(s) et notifié(s).",
#         )


# # =====================================================
# # ROLES ADMINS
# # =====================================================

# @admin.register(UserRole)
# class UserRoleAdmin(admin.ModelAdmin):
#     list_display = ("name", "description")
#     search_fields = ("name",)


# @admin.register(MembershipRole)
# class MembershipRoleAdmin(admin.ModelAdmin):
#     list_display = ("name", "description")
#     search_fields = ("name",)


# @admin.register(AdminRole)
# class AdminRoleAdmin(admin.ModelAdmin):
#     list_display = ("name", "is_active", "created_at")
#     readonly_fields = ("created_at", "updated_at")
#     list_filter = ("is_active",)
#     ordering = ("-created_at",)


# @admin.register(UserUserRole)
# class UserUserRoleAdmin(admin.ModelAdmin):
#     list_display = ("user", "role", "is_active", "created_at")
#     readonly_fields = ("created_at", "updated_at")
#     list_filter = ("role", "is_active")
#     ordering = ("-created_at",)


# # =====================================================
# # DASHBOARD NOTES ADMIN
# # =====================================================

# @admin.register(DashboardNote)
# class DashboardNoteAdmin(admin.ModelAdmin):
#     list_display = ("title", "user", "created_at")
#     search_fields = ("title", "user__email")
#     ordering = ("-created_at",)





# # accounts_users/admin.py
# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin
# from django.utils.html import format_html
# from django.utils.safestring import mark_safe
# from django.core.mail import send_mail
# from django.conf import settings

# from accounts_users.models.users import CustomUser
# from accounts_users.forms.auth_forms import CustomUserCreationForm, CustomUserChangeForm
# from accounts_users.models.users_profile import UserProfile
# from accounts_users.models.role import UserRole
# from accounts_users.models.membership_role import MembershipRole
# from accounts_users.models.admin_roles import AdminRole
# from accounts_users.models.user_role import UserRole as UserUserRole  # Renommage pour éviter conflit
# from accounts_users.models import DashboardNote

# # -----------------------------
# # CustomUser Admin
# # -----------------------------

# @admin.register(CustomUser)
# class CustomUserAdmin(UserAdmin):
#     add_form = CustomUserCreationForm
#     form = CustomUserChangeForm
#     model = CustomUser
#     list_display = ["email", "is_active", "is_staff", "is_superuser", "date_joined"]
#     list_filter = ("is_active", "is_staff", "is_superuser")
#     search_fields = ("email",)
#     ordering = ("-date_joined",)
#     readonly_fields = ("date_joined",)

#     fieldsets = (
#         (None, {"fields": ("email", "password")}),
#         ("Permissions", {"fields": ("is_staff", "is_active", "is_superuser", "groups", "user_permissions")}),
#         ("Dates", {"fields": ("last_login", "date_joined")}),
#     )
#     add_fieldsets = (
#         (None, {
#             "classes": ("wide",),
#             "fields": ("email", "password1", "password2", "is_staff", "is_active", "is_superuser")}
#         ),
#     )

# # -----------------------------
# # UserProfile Admin
# # -----------------------------

# STATUS_COLORS = {
#     'pending': 'secondary',
#     'approved': 'success',
#     'rejected': 'danger',
# }

# @admin.register(UserProfile)
# class UserProfileAdmin(admin.ModelAdmin):
#     list_display = [
#         'user', 'full_name', 'phone', 'country',
#         'role', 'membership_role', 'colored_status', 'created_at', 'thumbnail'
#     ]
#     search_fields = ['user__email', 'full_name', 'phone']
#     list_filter = ['country', 'role', 'membership_role', 'status']
#     readonly_fields = ['created_at', 'updated_at', 'thumbnail']
#     actions = ['valider_profils', 'refuser_profils']

#     def thumbnail(self, obj):
#         if obj.profile_picture:
#             return format_html('<img src="{}" style="height:50px; border-radius:5px;" />', obj.profile_picture.url)
#         return "-"
#     thumbnail.short_description = "Photo"

#     def colored_status(self, obj):
#         color = STATUS_COLORS.get(obj.status, 'secondary')
#         return mark_safe(f'<span class="badge bg-{color}">{obj.get_status_display()}</span>')
#     colored_status.short_description = "Statut"

#     def valider_profils(self, request, queryset):
#         updated = queryset.update(status='approved')
#         self.message_user(request, f"{updated} profil(s) validé(s).")
#     valider_profils.short_description = "✅ Valider les profils sélectionnés"

#     def refuser_profils(self, request, queryset):
#         for profile in queryset:
#             profile.status = 'rejected'
#             profile.save()
#             send_mail(
#                 subject="Votre profil a été refusé",
#                 message=f"Bonjour {profile.full_name},\n\nVotre profil a été refusé. Merci de contacter l’administrateur pour plus de détails.",
#                 from_email=settings.DEFAULT_FROM_EMAIL,
#                 recipient_list=[profile.user.email],
#                 fail_silently=True,
#             )
#         self.message_user(request, f"{queryset.count()} profil(s) refusé(s) et notifié(s).")
#     refuser_profils.short_description = "❌ Refuser les profils sélectionnés"

# # -----------------------------
# # Roles Admins
# # -----------------------------

# @admin.register(UserRole)
# class RoleAdmin(admin.ModelAdmin):
#     list_display = ['name', 'description']
#     search_fields = ['name']

# @admin.register(MembershipRole)
# class MembershipRoleAdmin(admin.ModelAdmin):
#     list_display = ['name', 'description']
#     search_fields = ['name']

# @admin.register(AdminRole)
# class AdminRoleAdmin(admin.ModelAdmin):
#     list_display = ('name', 'is_active', 'created_at')
#     readonly_fields = ('created_at', 'updated_at')
#     ordering = ('created_at',)
#     list_filter = ('is_active',)

# @admin.register(UserUserRole)
# class UserUserRoleAdmin(admin.ModelAdmin):
#     list_display = ('user', 'role', 'is_active', 'created_at')
#     readonly_fields = ('created_at', 'updated_at')
#     ordering = ('created_at',)
#     list_filter = ('role', 'is_active')

# # -----------------------------
# # Dashboard Notes Admin
# # -----------------------------

# @admin.register(DashboardNote)
# class DashboardNoteAdmin(admin.ModelAdmin):
#     list_display = ('title', 'user', 'created_at')
#     search_fields = ('title', 'user__email')
