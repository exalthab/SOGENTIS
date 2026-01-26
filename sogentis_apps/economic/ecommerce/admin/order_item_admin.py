# economic/ecommerce/admin/order_item_admin.py
from __future__ import annotations

from django.contrib import admin, messages
from django.utils.translation import gettext_lazy as _

from economic.ecommerce.models import OrderItem


@admin.action(description=_("Recalculer les totaux des commandes liées"))
def action_recalc_parent_orders(modeladmin, request, queryset):
    touched = set()
    done = 0

    qs = queryset.select_related("order").only("id", "order_id")
    for it in qs:
        if it.order_id and it.order_id not in touched:
            touched.add(it.order_id)
            try:
                it.order.recalc_totals(save=True)
                done += 1
            except Exception:
                pass

    modeladmin.message_user(
        request,
        _("%(n)s commande(s) recalculée(s).") % {"n": done},
        level=messages.SUCCESS,
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    save_on_top = True
    actions_on_top = True
    actions_on_bottom = True
    list_per_page = 50
    date_hierarchy = "created_at"

    autocomplete_fields = ("order", "product")

    list_display = (
        "id",
        "order_ref",
        "order_status",
        "product",
        "product_sku",
        "product_name",
        "quantity",
        "unit_price",
        "currency",
        "line_total",
        "created_at",
    )
    list_display_links = ("id", "product_name")
    ordering = ("-created_at", "id")

    list_filter = (
        "currency",
        ("created_at", admin.DateFieldListFilter),
        ("order__status", admin.ChoicesFieldListFilter),
        ("order__created_at", admin.DateFieldListFilter),
    )

    search_fields = (
        "order__reference",
        "order__uuid",
        "order__customer_email",
        "product_sku",
        "product_name",
        "product__sku",
        "product__translations__name",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "line_total",
    )

    fieldsets = (
        (_("Commande"), {"fields": ("order",)}),
        (_("Produit"), {"fields": ("product", "product_sku", "product_name")}),
        (_("Quantités & prix"), {"fields": ("quantity", "unit_price", "currency", "line_total")}),
        (_("Système"), {"fields": ("created_at", "updated_at")}),
    )

    actions = (action_recalc_parent_orders,)

    # -------- Perf --------
    def get_queryset(self, request):
        return super().get_queryset(request).select_related("order", "product")

    # -------- Columns helpers --------
    @admin.display(description=_("Commande"), ordering="order__reference")
    def order_ref(self, obj: OrderItem) -> str:
        ref = getattr(obj.order, "reference", None)
        uid = getattr(obj.order, "uuid", None)
        return ref or (str(uid) if uid else "—")

    @admin.display(description=_("Statut"), ordering="order__status")
    def order_status(self, obj: OrderItem) -> str:
        return getattr(obj.order, "status", "") or "—"

    @admin.display(description=_("Total ligne"))
    def line_total(self, obj: OrderItem):
        try:
            return obj.total_price
        except Exception:
            return "—"

    # -------- Locking (audit) --------
    def _order_editable(self, obj: OrderItem) -> bool:
        try:
            return bool(getattr(obj.order, "is_editable", False))
        except Exception:
            return False

    def has_change_permission(self, request, obj=None):
        perm = super().has_change_permission(request, obj)
        if not perm:
            return False
        if obj is None:
            return True
        # On bloque toute modification si la commande n’est plus pending
        return self._order_editable(obj)

    def has_delete_permission(self, request, obj=None):
        perm = super().has_delete_permission(request, obj)
        if not perm:
            return False
        if obj is None:
            return True
        return self._order_editable(obj)

    def get_readonly_fields(self, request, obj=None):
        ro = set(super().get_readonly_fields(request, obj))
        if obj and not self._order_editable(obj):
            # tout en lecture seule (audit)
            ro.update(
                {
                    "order",
                    "product",
                    "product_sku",
                    "product_name",
                    "quantity",
                    "unit_price",
                    "currency",
                }
            )
        return tuple(ro)

    # -------- Recalc parent totals after mutations --------
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        try:
            if obj.order_id:
                obj.order.recalc_totals(save=True)
        except Exception:
            pass

    def delete_model(self, request, obj):
        order = getattr(obj, "order", None)
        super().delete_model(request, obj)
        try:
            if order and getattr(order, "pk", None):
                order.recalc_totals(save=True)
        except Exception:
            pass





# # economic/ecommerce/admin/order_item_admin.py
# from __future__ import annotations

# from django.contrib import admin

# from economic.ecommerce.models import OrderItem


# @admin.register(OrderItem)
# class OrderItemAdmin(admin.ModelAdmin):
#     list_display = ("id", "order", "product", "quantity", "unit_price")
#     list_filter = ("order__created_at",)
#     search_fields = ("order__uuid", "product__translations__name", "product__sku")
#     autocomplete_fields = ("order", "product")





# # /economic/ecommerce/admin/order_item_admin.py
# from django.contrib import admin
# from ..models.order_item import OrderItem


# @admin.register(OrderItem)
# class OrderItemAdmin(admin.ModelAdmin):
#     list_display = ("order", "product", "quantity", "unit_price")
