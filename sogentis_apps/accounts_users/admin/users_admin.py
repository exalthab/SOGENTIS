# accounts_users/admin/users_admin.py
from __future__ import annotations

from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from accounts_users.forms.auth_forms import CustomUserCreationForm, CustomUserChangeForm
from accounts_users.models.custom_users import CustomUser

# Imports optionnels (safe)
try:
    from accounts_users.models.user_validation import UserValidation
except Exception:
    UserValidation = None  # type: ignore


def _has_field(model, field_name: str) -> bool:
    try:
        model._meta.get_field(field_name)
        return True
    except Exception:
        return False


@admin.register(CustomUser)
class CustomUserAdmin(DjangoUserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser

    list_display = (
        "email",
        "username_display",
        "is_active",
        "is_staff",
        "is_superuser",
        "validation_badge",
        "date_joined",
    )
    list_filter = ("is_active", "is_staff", "is_superuser")
    ordering = ("-date_joined",)
    readonly_fields = ("last_login", "date_joined")

    # ✅ requis pour autocomplete_fields dans autres apps
    _search = ["email", "first_name", "last_name"]
    if _has_field(CustomUser, "username"):
        _search.append("username")
    search_fields = tuple(_search)

    # Champs safe (si username absent, on ne l'affiche pas)
    _ident_fields = tuple([f for f in ("first_name", "last_name") if _has_field(CustomUser, f)])
    _user_fields = ["email", "password"]
    if _has_field(CustomUser, "username"):
        _user_fields.insert(1, "username")
    fieldsets = (
        (None, {"fields": tuple(_user_fields)}),
        (_("Informations"), {"fields": _ident_fields}),
        (_("Permissions"), {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        (_("Dates"), {"fields": ("last_login", "date_joined")}),
    )

    add_fields = ["email", "password1", "password2", "is_active", "is_staff", "is_superuser"]
    if _has_field(CustomUser, "username"):
        add_fields.insert(1, "username")
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": tuple(add_fields)}),
    )

    @admin.display(description=_("Identifiant"))
    def username_display(self, obj):
        if _has_field(CustomUser, "username"):
            return getattr(obj, "username", "") or "—"
        if hasattr(obj, "get_username"):
            try:
                return obj.get_username() or "—"
            except Exception:
                pass
        return "—"

    @admin.display(description=_("Validation"))
    def validation_badge(self, obj):
        if not UserValidation:
            return "—"
        try:
            v = getattr(obj, "validation", None)
            if not v:
                return "—"
            status = getattr(v, "status", "") or ""
            css = {"approved": "success", "pending": "warning", "refused": "danger"}.get(status, "secondary")

            # label
            try:
                label = v.get_status_display()
            except Exception:
                label = status

            return format_html('<span class="badge bg-{}">{}</span>', css, label or status)
        except Exception:
            return "—"
