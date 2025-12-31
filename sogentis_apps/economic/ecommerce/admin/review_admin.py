# sogentis_apps/economic/ecommerce/admin/review_admin.py

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from economic.ecommerce.models import Review


@admin.action(description=_("Approuver les avis sélectionnés"))
def approve_reviews(modeladmin, request, queryset):
    queryset.update(is_approved=True)


@admin.action(description=_("Désapprouver les avis sélectionnés"))
def unapprove_reviews(modeladmin, request, queryset):
    queryset.update(is_approved=False)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "product",
        "user",
        "rating",
        "is_approved",
        "created_at",
    )
    list_filter = ("rating", "is_approved", "created_at")
    search_fields = (
        "product__translations__name",
        "user__email",
        "title",
    )
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)

    actions = [approve_reviews, unapprove_reviews]

    fieldsets = (
        (_("Produit"), {"fields": ("product",)}),
        (_("Utilisateur"), {"fields": ("user",)}),
        (_("Contenu"), {"fields": ("rating", "title", "content")}),
        (_("Modération"), {"fields": ("is_approved",)}),
        (_("Dates"), {"fields": ("created_at",)}),
    )
