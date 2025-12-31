# economic/ecommerce/articles/admin.py
from django.contrib import admin
from economic.ecommerce.articles.models import Article

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "is_published", "published_at")
    list_filter = ("is_published",)
    prepopulated_fields = {"slug": ("title",)}
