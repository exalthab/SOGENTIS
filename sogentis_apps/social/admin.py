print("social.admin loaded !")

import csv
from io import BytesIO
from django.contrib import admin
from django.core.files.base import ContentFile
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from xhtml2pdf import pisa

from .models import Donation, Engagement, Project, Publication, DocumentPurchase

@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display = ("title", "created_at", "is_public")
    list_filter = ("is_public",)
    search_fields = ("title", "description")

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = (
        "donor_name", "email", "amount", "project",
        "get_donation_type", "payment_method", "status",
        "created_at", "pdf_receipt_link"
    )
    list_filter = ("project", "payment_method", "status", "monthly", "created_at")
    search_fields = ("donor_name", "email", "message", "project__title")
    readonly_fields = ("created_at", "pdf_receipt")
    actions = ["export_donations_as_csv"]

    def get_donation_type(self, obj):
        icon = "🔁" if obj.monthly else "💸"
        return format_html('{}&nbsp;{}', icon, obj.donation_type)
    get_donation_type.short_description = _("Type de don")

    def pdf_receipt_link(self, obj):
        if obj.pdf_receipt:
            return format_html(
                '<a href="{}" target="_blank">📄 Télécharger</a>',
                obj.pdf_receipt.url
            )
        return "—"
    pdf_receipt_link.short_description = _("Reçu PDF")

    def export_donations_as_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="donations.csv"'
        writer = csv.writer(response)
        writer.writerow([
            "Nom", "Email", "Montant", "Projet",
            "Méthode", "Type", "Statut", "Date"
        ])
        for obj in queryset:
            writer.writerow([
                obj.donor_name,
                obj.email,
                obj.amount,
                obj.project.title if obj.project else "",
                obj.get_payment_method_display(),
                obj.donation_type,
                obj.get_status_display(),
                obj.created_at.strftime("%Y-%m-%d %H:%M"),
            ])
        return response
    export_donations_as_csv.short_description = _("Exporter les dons sélectionnés en CSV")

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj.status == "paid" and not obj.pdf_receipt:
            self.generate_receipt_pdf(obj)
            self.send_receipt_by_email(obj)

    def generate_receipt_pdf(self, donation):
        html = render_to_string("social/receipt_template.html", {"donation": donation})
        pdf_file = BytesIO()
        result = pisa.CreatePDF(html, dest=pdf_file)
        if not result.err:
            filename = f"recu_{donation.id}.pdf"
            donation.pdf_receipt.save(filename, ContentFile(pdf_file.getvalue()))
            donation.save()

    def send_receipt_by_email(self, donation):
        html = render_to_string("social/receipt_template.html", {"donation": donation})
        pdf_file = BytesIO()
        pisa.CreatePDF(html, dest=pdf_file)
        email = EmailMessage(
            subject=_("Reçu de votre don"),
            body=_("Merci pour votre soutien. Veuillez trouver votre reçu ci-joint."),
            to=[donation.email],
        )
        email.attach(f"recu_{donation.id}.pdf", pdf_file.getvalue(), "application/pdf")
        email.send()

    def has_add_permission(self, request):
        return False  # désactive l’ajout manuel via l’admin


@admin.register(Engagement)
class EngagementAdmin(admin.ModelAdmin):
    list_display = ("user", "title", "date", "is_active")
    list_filter = ("is_active", "date")
    search_fields = ("user__email", "title")
    actions = ["export_as_csv"]

    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="engagements.csv"'
        writer = csv.writer(response)
        writer.writerow(["Utilisateur", "Titre", "Date", "Actif"])
        for obj in queryset:
            writer.writerow([
                str(obj.user), obj.title, obj.date, "Oui" if obj.is_active else "Non"
            ])
        return response
    export_as_csv.short_description = _("Exporter les engagements sélectionnés en CSV")

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "progress_bar", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("title",)

    def progress_bar(self, obj):
        percent = obj.percentage_collected()
        try:
            percent = float(percent)
        except (TypeError, ValueError):
            percent = 0.0

        percent_str = f"{percent:.1f}"
        bar_color = (
            "success" if percent >= 75 else
            "warning" if percent >= 50 else
            "danger"
        )
        return format_html(
            """
            <div style="width: 100px;">
              <div class="progress" style="height: 10px; background-color: #e9ecef;">
                <div class="progress-bar bg-{}" role="progressbar"
                     style="width: {}%;" aria-valuenow="{}"
                     aria-valuemin="0" aria-valuemax="100">
                </div>
              </div>
              <small>{}%</small>
            </div>
            """,
            bar_color, percent_str, percent_str, percent_str
        )
    progress_bar.short_description = _("Avancement")

@admin.register(DocumentPurchase)
class DocumentPurchaseAdmin(admin.ModelAdmin):
    list_display = (
        "user", "publication", "email", "amount_paid",
        "payment_method", "purchased_at", "copy_number", "has_downloaded"
    )
    search_fields = ("user__email", "publication__title", "email", "payment_id")
    list_filter = ("payment_method", "purchased_at", "has_downloaded")
    readonly_fields = ("purchased_at",)




# print("social.admin loaded !")
# #social/admin
# import csv
# from io import BytesIO
# from django.contrib import admin
# from django.core.files.base import ContentFile
# from django.core.mail import EmailMessage
# from django.http import HttpResponse
# from django.template.loader import render_to_string
# from django.utils.html import format_html
# from django.utils.translation import gettext_lazy as _
# from xhtml2pdf import pisa

# # 👇 si tu as une gestion DocumentPurchase, importe le fichier admin associé

# from .models import Donation, Engagement, Project, Publication, DocumentPurchase

# @admin.register(Publication)
# class PublicationAdmin(admin.ModelAdmin):
#     list_display = ("title", "created_at", "is_public")
#     list_filter = ("is_public",)
#     search_fields = ("title", "description")

# @admin.register(Donation)
# class DonationAdmin(admin.ModelAdmin):
#     list_display = (
#         "donor_name", "email", "amount", "project",
#         "get_donation_type", "payment_method", "status",
#         "created_at", "pdf_receipt_link"
#     )
#     list_filter = ("project", "payment_method", "status", "created_at")
#     search_fields = ("donor_name", "email", "message", "project__title")
#     readonly_fields = ("created_at", "pdf_receipt")
#     actions = ["export_donations_as_csv"]

#     def get_donation_type(self, obj):
#         return obj.donation_type
#     get_donation_type.short_description = _("Type de don")

#     def pdf_receipt_link(self, obj):
#         if obj.pdf_receipt:
#             return format_html(
#                 '<a href="{}" target="_blank">📄 Télécharger</a>',
#                 obj.pdf_receipt.url
#             )
#         return "—"
#     pdf_receipt_link.short_description = _("Reçu PDF")

#     def export_donations_as_csv(self, request, queryset):
#         response = HttpResponse(content_type="text/csv")
#         response["Content-Disposition"] = 'attachment; filename="donations.csv"'
#         writer = csv.writer(response)
#         writer.writerow(["Nom", "Email", "Montant", "Projet", "Méthode", "Type", "Statut", "Date"])
#         for obj in queryset:
#             writer.writerow([
#                 obj.donor_name,
#                 obj.email,
#                 obj.amount,
#                 obj.project.title if obj.project else "",
#                 obj.get_payment_method_display(),
#                 obj.donation_type,
#                 obj.get_status_display(),
#                 obj.created_at.strftime("%Y-%m-%d %H:%M"),
#             ])
#         return response
#     export_donations_as_csv.short_description = _("Exporter les dons sélectionnés en CSV")

#     def save_model(self, request, obj, form, change):
#         super().save_model(request, obj, form, change)
#         if obj.status == "paid" and not obj.pdf_receipt:
#             self.generate_receipt_pdf(obj)
#             self.send_receipt_by_email(obj)

#     def generate_receipt_pdf(self, donation):
#         html = render_to_string("social/receipt_template.html", {"donation": donation})
#         pdf_file = BytesIO()
#         result = pisa.CreatePDF(html, dest=pdf_file)
#         if not result.err:
#             filename = f"recu_{donation.id}.pdf"
#             donation.pdf_receipt.save(filename, ContentFile(pdf_file.getvalue()))
#             donation.save()

#     def send_receipt_by_email(self, donation):
#         html = render_to_string("social/receipt_template.html", {"donation": donation})
#         pdf_file = BytesIO()
#         pisa.CreatePDF(html, dest=pdf_file)
#         email = EmailMessage(
#             subject=_("Reçu de votre don"),
#             body=_("Merci pour votre soutien. Veuillez trouver votre reçu ci-joint."),
#             to=[donation.email],
#         )
#         email.attach(f"recu_{donation.id}.pdf", pdf_file.getvalue(), "application/pdf")
#         email.send()

#     def has_add_permission(self, request):
#         return False  # désactive l’ajout manuel via l’admin

# @admin.register(Engagement)
# class EngagementAdmin(admin.ModelAdmin):
#     list_display = ("user", "title", "date", "is_active")
#     list_filter = ("is_active", "date")
#     search_fields = ("user__email", "title")
#     actions = ["export_as_csv"]

#     def export_as_csv(self, request, queryset):
#         response = HttpResponse(content_type="text/csv")
#         response["Content-Disposition"] = 'attachment; filename="engagements.csv"'
#         writer = csv.writer(response)
#         writer.writerow(["Utilisateur", "Titre", "Date", "Actif"])
#         for obj in queryset:
#             writer.writerow([
#                 str(obj.user), obj.title, obj.date, "Oui" if obj.is_active else "Non"
#             ])
#         return response
#     export_as_csv.short_description = _("Exporter les engagements sélectionnés en CSV")

# @admin.register(Project)
# class ProjectAdmin(admin.ModelAdmin):
#     list_display = ("title", "description", "progress_bar", "is_active", "created_at")
#     list_filter = ("is_active",)
#     search_fields = ("title",)

#     def progress_bar(self, obj):
#         percent = obj.percentage_collected()
#         try:
#             percent = float(percent)
#         except (TypeError, ValueError):
#             percent = 0.0

#         percent_str = f"{percent:.1f}"
#         bar_color = (
#             "success" if percent >= 75 else
#             "warning" if percent >= 50 else
#             "danger"
#         )
#         return format_html(
#             """
#             <div style="width: 100px;">
#               <div class="progress" style="height: 10px; background-color: #e9ecef;">
#                 <div class="progress-bar bg-{}" role="progressbar"
#                      style="width: {}%;" aria-valuenow="{}"
#                      aria-valuemin="0" aria-valuemax="100">
#                 </div>
#               </div>
#               <small>{}%</small>
#             </div>
#             """,
#             bar_color, percent_str, percent_str, percent_str
#         )
#     progress_bar.short_description = _("Avancement")\
        
# @admin.register(DocumentPurchase)
# class DocumentPurchaseAdmin(admin.ModelAdmin):
#     list_display = ("user", "publication", "email", "amount_paid", "payment_method", "purchased_at", "copy_number", "has_downloaded")
#     search_fields = ("user__email", "publication__title", "email", "payment_id")
#     list_filter = ("payment_method", "purchased_at", "has_downloaded")
#     readonly_fields = ("purchased_at",)
