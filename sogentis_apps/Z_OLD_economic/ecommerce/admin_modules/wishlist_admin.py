# ecommerce/admin_modules//wishlist_admin.py
from django.contrib import admin
from economic.ecommerce.models import Wishlist, WishlistItem


class WishlistItemInline(admin.TabularInline):
    model = WishlistItem
    extra = 0
    readonly_fields = ("product", "created_at")
    fields = ("product", "created_at")
    show_change_link = True  # Allow admin to jump to the product


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ("user", "items_count", "created_at")
    readonly_fields = ("created_at",)
    inlines = [WishlistItemInline]

    search_fields = ("user__email",)
    list_filter = ("created_at",)

    def items_count(self, obj):
        return obj.items.count()
    items_count.short_description = "Nb. d’articles"
