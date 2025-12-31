# social/views/donations.py
from decimal import Decimal
from io import BytesIO
import os

import qrcode
from xhtml2pdf import pisa

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles import finders
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.mail import EmailMessage
from django.db import models
from django.http import FileResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from social.forms import DonationForm
from social.models import Donation, Project, Publication
from social.services.donation_target_service import DonationTargetService
from about.models.child import Child
from about.models.mother import Mother


# ---------------------------------------------------------
# Helpers PDF / STATIC
# ---------------------------------------------------------
def static_file_uri(static_path: str) -> str:
    abs_path = finders.find(static_path)
    if not abs_path:
        return ""
    abs_path = os.path.abspath(abs_path).replace("\\", "/")
    if ":" in abs_path[:3]:
        return f"file:///{abs_path}"
    return f"file://{abs_path}"


def generate_qr_code_uri(donation: Donation) -> str:
    """
    QR code stocké dans MEDIA/donations/qr/... et retourné en file://... pour xhtml2pdf
    Le QR pointe vers une page de vérification.
    """
    site_url = getattr(settings, "SITE_URL", "").rstrip("/")
    verify_url = f"{site_url}/social/donation/receipt/{donation.receipt_uid}/verify/" if site_url else f"RECEIPT:{donation.receipt_uid}"

    qr = qrcode.QRCode(
        version=2,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=2,
    )
    qr.add_data(verify_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    rel_path = f"donations/qr/receipt_{donation.id}_{donation.receipt_uid}.png"

    if not default_storage.exists(rel_path):
        buf = BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        default_storage.save(rel_path, ContentFile(buf.getvalue()))

    abs_path = default_storage.path(rel_path).replace("\\", "/")
    if ":" in abs_path[:3]:
        return f"file:///{abs_path}"
    return f"file://{abs_path}"


def build_receipt_context(donation: Donation) -> dict:
    return {
        "donation": donation,
        "receipt_uid": donation.receipt_uid,
        "logo_path": static_file_uri("images/logo.png"),
        "signature_path": static_file_uri("images/signature.png"),
        "stamp_path": static_file_uri("images/stamp.png"),
        "qr_code_path": generate_qr_code_uri(donation),
    }


def _is_owner(request, donation: Donation) -> bool:
    if donation.user_id:
        return donation.user_id == request.user.id
    return bool(donation.email) and donation.email == request.user.email


# ---------------------------------------------------------
# 1. Liste publique des 100 derniers dons (payés)
# ---------------------------------------------------------
def public_donations_view(request):
    donations = (
        Donation.objects.filter(status="paid")
        .select_related("project", "user")
        .order_by("-created_at")[:100]
    )
    return render(request, "social/public_donations.html", {"donations": donations})


# ---------------------------------------------------------
# 2. Accueil Social
# ---------------------------------------------------------
def soci_index_view(request):
    projects = Project.objects.filter(is_active=True)
    publications = Publication.objects.filter(is_public=True)
    for project in projects:
        project.percent = project.percentage_collected()
    return render(request, "social/soci_index.html", {"projects": projects, "publications": publications})


# ---------------------------------------------------------
# 3. Historique des dons du user connecté
# ---------------------------------------------------------
@login_required
def donation_history_view(request):
    donations = (
        Donation.objects.filter(
            models.Q(user=request.user) |
            models.Q(user__isnull=True, email=request.user.email)
        )
        .select_related("project", "user")
        .order_by("-created_at")
    )
    return render(request, "social/donation_history.html", {"donations": donations})


# ---------------------------------------------------------
# 4. Formulaire de don — Étape 1
# ---------------------------------------------------------
def donation_view(request, child_id=None, mother_id=None, target_type=None, target_id=None):
    target_obj = None

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

            if data.get("child"):
                target_type, target_id = "child", data["child"].id
            elif data.get("mother"):
                target_type, target_id = "mother", data["mother"].id

            if request.user.is_authenticated:
                donor_email = request.user.email
                donor_name = request.user.get_full_name().strip() or data.get("donor_name")
            else:
                donor_email = data.get("email")
                donor_name = data.get("donor_name")

            request.session["donation_data"] = {
                "amount": str(data.get("amount")),
                "donor_name": donor_name or "",
                "email": donor_email or "",
                "message": data.get("message") or "",
                "project": data.get("project").id if data.get("project") else None,
                "monthly": bool(data.get("monthly")),
                "target_type": target_type,
                "target_id": target_id,
            }
            return redirect("social:donation_payment_choice")
    else:
        initial = {}
        if request.user.is_authenticated:
            initial["email"] = request.user.email
            full_name = request.user.get_full_name().strip()
            if full_name:
                initial["donor_name"] = full_name

        form = DonationForm(initial=initial)

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
# 5. Choix paiement — Étape 2
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

        donation = Donation.objects.create(
            amount=Decimal(str(donation_data.get("amount"))),
            donor_name=donation_data.get("donor_name") or "",
            email=donation_data.get("email") or "",
            message=donation_data.get("message") or "",
            monthly=bool(donation_data.get("monthly", False)),
            payment_method=payment_method,
            target_type=donation_data.get("target_type"),
            target_id=donation_data.get("target_id"),
            project_id=donation_data.get("project"),
            user=request.user if request.user.is_authenticated else None,
            status="pending",
        )

        DonationTargetService.assign_gfk(donation)
        request.session["donation_id"] = donation.id

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
# 6. Succès paiement (retour)
# ---------------------------------------------------------
@login_required
def donation_success_view(request):
    donation_id = request.session.get("donation_id")
    if not donation_id:
        return redirect("social:donation")

    donation = get_object_or_404(Donation, id=donation_id)

    if not _is_owner(request, donation):
        raise Http404(_("Don introuvable"))

    if donation.status != "paid":
        messages.warning(request, _("Paiement en cours de confirmation."))

    if donation.status == "paid" and not donation.pdf_receipt:
        generate_receipt_pdf(donation)
        send_receipt_by_email(donation)

    return render(request, "social/donation_success.html", {"donation": donation})


# ---------------------------------------------------------
# 7. Génération du reçu PDF
# ---------------------------------------------------------
def generate_receipt_pdf(donation: Donation):
    context = build_receipt_context(donation)
    html = render_to_string("social/receipt_template.html", context)

    buffer = BytesIO()
    pisa.CreatePDF(html, dest=buffer)

    filename = f"recu_{slugify(donation.donor_name or 'don')}_{donation.created_at.date()}_{donation.id}.pdf"
    donation.pdf_receipt.save(filename, ContentFile(buffer.getvalue()))
    donation.save(update_fields=["pdf_receipt"])


# ---------------------------------------------------------
# 8. Envoi du reçu par email (PDF identique + images OK)
# ---------------------------------------------------------
def send_receipt_by_email(donation: Donation):
    to_email = donation.email or (donation.user.email if donation.user else "")
    if not to_email:
        return

    context = build_receipt_context(donation)
    pdf_html = render_to_string("social/receipt_template.html", context)

    pdf_buffer = BytesIO()
    pisa.CreatePDF(pdf_html, dest=pdf_buffer)

    body_html = render_to_string("social/receipt_email.html", {"donation": donation})

    email = EmailMessage(
        subject=_("Reçu de votre don"),
        body=body_html,
        to=[to_email],
    )
    email.content_subtype = "html"
    email.attach(f"recu_{donation.id}.pdf", pdf_buffer.getvalue(), "application/pdf")
    email.send(fail_silently=True)


# ---------------------------------------------------------
# 9. Téléchargement reçu (sécurisé)
# ---------------------------------------------------------
@login_required
def download_receipt_view(request, donation_id):
    donation = get_object_or_404(Donation, id=donation_id)

    if not _is_owner(request, donation):
        raise Http404(_("Reçu introuvable"))

    if not donation.pdf_receipt:
        raise Http404(_("Aucun reçu disponible"))

    return FileResponse(donation.pdf_receipt.open("rb"), content_type="application/pdf")


# ---------------------------------------------------------
# 10. Annulation du don
# ---------------------------------------------------------
@login_required
def donation_cancel_view(request):
    return render(request, "social/donation_cancel.html")


# ---------------------------------------------------------
# 11. Vérification du reçu (public)
# ---------------------------------------------------------
def receipt_verify_view(request, receipt_uid: str):
    donation = get_object_or_404(Donation, receipt_uid=receipt_uid)
    return render(request, "social/receipt_verify.html", {"donation": donation})





# # social/views/donations.py
# import os
# from django.contrib.staticfiles import finders
# from decimal import Decimal
# from io import BytesIO
# import hashlib

# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from django.core.files.base import ContentFile
# from django.core.mail import EmailMessage
# from django.db import models
# from django.http import FileResponse, Http404
# from django.shortcuts import render, redirect, get_object_or_404
# from django.template.loader import render_to_string
# from django.utils.text import slugify
# from django.utils.translation import gettext_lazy as _

# from xhtml2pdf import pisa

# from social.forms import DonationForm
# from social.models import Donation, Project, Publication
# from social.services.donation_target_service import DonationTargetService
# from about.models.child import Child
# from about.models.mother import Mother


# # ---------------------------------------------------------
# # 1. Liste publique des 100 derniers dons (payés)
# # ---------------------------------------------------------
# def public_donations_view(request):
#     donations = (
#         Donation.objects.filter(status="paid")
#         .select_related("project", "user")
#         .order_by("-created_at")[:100]
#     )
#     return render(request, "social/public_donations.html", {"donations": donations})


# # ---------------------------------------------------------
# # 2. Accueil Social
# # ---------------------------------------------------------
# def soci_index_view(request):
#     projects = Project.objects.filter(is_active=True)
#     publications = Publication.objects.filter(is_public=True)
#     for project in projects:
#         project.percent = project.percentage_collected()
#     return render(request, "social/soci_index.html", {
#         "projects": projects,
#         "publications": publications,
#     })


# # ---------------------------------------------------------
# # 3. Historique des dons de l'utilisateur connecté
# #    (supporte anciens dons "email-only" + nouveaux "user")
# # ---------------------------------------------------------
# @login_required
# def donation_history_view(request):
#     donations = (
#         Donation.objects.filter(
#             models.Q(user=request.user) |
#             models.Q(user__isnull=True, email=request.user.email)
#         )
#         .select_related("project", "user")
#         .order_by("-created_at")
#     )
#     return render(request, "social/donation_history.html", {"donations": donations})


# # ---------------------------------------------------------
# # 4. Formulaire de don — Étape 1
# # ---------------------------------------------------------
# def donation_view(request, child_id=None, mother_id=None, target_type=None, target_id=None):
#     target_obj = None

#     # Résolution cible
#     if child_id:
#         target_obj = get_object_or_404(Child, id=child_id)
#         target_type, target_id = "child", child_id
#     elif mother_id:
#         target_obj = get_object_or_404(Mother, id=mother_id)
#         target_type, target_id = "mother", mother_id
#     elif target_type and target_id:
#         target_obj = DonationTargetService.resolve_instance(target_type, target_id)

#     if request.method == "POST":
#         form = DonationForm(request.POST)
#         if form.is_valid():
#             data = form.cleaned_data

#             # cible choisie via form
#             if data.get("child"):
#                 target_type, target_id = "child", data["child"].id
#             elif data.get("mother"):
#                 target_type, target_id = "mother", data["mother"].id

#             # connecté => on force email / nom depuis user (fiable)
#             if request.user.is_authenticated:
#                 donor_email = request.user.email
#                 donor_name = request.user.get_full_name().strip() or data.get("donor_name")
#             else:
#                 donor_email = data.get("email")
#                 donor_name = data.get("donor_name")

#             request.session["donation_data"] = {
#                 "amount": str(data.get("amount")),
#                 "donor_name": donor_name or "",
#                 "email": donor_email or "",
#                 "message": data.get("message") or "",
#                 "project": data.get("project").id if data.get("project") else None,
#                 "monthly": bool(data.get("monthly")),
#                 "payment_method": data.get("payment_method") if "payment_method" in data else "",
#                 "target_type": target_type,
#                 "target_id": target_id,
#             }
#             return redirect("social:donation_payment_choice")
#     else:
#         # initial si connecté
#         initial = {}
#         if request.user.is_authenticated:
#             initial["email"] = request.user.email
#             full_name = request.user.get_full_name().strip()
#             if full_name:
#                 initial["donor_name"] = full_name

#         form = DonationForm(initial=initial)

#         if target_obj:
#             if isinstance(target_obj, Child):
#                 form.fields["child"].initial = target_obj.id
#             elif isinstance(target_obj, Mother):
#                 form.fields["mother"].initial = target_obj.id

#     return render(request, "social/donation_form.html", {
#         "form": form,
#         "target": getattr(target_obj, "name", None),
#         "target_type": target_type,
#         "target_id": target_id,
#     })


# # ---------------------------------------------------------
# # 5. Choix du mode de paiement — Étape 2
# # ---------------------------------------------------------
# def donation_payment_choice_view(request):
#     donation_data = request.session.get("donation_data")
#     if not donation_data:
#         messages.error(request, _("Données manquantes. Veuillez recommencer."))
#         return redirect("social:donation")

#     if request.method == "POST":
#         payment_method = request.POST.get("payment_method")
#         if not payment_method:
#             messages.error(request, _("Veuillez choisir un mode de paiement."))
#             return redirect("social:donation_payment_choice")

#         donation = Donation.objects.create(
#             amount=Decimal(str(donation_data.get("amount"))),
#             donor_name=donation_data.get("donor_name") or "",
#             email=donation_data.get("email") or "",
#             message=donation_data.get("message") or "",
#             monthly=bool(donation_data.get("monthly", False)),
#             payment_method=payment_method,
#             target_type=donation_data.get("target_type"),
#             target_id=donation_data.get("target_id"),
#             project_id=donation_data.get("project"),
#             # ✅ connecté => on lie au compte
#             user=request.user if request.user.is_authenticated else None,
#             status="pending",
#         )

#         DonationTargetService.assign_gfk(donation)
#         request.session["donation_id"] = donation.id

#         gateway_map = {
#             "stripe": "social:stripe_checkout",
#             "paypal": "social:paypal_checkout",
#             "orange_money": "social:orange_money_checkout",
#             "wave": "social:wave_checkout",
#             "visa": "social:visa_checkout",
#         }

#         if payment_method not in gateway_map:
#             messages.error(request, _("Méthode de paiement inconnue."))
#             return redirect("social:donation_payment_choice")

#         return redirect(gateway_map[payment_method], donation_id=donation.id)

#     return render(request, "social/donation_payment_choice.html", {"donation": donation_data})


# # ---------------------------------------------------------
# # 6. Succès du paiement (page de retour)
# #   ✅ autorise accès owner: user OU email
# # ---------------------------------------------------------
# @login_required
# def donation_success_view(request):
#     donation_id = request.session.get("donation_id")
#     if not donation_id:
#         return redirect("social:donation")

#     donation = get_object_or_404(Donation, id=donation_id)

#     if not _is_owner(request, donation):
#         raise Http404(_("Don introuvable"))

#     # en prod: status doit venir du webhook
#     # ici: on ne force pas paid si ce n'est pas confirmé
#     if donation.status != "paid":
#         messages.warning(request, _("Paiement en cours de confirmation."))

#     if donation.status == "paid" and not donation.pdf_receipt:
#         generate_receipt_pdf(donation)
#         send_receipt_by_email(donation)

#     return render(request, "social/donation_success.html", {"donation": donation})


# # ---------------------------------------------------------
# # 7. Génération du reçu PDF
# # ---------------------------------------------------------
# def generate_receipt_uid(donation):
#     raw = f"{donation.id}-{donation.created_at.timestamp()}"
#     return hashlib.sha1(raw.encode()).hexdigest()[:12]


# def generate_receipt_pdf(donation):
#     context = {
#         "donation": donation,
#         "receipt_uid": generate_receipt_uid(donation),
#         "logo_path": static_file_uri("images/logo.png"),
#         "signature_path": static_file_uri("images/signature.png"),
#         "stamp_path": static_file_uri("images/stamp.png"),
#         # si tu génères un QR code fichier, passe son file:// ici
#         "qr_code_path": "",  # ex: f"file://{absolute_qr_path}"
#     }

#     html = render_to_string("social/receipt_template.html", context)

#     buffer = BytesIO()
#     pisa.CreatePDF(html, dest=buffer)

#     filename = f"recu_{slugify(donation.donor_name or 'don')}_{donation.created_at.date()}_{donation.id}.pdf"
#     donation.pdf_receipt.save(filename, ContentFile(buffer.getvalue()))
#     donation.save(update_fields=["pdf_receipt"])



# # ---------------------------------------------------------
# # 8. Envoi du reçu par email
# # ---------------------------------------------------------
# def send_receipt_by_email(donation):
#     html = render_to_string("social/receipt_email.html", {"donation": donation})
#     buffer = BytesIO()
#     pisa.CreatePDF(
#         render_to_string("social/receipt_template.html", {"donation": donation}),
#         dest=buffer
#     )

#     email = EmailMessage(
#         subject=_("Reçu de votre don"),
#         body=html,
#         to=[donation.email] if donation.email else ([donation.user.email] if donation.user else []),
#     )

#     email.content_subtype = "html"
#     email.attach(f"recu_{donation.id}.pdf", buffer.getvalue(), "application/pdf")
#     if email.to:
#         email.send(fail_silently=True)


# # ---------------------------------------------------------
# # 9. Téléchargement du reçu PDF (sécurisé)
# # ---------------------------------------------------------
# @login_required
# def download_receipt_view(request, donation_id):
#     donation = get_object_or_404(Donation, id=donation_id)

#     if not _is_owner(request, donation):
#         raise Http404(_("Reçu introuvable"))

#     if not donation.pdf_receipt:
#         raise Http404(_("Aucun reçu disponible"))

#     return FileResponse(
#         donation.pdf_receipt.open("rb"),
#         content_type="application/pdf"
#     )


# # ---------------------------------------------------------
# # 10. Annulation du don
# # ---------------------------------------------------------
# @login_required
# def donation_cancel_view(request):
#     return render(request, "social/donation_cancel.html")

# # ---------------------------------------------------------
# # 🔒 Helper d'autorisation
# # ---------------------------------------------------------
# def _is_owner(request, donation: Donation) -> bool:
#     if donation.user_id:
#         return donation.user_id == request.user.id
#     return bool(donation.email) and donation.email == request.user.email


# def static_file_uri(static_path: str) -> str:
#     """
#     Convertit un chemin static en URI file:// utilisable par xhtml2pdf.
#     Ex: "images/logo.png" -> "file:///.../static/images/logo.png"
#     """
#     abs_path = finders.find(static_path)
#     if not abs_path:
#         return ""
#     return f"file://{abs_path}"








# # social/views/donations.py
# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages
# from django.template.loader import render_to_string
# from django.http import FileResponse
# from django.utils.translation import gettext_lazy as _
# from django.utils.text import slugify
# from django.core.files.base import ContentFile
# from django.core.mail import EmailMessage
# from io import BytesIO
# from xhtml2pdf import pisa
# from decimal import Decimal
# import hashlib
# import time

# from social.forms import DonationForm
# from social.models import Donation, Project, Publication
# from social.services.donation_target_service import DonationTargetService
# from about.models.child import Child
# from about.models.mother import Mother

# # ---------------------------------------------------------
# # 1. Liste publique des 100 derniers dons
# # ---------------------------------------------------------
# def public_donations_view(request):
#     donations = Donation.objects.filter(status="paid").order_by("-created_at")[:100]
#     return render(request, "social/public_donations.html", {"donations": donations})


# # ---------------------------------------------------------
# # 2. Accueil Social
# # ---------------------------------------------------------
# def soci_index_view(request):
#     projects = Project.objects.filter(is_active=True)
#     publications = Publication.objects.filter(is_public=True)
#     for project in projects:
#         project.percent = project.percentage_collected()
#     return render(request, "social/soci_index.html", {
#         "projects": projects,
#         "publications": publications,
#     })


# # ---------------------------------------------------------
# # 3. Historique des dons de l'utilisateur connecté
# # ---------------------------------------------------------
# @login_required
# def donation_history_view(request):
#     donations = Donation.objects.filter(email=request.user.email).order_by("-created_at")
#     return render(request, "social/donation_history.html", {"donations": donations})


# # ---------------------------------------------------------
# # 4. Formulaire de don — Étape 1
# # ---------------------------------------------------------
# def donation_view(request, child_id=None, mother_id=None, target_type=None, target_id=None):
#     target_obj = None

#     # 🔹 Résolution de la cible
#     if child_id:
#         target_obj = get_object_or_404(Child, id=child_id)
#         target_type, target_id = "child", child_id
#     elif mother_id:
#         target_obj = get_object_or_404(Mother, id=mother_id)
#         target_type, target_id = "mother", mother_id
#     elif target_type and target_id:
#         target_obj = DonationTargetService.resolve_instance(target_type, target_id)

#     if request.method == "POST":
#         form = DonationForm(request.POST)
#         if form.is_valid():
#             data = form.cleaned_data

#             # 🔹 Détection de la cible choisie
#             if data.get("child"):
#                 target_type, target_id = "child", data.get("child").id
#             elif data.get("mother"):
#                 target_type, target_id = "mother", data.get("mother").id

#             # 🔹 Stockage minimal en session
#             request.session["donation_data"] = {
#                 "amount": float(data.get("amount")),
#                 "donor_name": data.get("donor_name"),
#                 "email": data.get("email"),
#                 "message": data.get("message"),
#                 "project": data.get("project").id if data.get("project") else None,
#                 "monthly": bool(data.get("monthly")),
#                 "target_type": target_type,
#                 "target_id": target_id,
#             }
#             return redirect("social:donation_payment_choice")
#     else:
#         form = DonationForm()
#         if target_obj:
#             if isinstance(target_obj, Child):
#                 form.fields["child"].initial = target_obj.id
#             elif isinstance(target_obj, Mother):
#                 form.fields["mother"].initial = target_obj.id

#     return render(request, "social/donation_form.html", {
#         "form": form,
#         "target": getattr(target_obj, "name", None),
#         "target_type": target_type,
#         "target_id": target_id,
#     })


# # ---------------------------------------------------------
# # 5. Choix du mode de paiement — Étape 2
# # ---------------------------------------------------------
# def donation_payment_choice_view(request):
#     donation_data = request.session.get("donation_data")
#     if not donation_data:
#         messages.error(request, _("Données manquantes. Veuillez recommencer."))
#         return redirect("social:donation")

#     if request.method == "POST":
#         payment_method = request.POST.get("payment_method")
#         if not payment_method:
#             messages.error(request, _("Veuillez choisir un mode de paiement."))
#             return redirect("social:donation_payment_choice")

#         # 🔹 Création du don avant redirection vers la passerelle
#         donation = Donation.objects.create(
#             amount=Decimal(str(donation_data.get("amount"))),
#             donor_name=donation_data.get("donor_name"),
#             email=donation_data.get("email"),
#             message=donation_data.get("message"),
#             monthly=donation_data.get("monthly", False),
#             payment_method=payment_method,
#             target_type=donation_data.get("target_type"),
#             target_id=donation_data.get("target_id"),
#             project_id=donation_data.get("project"),
#         )

#         # 🔹 Associer la cible via GenericForeignKey
#         DonationTargetService.assign_gfk(donation)

#         # 🔹 Stockage de l'id du don en session
#         request.session["donation_id"] = donation.id

#         # 🔹 Redirection vers la passerelle correspondante
#         gateway_map = {
#             "stripe": "social:stripe_checkout",
#             "paypal": "social:paypal_checkout",
#             "orange_money": "social:orange_money_checkout",
#             "wave": "social:wave_checkout",
#             "visa": "social:visa_checkout",
#         }

#         if payment_method not in gateway_map:
#             messages.error(request, _("Méthode de paiement inconnue."))
#             return redirect("social:donation_payment_choice")

#         return redirect(gateway_map[payment_method], donation_id=donation.id)

#     return render(request, "social/donation_payment_choice.html", {"donation": donation_data})


# # ---------------------------------------------------------
# # 6. Succès du paiement
# # ---------------------------------------------------------
# @login_required
# def donation_success_view(request):
#     donation_id = request.session.get("donation_id")
#     if not donation_id:
#         return redirect("social:donation")

#     donation = get_object_or_404(Donation, id=donation_id, email=request.user.email)

#     # 🔹 Génération du reçu PDF si nécessaire
#     if not donation.pdf_receipt:
#         generate_receipt_pdf(donation)
#         send_receipt_by_email(donation)

#     return render(request, "social/donation_success.html", {"donation": donation})


# # ---------------------------------------------------------
# # 7. Génération du reçu PDF
# # ---------------------------------------------------------
# def generate_receipt_pdf(donation):
#     html = render_to_string("social/receipt_template.html", {"donation": donation})
#     buffer = BytesIO()
#     pisa.CreatePDF(html, dest=buffer)
#     filename = f"recu_{slugify(donation.donor_name or 'don')}_{donation.created_at.date()}.pdf"
#     donation.pdf_receipt.save(filename, ContentFile(buffer.getvalue()))
#     donation.save()

# def generate_receipt_uid(donation):
#     raw = f"{donation.id}-{donation.created_at.timestamp()}"
#     return hashlib.sha1(raw.encode()).hexdigest()[:12]

# # ---------------------------------------------------------
# # 8. Envoi du reçu par email
# # ---------------------------------------------------------
# def send_receipt_by_email(donation):
#     html = render_to_string("social/receipt_template.html", {"donation": donation})
#     buffer = BytesIO()
#     pisa.CreatePDF(html, dest=buffer)

#     email = EmailMessage(
#         _("Reçu de votre don"),
#         _("Merci pour votre générosité. Votre reçu est en pièce jointe."),
#         to=[donation.email],
#     )
#     email.attach(f"recu_{donation.id}.pdf", buffer.getvalue(), "application/pdf")
#     email.send()


# # ---------------------------------------------------------
# # 9. Téléchargement du reçu PDF
# # ---------------------------------------------------------
# @login_required
# def download_receipt_view(request, donation_id):
#     donation = get_object_or_404(Donation, id=donation_id, email=request.user.email)
#     return FileResponse(donation.pdf_receipt.open(), content_type="application/pdf")


# # ---------------------------------------------------------
# # 10. Annulation du don
# # ---------------------------------------------------------
# @login_required
# def donation_cancel_view(request):
#     return render(request, "social/donation_cancel.html")
