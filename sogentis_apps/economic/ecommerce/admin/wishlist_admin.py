# sogentis_apps/economic/ecommerce/admin/wishlist_admin.py

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from economic.ecommerce.models import Wishlist, WishlistItem


class WishlistItemInline(admin.TabularInline):
    model = WishlistItem
    extra = 0
    fields = ("product", "added_at")
    readonly_fields = ("added_at",)
    autocomplete_fields = ("product",)
    show_change_link = True


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    inlines = [WishlistItemInline]

    list_display = ("id", "user", "created_at", "items_count")
    search_fields = ("user__email", "user__username")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)

    fieldsets = (
        (_("Utilisateur"), {"fields": ("user",)}),
        (_("Dates"), {"fields": ("created_at",)}),
    )

    def items_count(self, obj):
        return obj.items.count()

    items_count.short_description = _("Nombre de produits")
