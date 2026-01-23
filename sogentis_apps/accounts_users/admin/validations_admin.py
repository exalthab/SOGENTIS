# accounts_users/admin/validations_admin.py
from __future__ import annotations

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from accounts_users.admin.admin_base import BaseAdmin

# Imports optionnels (ne doivent jamais casser l'admin)
try:
    from accounts_users.models.user_validation import UserValidation  # 1 user = 1 validation globale
except Exception:
    UserValidation = None  # type: ignore

try:
    from accounts_users.models.profile_validation import ProfileValidation  # workflow social (optionnel)
except Exception:
    ProfileValidation = None  # type: ignore


# =====================================================
# Helpers
# =====================================================
def _status_badge(status: str, label: str | None = None) -> str:
    st = (status or "").lower().strip()
    css = {
        "approved": "success",
        "active": "success",
        "validated": "success",
        "pending": "warning",
        "refused": "danger",
        "rejected": "danger",
        "cancelled": "secondary",
        "canceled": "secondary",
        "suspended": "warning",
    }.get(st, "secondary")
    text = (label or status or "—") or "—"
    return format_html('<span class="badge bg-{}">{}</span>', css, text)


# =====================================================
# UserValidationAdmin (si présent)
# =====================================================
if UserValidation:

    @admin.register(UserValidation)
    class UserValidationAdmin(BaseAdmin):
        """
        Validation globale attachée à l'utilisateur (1:1).
        """

        list_display = (
            "user",
            "status_badge",
            "decided_at",
            "decided_by",
            "created_at_display",
        )
        list_filter = ("status", "created_at")
        search_fields = ("user__email", "user__username")
        ordering = ("-created_at",)

        autocomplete_fields = ("user", "decided_by")

        fieldsets = (
            (_("Utilisateur"), {"fields": ("user",)}),
            (_("Décision"), {"fields": ("status", "reason", "decided_at", "decided_by")}),
            (_("Audit"), {"fields": ("created_at", "updated_at")}),
        )

        @admin.display(description=_("Statut"), ordering="status")
        def status_badge(self, obj):
            # get_status_display si dispo
            try:
                label = obj.get_status_display()
            except Exception:
                label = getattr(obj, "status", "")
            return _status_badge(getattr(obj, "status", ""), label)


# =====================================================
# ProfileValidationAdmin (si présent)
# =====================================================
if ProfileValidation:

    @admin.register(ProfileValidation)
    class ProfileValidationAdmin(BaseAdmin):
        """
        Workflow de validation social (optionnel).
        """

        list_display = (
            "profile",
            "status_badge",
            "validated_at",
            "validated_by",
            "created_at_display",
        )
        list_filter = ("status", "created_at")
        search_fields = ("profile__user__email", "profile__user__username")
        ordering = ("-created_at",)

        autocomplete_fields = ("profile", "validated_by")

        fieldsets = (
            (_("Profil"), {"fields": ("profile",)}),
            (_("Décision"), {"fields": ("status", "comment", "validated_at", "validated_by")}),
            (_("Audit"), {"fields": ("created_at", "updated_at")}),
        )

        @admin.display(description=_("Statut"), ordering="status")
        def status_badge(self, obj):
            try:
                label = obj.get_status_display()
            except Exception:
                label = getattr(obj, "status", "")
            return _status_badge(getattr(obj, "status", ""), label)
