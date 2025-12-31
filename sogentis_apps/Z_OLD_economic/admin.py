# # economic/admin.py

# from django.contrib import admin
# from .models import Product, Category

# @admin.register(Category)
# class CategoryAdmin(admin.ModelAdmin):
#     prepopulated_fields = {"slug": ("name",)}

# @admin.register(Product)
# class ProductAdmin(admin.ModelAdmin):
#     list_display = ("name", "category", "price", "is_new", "created_at")
#     list_filter = ("category", "is_new")
#     search_fields = ("name", "description")
#     prepopulated_fields = {"slug": ("name",)}
