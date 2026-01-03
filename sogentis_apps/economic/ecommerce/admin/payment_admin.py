from django.contrib import admin
from ..models.payment_transactions import PaymentTransactions


@admin.register(PaymentTransactions)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "uuid",
        "order",
        "provider",
        "status",
        "amount",
        "currency",
        "created_at",
    )
    list_filter = ("provider", "status", "currency")
    search_fields = ("uuid", "provider_payment_id", "order__uuid")
    readonly_fields = ("uuid", "created_at", "updated_at", "payload")
