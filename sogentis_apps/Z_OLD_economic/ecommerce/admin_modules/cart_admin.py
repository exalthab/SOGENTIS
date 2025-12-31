# /ecommerce/admin_modules/cart_admin.py
from django.contrib import admin
from economic.ecommerce.models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ("product", "quantity", "unit_price", "subtotal", "created_at")
    fields = ("product", "quantity", "unit_price", "subtotal", "created_at")


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "session_key", "items_count", "subtotal", "created_at")
    readonly_fields = ("created_at", "updated_at", "subtotal")
    inlines = [CartItemInline]

    search_fields = ("user__email", "session_key")
    list_filter = ("created_at", "updated_at")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return (
            qs.select_related("user")
              .prefetch_related("items", "items__product")
        )
