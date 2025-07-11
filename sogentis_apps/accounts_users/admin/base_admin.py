from django.contrib import admin

class BaseAdmin(admin.ModelAdmin):
    readonly_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]
    list_per_page = 25
