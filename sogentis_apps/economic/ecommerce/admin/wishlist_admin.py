# economic/ecommerce/admin/wishlist_admin.py
from __future__ import annotations

from django.contrib import admin, messages
from django.db import models
from django.db.models import Count, Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from economic.ecommerce.models import Wishlist, WishlistItem

from django.forms.models import BaseInlineFormSet


# ------------------------------------------------------------
# Inline Formset: "delete" => soft delete (is_active=False)
# ------------------------------------------------------------
# class SoftDeleteWishlistItemInlineFormSet(admin.helpers.BaseInlineFormSet):
class SoftDeleteWishlistItemInlineFormSet(BaseInlineFormSet):

    """
    Empêche le hard delete via inline.
    Toute suppression demandée dans l'admin devient un soft delete:
    is_active=False + updated_at.
    """

    def delete_existing_objects(self, commit=True):
        if not commit:
            return

        now = timezone.now()
        for obj in getattr(self, "deleted_objects", []):
            try:
                # soft delete
                obj.is_active = False
                obj.updated_at = now  # champ existe dans ton modèle
                obj.save(update_fields=["is_active", "updated_at"])
            except Exception:
                pass

        # IMPORTANT: on vide la liste pour éviter un delete() ensuite
        self.deleted_objects = []


# ------------------------------------------------------------
# Inline Items (dans WishlistAdmin)
# ------------------------------------------------------------
class WishlistItemInline(admin.TabularInline):
    model = WishlistItem
    formset = SoftDeleteWishlistItemInlineFormSet

    extra = 0
    show_change_link = True
    autocomplete_fields = ("product",)

    fields = ("product", "is_active", "added_at", "updated_at")
    readonly_fields = ("added_at", "updated_at")
    ordering = ("-added_at", "id")


# ------------------------------------------------------------
# Filters
# ------------------------------------------------------------
class WishlistHasInactiveFilter(admin.SimpleListFilter):
    title = _("Contient des éléments inactifs")
    parameter_name = "has_inactive"

    def lookups(self, request, model_admin):
        return (
            ("yes", _("Oui")),
            ("no", _("Non")),
        )

    def queryset(self, request, queryset):
        v = self.value()
        if v == "yes":
            return queryset.filter(items__is_active=False).distinct()
        if v == "no":
            return queryset.exclude(items__is_active=False).distinct()
        return queryset


# ------------------------------------------------------------
# Actions Wishlist (prod-safe)
# ------------------------------------------------------------
@admin.action(description=_("Vider les wishlists (soft delete: désactiver les items actifs)"))
def action_clear_wishlists(modeladmin, request, queryset):
    ids = list(queryset.values_list("id", flat=True))
    if not ids:
        return

    # Désactive uniquement les actifs (historique conservé)
    n_items = WishlistItem.objects.filter(wishlist_id__in=ids, is_active=True).update(
        is_active=False,
        updated_at=timezone.now(),
    )

    # Touch updated_at wishlist
    n_w = Wishlist.objects.filter(id__in=ids).update(updated_at=models.functions.Now())

    modeladmin.message_user(
        request,
        _("%(w)s wishlist(s) touchée(s), %(n)s item(s) désactivé(s).") % {"w": n_w, "n": n_items},
        level=messages.SUCCESS,
    )


@admin.action(description=_("Restaurer les wishlists (réactiver tous les items)"))
def action_restore_wishlists(modeladmin, request, queryset):
    ids = list(queryset.values_list("id", flat=True))
    if not ids:
        return

    n_items = WishlistItem.objects.filter(wishlist_id__in=ids, is_active=False).update(
        is_active=True,
        updated_at=timezone.now(),
    )
    n_w = Wishlist.objects.filter(id__in=ids).update(updated_at=models.functions.Now())

    modeladmin.message_user(
        request,
        _("%(w)s wishlist(s) touchée(s), %(n)s item(s) réactivé(s).") % {"w": n_w, "n": n_items},
        level=messages.SUCCESS,
    )


@admin.action(description=_("Hard delete items (supprimer définitivement) — superuser only"))
def action_hard_delete_items(modeladmin, request, queryset):
    if not request.user.is_superuser:
        modeladmin.message_user(request, _("Action réservée au superuser."), level=messages.ERROR)
        return

    ids = list(queryset.values_list("id", flat=True))
    if not ids:
        return

    # Hard delete des items liés
    n_items = WishlistItem.objects.filter(wishlist_id__in=ids).count()
    WishlistItem.objects.filter(wishlist_id__in=ids).delete()

    # Touch updated_at wishlist
    n_w = Wishlist.objects.filter(id__in=ids).update(updated_at=models.functions.Now())

    modeladmin.message_user(
        request,
        _("%(w)s wishlist(s) touchée(s), %(n)s item(s) supprimé(s) définitivement.") % {"w": n_w, "n": n_items},
        level=messages.WARNING,
    )


@admin.action(description=_("Toucher updated_at (marquer comme modifié)"))
def action_touch_wishlists(modeladmin, request, queryset):
    n = queryset.update(updated_at=models.functions.Now())
    modeladmin.message_user(
        request,
        _("%(n)s wishlist(s) mise(s) à jour (updated_at).") % {"n": n},
        level=messages.SUCCESS,
    )


# ------------------------------------------------------------
# WishlistAdmin (production)
# ------------------------------------------------------------
@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    inlines = [WishlistItemInline]

    save_on_top = True
    actions_on_top = True
    actions_on_bottom = True
    list_per_page = 50
    date_hierarchy = "created_at"

    list_display = (
        "id",
        "user",
        "name",
        "items_total_count",
        "items_active_count",
        "created_at",
        "updated_at",
    )
    list_display_links = ("id", "user", "name")
    ordering = ("-updated_at", "-created_at", "id")

    list_filter = (
        WishlistHasInactiveFilter,
        ("created_at", admin.DateFieldListFilter),
        ("updated_at", admin.DateFieldListFilter),
    )

    search_fields = ("name", "user__email", "user__phone", "user__first_name", "user__last_name")
    autocomplete_fields = ("user",)

    readonly_fields = ("created_at", "updated_at", "items_total_count", "items_active_count")

    fieldsets = (
        (_("Utilisateur"), {"fields": ("user",)}),
        (_("Wishlist"), {"fields": ("name", "items_total_count", "items_active_count")}),
        (_("Dates"), {"fields": ("created_at", "updated_at")}),
    )

    actions = (
        action_clear_wishlists,
        action_restore_wishlists,
        action_hard_delete_items,
        action_touch_wishlists,
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related("user")

        # Total items
        qs = qs.annotate(_items_total=Count("items", distinct=True))

        # Active items (soft delete aware)
        qs = qs.annotate(
            _items_active=Count("items", filter=Q(items__is_active=True), distinct=True)
        )

        return qs

    @admin.display(description=_("Produits (total)"), ordering="_items_total")
    def items_total_count(self, obj: Wishlist) -> int:
        return int(getattr(obj, "_items_total", 0) or 0)

    @admin.display(description=_("Produits (actifs)"), ordering="_items_active")
    def items_active_count(self, obj: Wishlist) -> int:
        return int(getattr(obj, "_items_active", 0) or 0)

    def save_related(self, request, form, formsets, change):
        """
        Ajouter/supprimer/désactiver des WishlistItem via inline
        ne touche pas Wishlist.updated_at automatiquement.
        """
        super().save_related(request, form, formsets, change)
        try:
            w = form.instance
            if w and w.pk:
                type(w).objects.filter(pk=w.pk).update(updated_at=models.functions.Now())
        except Exception:
            pass





# # economic/ecommerce/admin/wishlist_admin.py
# from __future__ import annotations

# from django.contrib import admin
# from django.utils.translation import gettext_lazy as _

# from economic.ecommerce.models import Wishlist, WishlistItem


# class WishlistItemInline(admin.TabularInline):
#     model = WishlistItem
#     extra = 0
#     fields = ("product", "added_at")
#     readonly_fields = ("added_at",)
#     autocomplete_fields = ("product",)
#     show_change_link = True


# @admin.register(Wishlist)
# class WishlistAdmin(admin.ModelAdmin):
#     inlines = [WishlistItemInline]

#     list_display = ("id", "user", "created_at", "items_count")
#     search_fields = ("user__email", "user__phone", "user__first_name", "user__last_name")
#     ordering = ("-created_at",)
#     readonly_fields = ("created_at",)
#     autocomplete_fields = ("user",)

#     fieldsets = (
#         (_("Utilisateur"), {"fields": ("user",)}),
#         (_("Dates"), {"fields": ("created_at",)}),
#     )

#     @admin.display(description=_("Nombre de produits"))
#     def items_count(self, obj):
#         return obj.items.count()




# # /economic/ecommerce/admin/wishlist_admin.py

# from django.contrib import admin
# from django.utils.translation import gettext_lazy as _

# from economic.ecommerce.models import Wishlist, WishlistItem


# class WishlistItemInline(admin.TabularInline):
#     model = WishlistItem
#     extra = 0
#     fields = ("product", "added_at")
#     readonly_fields = ("added_at",)
#     autocomplete_fields = ("product",)
#     show_change_link = True


# @admin.register(Wishlist)
# class WishlistAdmin(admin.ModelAdmin):
#     inlines = [WishlistItemInline]

#     list_display = ("id", "user", "created_at", "items_count")
#     search_fields = ("user__email", "user__username")
#     ordering = ("-created_at",)
#     readonly_fields = ("created_at",)

#     fieldsets = (
#         (_("Utilisateur"), {"fields": ("user",)}),
#         (_("Dates"), {"fields": ("created_at",)}),
#     )

#     def items_count(self, obj):
#         return obj.items.count()

#     items_count.short_description = _("Nombre de produits")
