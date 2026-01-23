# economic/formations/admin/certificate_admin.py
from __future__ import annotations

from django.contrib import admin, messages
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from ..models import Certificate

try:
    from economic.formations.services.certificate_pdf import generate_certificate_pdf_and_attach
except Exception:
    generate_certificate_pdf_and_attach = None

try:
    from economic.formations.services.certificate_email import send_certificate_email
except Exception:
    send_certificate_email = None


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ("code", "course", "session", "learner", "issued_at", "has_pdf", "revoked", "download_link")
    list_filter = ("revoked", "course")
    search_fields = ("code", "uuid", "course__translations__title", "enrollment__user__email", "enrollment__user__username")
    ordering = ("-issued_at",)
    autocomplete_fields = ("enrollment", "course", "session")
    readonly_fields = ("uuid", "issued_at", "code", "course", "session")

    actions = ["regenerate_pdf", "resend_email", "revoke", "unrevoke"]

    def learner(self, obj: Certificate):
        u = obj.enrollment.user
        return getattr(u, "email", None) or getattr(u, "username", None) or str(u)

    learner.short_description = _("Apprenant")

    def has_pdf(self, obj: Certificate):
        return bool(obj.pdf_file)

    has_pdf.boolean = True
    has_pdf.short_description = _("PDF")

    def download_link(self, obj: Certificate):
        try:
            url = reverse("economic:formations:certificate_download", kwargs={"uuid": obj.uuid})
            return format_html('<a class="button" href="{}">{}</a>', url, _("Télécharger"))
        except Exception:
            return "—"

    download_link.short_description = _("Lien")

    @admin.action(description=_("Régénérer PDF"))
    def regenerate_pdf(self, request, queryset):
        if not generate_certificate_pdf_and_attach:
            messages.error(request, _("Service PDF indisponible."))
            return
        n = 0
        for c in queryset:
            try:
                generate_certificate_pdf_and_attach(c, force=True)
                n += 1
            except Exception as exc:
                messages.error(request, f"{c.code}: {exc}")
        if n:
            messages.success(request, _("%(n)s PDF régénérés.") % {"n": n})

    @admin.action(description=_("Renvoyer email"))
    def resend_email(self, request, queryset):
        if not send_certificate_email:
            messages.error(request, _("Service email indisponible."))
            return
        n = 0
        for c in queryset:
            try:
                send_certificate_email(c)
                n += 1
            except Exception as exc:
                messages.error(request, f"{c.code}: {exc}")
        if n:
            messages.success(request, _("%(n)s emails envoyés.") % {"n": n})

    @admin.action(description=_("Révoquer"))
    def revoke(self, request, queryset):
        updated = queryset.update(revoked=True)
        messages.success(request, _("%(n)s certificats révoqués.") % {"n": updated})

    @admin.action(description=_("Annuler révocation"))
    def unrevoke(self, request, queryset):
        updated = queryset.update(revoked=False)
        messages.success(request, _("%(n)s certificats ré-activés.") % {"n": updated})




# # economic/formations/admin/certificate_admin.py
# from django.contrib import admin, messages
# from django.urls import reverse
# from django.utils.html import format_html
# from django.utils.translation import gettext_lazy as _

# from ..models import Certificate

# try:
#     from economic.formations.services.certificate_pdf import generate_certificate_pdf_and_attach
# except Exception:
#     generate_certificate_pdf_and_attach = None

# try:
#     from economic.formations.services.certificate_email import send_certificate_email
# except Exception:
#     send_certificate_email = None


# @admin.register(Certificate)
# class CertificateAdmin(admin.ModelAdmin):
#     list_display = ("code", "course", "learner", "issued_at", "has_pdf", "revoked", "download_link")
#     list_filter = ("revoked", "course")
#     search_fields = ("code", "uuid", "course__translations__title", "enrollment__user__email", "enrollment__user__username")
#     ordering = ("-issued_at",)
#     autocomplete_fields = ("enrollment", "course")
#     readonly_fields = ("uuid", "issued_at", "code")

#     actions = ["regenerate_pdf", "resend_email", "revoke", "unrevoke"]

#     def learner(self, obj: Certificate):
#         u = obj.enrollment.user
#         return getattr(u, "email", None) or getattr(u, "username", None) or str(u)
#     learner.short_description = _("Apprenant")

#     def has_pdf(self, obj: Certificate):
#         return bool(obj.pdf_file)
#     has_pdf.boolean = True
#     has_pdf.short_description = _("PDF")

#     def download_link(self, obj: Certificate):
#         try:
#             url = reverse("economic:formations:certificate_download", kwargs={"uuid": obj.uuid})
#             return format_html('<a class="button" href="{}">{}</a>', url, _("Télécharger"))
#         except Exception:
#             return "—"
#     download_link.short_description = _("Lien")

#     @admin.action(description=_("Régénérer PDF"))
#     def regenerate_pdf(self, request, queryset):
#         if not generate_certificate_pdf_and_attach:
#             messages.error(request, _("Service PDF indisponible."))
#             return
#         n = 0
#         for c in queryset:
#             try:
#                 generate_certificate_pdf_and_attach(c, force=True)
#                 n += 1
#             except Exception as exc:
#                 messages.error(request, f"{c.code}: {exc}")
#         if n:
#             messages.success(request, _("%(n)s PDF régénérés.") % {"n": n})

#     @admin.action(description=_("Renvoyer email"))
#     def resend_email(self, request, queryset):
#         if not send_certificate_email:
#             messages.error(request, _("Service email indisponible."))
#             return
#         n = 0
#         for c in queryset:
#             try:
#                 send_certificate_email(c)
#                 n += 1
#             except Exception as exc:
#                 messages.error(request, f"{c.code}: {exc}")
#         if n:
#             messages.success(request, _("%(n)s emails envoyés.") % {"n": n})

#     @admin.action(description=_("Révoquer"))
#     def revoke(self, request, queryset):
#         updated = queryset.update(revoked=True)
#         messages.success(request, _("%(n)s certificats révoqués.") % {"n": updated})

#     @admin.action(description=_("Annuler révocation"))
#     def unrevoke(self, request, queryset):
#         updated = queryset.update(revoked=False)
#         messages.success(request, _("%(n)s certificats ré-activés.") % {"n": updated})





# from django.contrib import admin

# from ..models import Certificate


# @admin.register(Certificate)
# class CertificateAdmin(admin.ModelAdmin):
#     list_display = ("course", "issued_at")
#     readonly_fields = ("uuid", "issued_at")
