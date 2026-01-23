# dashboard/admin/dashboard_note_admin.py
from __future__ import annotations

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from dashboard.models.dashboard_note import DashboardNote


def _has_field(model, field_name: str) -> bool:
    try:
        model._meta.get_field(field_name)
        return True
    except Exception:
        return False


@admin.register(DashboardNote)
class DashboardNoteAdmin(admin.ModelAdmin):
    """
    Admin Notes (dashboard)
    - suppose que le modèle a un champ FK `author` (comme ton fichier l'indique)
    - compatible si certains champs optionnels existent (is_pinned/is_archived, etc.)
    """

    list_display = (
        "title",
        "author",
        "visibility_badge",
        "preview_content",
        "created_at",
        "updated_at",
    )
    list_filter = tuple([f for f in ("is_public", "created_at") if _has_field(DashboardNote, f)])
    search_fields = ("title", "content", "author__email", "author__first_name", "author__last_name")
    ordering = ("-created_at",)

    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ("author",)

    fieldsets = (
        (None, {"fields": tuple([f for f in ("title", "author", "is_public", "content") if _has_field(DashboardNote, f)])}),
        (_("Options"), {"fields": tuple([f for f in ("is_pinned", "is_archived") if _has_field(DashboardNote, f)])}),
        (_("Métadonnées"), {"fields": ("created_at", "updated_at")}),
    )

    actions = ["make_public", "make_private"]

    @admin.display(description=_("Visibilité"))
    def visibility_badge(self, obj: DashboardNote):
        if not _has_field(DashboardNote, "is_public"):
            return "—"
        is_public = bool(getattr(obj, "is_public", False))
        css = "success" if is_public else "secondary"
        label = _("Public") if is_public else _("Privé")
        return format_html('<span class="badge bg-{}">{}</span>', css, label)

    @admin.display(description=_("Aperçu"))
    def preview_content(self, obj: DashboardNote):
        text = (getattr(obj, "content", "") or "").strip()
        if not text:
            return "—"
        if len(text) > 120:
            text = text[:120] + "…"
        return format_html(
            "<div style='max-width:520px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;'>{}</div>",
            text,
        )

    @admin.action(description=_("Rendre public"))
    def make_public(self, request, queryset):
        if not _has_field(DashboardNote, "is_public"):
            self.message_user(request, _("Champ is_public introuvable sur ce modèle."))
            return
        n = queryset.update(is_public=True)
        self.message_user(request, _("%(n)s note(s) rendue(s) publique(s).") % {"n": n})

    @admin.action(description=_("Rendre privé"))
    def make_private(self, request, queryset):
        if not _has_field(DashboardNote, "is_public"):
            self.message_user(request, _("Champ is_public introuvable sur ce modèle."))
            return
        n = queryset.update(is_public=False)
        self.message_user(request, _("%(n)s note(s) rendue(s) privée(s).") % {"n": n})






# # dashboard/admin/notes_admin.py

# from django.contrib import admin
# from dashboard.models.dashboard_note import DashboardNote
# from django.utils.html import format_html
# from django.utils.translation import gettext_lazy as _

# @admin.register(DashboardNote)
# class DashboardNoteAdmin(admin.ModelAdmin):
#     list_display = ("title", "author", "preview_content", "is_public", "created_at")
#     list_filter = ("is_public", "created_at")
#     search_fields = ("title", "content", "author__email", "author__first_name", "author__last_name")
#     ordering = ("-created_at",)
#     readonly_fields = ("created_at", "updated_at")

#     fieldsets = (
#         (None, {
#             "fields": ("title", "author", "is_public", "content")
#         }),
#         (_("Métadonnées"), {
#             "fields": ("created_at", "updated_at"),
#         }),
#     )

#     def preview_content(self, obj):
#         return format_html(
#             "<div style='max-width: 400px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;'>{}</div>",
#             obj.content[:100]
#         )
#     preview_content.short_description = _("Aperçu")
