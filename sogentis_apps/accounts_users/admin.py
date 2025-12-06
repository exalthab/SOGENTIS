from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.core.mail import send_mail
from django.conf import settings

from accounts_users.models.users import CustomUser
from accounts_users.forms.auth_forms import CustomUserCreationForm, CustomUserChangeForm
from accounts_users.models.users_profile import UserProfile
from accounts_users.models.role import UserRole
from accounts_users.models.membership_role import MembershipRole
from accounts_users.models.admin_roles import AdminRole
from accounts_users.models.user_role import UserRole as UserUserRole  # Renommage pour éviter conflit
from accounts_users.models import DashboardNote

# -----------------------------
# CustomUser Admin
# -----------------------------

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ["email", "is_active", "is_staff", "is_superuser", "date_joined"]
    list_filter = ("is_active", "is_staff", "is_superuser")
    search_fields = ("email",)
    ordering = ("-date_joined",)
    readonly_fields = ("date_joined",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "is_superuser", "groups", "user_permissions")}),
        ("Dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "is_staff", "is_active", "is_superuser")}
        ),
    )

# -----------------------------
# UserProfile Admin
# -----------------------------

STATUS_COLORS = {
    'pending': 'secondary',
    'approved': 'success',
    'rejected': 'danger',
}

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'full_name', 'phone', 'country',
        'role', 'membership_role', 'colored_status', 'created_at', 'thumbnail'
    ]
    search_fields = ['user__email', 'full_name', 'phone']
    list_filter = ['country', 'role', 'membership_role', 'status']
    readonly_fields = ['created_at', 'updated_at', 'thumbnail']
    actions = ['valider_profils', 'refuser_profils']

    def thumbnail(self, obj):
        if obj.profile_picture:
            return format_html('<img src="{}" style="height:50px; border-radius:5px;" />', obj.profile_picture.url)
        return "-"
    thumbnail.short_description = "Photo"

    def colored_status(self, obj):
        color = STATUS_COLORS.get(obj.status, 'secondary')
        return mark_safe(f'<span class="badge bg-{color}">{obj.get_status_display()}</span>')
    colored_status.short_description = "Statut"

    def valider_profils(self, request, queryset):
        updated = queryset.update(status='approved')
        self.message_user(request, f"{updated} profil(s) validé(s).")
    valider_profils.short_description = "✅ Valider les profils sélectionnés"

    def refuser_profils(self, request, queryset):
        for profile in queryset:
            profile.status = 'rejected'
            profile.save()
            send_mail(
                subject="Votre profil a été refusé",
                message=f"Bonjour {profile.full_name},\n\nVotre profil a été refusé. Merci de contacter l’administrateur pour plus de détails.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[profile.user.email],
                fail_silently=True,
            )
        self.message_user(request, f"{queryset.count()} profil(s) refusé(s) et notifié(s).")
    refuser_profils.short_description = "❌ Refuser les profils sélectionnés"

# -----------------------------
# Roles Admins
# -----------------------------

@admin.register(UserRole)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']

@admin.register(MembershipRole)
class MembershipRoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']

@admin.register(AdminRole)
class AdminRoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('created_at',)
    list_filter = ('is_active',)

@admin.register(UserUserRole)
class UserUserRoleAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'is_active', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('created_at',)
    list_filter = ('role', 'is_active')

# -----------------------------
# Dashboard Notes Admin
# -----------------------------

@admin.register(DashboardNote)
class DashboardNoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at')
    search_fields = ('title', 'user__email')
