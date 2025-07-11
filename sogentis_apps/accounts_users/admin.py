# accounts_users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from accounts_users.models.users import CustomUser
from accounts_users.models.users_profile import UserProfile
from accounts_users.models.membership_role import MembershipRole
from accounts_users.models.user_role import UserRole
from accounts_users.models.admin_roles import AdminRole
from accounts_users.admin.base_admin import BaseAdmin


@admin.register(CustomUser)
class UserAdmin(BaseUserAdmin):
    list_display = ("email", "is_staff", "is_active", "date_joined")
    search_fields = ("email",)
    ordering = ("-date_joined",)
    readonly_fields = ("date_joined",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "is_active", "is_staff", "is_superuser")}
        ),
    )

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin, BaseAdmin):
    model = CustomUser

    list_display = ("email", "is_active", "is_staff", "is_superuser", "date_joined")
    list_filter = ("is_active", "is_staff", "is_superuser")
    search_fields = ("email",)
    ordering = ("-date_joined",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "is_staff", "is_active")}
        ),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'user', 'phone', 'country', 'membership_role', 'is_validated')
    search_fields = ('full_name', 'user__email')
    list_filter = ('membership_role', 'is_validated')

@admin.register(MembershipRole)
class MembershipRoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')

admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'is_active', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('created_at',)
    list_filter = ('role', 'is_active')

@admin.register(AdminRole)
class AdminRoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('created_at',)
    list_filter = ('is_active',)





## accounts_users/admin.py -> 01/07
# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin
# from accounts_users.models.users import CustomUser
# from accounts_users.forms.auth_forms import CustomUserCreationForm, CustomUserChangeForm
# from accounts_users.models.users_profile import UserProfile
# from accounts_users.models.role import UserRole

# @admin.register(CustomUser)
# class CustomUserAdmin(UserAdmin):
#     add_form = CustomUserCreationForm
#     form = CustomUserChangeForm
#     model = CustomUser
#     list_display = ["email", "is_active", "is_staff"]
#     fieldsets = (
#         (None, {"fields": ("email", "password")}),
#         ("Permissions", {"fields": ("is_staff", "is_active", "is_superuser", "groups", "user_permissions")}),
#         ("Dates", {"fields": ("last_login",)}),
#     )
#     add_fieldsets = (
#         (None, {
#             "classes": ("wide",),
#             "fields": ("email", "password1", "password2", "is_staff", "is_active")}
#         ),
#     )
#     search_fields = ("email",)
#     ordering = ("email",)

# @admin.register(UserProfile)
# class UserProfileAdmin(admin.ModelAdmin):
#     list_display = ['user', 'full_name', 'phone', 'country', 'role']


# @admin.register(UserRole)
# class RoleAdmin(admin.ModelAdmin):
#     list_display = ['name', 'description']







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

# from .models import DashboardNote


# @admin.register(DashboardNote)
# class DashboardNoteAdmin(admin.ModelAdmin):
#     list_display = ('title', 'user', 'created_at')
#     search_fields = ('title', 'user__email')

# @admin.register(CustomUser)
# class CustomUserAdmin(UserAdmin):
#     add_form = CustomUserCreationForm
#     form = CustomUserChangeForm
#     model = CustomUser
#     list_display = ["email", "is_active", "is_staff", "is_superuser"]
#     fieldsets = (
#         (None, {"fields": ("email", "password")}),
#         ("Permissions", {"fields": ("is_staff", "is_active", "is_superuser", "groups", "user_permissions")}),
#         ("Dates", {"fields": ("last_login",)}),
#     )
#     add_fieldsets = (
#         (None, {
#             "classes": ("wide",),
#             "fields": ("email", "password1", "password2", "is_staff", "is_active")}
#         ),
#     )
#     search_fields = ("email",)
#     ordering = ("email",)


# @admin.register(UserProfile)
# class UserProfileAdmin(admin.ModelAdmin):
#     list_display = [
#         'user', 'full_name', 'phone', 'country',
#         'role', 'membership_role',
#         'status',  # ou 'is_verified' selon ton modèle
#         'created_at', 'thumbnail'
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

#     def valider_profils(self, request, queryset):
#         updated = queryset.update(status='approved')
#         self.message_user(request, f"{updated} profil(s) validé(s).")
#     valider_profils.short_description = "✅ Valider les profils sélectionnés"

#     def refuser_profils(self, request, queryset):
#         updated = queryset.update(status='rejected')
#         self.message_user(request, f"{updated} profil(s) refusé(s).")
#     refuser_profils.short_description = "❌ Refuser les profils sélectionnés"


# @admin.register(UserRole)
# class UserRoleAdmin(admin.ModelAdmin):
#     list_display = ['name', 'description']
#     search_fields = ['name']


# @admin.register(MembershipRole)
# class MembershipRoleAdmin(admin.ModelAdmin):
#     list_display = ['name', 'description']
#     search_fields = ['name']

# STATUS_COLORS = {
#     'pending': 'secondary',
#     'approved': 'success',
#     'rejected': 'danger',
# }

# def colored_status(self, obj):
#     color = STATUS_COLORS.get(obj.status, 'secondary')
#     return mark_safe(f'<span class="badge bg-{color}">{obj.get_status_display()}</span>')
# colored_status.short_description = "Statut"

# list_display = [
#     'user', 'full_name', 'phone', 'country',
#     'role', 'membership_role', 'colored_status', 'created_at', 'thumbnail'
# ]
# list_filter = ['status', 'country', 'role', 'membership_role']


# def refuser_profils(self, request, queryset):
#     for profile in queryset:
#         profile.status = 'rejected'
#         profile.save()
#         send_mail(
#             subject="Votre profil a été refusé",
#             message=f"Bonjour {profile.full_name},\n\nVotre profil a été refusé. Merci de contacter l’administrateur pour plus de détails.",
#             from_email=settings.DEFAULT_FROM_EMAIL,
#             recipient_list=[profile.user.email],
#             fail_silently=True,
#         )
#     self.message_user(request, f"{queryset.count()} profil(s) refusé(s) et notifié(s).")



