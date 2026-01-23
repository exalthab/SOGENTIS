# economic/formations/admin/course_admin.py
from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from parler.admin import TranslatableAdmin

from ..models import Course

try:
    from ..models import Module
except Exception:
    Module = None

try:
    from ..models import CourseSession
except Exception:
    CourseSession = None

try:
    from ..models import CourseInstructor
except Exception:
    CourseInstructor = None


# -----------------------------
# Inlines
# -----------------------------
if CourseInstructor:
    class CourseInstructorInline(admin.TabularInline):
        model = CourseInstructor
        extra = 0
        autocomplete_fields = ("user",)
        fields = ("user", "role", "display_order", "is_active")
        ordering = ("display_order",)


if Module:
    class ModuleInline(admin.TabularInline):
        model = Module
        extra = 0
        fields = ("order", "is_active")
        ordering = ("order",)
        show_change_link = True


if CourseSession:
    class CourseSessionInline(admin.TabularInline):
        model = CourseSession
        extra = 0
        fields = (
            "title",
            "status",
            "is_active",
            "start_at",
            "end_at",
            "seat_limit",
            "location",
            "meeting_url",
            "enroll_open_at",
            "enroll_close_at",
        )
        ordering = ("-start_at",)
        show_change_link = True


# -----------------------------
# Admin
# -----------------------------
@admin.register(Course)
class CourseAdmin(TranslatableAdmin):
    list_display = (
        "get_title",
        "slug",
        "category",
        "type",
        "level",
        "price",
        "currency",
        "is_featured",
        "is_active",
        "published_at",
        "created_at",
    )
    list_filter = ("is_active", "is_featured", "type", "level", "currency", "category")
    search_fields = ("translations__title", "slug")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "created_at"

    fieldsets = (
        (None, {"fields": ("is_active", "is_featured", "category", "slug")}),
        (_("Type & niveau"), {"fields": ("type", "level", "language", "duration_hours")}),
        (_("Tarification"), {"fields": ("price", "currency")}),
        (_("Hybride / Présentiel (par défaut)"), {"fields": ("start_date", "end_date", "location", "meeting_url", "seat_limit")}),
        (_("Média"), {"fields": ("cover_image", "promo_video_url")}),
        (_("Contenu"), {"fields": ("title", "short_description", "description")}),
        (_("Publication"), {"fields": ("published_at",)}),
        (_("Audit"), {"fields": ("created_at", "updated_at")}),
    )

    inlines = [i for i in (
        CourseInstructorInline if CourseInstructor else None,
        ModuleInline if Module else None,
        CourseSessionInline if CourseSession else None,
    ) if i]

    def get_title(self, obj: Course):
        return obj.safe_translation_getter("title", any_language=True)

    get_title.short_description = _("Titre")





# # economic/formations/admin/course_admin.py
# from django.contrib import admin
# from django.utils.translation import gettext_lazy as _
# from parler.admin import TranslatableAdmin

# from ..models import Course

# # ---------- Inlines optionnels ----------

# try:
#     from ..models import Module
# except Exception:
#     Module = None

# try:
#     from ..models import CourseSession
# except Exception:
#     CourseSession = None


# if Module:
#     class ModuleInline(admin.TabularInline):
#         model = Module
#         extra = 0
#         fields = ("title", "order")
#         ordering = ("order",)
#         show_change_link = True


# if CourseSession:
#     class CourseSessionInline(admin.TabularInline):
#         model = CourseSession
#         extra = 0
#         fields = (
#             "starts_at",
#             "ends_at",
#             "location",
#             "meeting_url",
#             "capacity",
#             "is_cancelled",
#         )
#         ordering = ("starts_at",)
#         show_change_link = True


# # ---------- Course admin ----------

# @admin.register(Course)
# class CourseAdmin(TranslatableAdmin):
#     list_display = (
#         "get_title",
#         "slug",
#         "category",
#         "type",
#         "level",
#         "price",
#         "is_featured",
#         "is_active",
#         "created_at",
#     )

#     list_filter = (
#         "is_active",
#         "is_featured",
#         "type",
#         "level",
#         "category",
#     )

#     search_fields = (
#         "translations__title",
#         "slug",
#     )

#     prepopulated_fields = {}
#     ordering = ("-created_at",)
#     readonly_fields = ("created_at",)

#     fieldsets = (
#         (None, {
#             "fields": (
#                 "is_active",
#                 "is_featured",
#                 "slug",
#                 "category",
#             )
#         }),
#         (_("Type & niveau"), {
#             "fields": (
#                 "type",
#                 "level",
#                 "language",
#                 "duration_hours",
#                 "price",
#             )
#         }),
#         (_("Contenu"), {
#             "fields": (
#                 "title",
#                 "short_description",
#                 "description",
#             )
#         }),
#         (_("Publication"), {
#             "fields": (
#                 "published_at",
#             )
#         }),
#         (_("Audit"), {
#             "fields": (
#                 "created_at",
#             )
#         }),
#     )

#     inlines = [i for i in (
#         ModuleInline if Module else None,
#         CourseSessionInline if CourseSession else None,
#     ) if i]

#     # ---------- Helpers ----------

#     def get_title(self, obj):
#         return obj.safe_translation_getter("title", any_language=True)

#     get_title.short_description = _("Titre")





# # economic/formations/admin/course_admin.py
# from django.contrib import admin
# from parler.admin import TranslatableAdmin

# from ..models import Course


# @admin.register(Course)
# class CourseAdmin(TranslatableAdmin):
#     list_display = ("get_title", "slug", "is_active", "created_at")
#     list_filter = ("is_active",)
#     search_fields = ("translations__title",)
#     ordering = ("-created_at",)

#     fieldsets = (
#         (None, {
#             "fields": ("slug", "is_active"),
#         }),
#         ("Contenu", {
#             "fields": ("title", "description"),
#         }),
#         ("Système", {
#             "fields": ("created_at",),
#         }),
#     )

#     readonly_fields = ("created_at",)

#     def get_title(self, obj):
#         return obj.safe_translation_getter("title", any_language=True)

#     get_title.short_description = "Titre"
