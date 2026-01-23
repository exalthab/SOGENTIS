# # accounts_users/admin/dashboard_note_admin.py
# from __future__ import annotations

# from django.contrib import admin
# from django.utils.translation import gettext_lazy as _

# from accounts_users.admin.admin_base import BaseAdmin

# # DashboardNote est normalement dans dashboard/
# try:
#     from dashboard.models.dashboard_note import DashboardNote
# except Exception:
#     DashboardNote = None  # type: ignore


# if DashboardNote:

#     @admin.register(DashboardNote)
#     class DashboardNoteAdmin(BaseAdmin):
#         """
#         Notes dashboard (optionnel) — safe import.
#         """

#         list_display = (
#             "title",
#             "user",
#             "is_pinned_display",
#             "created_at_display",
#             "updated_at_display",
#         )
#         search_fields = ("title", "content", "user__email", "user__username")
#         list_filter = ("created_at",)
#         ordering = ("-created_at",)

#         autocomplete_fields = ("user",)

#         fieldsets = (
#             (None, {"fields": ("user", "title", "content")}),
#             (_("Options"), {"fields": tuple([f for f in ("is_pinned", "is_archived") if hasattr(DashboardNote, f)])}),
#             (_("Audit"), {"fields": ("created_at", "updated_at")}),
#         )

#         @admin.display(description=_("Épinglée"))
#         def is_pinned_display(self, obj):
#             if hasattr(obj, "is_pinned"):
#                 return bool(getattr(obj, "is_pinned", False))
#             return False

#         is_pinned_display.boolean = True

