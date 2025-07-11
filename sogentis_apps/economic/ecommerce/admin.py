print("economic.ecommerce.admin loaded !")

from django.contrib import admin
from .models import Product, Category, Order, OrderItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "is_new", "created_at", "stock_display")
    list_filter = ("category", "is_new", "created_at")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    date_hierarchy = "created_at"

    readonly_fields = ("created_at",)

    def stock_display(self, obj):
        return obj.stock if hasattr(obj, "stock") else "-"
    stock_display.short_description = "Stock"

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("tracking_code", "full_name", "status", "created_at")
    search_fields = ("tracking_code", "full_name", "email")

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "quantity", "price")