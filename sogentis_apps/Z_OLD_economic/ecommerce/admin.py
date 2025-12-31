print("economic.ecommerce.admin loaded !")
# economic/ecommerce/admin.py

from django.contrib import admin
from .admin_modules import *

from .admin_modules.category_admin import *
from .admin_modules.product_admin import *
from .admin_modules.review_admin import *
from .admin_modules.order_admin import *
from .admin_modules.cart_admin import *
from .admin_modules.wishlist_admin import *

admin.site.site_header = "SOGENTIS — E-Commerce Admin"
admin.site.site_title = "SOGENTIS Admin"
admin.site.index_title = "Gestion Marketplace & Commandes"









# print("economic.ecommerce.admin loaded !")
# # economic/ecommerce/admin.py
# from django.contrib import admin
# from .models import Product, Category, Order, OrderItem

# @admin.register(Category)
# class CategoryAdmin(admin.ModelAdmin):
#     list_display = ("name", "slug")
#     prepopulated_fields = {"slug": ("name",)}
#     search_fields = ("name",)
#     ordering = ("name",)


# @admin.register(Product)
# class ProductAdmin(admin.ModelAdmin):
#     list_display = ("name", "category", "price", "is_new", "created_at", "stock_display")
#     list_filter = ("category", "is_new", "created_at")
#     search_fields = ("name", "description")
#     prepopulated_fields = {"slug": ("name",)}
#     date_hierarchy = "created_at"

#     readonly_fields = ("created_at",)

#     def stock_display(self, obj):
#         return obj.stock if hasattr(obj, "stock") else "-"
#     stock_display.short_description = "Stock"

# @admin.register(Order)
# class OrderAdmin(admin.ModelAdmin):
#     list_display = ("tracking_code", "full_name", "status", "created_at")
#     search_fields = ("tracking_code", "full_name", "email")

# @admin.register(OrderItem)
# class OrderItemAdmin(admin.ModelAdmin):
#     list_display = ("order", "product", "quantity", "price")