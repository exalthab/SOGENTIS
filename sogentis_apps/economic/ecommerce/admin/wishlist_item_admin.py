# economic/ecommerce/admin/wishlist_item_admin.py
from __future__ import annotations

from django.contrib import admin, messages
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from economic.ecommerce.models import WishlistItem


# ------------------------------------------------------------
# Actions (prod-safe): soft delete / restore
# ------------------------------------------------------------
@admin.action(description=_("Retirer de la wishlist (désactiver)"))
def action_deactivate_items(modeladmin, request, queryset):
    n = queryset.update(is_active=False)
    modeladmin.message_user(
        request,
        _("%(n)s élément(s) désactivé(s).") % {"n": n},
        level=messages.SUCCESS,
    )


@admin.action(description=_("Restaurer (réactiver)"))
def action_reactivate_items(modeladmin, request, queryset):
    n = queryset.update(is_active=True)
    modeladmin.message_user(
        request,
        _("%(n)s élément(s) réactivé(s).") % {"n": n},
        level=messages.SUCCESS,
    )


@admin.action(description=_("Hard delete (supprimer définitivement)"))
def action_hard_delete(modeladmin, request, queryset):
    """
    Optionnel: en prod on préfère soft delete.
    On limite au superuser pour éviter les erreurs d'audit.
    """
    if not request.user.is_superuser:
        modeladmin.message_user(
            request,
            _("Action réservée au superuser."),
            level=messages.ERROR,
        )
        return

    count = queryset.count()
    queryset.delete()
    modeladmin.message_user(
        request,
        _("%(n)s élément(s) supprimé(s) définitivement.") % {"n": count},
        level=messages.WARNING,
    )


# ------------------------------------------------------------
# Admin
# ------------------------------------------------------------
@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    save_on_top = True
    actions_on_top = True
    actions_on_bottom = True
    list_per_page = 50
    date_hierarchy = "added_at"

    autocomplete_fields = ("wishlist", "product")

    list_display = (
        "id",
        "wishlist",
        "wishlist_user",
        "product",
        "product_sku",
        "is_active",
        "added_at",
        "updated_at",
    )
    list_display_links = ("id", "product")
    ordering = ("-added_at", "id")

    list_filter = (
        "is_active",
        ("added_at", admin.DateFieldListFilter),
        ("updated_at", admin.DateFieldListFilter),
        ("wishlist__created_at", admin.DateFieldListFilter),
    )

    search_fields = (
        "wishlist__user__email",
        "wishlist__user__phone",
        "wishlist__user__first_name",
        "wishlist__user__last_name",
        "product__sku",
        "product__translations__name",
    )

    readonly_fields = ("added_at", "updated_at")

    fieldsets = (
        (_("Wishlist"), {"fields": ("wishlist",)}),
        (_("Produit"), {"fields": ("product", "is_active")}),
        (_("Dates"), {"fields": ("added_at", "updated_at")}),
    )

    actions = (action_deactivate_items, action_reactivate_items, action_hard_delete)

    # ---- Perf ----
    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("wishlist", "wishlist__user", "product")
        )

    # ---- Columns helpers ----
    @admin.display(description=_("Utilisateur"))
    def wishlist_user(self, obj: WishlistItem) -> str:
        u = getattr(getattr(obj, "wishlist", None), "user", None)
        return getattr(u, "email", "") or (str(u) if u else "—")

    @admin.display(description=_("SKU"))
    def product_sku(self, obj: WishlistItem) -> str:
        p = getattr(obj, "product", None)
        return getattr(p, "sku", "") or "—"

    # ---- Soft delete by default in admin ----
    def delete_model(self, request, obj):
        """
        Par défaut: soft delete (désactivation),
        pour respecter l'historique.
        """
        obj.is_active = False
        obj.save(update_fields=["is_active", "updated_at"])
        self.message_user(
            request,
            _("Élément retiré (désactivé) — pas supprimé définitivement."),
            level=messages.SUCCESS,
        )

    def delete_queryset(self, request, queryset):
        """
        Bulk delete dans l'admin => soft delete.
        """
        n = queryset.update(is_active=False, updated_at=timezone.now())
        self.message_user(
            request,
            _("%(n)s élément(s) retiré(s) (désactivés).") % {"n": n},
            level=messages.SUCCESS,
        )

    # ---- Touch wishlist updated_at after save ----
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        try:
            w = getattr(obj, "wishlist", None)
            if w and w.pk:
                type(w).objects.filter(pk=w.pk).update(updated_at=models.functions.Now())
        except Exception:
            pass

