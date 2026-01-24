# economic/ecommerce/admin/payment_admin.py
from __future__ import annotations

from django.contrib import admin

from economic.ecommerce.models import PaymentTransaction


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ("uuid", "order", "provider", "status", "amount", "currency", "created_at")
    list_filter = ("provider", "status", "currency", "created_at")
    search_fields = ("uuid", "provider_payment_id", "order__uuid")
    readonly_fields = ("uuid", "created_at", "updated_at", "payload")
    ordering = ("-created_at",)
    autocomplete_fields = ("order",)





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
