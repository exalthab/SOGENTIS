# economic/ecommerce/admin/cart_item_admin.py
from __future__ import annotations

from decimal import Decimal

from django.contrib import admin, messages
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _

from economic.ecommerce.models import CartItem


# ------------------------------------------------------------
# Actions (prod)
# ------------------------------------------------------------
@admin.action(description=_("Recalculer unit_price depuis Product (ou Pricing)"))
def action_reprice_items(modeladmin, request, queryset):
    """
    Recalcule unit_price via CartItem._resolve_unit_price().
    Utile après changement de prix, migration, import.
    """
    updated = 0
    with transaction.atomic():
        qs = queryset.select_related("product", "cart").select_for_update()
        for it in qs:
            try:
                new_price = it._resolve_unit_price()
                if new_price is None:
                    continue
                new_price = Decimal(new_price).quantize(Decimal("0.01"))
                if it.unit_price != new_price:
                    CartItem.objects.filter(pk=it.pk).update(
                        unit_price=new_price,
                        updated_at=models.functions.Now(),
                    )
                    updated += 1
            except Exception:
                continue

    modeladmin.message_user(
        request,
        _("%(n)s article(s) repricé(s).") % {"n": updated},
        level=messages.SUCCESS,
    )


@admin.action(description=_("Aligner la devise sur le panier (currency)"))
def action_sync_currency_from_cart(modeladmin, request, queryset):
    updated = 0
    with transaction.atomic():
        qs = queryset.select_related("cart").select_for_update()
        for it in qs:
            try:
                cart_cur = getattr(it.cart, "currency", "") or ""
                cart_cur = cart_cur.strip().upper()
                if not cart_cur:
                    continue
                if (it.currency or "").strip().upper() != cart_cur:
                    CartItem.objects.filter(pk=it.pk).update(
                        currency=cart_cur,
                        updated_at=models.functions.Now(),
                    )
                    updated += 1
            except Exception:
                continue

    modeladmin.message_user(
        request,
        _("%(n)s article(s) mis à jour (currency).") % {"n": updated},
        level=messages.SUCCESS,
    )


@admin.action(description=_("Forcer unit_price = 0 (sera recalculé au prochain save)"))
def action_zero_unit_price(modeladmin, request, queryset):
    n = queryset.update(unit_price=Decimal("0.00"), updated_at=models.functions.Now())
    modeladmin.message_user(
        request,
        _("%(n)s article(s) mis à zéro (unit_price).") % {"n": n},
        level=messages.WARNING,
    )


# ------------------------------------------------------------
# Admin (production)
# ------------------------------------------------------------
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    save_on_top = True
    actions_on_top = True
    actions_on_bottom = True
    list_per_page = 50

    autocomplete_fields = ("cart", "product")

    list_display = (
        "id",
        "cart",
        "cart_owner",
        "product",
        "product_sku",
        "quantity",
        "unit_price",
        "currency",
        "line_total",
        "created_at",
        "updated_at",
    )
    list_display_links = ("id", "product")

    ordering = ("-created_at", "id")

    list_filter = (
        ("created_at", admin.DateFieldListFilter),
        ("updated_at", admin.DateFieldListFilter),
        ("currency", admin.AllValuesFieldListFilter),
    )

    search_fields = (
        "cart__id",
        "cart__user__email",
        "cart__user__phone",
        "cart__session_key",
        "product__sku",
        "product__translations__name",
    )

    readonly_fields = ("created_at", "updated_at", "line_total", "cart_owner", "product_sku")

    fieldsets = (
        (_("Lien"), {"fields": ("cart", "cart_owner", "product", "product_sku")}),
        (_("Quantités & prix"), {"fields": ("quantity", ("unit_price", "currency"), "line_total")}),
        (_("Système"), {"fields": ("created_at", "updated_at")}),
    )

    actions = (
        action_reprice_items,
        action_sync_currency_from_cart,
        action_zero_unit_price,
    )

    def get_queryset(self, request):
        # perf: user / product / translations
        return (
            super()
            .get_queryset(request)
            .select_related("cart", "cart__user", "product")
        )

    @admin.display(description=_("Client / session"))
    def cart_owner(self, obj: CartItem) -> str:
        c = getattr(obj, "cart", None)
        if not c:
            return "—"
        u = getattr(c, "user", None)
        if u:
            return getattr(u, "email", "") or getattr(u, "phone", "") or str(u)
        sk = getattr(c, "session_key", None)
        return (sk or "—")

    @admin.display(description=_("SKU"))
    def product_sku(self, obj: CartItem) -> str:
        p = getattr(obj, "product", None)
        return (getattr(p, "sku", "") or "—")

    @admin.display(description=_("Total"), ordering="unit_price")
    def line_total(self, obj: CartItem):
        try:
            return obj.total_price
        except Exception:
            try:
                return (Decimal(obj.unit_price) * Decimal(obj.quantity)).quantize(Decimal("0.01"))
            except Exception:
                return Decimal("0.00")
