# economic/ecommerce/admin/order_item_admin.py
from __future__ import annotations

from django.contrib import admin

from economic.ecommerce.models import OrderItem


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "product", "quantity", "unit_price")
    list_filter = ("order__created_at",)
    search_fields = ("order__uuid", "product__translations__name", "product__sku")
    autocomplete_fields = ("order", "product")





# # /economic/ecommerce/admin/order_item_admin.py
# from django.contrib import admin
# from ..models.order_item import OrderItem


# @admin.register(OrderItem)
# class OrderItemAdmin(admin.ModelAdmin):
#     list_display = ("order", "product", "quantity", "unit_price")
