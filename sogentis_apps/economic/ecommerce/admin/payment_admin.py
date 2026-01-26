# economic/ecommerce/admin/payment_admin.py
from __future__ import annotations

import json

from django.contrib import admin, messages
from django.db import models
from django.utils import timezone
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from economic.ecommerce.models import PaymentTransaction


# ------------------------------------------------------------
# Admin actions (prod-safe)
# ------------------------------------------------------------
@admin.action(description=_("Marquer en 'En attente' (pending)"))
def action_mark_pending(modeladmin, request, queryset):
    n = 0
    for tx in queryset.select_related("order").only("id", "status"):
        try:
            if tx.status in {tx.STATUS_INITIATED, tx.STATUS_PENDING}:
                tx.mark_pending()
                n += 1
        except Exception:
            continue
    modeladmin.message_user(request, _("%(n)s transaction(s) passée(s) en pending.") % {"n": n}, messages.SUCCESS)


@admin.action(description=_("Bump attempt_count (+1)"))
def action_bump_attempt(modeladmin, request, queryset):
    n = queryset.update(attempt_count=models.F("attempt_count") + 1, updated_at=timezone.now())
    modeladmin.message_user(request, _("%(n)s transaction(s) bumpée(s).") % {"n": n}, messages.SUCCESS)


@admin.action(description=_("Marquer 'webhook reçu' (last_webhook_at=now)"))
def action_mark_webhook_now(modeladmin, request, queryset):
    n = queryset.update(last_webhook_at=timezone.now(), updated_at=timezone.now())
    modeladmin.message_user(request, _("%(n)s transaction(s): webhook timestamp mis à jour.") % {"n": n}, messages.SUCCESS)


@admin.action(description=_("Normaliser / re-valider (full_clean + save)"))
def action_revalidate(modeladmin, request, queryset):
    ok = 0
    for tx in queryset.select_related("order"):
        try:
            tx.save()
            ok += 1
        except Exception as e:
            modeladmin.message_user(request, f"[{tx.pk}] {e}", level=messages.ERROR)
    if ok:
        modeladmin.message_user(request, _("%(n)s transaction(s) re-validée(s).") % {"n": ok}, messages.SUCCESS)


# ------------------------------------------------------------
# Admin
# ------------------------------------------------------------
@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    save_on_top = True
    actions_on_top = True
    actions_on_bottom = True
    list_per_page = 50
    date_hierarchy = "created_at"

    ordering = ("-created_at",)
    autocomplete_fields = ("order",)

    list_display = (
        "uuid",
        "order_link",
        "provider_badge",
        "status_badge",
        "amount",
        "currency",
        "net_amount_display",
        "attempt_count",
        "last_webhook_at",
        "created_at",
    )
    list_display_links = ("uuid",)

    list_filter = (
        "provider",
        "status",
        "currency",
        ("created_at", admin.DateFieldListFilter),
        ("updated_at", admin.DateFieldListFilter),
    )

    search_fields = (
        "uuid",
        "idempotency_key",
        "provider_payment_id",
        "provider_event_id",
        "order__uuid",
        "order__reference",
        "order__user__email",
        "order__user__phone",
        "order__user__first_name",
        "order__user__last_name",
    )

    readonly_fields = (
        "uuid",
        "created_at",
        "updated_at",
        "succeeded_at",
        "failed_at",
        "cancelled_at",
        "net_amount_display",
        "payload_pretty",
    )

    fieldsets = (
        (_("Commande"), {"fields": ("order",)}),
        (_("Paiement"), {"fields": ("provider", "status", ("amount", "currency"), "provider_fee", "net_amount_display")}),
        (_("Idempotence & Provider IDs"), {"fields": ("idempotency_key", "provider_payment_id", "provider_event_id", "payment_url")}),
        (_("Observabilité"), {"fields": ("attempt_count", "last_webhook_at")}),
        (_("Échecs"), {"fields": ("failure_code", "failure_message"), "classes": ("collapse",)}),
        (_("Timestamps"), {"fields": ("created_at", "updated_at", "succeeded_at", "failed_at", "cancelled_at"), "classes": ("collapse",)}),
        (_("Payload"), {"fields": ("payload_pretty",), "classes": ("collapse",)}),
    )

    actions = (action_mark_pending, action_bump_attempt, action_mark_webhook_now, action_revalidate)

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("order", "order__user")
        )

    # ---------- UI helpers ----------
    @admin.display(description=_("Commande"), ordering="order__created_at")
    def order_link(self, obj: PaymentTransaction):
        try:
            ref = getattr(obj.order, "reference", None) or str(obj.order.uuid)
            return ref
        except Exception:
            return "—"

    @admin.display(description=_("Prestataire"))
    def provider_badge(self, obj: PaymentTransaction):
        p = obj.provider or ""
        label = obj.get_provider_display()
        if p in {obj.PROVIDER_STRIPE, obj.PROVIDER_PAYPAL}:
            return format_html('<span style="padding:2px 8px;border-radius:999px;border:1px solid #cbd5e1;">{}</span>', label)
        if p in {obj.PROVIDER_WAVE, obj.PROVIDER_ORANGE}:
            return format_html('<span style="padding:2px 8px;border-radius:999px;border:1px solid #fde68a;">{}</span>', label)
        return label

    @admin.display(description=_("Statut"))
    def status_badge(self, obj: PaymentTransaction):
        s = obj.status
        label = obj.get_status_display()
        if s == obj.STATUS_SUCCEEDED:
            return format_html('<b style="color:#16a34a;">● {}</b>', label)
        if s == obj.STATUS_FAILED:
            return format_html('<b style="color:#dc2626;">● {}</b>', label)
        if s == obj.STATUS_CANCELLED:
            return format_html('<b style="color:#6b7280;">● {}</b>', label)
        if s == obj.STATUS_PENDING:
            return format_html('<b style="color:#d97706;">● {}</b>', label)
        return format_html('<span style="color:#334155;">● {}</span>', label)

    @admin.display(description=_("Net"), ordering="provider_fee")
    def net_amount_display(self, obj: PaymentTransaction):
        try:
            return obj.net_amount
        except Exception:
            return "—"

    @admin.display(description=_("Payload (pretty)"))
    def payload_pretty(self, obj: PaymentTransaction):
        payload = getattr(obj, "payload", None) or {}
        try:
            txt = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)
        except Exception:
            txt = str(payload)
        return format_html(
            '<pre style="max-width:100%;white-space:pre-wrap;word-break:break-word;'
            'padding:12px;border:1px solid #e5e7eb;border-radius:10px;background:#f8fafc;">{}</pre>',
            txt,
        )




# # economic/ecommerce/admin/payment_admin.py
# from __future__ import annotations

# from django.contrib import admin

# from economic.ecommerce.models import PaymentTransaction


# @admin.register(PaymentTransaction)
# class PaymentTransactionAdmin(admin.ModelAdmin):
#     list_display = ("uuid", "order", "provider", "status", "amount", "currency", "created_at")
#     list_filter = ("provider", "status", "currency", "created_at")
#     search_fields = ("uuid", "provider_payment_id", "order__uuid")
#     readonly_fields = ("uuid", "created_at", "updated_at", "payload")
#     ordering = ("-created_at",)
#     autocomplete_fields = ("order",)





# # /economic/ecommerce/admin/payment_admin.py
# from django.contrib import admin
# from ..models.payment_transaction import PaymentTransaction


# @admin.register(PaymentTransaction)
# class PaymentTransactionAdmin(admin.ModelAdmin):
#     list_display = (
#         "uuid",
#         "order",
#         "provider",
#         "status",
#         "amount",
#         "currency",
#         "created_at",
#     )
#     list_filter = ("provider", "status", "currency")
#     search_fields = ("uuid", "provider_payment_id", "order__uuid")
#     readonly_fields = ("uuid", "created_at", "updated_at", "payload")
