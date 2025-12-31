from django.contrib import admin

from ..models import Certificate


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ("course", "issued_at")
    readonly_fields = ("uuid", "issued_at")
