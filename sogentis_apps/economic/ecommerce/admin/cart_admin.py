# economic/ecommerce/admin/cart_admin.py
from __future__ import annotations

from decimal import Decimal

from django.contrib import admin, messages
from django.db import models
from django.db.models import (
    Count,
    Sum,
    F,
    Q,
    Value,
    IntegerField,
    DecimalField,
    ExpressionWrapper,
)
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from economic.ecommerce.models import Cart, CartItem

D0 = Decimal("0.00")


# ------------------------------------------------------------
# Helpers (admin-safe: s'adapte au vrai modèle CartItem)
# ------------------------------------------------------------
def _model_field_names(model) -> set[str]:
    try:
        return {f.name for f in model._meta.fields}
    except Exception:
        return set()


def _pick_fields(model, candidates: list[str]) -> list[str]:
    available = _model_field_names(model)
    return [f for f in candidates if f in available]


CARTITEM_FIELDS = _model_field_names(CartItem)
HAS_ITEM_QTY = "quantity" in CARTITEM_FIELDS
HAS_ITEM_UNIT_PRICE = "unit_price" in CARTITEM_FIELDS
HAS_ITEM_CREATED_AT = "created_at" in CARTITEM_FIELDS


# ------------------------------------------------------------
# Filters
# ------------------------------------------------------------
class CartOwnerTypeFilter(admin.SimpleListFilter):
    title = _("Type")
    parameter_name = "owner_type"

    def lookups(self, request, model_admin):
        return (
            ("user", _("Utilisateur")),
            ("guest", _("Invité (session)")),
        )

    def queryset(self, request, queryset):
        v = self.value()
        if v == "user":
            return queryset.filter(user__isnull=False)
        if v == "guest":
            return queryset.filter(user__isnull=True)
        return queryset


class CartExpiredFilter(admin.SimpleListFilter):
    title = _("Expiration")
    parameter_name = "expired"

    def lookups(self, request, model_admin):
        return (
            ("yes", _("Expiré")),
            ("no", _("Non expiré")),
        )

    def queryset(self, request, queryset):
        v = self.value()
        now = timezone.now()
        if v == "yes":
            return queryset.filter(expires_at__isnull=False, expires_at__lt=now)
        if v == "no":
            return queryset.filter(Q(expires_at__isnull=True) | Q(expires_at__gte=now))
        return queryset


# ------------------------------------------------------------
# Inline Cart Items (dans CartAdmin)
# ------------------------------------------------------------
INLINE_FIELDS = _pick_fields(
    CartItem,
    ["product", "quantity", "unit_price", "created_at", "updated_at"],
)
INLINE_READONLY = tuple(f for f in ("created_at", "updated_at") if f in INLINE_FIELDS)


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    show_change_link = True
    autocomplete_fields = ("product",) if "product" in INLINE_FIELDS else ()

    fields = tuple(INLINE_FIELDS + ["line_total"]) if INLINE_FIELDS else ("product", "quantity", "line_total")
    readonly_fields = tuple(list(INLINE_READONLY) + ["line_total"])
    ordering = (("-created_at", "id") if HAS_ITEM_CREATED_AT else ("id",))

    @admin.display(description=_("Total ligne"))
    def line_total(self, obj: CartItem):
        if not obj:
            return "—"
        if HAS_ITEM_QTY and HAS_ITEM_UNIT_PRICE:
            try:
                return (Decimal(obj.unit_price or 0) * Decimal(obj.quantity or 0)).quantize(Decimal("0.01"))
            except Exception:
                return "—"
        return "—"


# ------------------------------------------------------------
# Actions (prod) — Cart
# ------------------------------------------------------------
@admin.action(description=_("Activer les paniers"))
def action_activate_carts(modeladmin, request, queryset):
    n = queryset.update(is_active=True, updated_at=models.functions.Now())
    modeladmin.message_user(request, _("%(n)s panier(s) activé(s).") % {"n": n}, messages.SUCCESS)


@admin.action(description=_("Désactiver les paniers"))
def action_deactivate_carts(modeladmin, request, queryset):
    n = queryset.update(is_active=False, updated_at=models.functions.Now())
    modeladmin.message_user(request, _("%(n)s panier(s) désactivé(s).") % {"n": n}, messages.SUCCESS)


@admin.action(description=_("Vider les paniers (supprime les items)"))
def action_clear_carts(modeladmin, request, queryset):
    done = 0
    for c in queryset.only("id"):
        try:
            c.clear()
            c.touch()
            done += 1
        except Exception:
            pass
    modeladmin.message_user(
        request,
        _("%(n)s panier(s) vidé(s).") % {"n": done},
        level=messages.SUCCESS,
    )


@admin.action(description=_("Toucher updated_at (marquer comme modifié)"))
def action_touch_carts(modeladmin, request, queryset):
    n = queryset.update(updated_at=models.functions.Now())
    modeladmin.message_user(
        request,
        _("%(n)s panier(s) mis à jour (updated_at).") % {"n": n},
        level=messages.SUCCESS,
    )


# ------------------------------------------------------------
# CartAdmin (production)
# ------------------------------------------------------------
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    inlines = [CartItemInline]

    save_on_top = True
    actions_on_top = True
    actions_on_bottom = True
    list_per_page = 50
    date_hierarchy = "created_at"

    list_display = (
        "id",
        "owner_badge",
        "user",
        "session_key",
        "currency",
        "is_active",
        "expires_at",
        "items_lines",
        "items_qty",
        "subtotal",
        "created_at",
        "updated_at",
    )
    list_display_links = ("id",)
    ordering = ("-updated_at", "-created_at", "id")

    list_filter = (
        "is_active",
        "currency",
        CartOwnerTypeFilter,
        CartExpiredFilter,
        ("created_at", admin.DateFieldListFilter),
        ("updated_at", admin.DateFieldListFilter),
        ("expires_at", admin.DateFieldListFilter),
    )

    search_fields = (
        "session_key",
        "user__email",
        "user__phone",
        "user__first_name",
        "user__last_name",
    )

    readonly_fields = ("created_at", "updated_at", "owner_badge", "items_lines", "items_qty", "subtotal")

    fieldsets = (
        (_("Propriétaire"), {"fields": ("owner_badge", "user", "session_key")}),
        (_("Statut & Devise"), {"fields": ("is_active", "currency", "expires_at")}),
        (_("Indicateurs"), {"fields": ("items_lines", "items_qty", "subtotal")}),
        (_("Système"), {"fields": ("created_at", "updated_at")}),
    )

    actions = (action_activate_carts, action_deactivate_carts, action_clear_carts, action_touch_carts)

    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related("user")

        qs = qs.annotate(_items_lines=Count("items", distinct=True))

        if HAS_ITEM_QTY:
            qs = qs.annotate(
                _items_qty=Coalesce(Sum("items__quantity"), Value(0, output_field=IntegerField()))
            )
        else:
            qs = qs.annotate(_items_qty=Value(0, output_field=IntegerField()))

        if HAS_ITEM_QTY and HAS_ITEM_UNIT_PRICE:
            expr = ExpressionWrapper(
                F("items__unit_price") * F("items__quantity"),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            )
            qs = qs.annotate(
                _subtotal=Coalesce(
                    Sum(expr),
                    Value(D0, output_field=DecimalField(max_digits=12, decimal_places=2)),
                )
            )
        else:
            qs = qs.annotate(
                _subtotal=Value(D0, output_field=DecimalField(max_digits=12, decimal_places=2))
            )

        return qs

    @admin.display(description=_("Type"))
    def owner_badge(self, obj: Cart) -> str:
        if obj.user_id:
            return format_html(
                '<span style="display:inline-block;padding:.15rem .5rem;border-radius:999px;'
                'font-weight:700;background:#0ea5e9;color:white;">{}</span>',
                _("Utilisateur"),
            )
        return format_html(
            '<span style="display:inline-block;padding:.15rem .5rem;border-radius:999px;'
            'font-weight:700;background:#6b7280;color:white;">{}</span>',
            _("Invité"),
        )

    @admin.display(description=_("Lignes"), ordering="_items_lines")
    def items_lines(self, obj: Cart) -> int:
        return int(getattr(obj, "_items_lines", 0) or 0)

    @admin.display(description=_("Qté"), ordering="_items_qty")
    def items_qty(self, obj: Cart) -> int:
        return int(getattr(obj, "_items_qty", 0) or 0)

    @admin.display(description=_("Sous-total"), ordering="_subtotal")
    def subtotal(self, obj: Cart):
        return getattr(obj, "_subtotal", D0) or D0

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        # Inline items: forcer updated_at du panier
        try:
            cart = form.instance
            if cart and cart.pk:
                cart.touch()
        except Exception:
            pass







# # economic/ecommerce/admin/cart_admin.py
# from __future__ import annotations

# from django.contrib import admin

# from economic.ecommerce.models import Cart, CartItem


# @admin.register(Cart)
# class CartAdmin(admin.ModelAdmin):
#     list_display = ("id", "user", "created_at")
#     list_filter = ("created_at",)
#     search_fields = ("user__email", "user__phone", "user__first_name", "user__last_name")
#     ordering = ("-created_at",)
#     readonly_fields = ("created_at",)


# @admin.register(CartItem)
# class CartItemAdmin(admin.ModelAdmin):
#     list_display = ("id", "cart", "product", "quantity")
#     list_filter = ("cart__created_at",)
#     search_fields = ("cart__user__email", "product__translations__name", "product__sku")
#     autocomplete_fields = ("cart", "product")





# # /economic/ecommerce/admin/cart_admin.py
# from django.contrib import admin
# from ..models.cart import Cart
# from ..models.cart_item import CartItem


# @admin.register(Cart)
# class CartAdmin(admin.ModelAdmin):
#     list_display = ("id", "user", "created_at")


# @admin.register(CartItem)
# class CartItemAdmin(admin.ModelAdmin):
#     list_display = ("cart", "product", "quantity")
