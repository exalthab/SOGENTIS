from django.contrib import admin
from economic.ecommerce.models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product_name", "quantity", "unit_price", "line_total")
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "tracking_code",
        "full_name",
        "status",
        "total",
        "payment_method",
        "created_at",
    )

    list_filter = ("status", "payment_method", "created_at")
    search_fields = ("tracking_code", "full_name", "email")
    ordering = ("-created_at",)

    readonly_fields = (
        "tracking_code",
        "subtotal",
        "tax",
        "shipping_fee",
        "discount_total",
        "total",
        "created_at",
        "updated_at",
    )

    inlines = [OrderItemInline]

    fieldsets = (
        ("🧾 Commande", {
            "fields": ("tracking_code", "status")
        }),
        ("👤 Client", {
            "fields": ("user", "full_name", "email", "phone")
        }),
        ("📦 Livraison", {
            "fields": ("shipping_address", "shipping_city", "shipping_country")
        }),
        ("💳 Paiement", {
            "fields": ("payment_method", "transaction_id", "paid_at")
        }),
        ("💰 Totaux", {
            "fields": ("subtotal", "tax", "shipping_fee", "discount_total", "total")
        }),
        ("🕒 Dates", {
            "fields": ("created_at", "updated_at")
        }),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product_name", "quantity", "unit_price")
    readonly_fields = ("order", "product_name", "quantity", "unit_price")
