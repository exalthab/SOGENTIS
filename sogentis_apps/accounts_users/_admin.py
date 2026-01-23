# #accounts_users/admin.py
# from __future__ import annotations

# from django.contrib import admin
# from django.contrib.auth import get_user_model
# from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
# from django.utils.html import format_html
# from django.utils.translation import gettext_lazy as _

# from accounts_users.forms.auth_forms import CustomUserCreationForm, CustomUserChangeForm, AuthenticationEmailForm

# from accounts_users.models.custom_users import CustomUser
# from accounts_users.models.membership_role import MembershipRole
# from accounts_users.models.user_role import UserRole
# from accounts_users.models.admin_roles import AdminRole

# # --------- Imports optionnels (ne doivent jamais casser l'admin) ----------
# try:
#     from accounts_users.models.users_profile import UserProfile as SocialUserProfile  # profil identité social
# except Exception:
#     SocialUserProfile = None  # type: ignore

# try:
#     from accounts_users.models.users_economic_profile import UserEconomicProfile  # profil économique
# except Exception:
#     UserEconomicProfile = None  # type: ignore

# try:
#     from accounts_users.models.user_validation import UserValidation  # validation globale (1 user = 1 validation)
# except Exception:
#     UserValidation = None  # type: ignore

# try:
#     from accounts_users.models.profile_validation import ProfileValidation  # workflow social (optionnel)
# except Exception:
#     ProfileValidation = None  # type: ignore

# # DashboardNote est normalement dans dashboard/, donc import safe uniquement.
# try:
#     from dashboard.models.dashboard_note import DashboardNote  # type: ignore
# except Exception:
#     DashboardNote = None  # type: ignore

# # ⚠️ Forcer le chargement des sous-admins (safe)
# for _mod in (
#     "accounts_users.admin.admin_social_profile",
#     "accounts_users.admin.admin_client_profile",
#     "accounts_users.admin.admin_vendor_profile",
#     "accounts_users.admin.admin_company_profile",
# ):
#     try:
#         __import__(_mod)
#     except Exception:
#         pass


# User = get_user_model()


# # =====================================================
# # Helpers admin (robuste)
# # =====================================================
# class SafeFieldsAdminMixin:
#     @staticmethod
#     def _has_field(model, field_name: str) -> bool:
#         try:
#             model._meta.get_field(field_name)
#             return True
#         except Exception:
#             return False

#     @staticmethod
#     def _get(obj, *names, default=""):
#         for n in names:
#             try:
#                 v = getattr(obj, n)
#                 if v not in (None, ""):
#                     return v
#             except Exception:
#                 continue
#         return default


# # =====================================================
# # CUSTOM USER ADMIN
# # =====================================================
# @admin.register(CustomUser)
# class CustomUserAdmin(DjangoUserAdmin):
#     add_form = CustomUserCreationForm
#     form = CustomUserChangeForm
#     model = CustomUser

#     list_display = (
#         "email",
#         "username",
#         "is_active",
#         "is_staff",
#         "is_superuser",
#         "validation_badge",
#         "date_joined",
#     )
#     list_filter = ("is_active", "is_staff", "is_superuser")
#     search_fields = ("email", "username", "first_name", "last_name")
#     ordering = ("-date_joined",)
#     readonly_fields = ("last_login", "date_joined")

#     fieldsets = (
#         (None, {"fields": ("email", "username", "password")}),
#         (_("Informations"), {"fields": ("first_name", "last_name")}),
#         (
#             _("Permissions"),
#             {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")},
#         ),
#         (_("Dates"), {"fields": ("last_login", "date_joined")}),
#     )

#     add_fieldsets = (
#         (
#             None,
#             {
#                 "classes": ("wide",),
#                 "fields": ("email", "username", "password1", "password2", "is_active", "is_staff", "is_superuser"),
#             },
#         ),
#     )

#     def validation_badge(self, obj):
#         """
#         Badge validation globale (si UserValidation existe).
#         """
#         if not UserValidation:
#             return "—"
#         try:
#             v = getattr(obj, "validation", None)
#             if not v:
#                 return "—"
#             status = getattr(v, "status", "")
#             css = {
#                 "approved": "success",
#                 "pending": "warning",
#                 "refused": "danger",
#             }.get(status, "secondary")
#             label = dict(getattr(v, "UserValidationStatus", {}).choices).get(status, status) if hasattr(v, "UserValidationStatus") else status
#             return format_html('<span class="badge bg-{}">{}</span>', css, label or status)
#         except Exception:
#             return "—"

#     validation_badge.short_description = _("Validation")


# # =====================================================
# # PROFIL ÉCONOMIQUE ADMIN (si présent)
# # =====================================================
# if UserEconomicProfile:

#     @admin.register(UserEconomicProfile)
#     class UserEconomicProfileAdmin(admin.ModelAdmin, SafeFieldsAdminMixin):
#         """
#         Profil économique : CLIENT / VENDOR / B2B…
#         Admin prod-safe : s’adapte si certains champs n'existent pas.
#         """

#         def get_list_display(self, request):
#             base = ["user", "full_name", "phone_display", "economic_role_display", "created_at_display", "picture_thumb"]
#             # status optionnel
#             if self._has_field(self.model, "status"):
#                 base.insert(4, "status_badge")
#             return tuple(base)

#         def get_search_fields(self, request):
#             fields = ["user__email", "user__username"]
#             for f in ("first_name", "last_name", "phone", "phone_number"):
#                 if self._has_field(self.model, f):
#                     fields.append(f)
#             return tuple(fields)

#         def get_list_filter(self, request):
#             filters = []
#             if self._has_field(self.model, "status"):
#                 filters.append("status")
#             if self._has_field(self.model, "economic_role"):
#                 filters.append("economic_role")
#             return tuple(filters)

#         def get_readonly_fields(self, request, obj=None):
#             ro = ["created_at", "updated_at", "picture_thumb"]
#             for f in ("economic_registration_code", "social_registration_code"):
#                 if self._has_field(self.model, f):
#                     ro.append(f)
#             return tuple(ro)

#         def get_fieldsets(self, request, obj=None):
#             fs = [(_("Utilisateur"), {"fields": ("user",)})]

#             ident = []
#             for f in ("first_name", "last_name", "middle_names", "nickname", "date_of_birth", "place_of_birth"):
#                 if self._has_field(self.model, f):
#                     ident.append(f)
#             if ident:
#                 fs.append((_("Identité"), {"fields": tuple(ident)}))

#             residence = []
#             for f in ("country_of_residence", "city_of_residence", "address", "country_of_birth"):
#                 if self._has_field(self.model, f):
#                     residence.append(f)
#             if residence:
#                 fs.append((_("Résidence"), {"fields": tuple(residence)}))

#             contact = []
#             for f in ("phone", "phone_number", "profession", "function"):
#                 if self._has_field(self.model, f):
#                     contact.append(f)
#             if contact:
#                 fs.append((_("Contact / Profession"), {"fields": tuple(contact)}))

#             eco = []
#             for f in ("economic_role",):
#                 if self._has_field(self.model, f):
#                     eco.append(f)
#             if eco:
#                 fs.append((_("Rôle économique"), {"fields": tuple(eco)}))

#             if self._has_field(self.model, "status"):
#                 fs.append((_("Statut"), {"fields": ("status",)}))

#             codes = []
#             for f in ("economic_registration_code", "social_registration_code"):
#                 if self._has_field(self.model, f):
#                     codes.append(f)
#             if codes:
#                 fs.append((_("Codes"), {"fields": tuple(codes)}))

#             dates = []
#             for f in ("created_at", "updated_at"):
#                 if self._has_field(self.model, f):
#                     dates.append(f)
#             if dates:
#                 fs.append((_("Dates"), {"fields": tuple(dates)}))

#             if self._has_field(self.model, "profile_picture"):
#                 fs.append((_("Photo"), {"fields": ("profile_picture", "picture_thumb")}))

#             return tuple(fs)

#         # ---------- helpers ----------
#         def full_name(self, obj):
#             first = self._get(obj, "first_name", default="")
#             last = self._get(obj, "last_name", default="")
#             s = f"{last} {first}".strip()
#             return s or "—"

#         full_name.short_description = _("Nom complet")

#         def phone_display(self, obj):
#             return self._get(obj, "phone", "phone_number", default="—")

#         phone_display.short_description = _("Téléphone")

#         def economic_role_display(self, obj):
#             v = self._get(obj, "economic_role", default="")
#             return v or "—"

#         economic_role_display.short_description = _("Rôle")

#         def created_at_display(self, obj):
#             return self._get(obj, "created_at", default="—")

#         created_at_display.short_description = _("Créé le")

#         def picture_thumb(self, obj):
#             img = getattr(obj, "profile_picture", None)
#             try:
#                 if img and getattr(img, "url", None):
#                     return format_html('<img src="{}" style="height:42px;border-radius:8px;object-fit:cover;" />', img.url)
#             except Exception:
#                 pass
#             return "—"

#         picture_thumb.short_description = _("Photo")

#         def status_badge(self, obj):
#             st = self._get(obj, "status", default="")
#             css = {
#                 "pending": "secondary",
#                 "approved": "success",
#                 "active": "success",
#                 "refused": "danger",
#                 "rejected": "danger",
#                 "suspended": "warning",
#             }.get(str(st), "secondary")
#             # get_status_display si dispo
#             try:
#                 label = obj.get_status_display()
#             except Exception:
#                 label = st
#             return format_html('<span class="badge bg-{}">{}</span>', css, label or st)

#         status_badge.short_description = _("Statut")


# # =====================================================
# # ROLES & CONFIGURATION
# # =====================================================
# @admin.register(UserRole)
# class UserRoleAdmin(admin.ModelAdmin):
#     """
#     UserRole est souvent: code/name/description.
#     On affiche ce qui existe sans casser.
#     """
#     list_display = tuple([f for f in ("code", "name", "label", "description") if hasattr(UserRole, f)]) or ("id",)
#     search_fields = tuple([f for f in ("code", "name", "label") if hasattr(UserRole, f)]) or ("id",)


# @admin.register(MembershipRole)
# class MembershipRoleAdmin(admin.ModelAdmin):
#     list_display = ("code", "label", "is_active")
#     search_fields = ("code", "label")
#     list_filter = ("is_active",)
#     ordering = ("label",)


# @admin.register(AdminRole)
# class AdminRoleAdmin(admin.ModelAdmin):
#     list_display = ("label", "is_active", "created_at")
#     search_fields = ("label",)
#     list_filter = ("is_active",)
#     readonly_fields = ("created_at", "updated_at")
#     ordering = ("label",)


# # =====================================================
# # VALIDATIONS (si présents)
# # =====================================================
# if UserValidation:
#     @admin.register(UserValidation)
#     class UserValidationAdmin(admin.ModelAdmin):
#         list_display = ("user", "status", "decided_at", "decided_by", "created_at")
#         list_filter = ("status",)
#         search_fields = ("user__email", "user__username")
#         readonly_fields = ("created_at", "updated_at", "decided_at", "decided_by")


# if ProfileValidation:
#     @admin.register(ProfileValidation)
#     class ProfileValidationAdmin(admin.ModelAdmin):
#         list_display = ("profile", "status", "validated_at", "validated_by", "created_at")
#         list_filter = ("status",)
#         search_fields = ("profile__user__email",)
#         readonly_fields = ("created_at", "updated_at", "validated_at", "validated_by")


# # =====================================================
# # DASHBOARD NOTES (si présent)
# # =====================================================
# if DashboardNote:
#     @admin.register(DashboardNote)
#     class DashboardNoteAdmin(admin.ModelAdmin):
#         list_display = ("title", "user", "created_at")
#         search_fields = ("title", "user__email")
#         ordering = ("-created_at",)
#         readonly_fields = ("created_at", "updated_at")





# # accounts_users/admin.py
# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin
# from django.utils.html import format_html
# from django.utils.safestring import mark_safe
# from django.utils.translation import gettext_lazy as _

# from accounts_users.models.custom_users import CustomUser
# from accounts_users.forms.auth_forms import (
#     CustomUserCreationForm,
#     CustomUserChangeForm,
# )

# from accounts_users.models.users_economic_profile import UserProfile
# from accounts_users.models.membership_role import MembershipRole
# from accounts_users.models.user_role import UserRole
# from accounts_users.models.admin_roles import AdminRole
# from accounts_users.models import DashboardNote

# # ⚠️ Forcer le chargement des sous-admins
# from accounts_users.admin.admin_social_profile import SocialProfileAdmin  # noqa
# from accounts_users.admin.admin_client_profile import ClientProfileAdmin  # noqa
# from accounts_users.admin.admin_vendor_profile import VendorProfileAdmin  # noqa
# from accounts_users.admin.admin_company_profile import CompanyProfileAdmin  # noqa


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
# # USER PROFILE ADMIN (PLATEFORME / ÉCONOMIQUE)
# # =====================================================
# STATUS_COLORS = {
#     "pending": "secondary",
#     "approved": "success",
#     "rejected": "danger",
# }


# @admin.register(UserProfile)
# class UserProfileAdmin(admin.ModelAdmin):
#     """
#     Profil utilisateur CENTRAL
#     - Client / Vendeur / Entreprise
#     - AUCUNE donnée sociale ici
#     """

#     list_display = (
#         "user",
#         "display_full_name",
#         "phone",
#         "economic_role",
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
#         "economic_role",
#     )

#     readonly_fields = (
#         "created_at",
#         "updated_at",
#         "thumbnail",
#         "economic_registration_code",
#         "social_registration_code",
#     )

#     fieldsets = (
#         (_("Utilisateur"), {
#             "fields": ("user",)
#         }),

#         (_("Identité"), {
#             "fields": (
#                 "first_name",
#                 "last_name",
#                 "middle_names",
#                 "nickname",
#                 "date_of_birth",
#                 "place_of_birth",
#             )
#         }),

#         (_("Résidence"), {
#             "fields": (
#                 "country_of_residence",
#                 "city_of_residence",
#                 "address",
#             )
#         }),

#         (_("Contact / Profession"), {
#             "fields": (
#                 "phone",
#                 "profession",
#                 "function",
#             )
#         }),

#         (_("Rôle économique"), {
#             "fields": (
#                 "economic_role",
#             )
#         }),

#         (_("Statut"), {
#             "fields": (
#                 "status",
#             )
#         }),

#         (_("Codes"), {
#             "fields": (
#                 "economic_registration_code",
#                 "social_registration_code",
#             )
#         }),

#         (_("Dates"), {
#             "fields": (
#                 "created_at",
#                 "updated_at",
#             )
#         }),
#     )

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


# # =====================================================
# # ROLES & CONFIGURATION
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


# # =====================================================
# # DASHBOARD NOTES
# # =====================================================
# @admin.register(DashboardNote)
# class DashboardNoteAdmin(admin.ModelAdmin):
#     list_display = ("title", "user", "created_at")
#     search_fields = ("title", "user__email")
#     ordering = ("-created_at",)
    
    
    
    
    
    
    
    
    
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
