# review_admin.py
from django.contrib import admin
from economic.ecommerce.models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "rating", "is_approved", "created_at")
    list_filter = ("rating", "is_approved", "created_at")
    search_fields = ("product__translations__name", "user__email", "comment")
    ordering = ("-created_at",)

    actions = ["approve_reviews"]

    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)

    approve_reviews.short_description = "Approuver les avis sélectionnés"
