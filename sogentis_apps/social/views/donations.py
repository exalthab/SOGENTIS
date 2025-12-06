
# social/views/donations.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.template.loader import render_to_string
from django.http import FileResponse
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.core.files.base import ContentFile
from django.core.mail import EmailMessage
from io import BytesIO
from xhtml2pdf import pisa
from decimal import Decimal
import hashlib
import time

from social.forms import DonationForm
from social.models import Donation, Project, Publication
from social.services.donation_target_service import DonationTargetService
from about.models.child import Child
from about.models.mother import Mother

# ---------------------------------------------------------
# 1. Liste publique des 100 derniers dons
# ---------------------------------------------------------
def public_donations_view(request):
    donations = Donation.objects.filter(status="paid").order_by("-created_at")[:100]
    return render(request, "social/public_donations.html", {"donations": donations})


# ---------------------------------------------------------
# 2. Accueil Social
# ---------------------------------------------------------
def soci_index_view(request):
    projects = Project.objects.filter(is_active=True)
    publications = Publication.objects.filter(is_public=True)
    for project in projects:
        project.percent = project.percentage_collected()
    return render(request, "social/soci_index.html", {
        "projects": projects,
        "publications": publications,
    })


# ---------------------------------------------------------
# 3. Historique des dons de l'utilisateur connecté
# ---------------------------------------------------------
@login_required
def donation_history_view(request):
    donations = Donation.objects.filter(email=request.user.email).order_by("-created_at")
    return render(request, "social/donation_history.html", {"donations": donations})


# ---------------------------------------------------------
# 4. Formulaire de don — Étape 1
# ---------------------------------------------------------
def donation_view(request, child_id=None, mother_id=None, target_type=None, target_id=None):
    target_obj = None

    # 🔹 Résolution de la cible
    if child_id:
        target_obj = get_object_or_404(Child, id=child_id)
        target_type, target_id = "child", child_id
    elif mother_id:
        target_obj = get_object_or_404(Mother, id=mother_id)
        target_type, target_id = "mother", mother_id
    elif target_type and target_id:
        target_obj = DonationTargetService.resolve_instance(target_type, target_id)

    if request.method == "POST":
        form = DonationForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            # 🔹 Détection de la cible choisie
            if data.get("child"):
                target_type, target_id = "child", data.get("child").id
            elif data.get("mother"):
                target_type, target_id = "mother", data.get("mother").id

            # 🔹 Stockage minimal en session
            request.session["donation_data"] = {
                "amount": float(data.get("amount")),
                "donor_name": data.get("donor_name"),
                "email": data.get("email"),
                "message": data.get("message"),
                "project": data.get("project").id if data.get("project") else None,
                "monthly": bool(data.get("monthly")),
                "target_type": target_type,
                "target_id": target_id,
            }
            return redirect("social:donation_payment_choice")
    else:
        form = DonationForm()
        if target_obj:
            if isinstance(target_obj, Child):
                form.fields["child"].initial = target_obj.id
            elif isinstance(target_obj, Mother):
                form.fields["mother"].initial = target_obj.id

    return render(request, "social/donation_form.html", {
        "form": form,
        "target": getattr(target_obj, "name", None),
        "target_type": target_type,
        "target_id": target_id,
    })


# ---------------------------------------------------------
# 5. Choix du mode de paiement — Étape 2
# ---------------------------------------------------------
def donation_payment_choice_view(request):
    donation_data = request.session.get("donation_data")
    if not donation_data:
        messages.error(request, _("Données manquantes. Veuillez recommencer."))
        return redirect("social:donation")

    if request.method == "POST":
        payment_method = request.POST.get("payment_method")
        if not payment_method:
            messages.error(request, _("Veuillez choisir un mode de paiement."))
            return redirect("social:donation_payment_choice")

        # 🔹 Création du don avant redirection vers la passerelle
        donation = Donation.objects.create(
            amount=Decimal(str(donation_data.get("amount"))),
            donor_name=donation_data.get("donor_name"),
            email=donation_data.get("email"),
            message=donation_data.get("message"),
            monthly=donation_data.get("monthly", False),
            payment_method=payment_method,
            target_type=donation_data.get("target_type"),
            target_id=donation_data.get("target_id"),
            project_id=donation_data.get("project"),
        )

        # 🔹 Associer la cible via GenericForeignKey
        DonationTargetService.assign_gfk(donation)

        # 🔹 Stockage de l'id du don en session
        request.session["donation_id"] = donation.id

        # 🔹 Redirection vers la passerelle correspondante
        gateway_map = {
            "stripe": "social:stripe_checkout",
            "paypal": "social:paypal_checkout",
            "orange_money": "social:orange_money_checkout",
            "wave": "social:wave_checkout",
            "visa": "social:visa_checkout",
        }

        if payment_method not in gateway_map:
            messages.error(request, _("Méthode de paiement inconnue."))
            return redirect("social:donation_payment_choice")

        return redirect(gateway_map[payment_method], donation_id=donation.id)

    return render(request, "social/donation_payment_choice.html", {"donation": donation_data})


# ---------------------------------------------------------
# 6. Succès du paiement
# ---------------------------------------------------------
@login_required
def donation_success_view(request):
    donation_id = request.session.get("donation_id")
    if not donation_id:
        return redirect("social:donation")

    donation = get_object_or_404(Donation, id=donation_id, email=request.user.email)

    # 🔹 Génération du reçu PDF si nécessaire
    if not donation.pdf_receipt:
        generate_receipt_pdf(donation)
        send_receipt_by_email(donation)

    return render(request, "social/donation_success.html", {"donation": donation})


# ---------------------------------------------------------
# 7. Génération du reçu PDF
# ---------------------------------------------------------
def generate_receipt_pdf(donation):
    html = render_to_string("social/receipt_template.html", {"donation": donation})
    buffer = BytesIO()
    pisa.CreatePDF(html, dest=buffer)
    filename = f"recu_{slugify(donation.donor_name or 'don')}_{donation.created_at.date()}.pdf"
    donation.pdf_receipt.save(filename, ContentFile(buffer.getvalue()))
    donation.save()

def generate_receipt_uid(donation):
    raw = f"{donation.id}-{donation.created_at.timestamp()}"
    return hashlib.sha1(raw.encode()).hexdigest()[:12]

# ---------------------------------------------------------
# 8. Envoi du reçu par email
# ---------------------------------------------------------
def send_receipt_by_email(donation):
    html = render_to_string("social/receipt_template.html", {"donation": donation})
    buffer = BytesIO()
    pisa.CreatePDF(html, dest=buffer)

    email = EmailMessage(
        _("Reçu de votre don"),
        _("Merci pour votre générosité. Votre reçu est en pièce jointe."),
        to=[donation.email],
    )
    email.attach(f"recu_{donation.id}.pdf", buffer.getvalue(), "application/pdf")
    email.send()


# ---------------------------------------------------------
# 9. Téléchargement du reçu PDF
# ---------------------------------------------------------
@login_required
def download_receipt_view(request, donation_id):
    donation = get_object_or_404(Donation, id=donation_id, email=request.user.email)
    return FileResponse(donation.pdf_receipt.open(), content_type="application/pdf")


# ---------------------------------------------------------
# 10. Annulation du don
# ---------------------------------------------------------
@login_required
def donation_cancel_view(request):
    return render(request, "social/donation_cancel.html")
