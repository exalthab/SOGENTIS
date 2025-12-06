# documents/admin.py
from django.contrib import admin
from .models import Document

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "is_public", "download_count", "created_at")
    list_filter = ("is_public", "created_at")
    search_fields = ("title", "description")

