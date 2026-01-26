# economic/ecommerce/admin/invoice_admin.py
from __future__ import annotations

from django.contrib import admin, messages
from django.db import models
from django.utils import timezone
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from economic.ecommerce.models import Invoice


# ------------------------------------------------------------
# Actions (prod)
# ------------------------------------------------------------
@admin.action(description=_("Marquer comme Émise (issued)"))
def action_mark_issued(modeladmin, request, queryset):
    ok = 0
    for inv in queryset.only("id", "status", "issued_at", "voided_at"):
        try:
            if inv.status != Invoice.STATUS_VOID:
                inv.mark_issued()
                ok += 1
        except Exception as e:
            modeladmin.message_user(request, f"[{inv.pk}] {e}", level=messages.ERROR)
    if ok:
        modeladmin.message_user(request, _("%(n)s facture(s) marquée(s) émise(s).") % {"n": ok}, messages.SUCCESS)


@admin.action(description=_("Marquer comme Annulée (void)"))
def action_mark_void(modeladmin, request, queryset):
    ok = 0
    for inv in queryset.only("id", "status"):
        try:
            inv.mark_void()
            ok += 1
        except Exception as e:
            modeladmin.message_user(request, f"[{inv.pk}] {e}", level=messages.ERROR)
    if ok:
        modeladmin.message_user(request, _("%(n)s facture(s) annulée(s).") % {"n": ok}, messages.SUCCESS)


@admin.action(description=_("Synchroniser montant/devise depuis la commande"))
def action_sync_from_order(modeladmin, request, queryset):
    ok = 0
    for inv in queryset.select_related("order").only("id", "amount", "currency", "order__total_amount", "order__currency"):
        try:
            changed = False
            ot = getattr(inv.order, "total_amount", None)
            oc = getattr(inv.order, "currency", None)

            if ot is not None and inv.amount != ot:
                inv.amount = ot
                changed = True
            if oc and (inv.currency or "").upper() != (oc or "").upper():
                inv.currency = oc
                changed = True

            if changed:
                inv.save(update_fields=["amount", "currency", "updated_at"])
            ok += 1
        except Exception as e:
            modeladmin.message_user(request, f"[{inv.pk}] {e}", level=messages.ERROR)

    modeladmin.message_user(request, _("%(n)s facture(s) synchronisée(s).") % {"n": ok}, messages.SUCCESS)


@admin.action(description=_("Recalculer checksum PDF (sha256)"))
def action_recompute_checksum(modeladmin, request, queryset):
    ok = 0
    for inv in queryset.only("id", "file", "checksum"):
        try:
            if not inv.file:
                continue
            digest = inv._compute_checksum_sha256()
            if digest:
                Invoice.objects.filter(pk=inv.pk).update(checksum=digest, updated_at=timezone.now())
                ok += 1
        except Exception as e:
            modeladmin.message_user(request, f"[{inv.pk}] {e}", level=messages.ERROR)

    if ok:
        modeladmin.message_user(request, _("%(n)s checksum(s) recalculé(s).") % {"n": ok}, messages.SUCCESS)


# ------------------------------------------------------------
# Admin
# ------------------------------------------------------------
@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    save_on_top = True
    actions_on_top = True
    actions_on_bottom = True
    list_per_page = 50
    date_hierarchy = "created_at"

    ordering = ("-created_at",)
    autocomplete_fields = ("order",)

    list_display = (
        "invoice_number",
        "uuid",
        "status_badge",
        "order_ref",
        "order_user",
        "amount",
        "currency",
        "pdf_link",
        "checksum_short",
        "created_at",
        "issued_at",
    )
    list_display_links = ("invoice_number", "uuid")

    list_filter = (
        "status",
        "currency",
        ("created_at", admin.DateFieldListFilter),
        ("updated_at", admin.DateFieldListFilter),
        ("issued_at", admin.DateFieldListFilter),
    )

    search_fields = (
        "invoice_number",
        "uuid",
        "order__uuid",
        "order__reference",
        "order__user__email",
        "order__user__phone",
        "order__user__first_name",
        "order__user__last_name",
    )

    readonly_fields = (
        "uuid",
        "invoice_number",
        "created_at",
        "updated_at",
        "issued_at",
        "voided_at",
        "checksum",
        "pdf_link",
        "file_size",
    )

    fieldsets = (
        (_("Facture"), {"fields": ("uuid", "invoice_number", "status")}),
        (_("Commande"), {"fields": ("order",)}),
        (_("Montants"), {"fields": (("amount", "currency"),)}),
        (_("PDF"), {"fields": ("file", "pdf_link", "file_size", "checksum"), "classes": ("collapse",)}),
        (_("Dates"), {"fields": ("created_at", "updated_at", "issued_at", "voided_at"), "classes": ("collapse",)}),
    )

    actions = (
        action_mark_issued,
        action_mark_void,
        action_sync_from_order,
        action_recompute_checksum,
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("order", "order__user")

    # -------------------------
    # UI helpers
    # -------------------------
    @admin.display(description=_("Statut"), ordering="status")
    def status_badge(self, obj: Invoice):
        s = obj.status
        label = obj.get_status_display()
        if s == Invoice.STATUS_ISSUED:
            return format_html('<b style="color:#16a34a;">● {}</b>', label)
        if s == Invoice.STATUS_VOID:
            return format_html('<b style="color:#6b7280;">● {}</b>', label)
        return format_html('<span style="color:#d97706;">● {}</span>', label)

    @admin.display(description=_("Commande"))
    def order_ref(self, obj: Invoice):
        o = getattr(obj, "order", None)
        if not o:
            return "—"
        ref = getattr(o, "reference", None) or getattr(o, "uuid", None) or str(o.pk)
        return str(ref)

    @admin.display(description=_("Client"))
    def order_user(self, obj: Invoice):
        o = getattr(obj, "order", None)
        u = getattr(o, "user", None) if o else None
        if not u:
            return "—"
        return getattr(u, "email", "") or str(u)

    @admin.display(description=_("PDF"))
    def pdf_link(self, obj: Invoice):
        if not obj.file:
            return "—"
        try:
            return format_html('<a href="{}" target="_blank" rel="noopener">📄 {}</a>', obj.file.url, _("Ouvrir"))
        except Exception:
            return _("(stockage indisponible)")

    @admin.display(description=_("Taille PDF"))
    def file_size(self, obj: Invoice):
        if not obj.file:
            return "—"
        try:
            sz = obj.file.size
            if sz is None:
                return "—"
            # format simple
            for unit in ["B", "KB", "MB", "GB"]:
                if sz < 1024:
                    return f"{sz:.0f} {unit}"
                sz = sz / 1024
            return f"{sz:.1f} TB"
        except Exception:
            return "—"

    @admin.display(description=_("Checksum"))
    def checksum_short(self, obj: Invoice):
        c = (obj.checksum or "").strip()
        return (c[:10] + "…") if c else "—"





# # economic/ecommerce/admin/invoice_admin.py
# from __future__ import annotations

# from django.contrib import admin

# from economic.ecommerce.models import Invoice


# @admin.register(Invoice)
# class InvoiceAdmin(admin.ModelAdmin):
#     list_display = ("uuid", "order", "created_at")
#     readonly_fields = ("uuid", "created_at", "file")
#     ordering = ("-created_at",)
#     autocomplete_fields = ("order",)
#     search_fields = ("uuid", "order__uuid")





# # /economic/ecommerce/admin/invoice_admin.py
# from django.contrib import admin
# from ..models.invoice import Invoice


# @admin.register(Invoice)
# class InvoiceAdmin(admin.ModelAdmin):
#     list_display = ("uuid", "order", "created_at")
#     readonly_fields = ("uuid", "created_at", "file")
