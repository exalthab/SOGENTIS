# search/admin.py
from django.contrib import admin
from .models import IndexedDocument


@admin.register(IndexedDocument)
class IndexedDocumentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "source_app",
        "source_model",
        "object_id",
        "author",
        "is_public",
        "created_at",
    )
    search_fields = ("title", "description", "body", "file_url")
    list_filter = ("source_app", "source_model", "is_public")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)





# # search/admin.py
# from django.contrib import admin
# from .models import IndexedDocument

# @admin.register(IndexedDocument)
# class IndexedDocumentAdmin(admin.ModelAdmin):
#     list_display = ("id", "title", "source_app", "source_model", "object_id", "author", "is_public", "created_at")
#     search_fields = ("title", "description", "body", "file_url")
#     list_filter = ("source_app", "source_model", "is_public")
#     readonly_fields = ("created_at", "updated_at")
#     ordering = ("-created_at",)
