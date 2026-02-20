# # economic/ecommerce/admin/review_admin.py
from __future__ import annotations

from django.contrib import admin, messages
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from economic.ecommerce.models import Review


# ============================================================
# Actions (prod-safe): modération + soft delete + hard delete
# ============================================================
@admin.action(description=_("Approuver (modération)"))
def action_approve(modeladmin, request, queryset):
    now = timezone.now()
    # ⚠️ update() bypass save/full_clean -> on set tout ce qui est métier
    n = queryset.update(
        is_approved=True,
        is_active=True,
        approved_at=now,
        moderated_by=request.user,
        moderation_note="",
        updated_at=now,
    )
    modeladmin.message_user(
        request,
        _("%(n)s avis approuvé(s).") % {"n": n},
        level=messages.SUCCESS,
    )


@admin.action(description=_("Désapprouver (retirer l'approbation)"))
def action_unapprove(modeladmin, request, queryset):
    now = timezone.now()
    n = queryset.update(
        is_approved=False,
        approved_at=None,
        moderated_by=request.user,
        updated_at=now,
    )
    modeladmin.message_user(
        request,
        _("%(n)s avis désapprouvé(s).") % {"n": n},
        level=messages.SUCCESS,
    )


@admin.action(description=_("Désactiver (masquer) — soft delete"))
def action_deactivate(modeladmin, request, queryset):
    now = timezone.now()
    # On masque -> par cohérence on retire l'approbation
    n = queryset.update(
        is_active=False,
        is_approved=False,
        approved_at=None,
        moderated_by=request.user,
        updated_at=now,
    )
    modeladmin.message_user(
        request,
        _("%(n)s avis désactivé(s).") % {"n": n},
        level=messages.SUCCESS,
    )


@admin.action(description=_("Réactiver (afficher)"))
def action_activate(modeladmin, request, queryset):
    now = timezone.now()
    n = queryset.update(is_active=True, updated_at=now)
    modeladmin.message_user(
        request,
        _("%(n)s avis réactivé(s).") % {"n": n},
        level=messages.SUCCESS,
    )


@admin.action(description=_("Hard delete (suppression définitive) — superuser only"))
def action_hard_delete(modeladmin, request, queryset):
    if not request.user.is_superuser:
        modeladmin.message_user(request, _("Action réservée au superuser."), level=messages.ERROR)
        return
    count = queryset.count()
    queryset.delete()
    modeladmin.message_user(
        request,
        _("%(n)s avis supprimé(s) définitivement.") % {"n": count},
        level=messages.WARNING,
    )


# ============================================================
# Admin
# ============================================================
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    save_on_top = True
    actions_on_top = True
    actions_on_bottom = True
    list_per_page = 50
    date_hierarchy = "created_at"

    list_display = (
        "id",
        "product",
        "product_sku",
        "user",
        "rating",
        "is_active",
        "is_approved",
        "approved_at",
        "moderated_by",
        "created_at",
    )
    list_display_links = ("id", "product")
    ordering = ("-created_at", "id")

    list_filter = (
        "is_active",
        "is_approved",
        "rating",
        ("created_at", admin.DateFieldListFilter),
        ("approved_at", admin.DateFieldListFilter),
    )

    search_fields = (
        "product__sku",
        "product__translations__name",
        "user__email",
        "user__phone",
        "user__first_name",
        "user__last_name",
        "title",
    )

    autocomplete_fields = ("product", "user")
    readonly_fields = ("created_at", "updated_at", "approved_at", "moderated_by")

    fieldsets = (
        (_("Produit"), {"fields": ("product",)}),
        (_("Utilisateur"), {"fields": ("user",)}),
        (_("Contenu"), {"fields": ("rating", "title", "content")}),
        (
            _("Modération"),
            {
                "fields": (
                    "is_active",
                    "is_approved",
                    "approved_at",
                    "moderated_by",
                    "moderation_note",
                )
            },
        ),
        (_("Dates"), {"fields": ("created_at", "updated_at")}),
    )

    actions = (
        action_approve,
        action_unapprove,
        action_deactivate,
        action_activate,
        action_hard_delete,
    )

    def get_queryset(self, request):
        # Perf: évite N+1, et précharge traductions produit (Parler)
        return (
            super()
            .get_queryset(request)
            .select_related("product", "user", "moderated_by")
            .prefetch_related("product__translations")
        )

    @admin.display(description=_("SKU"))
    def product_sku(self, obj: Review) -> str:
        p = getattr(obj, "product", None)
        return getattr(p, "sku", "") or "—"

    def save_model(self, request, obj, form, change):
        """
        Si un admin coche/décoche manuellement 'is_approved',
        on trace automatiquement le modérateur + timestamps.
        """
        now = timezone.now()
        previous = None

        if change and obj.pk:
            previous = (
                type(obj).objects.filter(pk=obj.pk)
                .values("is_approved", "is_active")
                .first()
            )

        # Si on (dés)approuve, on log le modérateur
        if previous is not None:
            prev_approved = bool(previous.get("is_approved"))
            prev_active = bool(previous.get("is_active"))

            if obj.is_approved != prev_approved:
                obj.moderated_by = request.user
                if obj.is_approved:
                    obj.approved_at = now
                    obj.moderation_note = ""
                    obj.is_active = True
                else:
                    obj.approved_at = None

            # Si on désactive, on retire l'approbation par cohérence
            if obj.is_active is False and prev_active is True:
                obj.is_approved = False
                obj.approved_at = None
                obj.moderated_by = request.user

        super().save_model(request, obj, form, change)

    # Soft delete par défaut en admin
    def delete_model(self, request, obj):
        now = timezone.now()
        type(obj).objects.filter(pk=obj.pk).update(
            is_active=False,
            is_approved=False,
            approved_at=None,
            moderated_by=request.user,
            updated_at=now,
        )
        self.message_user(
            request,
            _("Avis masqué (désactivé) — pas supprimé définitivement."),
            level=messages.SUCCESS,
        )

    def delete_queryset(self, request, queryset):
        now = timezone.now()
        n = queryset.update(
            is_active=False,
            is_approved=False,
            approved_at=None,
            moderated_by=request.user,
            updated_at=now,
        )
        self.message_user(
            request,
            _("%(n)s avis masqué(s) (désactivés).") % {"n": n},
            level=messages.SUCCESS,
        )





# # economic/ecommerce/admin/review_admin.py
# from __future__ import annotations

# from django.contrib import admin
# from django.utils.translation import gettext_lazy as _

# from economic.ecommerce.models import Review


# @admin.action(description=_("Approuver les avis sélectionnés"))
# def approve_reviews(modeladmin, request, queryset):
#     queryset.update(is_approved=True)


# @admin.action(description=_("Désapprouver les avis sélectionnés"))
# def unapprove_reviews(modeladmin, request, queryset):
#     queryset.update(is_approved=False)


# @admin.register(Review)
# class ReviewAdmin(admin.ModelAdmin):
#     list_display = ("id", "product", "user", "rating", "is_approved", "created_at")
#     list_filter = ("rating", "is_approved", "created_at")
#     search_fields = ("product__translations__name", "product__sku", "user__email", "title")
#     ordering = ("-created_at",)
#     readonly_fields = ("created_at",)
#     autocomplete_fields = ("product", "user")

#     actions = [approve_reviews, unapprove_reviews]

#     fieldsets = (
#         (_("Produit"), {"fields": ("product",)}),
#         (_("Utilisateur"), {"fields": ("user",)}),
#         (_("Contenu"), {"fields": ("rating", "title", "content")}),
#         (_("Modération"), {"fields": ("is_approved",)}),
#         (_("Dates"), {"fields": ("created_at",)}),
#     )





# # economic/ecommerce/admin/review_admin.py

# from django.contrib import admin
# from django.utils.translation import gettext_lazy as _

# from economic.ecommerce.models import Review


# @admin.action(description=_("Approuver les avis sélectionnés"))
# def approve_reviews(modeladmin, request, queryset):
#     queryset.update(is_approved=True)


# @admin.action(description=_("Désapprouver les avis sélectionnés"))
# def unapprove_reviews(modeladmin, request, queryset):
#     queryset.update(is_approved=False)


# @admin.register(Review)
# class ReviewAdmin(admin.ModelAdmin):
#     list_display = (
#         "id",
#         "product",
#         "user",
#         "rating",
#         "is_approved",
#         "created_at",
#     )
#     list_filter = ("rating", "is_approved", "created_at")
#     search_fields = (
#         "product__translations__name",
#         "user__email",
#         "title",
#     )
#     ordering = ("-created_at",)
#     readonly_fields = ("created_at",)

#     actions = [approve_reviews, unapprove_reviews]

#     fieldsets = (
#         (_("Produit"), {"fields": ("product",)}),
#         (_("Utilisateur"), {"fields": ("user",)}),
#         (_("Contenu"), {"fields": ("rating", "title", "content")}),
#         (_("Modération"), {"fields": ("is_approved",)}),
#         (_("Dates"), {"fields": ("created_at",)}),
#     )
