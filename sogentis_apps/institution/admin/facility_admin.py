from django.contrib import admin

from institution.models.facility import Facility


@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display = ("name", "facility_type", "city", "country", "is_active", "created_at")
    list_filter = ("facility_type", "country", "is_active")
    search_fields = ("name", "city", "address", "email", "phone")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("-created_at",)
