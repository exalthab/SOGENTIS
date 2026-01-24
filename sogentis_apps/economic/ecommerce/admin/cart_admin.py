# economic/ecommerce/admin/cart_admin.py
from __future__ import annotations

from django.contrib import admin

from economic.ecommerce.models import Cart, CartItem


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__email", "user__phone", "user__first_name", "user__last_name")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("id", "cart", "product", "quantity")
    list_filter = ("cart__created_at",)
    search_fields = ("cart__user__email", "product__translations__name", "product__sku")
    autocomplete_fields = ("cart", "product")





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
