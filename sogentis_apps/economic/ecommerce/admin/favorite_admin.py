# economic/ecommerce/admin/favorite_admin.py
from __future__ import annotations

from django.contrib import admin, messages
from django.db.models import F
from django.utils.translation import gettext_lazy as _

from economic.ecommerce.models import Favorite


@admin.action(description=_("Supprimer les favoris sélectionnés"))
def action_delete_favorites(modeladmin, request, queryset):
    n = queryset.count()
    queryset.delete()
    modeladmin.message_user(
        request,
        _("%(n)s favori(s) supprimé(s).") % {"n": n},
        level=messages.SUCCESS,
    )


@admin.action(description=_("Afficher seulement les favoris de ces utilisateurs (filtre rapide)"))
def action_filter_by_users(modeladmin, request, queryset):
    """
    Astuce admin: ne modifie rien, mais aide l'opérateur à pivot sur users.
    (Django admin ne permet pas de "set filter" directement, donc on affiche un message).
    """
    user_ids = list(queryset.values_list("user_id", flat=True).distinct()[:50])
    if not user_ids:
        modeladmin.message_user(request, _("Aucun utilisateur détecté."), level=messages.INFO)
        return
    modeladmin.message_user(
        request,
        _("Astuce: filtre 'user' avec ces IDs (max 50): %(ids)s") % {"ids": ", ".join(map(str, user_ids))},
        level=messages.INFO,
    )


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """
    Admin Favoris — prod:
    - list_display riche (user + produit + infos SKU/nom i18n)
    - perf: select_related user/product/category/vendor
    - filtres: date, vendor, category
    - actions: suppression bulk + aide pivot utilisateur
    """

    save_on_top = True
    actions_on_top = True
    actions_on_bottom = True
    list_per_page = 50
    date_hierarchy = "created_at"

    ordering = ("-created_at", "id")

    # ---- Affichage liste
    list_display = (
        "id",
        "created_at",
        "user",
        "user_email",
        "product",
        "product_sku",
        "product_name_i18n",
        "product_category",
        "product_vendor",
    )
    list_display_links = ("id", "product", "user")

    # ---- Filtres
    list_filter = (
        ("created_at", admin.DateFieldListFilter),
        "product__category",
        "product__vendor",
    )

    # ---- Recherche robuste (email-only safe)
    search_fields = (
        "user__email",
        "user__phone",
        "user__first_name",
        "user__last_name",
        "product__sku",
        "product__translations__name",
        "product__translations__slug",
    )

    # ---- UX
    autocomplete_fields = ("user", "product")
    readonly_fields = ("created_at",)

    fieldsets = (
        (_("Favori"), {"fields": ("user", "product")}),
        (_("Dates"), {"fields": ("created_at",)}),
    )

    actions = (action_delete_favorites, action_filter_by_users)

    # ---- Perf / queryset
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Favori -> user, product ; Product -> category, vendor
        return qs.select_related("user", "product", "product__category", "product__vendor")

    # ---- Helpers affichage
    @admin.display(description=_("Email"))
    def user_email(self, obj: Favorite) -> str:
        u = getattr(obj, "user", None)
        return getattr(u, "email", "") or "—"

    @admin.display(description=_("SKU"))
    def product_sku(self, obj: Favorite) -> str:
        p = getattr(obj, "product", None)
        return getattr(p, "sku", "") or "—"

    @admin.display(description=_("Nom (i18n)"))
    def product_name_i18n(self, obj: Favorite) -> str:
        p = getattr(obj, "product", None)
        if not p:
            return "—"
        # Product est TranslatableModel (Parler) chez toi
        try:
            return p.safe_translation_getter("name", any_language=True) or "—"
        except Exception:
            return str(p)

    @admin.display(description=_("Catégorie"))
    def product_category(self, obj: Favorite) -> str:
        p = getattr(obj, "product", None)
        c = getattr(p, "category", None) if p else None
        if not c:
            return "—"
        try:
            return c.safe_translation_getter("name", any_language=True) or str(c)
        except Exception:
            return str(c)

    @admin.display(description=_("Vendeur"))
    def product_vendor(self, obj: Favorite) -> str:
        p = getattr(obj, "product", None)
        v = getattr(p, "vendor", None) if p else None
        return getattr(v, "company_name", "") or (str(v) if v else "—")
