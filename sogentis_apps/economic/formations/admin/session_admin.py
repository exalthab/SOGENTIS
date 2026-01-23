# economic/formations/admin/session_admin.py
from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from ..models import CourseSession


@admin.register(CourseSession)
class CourseSessionAdmin(admin.ModelAdmin):
    list_display = ("__str__", "course", "status", "is_active", "start_at", "end_at", "seat_limit")
    list_filter = ("status", "is_active", "course")
    search_fields = ("title", "course__slug", "course__translations__title", "location")
    ordering = ("-start_at", "-created_at")
    autocomplete_fields = ("course",)
    filter_horizontal = ("instructors",)
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (None, {"fields": ("course", "title", "status", "is_active")}),
        (_("Planning"), {"fields": ("start_at", "end_at", "enroll_open_at", "enroll_close_at")}),
        (_("Logistique"), {"fields": ("seat_limit", "location", "meeting_url")}),
        (_("Formateurs"), {"fields": ("instructors",)}),
        (_("Audit"), {"fields": ("created_at", "updated_at")}),
    )





# # economic/formations/admin/session_admin.py
# from django.contrib import admin
# from django.utils.translation import gettext_lazy as _

# try:
#     from ..models import CourseSession
# except Exception:
#     CourseSession = None


# if CourseSession:
#     @admin.register(CourseSession)
#     class CourseSessionAdmin(admin.ModelAdmin):
#         list_display = ("__str__", "title", "course", "starts_at", "ends_at", "location", "is_cancelled")
#         list_filter = ("is_cancelled", "course")
#         search_fields = ("course__translations__title", "title", "location")
#         ordering = ("-starts_at",)

#         fieldsets = (
#             (None, {"fields": ("course", "title")}),
#             (_("Planification"), {"fields": ("starts_at", "ends_at")}),
#             (_("Lieu / visio"), {"fields": ("location", "meeting_url")}),
#             (_("Capacité"), {"fields": ("capacity",)}),
#             (_("Statut"), {"fields": ("is_cancelled",)}),
#         )
