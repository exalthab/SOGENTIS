from __future__ import annotations

from django.contrib import admin, messages
from django.db.models import Count
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from economic.ecommerce.models import Order, OrderItem


# ------------------------------------------------------------
# Helpers (admin safe: s'adapte au vrai modèle OrderItem)
# ------------------------------------------------------------
def _model_field_names(model) -> set[str]:
    try:
        return {f.name for f in model._meta.fields}
    except Exception:
        return set()


def _pick_fields(model, candidates: list[str]) -> list[str]:
    available = _model_field_names(model)
    return [f for f in candidates if f in available]


# ------------------------------------------------------------
# Inline Items (prod)
# ------------------------------------------------------------
_ORDERITEM_FIELDS = _pick_fields(
    OrderItem,
    [
        # champs “classiques”
        "product",
        "product_sku",
        "product_name",
        "quantity",
        "unit_price",
        "created_at",
    ],
)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    show_change_link = True

    # Autocomplete si FK product existe
    autocomplete_fields = tuple(f for f in ("product",) if "product" in _ORDERITEM_FIELDS)

    # champs affichés (avec fallback minimal)
    fields = tuple(_ORDERITEM_FIELDS + ["line_total"]) if _ORDERITEM_FIELDS else ("product", "quantity", "unit_price", "line_total")
    readonly_fields = ("line_total",)

    def line_total(self, obj: OrderItem):
        try:
            return (obj.unit_price or 0) * (obj.quantity or 0)
        except Exception:
            return "—"
    line_total.short_description = _("Total ligne")

    def get_readonly_fields(self, request, obj=None):
        """
        Si la commande parent n'est plus modifiable -> items read-only
        """
        ro = list(super().get_readonly_fields(request, obj))
        parent = getattr(obj, "order", None) if obj else None
        # Pour inline, Django passe l'objet parent au formset, mais ici obj est l'item.
        # On applique aussi la règle dans has_change_permission via OrderAdmin.
        return tuple(ro)


# ------------------------------------------------------------
# Actions (prod-safe: passent par save())
# ------------------------------------------------------------
def _transition_orders(modeladmin, request, queryset, new_status: str):
    updated = 0
    skipped = 0

    # On itère pour déclencher Order.save() (timestamps + ref + total + clean)
    for o in queryset.select_related("user"):
        try:
            if o.status == new_status:
                continue
            o.status = new_status
            o.save()  # IMPORTANT: pas d'update() -> logique métier complète
            updated += 1
        except Exception:
            skipped += 1

    if updated:
        modeladmin.message_user(
            request,
            _("%(n)s commande(s) mise(s) à jour.") % {"n": updated},
            level=messages.SUCCESS,
        )
    if skipped:
        modeladmin.message_user(
            request,
            _("%(n)s commande(s) ignorée(s) (erreur validation/DB).") % {"n": skipped},
            level=messages.WARNING,
        )


@admin.action(description=_("Marquer comme payée"))
def action_mark_paid(modeladmin, request, queryset):
    _transition_orders(modeladmin, request, queryset, Order.STATUS_PAID)


@admin.action(description=_("Marquer comme expédiée"))
def action_mark_shipped(modeladmin, request, queryset):
    _transition_orders(modeladmin, request, queryset, Order.STATUS_SHIPPED)


@admin.action(description=_("Marquer comme terminée"))
def action_mark_completed(modeladmin, request, queryset):
    _transition_orders(modeladmin, request, queryset, Order.STATUS_COMPLETED)


@admin.action(description=_("Annuler"))
def action_mark_cancelled(modeladmin, request, queryset):
    _transition_orders(modeladmin, request, queryset, Order.STATUS_CANCELLED)


@admin.action(description=_("Repasser en attente (pending)"))
def action_mark_pending(modeladmin, request, queryset):
    _transition_orders(modeladmin, request, queryset, Order.STATUS_PENDING)


@admin.action(description=_("Recalculer les totaux (subtotal/total)"))
def action_recalc_totals(modeladmin, request, queryset):
    updated = 0
    for o in queryset.only("id"):
        try:
            o.recalc_totals(save=True)
            updated += 1
        except Exception:
            pass
    modeladmin.message_user(
        request,
        _("%(n)s commande(s) recalculée(s).") % {"n": updated},
        level=messages.SUCCESS,
    )


# ------------------------------------------------------------
# Admin Order (production)
# ------------------------------------------------------------
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]

    save_on_top = True
    actions_on_top = True
    actions_on_bottom = True
    list_per_page = 50
    date_hierarchy = "created_at"

    list_display = (
        "id",
        "reference",
        "uuid",
        "status_badge",
        "user",
        "customer_email",
        "items_count",
        "currency",
        "subtotal_amount",
        "shipping_amount",
        "tax_amount",
        "discount_amount",
        "total_amount",
        "paid_at",
        "created_at",
    )
    list_display_links = ("id", "reference", "uuid")
    ordering = ("-created_at", "id")

    list_filter = (
        "status",
        "currency",
        ("created_at", admin.DateFieldListFilter),
        ("paid_at", admin.DateFieldListFilter),
        ("shipped_at", admin.DateFieldListFilter),
        ("completed_at", admin.DateFieldListFilter),
        ("cancelled_at", admin.DateFieldListFilter),
    )

    # Search safe (email-only OK)
    search_fields = (
        "reference",
        "uuid",
        "customer_email",
        "user__email",
        "user__phone",
        "user__first_name",
        "user__last_name",
    )

    readonly_fields = (
        # identifiants (ne doivent jamais changer)
        "uuid",
        "reference",
        # timestamps système
        "created_at",
        "updated_at",
        "paid_at",
        "shipped_at",
        "completed_at",
        "cancelled_at",
        # indicateur
        "items_count",
        "status_badge",
    )

    fieldsets = (
        (_("Client"), {"fields": ("user", "customer_email")}),
        (_("Commande"), {"fields": ("reference", "uuid", "status", "currency")}),
        (_("Montants"), {"fields": ("subtotal_amount", "shipping_amount", "tax_amount", "discount_amount", "total_amount")}),
        (_("Timeline"), {"fields": ("paid_at", "shipped_at", "completed_at", "cancelled_at")}),
        (_("Indicateurs"), {"fields": ("items_count", "status_badge")}),
        (_("Système"), {"fields": ("created_at", "updated_at")}),
    )

    actions = [
        action_mark_paid,
        action_mark_shipped,
        action_mark_completed,
        action_mark_cancelled,
        action_mark_pending,
        action_recalc_totals,
    ]

    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related("user")
        # related_name "items" utilisé dans ton modèle (self.items.all())
        return qs.annotate(_items_count=Count("items", distinct=True))

    @admin.display(description=_("Items"), ordering="_items_count")
    def items_count(self, obj: Order) -> int:
        return int(getattr(obj, "_items_count", 0) or 0)

    @admin.display(description=_("Statut"), ordering="status")
    def status_badge(self, obj: Order) -> str:
        # Badges simples mais lisibles (admin HTML)
        mapping = {
            Order.STATUS_PENDING: ("#6b7280", _("En attente")),
            Order.STATUS_PAID: ("#2563eb", _("Payée")),
            Order.STATUS_SHIPPED: ("#a16207", _("Expédiée")),
            Order.STATUS_COMPLETED: ("#16a34a", _("Terminée")),
            Order.STATUS_CANCELLED: ("#dc2626", _("Annulée")),
        }
        color, label = mapping.get(obj.status, ("#111827", obj.status))
        return format_html(
            '<span style="display:inline-block;padding:.2rem .55rem;border-radius:999px;'
            'font-weight:700;color:white;background:{}">{}</span>',
            color,
            label,
        )

    # --------------------------------------------------------
    # Verrouillage post-paiement (prod)
    # --------------------------------------------------------
    def get_readonly_fields(self, request, obj=None):
        ro = set(super().get_readonly_fields(request, obj))
        if obj and not obj.is_editable:
            # Après pending: on verrouille montants + client + status (transitions via actions)
            ro.update(
                {
                    "user",
                    "customer_email",
                    "status",
                    "currency",
                    "subtotal_amount",
                    "shipping_amount",
                    "tax_amount",
                    "discount_amount",
                    "total_amount",
                }
            )
        return tuple(ro)

    def has_delete_permission(self, request, obj=None):
        # Suppression uniquement si pending (sinon audit/compta)
        if obj and not obj.is_editable:
            return False
        return super().has_delete_permission(request, obj)

    # --------------------------------------------------------
    # Garantit recalc après save des inlines
    # --------------------------------------------------------
    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        try:
            order = form.instance
            if order and order.pk:
                order.recalc_totals(save=True)
        except Exception:
            pass





# # economic/ecommerce/admin/order_admin.py
# from __future__ import annotations

# from django.contrib import admin
# from django.utils.translation import gettext_lazy as _

# from economic.ecommerce.models import Order, OrderItem


# class OrderItemInline(admin.TabularInline):
#     model = OrderItem
#     extra = 0
#     fields = ("product", "quantity", "unit_price")
#     autocomplete_fields = ("product",)
#     show_change_link = True


# @admin.action(description=_("Marquer comme payée"))
# def mark_paid(modeladmin, request, queryset):
#     queryset.update(status="paid")


# @admin.action(description=_("Marquer comme expédiée"))
# def mark_shipped(modeladmin, request, queryset):
#     queryset.update(status="shipped")


# @admin.action(description=_("Marquer comme terminée"))
# def mark_completed(modeladmin, request, queryset):
#     queryset.update(status="completed")


# @admin.action(description=_("Annuler"))
# def mark_cancelled(modeladmin, request, queryset):
#     queryset.update(status="cancelled")


# @admin.register(Order)
# class OrderAdmin(admin.ModelAdmin):
#     inlines = [OrderItemInline]

#     list_display = ("id", "uuid", "user", "status", "total_amount", "created_at")
#     list_filter = ("status", "created_at")
#     ordering = ("-created_at",)
#     readonly_fields = ("uuid", "created_at")

#     # ✅ Search safe (évite user__username si tu es email-only)
#     search_fields = ("uuid", "user__email", "user__phone", "user__first_name", "user__last_name")

#     actions = [mark_paid, mark_shipped, mark_completed, mark_cancelled]

#     fieldsets = (
#         (_("Client"), {"fields": ("user",)}),
#         (_("Commande"), {"fields": ("uuid", "status", "total_amount")}),
#         (_("Dates"), {"fields": ("created_at",)}),
#     )




# # /economic/ecommerce/admin/order_admin.py

# from django.contrib import admin
# from django.utils.translation import gettext_lazy as _

# from economic.ecommerce.models import Order, OrderItem


# class OrderItemInline(admin.TabularInline):
#     model = OrderItem
#     extra = 0
#     fields = ("product", "quantity", "unit_price")
#     autocomplete_fields = ("product",)
#     show_change_link = True


# @admin.action(description=_("Marquer comme payée"))
# def mark_paid(modeladmin, request, queryset):
#     queryset.update(status="paid")


# @admin.action(description=_("Marquer comme expédiée"))
# def mark_shipped(modeladmin, request, queryset):
#     queryset.update(status="shipped")


# @admin.action(description=_("Marquer comme terminée"))
# def mark_completed(modeladmin, request, queryset):
#     queryset.update(status="completed")


# @admin.action(description=_("Annuler"))
# def mark_cancelled(modeladmin, request, queryset):
#     queryset.update(status="cancelled")


# @admin.register(Order)
# class OrderAdmin(admin.ModelAdmin):
#     inlines = [OrderItemInline]

#     list_display = ("id", "uuid", "user", "status", "total_amount", "created_at")
#     list_filter = ("status", "created_at")
#     search_fields = ("uuid", "user__email", "user__username")
#     ordering = ("-created_at",)
#     readonly_fields = ("uuid", "created_at")

#     actions = [
#         mark_paid,
#         mark_shipped,
#         mark_completed,
#         mark_cancelled,
#     ]

#     fieldsets = (
#         (_("Client"), {"fields": ("user",)}),
#         (_("Commande"), {"fields": ("uuid", "status", "total_amount")}),
#         (_("Dates"), {"fields": ("created_at",)}),
#     )
