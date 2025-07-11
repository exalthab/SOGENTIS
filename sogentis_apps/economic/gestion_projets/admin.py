from django.contrib import admin
from .models import Service

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "is_active", "created_at")
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "short_description", "description")
