from __future__ import annotations

from django.contrib import admin, messages
from django.db.models import Count
from django.utils.translation import gettext_lazy as _
from parler.admin import TranslatableAdmin

from economic.ecommerce.models import Category


# -------------------------
# Filters (production)
# -------------------------
class CategoryHierarchyFilter(admin.SimpleListFilter):
    title = _("Hiérarchie")
    parameter_name = "hier"

    def lookups(self, request, model_admin):
        return (
            ("root", _("Racines (sans parent)")),
            ("child", _("Sous-catégories (avec parent)")),
        )

    def queryset(self, request, queryset):
        v = self.value()
        if v == "root":
            return queryset.filter(parent__isnull=True)
        if v == "child":
            return queryset.filter(parent__isnull=False)
        return queryset


class CategoryCodeFilter(admin.SimpleListFilter):
    title = _("Code (CATCODE)")
    parameter_name = "code_presence"

    def lookups(self, request, model_admin):
        return (
            ("with", _("Avec code")),
            ("without", _("Sans code")),
        )

    def queryset(self, request, queryset):
        v = self.value()
        if v == "with":
            return queryset.exclude(code__isnull=True).exclude(code__exact="")
        if v == "without":
            return queryset.filter(code__isnull=True) | queryset.filter(code__exact="")
        return queryset


@admin.register(Category)
class CategoryAdmin(TranslatableAdmin):
    # -------------------------
    # UX / perf
    # -------------------------
    save_on_top = True
    actions_on_top = True
    actions_on_bottom = True
    list_per_page = 50
    date_hierarchy = "created_at"

    autocomplete_fields = ("parent",)
    list_select_related = ("parent",)

    # -------------------------
    # List view (métier)
    # -------------------------
    list_display = (
        "id",
        "code",
        "name_i18n",
        "parent",
        "children_count",
        "products_count",
        "is_active",
        "order",
        "updated_at",
    )
    list_display_links = ("id", "name_i18n")
    list_editable = ("is_active", "order")
    ordering = ("order", "id")

    list_filter = (
        "is_active",
        CategoryHierarchyFilter,
        CategoryCodeFilter,
        # ⚠️ parent en filtre peut être lourd si gros volume.
        # Si tu veux l’activer: ("parent", admin.RelatedOnlyFieldListFilter),
    )

    search_fields = (
        "code",
        "translations__name",
        "translations__slug",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "children_count",
        "products_count",
    )

    fieldsets = (
        (_("Structure"), {"fields": ("code", "parent", "is_active", "order")}),
        (_("Traductions"), {"fields": ("name", "slug", "description")}),
        (_("SEO"), {"fields": ("seo_title", "seo_description")}),
        (_("Indicateurs"), {"fields": ("children_count", "products_count")}),
        (_("Système"), {"fields": ("created_at", "updated_at")}),
    )

    # -------------------------
    # Queryset optimisé + counts
    # -------------------------
    def _product_accessor_name(self) -> str | None:
        """
        Détecte dynamiquement l'accessor inverse depuis Category -> Product
        (ex: 'products', 'product_set', etc.) sans supposer un related_name.
        Retourne None si aucune relation trouvée.
        """
        for rel in Category._meta.related_objects:
            # On cible une FK "category" sur un modèle "product" (app ecommerce)
            rm = rel.related_model
            if rm is None:
                continue
            if rm._meta.model_name == "product" and rm._meta.app_label == "ecommerce":
                # rel.field.name = nom du champ FK côté Product
                if getattr(rel.field, "name", None) == "category":
                    return rel.get_accessor_name()
        return None

    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related("parent")

        # children : related_name="children" dans ton model Category.parent
        qs = qs.annotate(_children_count=Count("children", distinct=True))

        # products : détecté dynamiquement (products/product_set/...)
        accessor = self._product_accessor_name()
        if accessor:
            qs = qs.annotate(_products_count=Count(accessor, distinct=True))

        return qs

    # -------------------------
    # Display helpers
    # -------------------------
    @admin.display(description=_("Nom"))
    def name_i18n(self, obj: Category) -> str:
        return obj.safe_translation_getter("name", any_language=True) or "-"

    @admin.display(description=_("Sous-catégories"), ordering="_children_count")
    def children_count(self, obj: Category) -> int:
        return int(getattr(obj, "_children_count", 0) or 0)

    @admin.display(description=_("Produits"), ordering="_products_count")
    def products_count(self, obj: Category) -> str:
        # Si l'annotation n'existe pas (pas de relation Product trouvée), on n'affiche pas un faux 0.
        if not hasattr(obj, "_products_count"):
            return "—"
        return str(int(getattr(obj, "_products_count", 0) or 0))

    # -------------------------
    # Actions pro
    # -------------------------
    actions = (
        "action_activate",
        "action_deactivate",
        "action_make_root",
        "action_normalize_codes",
        "action_normalize_order",
    )

    @admin.action(description=_("Activer"))
    def action_activate(self, request, queryset):
        n = queryset.update(is_active=True)
        self.message_user(request, _("%(n)s catégorie(s) activée(s).") % {"n": n}, messages.SUCCESS)

    @admin.action(description=_("Désactiver"))
    def action_deactivate(self, request, queryset):
        n = queryset.update(is_active=False)
        self.message_user(request, _("%(n)s catégorie(s) désactivée(s).") % {"n": n}, messages.SUCCESS)

    @admin.action(description=_("Mettre à la racine (supprimer le parent)"))
    def action_make_root(self, request, queryset):
        n = queryset.update(parent=None)
        self.message_user(request, _("%(n)s catégorie(s) déplacée(s) à la racine.") % {"n": n}, messages.SUCCESS)

    @admin.action(description=_("Normaliser les codes (trim + UPPER, vide => NULL)"))
    def action_normalize_codes(self, request, queryset):
        changed = 0
        objs = list(queryset.only("id", "code"))
        for obj in objs:
            before = obj.code
            after = (before or "").strip().upper() or None
            if before != after:
                obj.code = after
                changed += 1
        if changed:
            Category.objects.bulk_update(objs, ["code"])
        self.message_user(
            request,
            _("%(n)s catégorie(s) mise(s) à jour (code normalisé).") % {"n": changed},
            messages.SUCCESS,
        )

    @admin.action(description=_("Normaliser l’ordre (0..N) selon tri actuel"))
    def action_normalize_order(self, request, queryset):
        qs = queryset.order_by("order", "id").only("id", "order")
        to_update = []
        i = 0
        for obj in qs:
            if obj.order != i:
                obj.order = i
                to_update.append(obj)
            i += 1
        if to_update:
            Category.objects.bulk_update(to_update, ["order"])
        self.message_user(
            request,
            _("%(n)s catégorie(s) renumérotée(s).") % {"n": len(to_update)},
            messages.SUCCESS,
        )

    # -------------------------
    # Save safety (admin)
    # -------------------------
    def save_model(self, request, obj, form, change):
        # Model le fait déjà, mais on renforce côté admin (saisie humaine)
        if obj.code:
            obj.code = obj.code.strip().upper() or None
        super().save_model(request, obj, form, change)






# # economic/ecommerce/admin/category_admin.py
# from __future__ import annotations

# from django.contrib import admin
# from django.utils.translation import gettext_lazy as _
# from parler.admin import TranslatableAdmin

# from economic.ecommerce.models import Category


# @admin.register(Category)
# class CategoryAdmin(TranslatableAdmin):
#     list_display = ("id", "name_i18n", "parent", "is_active", "order")
#     list_filter = ("is_active", "parent")
#     search_fields = ("translations__name", "translations__slug")
#     ordering = ("order", "id")
#     list_editable = ("is_active", "order")
#     autocomplete_fields = ("parent",)

#     fieldsets = (
#         (_("Structure"), {"fields": ("parent", "is_active", "order")}),
#         (_("Traductions"), {"fields": ("name", "slug", "description", "seo_title", "seo_description")}),
#         (_("Système"), {"fields": ("created_at", "updated_at")}),
#     )
#     readonly_fields = ("created_at", "updated_at")

#     def get_queryset(self, request):
#         qs = super().get_queryset(request)
#         return qs.select_related("parent")

#     @admin.display(description=_("Nom"))
#     def name_i18n(self, obj):
#         return obj.safe_translation_getter("name", any_language=True) or "-"




# # /economic/ecommerce/admin/category_admin.py

# from django.contrib import admin
# from django.utils.translation import gettext_lazy as _
# from parler.admin import TranslatableAdmin

# from economic.ecommerce.models import Category


# @admin.register(Category)
# class CategoryAdmin(TranslatableAdmin):
#     list_display = ("id", "name_i18n", "parent", "is_active", "order")
#     list_filter = ("is_active", "parent")
#     search_fields = ("translations__name", "translations__slug")
#     ordering = ("order", "id")
#     list_editable = ("is_active", "order")

#     fieldsets = (
#         (_("Structure"), {
#             "fields": ("parent", "is_active", "order"),
#         }),
#         (_("Traductions"), {
#             "fields": ("name", "slug", "description"),
#         }),
#     )

#     def name_i18n(self, obj):
#         return obj.safe_translation_getter("name", any_language=True) or "-"

#     name_i18n.short_description = _("Nom")
