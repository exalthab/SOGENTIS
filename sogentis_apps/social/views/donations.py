# #social/views/donations.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.http import FileResponse
from django.template.loader import render_to_string
from django.utils.text import slugify
from django.core.files.base import ContentFile
from django.core.mail import EmailMessage
from django.urls import reverse

from io import BytesIO
from xhtml2pdf import pisa

from social.forms import DonationForm
from social.models import Donation, Project, Publication

# 🔓 Liste publique des dons
def public_donations_view(request):
    donations = Donation.objects.filter(status="paid").order_by("-created_at")[:100]
    return render(request, "social/public_donations.html", {"donations": donations})

# 🏠 Accueil Social (utilise soci_index_view en pratique)
def soci_index(request):
    projects = Project.objects.filter(is_active=True)
    publications = Publication.objects.filter(is_public=True)
    for project in projects:
        project.percent = project.percentage_collected()
    return render(request, "social/soci_index.html", {
        "projects": projects,
        "publications": publications,
    })

@login_required
def donation_history_view(request):
    donations = Donation.objects.filter(
        email=request.user.email
    ).order_by("-created_at")
    return render(request, "social/donation_history.html", {"donations": donations})

def donation_view(request):
    if request.method == 'POST':
        form = DonationForm(request.POST)
        if form.is_valid():
            donation = form.save(commit=False)
            # Priorité à l'utilisateur connecté
            if request.user.is_authenticated:
                donation.email = request.user.email
            donation.save()
            request.session["donation_id"] = donation.id
            return redirect("social:donation_payment_choice")
    else:
        form = DonationForm()
    return render(request, "social/donation_form.html", {"form": form})

def donation_payment_choice_view(request):
    donation_id = request.session.get("donation_id")
    if not donation_id:
        messages.error(request, _("Aucun don en attente."))
        return redirect("social:donation")
    if request.method == "POST":
        payment_method = request.POST.get("payment_method")
        donation = get_object_or_404(Donation, id=donation_id)
        if payment_method:
            donation.payment_method = payment_method
            donation.save()
            # Redirige vers la bonne passerelle
            return redirect(reverse(f"social:{payment_method}_checkout", args=[donation.id]))
        messages.error(request, _("Méthode de paiement non reconnue."))
        return redirect("social:donation_payment_choice")
    return render(request, "social/donation_payment_choice.html")

@login_required
def donation_success_view(request):
    donation_id = request.session.get("donation_id")
    if not donation_id:
        return redirect("social:donation")
    donation = get_object_or_404(Donation, id=donation_id, email=request.user.email)
    if not donation.pdf_receipt:
        generate_receipt_pdf(donation)
        send_receipt_by_email(donation)
    return render(request, "social/donation_success.html", {"donation_id": donation.id})

def generate_receipt_pdf(donation):
    html = render_to_string("social/receipt_template.html", {"donation": donation})
    pdf_file = BytesIO()
    pisa.CreatePDF(html, dest=pdf_file)
    filename = f"recu_{slugify(donation.donor_name or 'anonyme')}_{donation.created_at.date()}.pdf"
    donation.pdf_receipt.save(filename, ContentFile(pdf_file.getvalue()))
    donation.save()

def send_receipt_by_email(donation):
    html = render_to_string("social/receipt_template.html", {"donation": donation})
    pdf_file = BytesIO()
    pisa.CreatePDF(html, dest=pdf_file)
    email = EmailMessage(
        _("Reçu de votre don"),
        _("Merci pour votre générosité. Veuillez trouver ci-joint votre reçu."),
        to=[donation.email]
    )
    email.attach(f"recu_{donation.id}.pdf", pdf_file.getvalue(), 'application/pdf')
    email.send()

@login_required
def download_receipt_view(request, donation_id):
    donation = get_object_or_404(Donation, id=donation_id, email=request.user.email)
    return FileResponse(donation.pdf_receipt.open(), content_type='application/pdf')

@login_required
def donation_cancel_view(request):
    return render(request, "social/donation_cancel.html")