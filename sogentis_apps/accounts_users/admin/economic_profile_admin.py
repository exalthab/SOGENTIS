# accounts_users/admin/economic_profile_admin.py
from __future__ import annotations

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from accounts_users.admin.admin_base import BaseAdmin

try:
    from accounts_users.models.users_economic_profile import UserEconomicProfile
except Exception:
    UserEconomicProfile = None  # type: ignore


def _has_field(model, field_name: str) -> bool:
    try:
        model._meta.get_field(field_name)
        return True
    except Exception:
        return False


def _get(obj, *names, default=""):
    for n in names:
        try:
            v = getattr(obj, n, None)
            if v not in (None, ""):
                return v
        except Exception:
            continue
    return default


if UserEconomicProfile:

    @admin.register(UserEconomicProfile)
    class UserEconomicProfileAdmin(BaseAdmin):
        """
        Admin minimal MAIS suffisant pour autocomplete_fields partout (E039).
        """

        list_display = (
            "id",
            "user",
            "full_name",
            "phone_display",
            "role_display",
            "status_badge",
            "created_at_display",
        )

        search_fields = (
            "user__email",
            "user__username",
        ) + tuple([f for f in ("first_name", "last_name", "phone", "phone_number") if _has_field(UserEconomicProfile, f)])

        list_filter = tuple([f for f in ("status", "economic_role") if _has_field(UserEconomicProfile, f)])

        ordering = ("-created_at",)
        autocomplete_fields = ("user",)

        fieldsets = (
            (_("Utilisateur"), {"fields": ("user",)}),
            (_("Identité"), {"fields": tuple([f for f in ("first_name", "last_name", "middle_names", "nickname") if _has_field(UserEconomicProfile, f)])}),
            (_("Contact"), {"fields": tuple([f for f in ("phone", "phone_number", "address", "city_of_residence", "country_of_residence") if _has_field(UserEconomicProfile, f)])}),
            (_("Rôle / Statut"), {"fields": tuple([f for f in ("economic_role", "status") if _has_field(UserEconomicProfile, f)])}),
            (_("Audit"), {"fields": ("created_at", "updated_at")}),
        )

        @admin.display(description=_("Nom"))
        def full_name(self, obj):
            first = _get(obj, "first_name", default="")
            last = _get(obj, "last_name", default="")
            s = f"{last} {first}".strip()
            return s or "—"

        @admin.display(description=_("Téléphone"))
        def phone_display(self, obj):
            return _get(obj, "phone", "phone_number", default="—")

        @admin.display(description=_("Rôle"))
        def role_display(self, obj):
            if _has_field(UserEconomicProfile, "economic_role"):
                try:
                    return obj.get_economic_role_display()
                except Exception:
                    return _get(obj, "economic_role", default="—")
            return "—"

        @admin.display(description=_("Statut"))
        def status_badge(self, obj):
            if not _has_field(UserEconomicProfile, "status"):
                return "—"
            st = str(_get(obj, "status", default="")).lower()
            css = {
                "approved": "success",
                "active": "success",
                "pending": "warning",
                "refused": "danger",
                "rejected": "danger",
                "suspended": "warning",
            }.get(st, "secondary")
            try:
                label = obj.get_status_display()
            except Exception:
                label = _get(obj, "status", default="—")
            return format_html('<span class="badge bg-{}">{}</span>', css, label or "—")
