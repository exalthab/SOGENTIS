from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum, Q
from django.core.files.base import ContentFile
from django.template.loader import render_to_string
from django.utils.text import slugify
from decimal import Decimal
from io import BytesIO
from xhtml2pdf import pisa
from django.http import FileResponse, Http404

from .forms import DonationForm, EngagementForm, ProjectForm
from .models import Project, Donation, Engagement, Publication

# 🏠 Page d'accueil sociale
def soci_index_view(request):
    total_raised = Donation.objects.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    goal = Project.objects.aggregate(goal=Sum('goal_amount'))['goal'] or Decimal('0.00')  # Correction ici
    progress_percentage = round((total_raised / goal) * 100, 2) if goal else 0
    publications = Publication.objects.filter(is_public=True)
    projects = Project.objects.filter(is_active=True).order_by("-created_at")[:6]
    context = {
        "total_raised": total_raised,
        "goal": goal,
        "progress_percentage": progress_percentage,
        "publications": publications,
        "projects": projects,
    }
    return render(request, "social/soci_index.html", context)

# 📥 Téléchargement sécurisé d'un document Publication
@login_required
def download_publication(request, pk):
    publication = get_object_or_404(Publication, pk=pk, is_public=True)
    if not publication.file:
        raise Http404(_("Fichier non trouvé"))
    # Tu peux ici logger le téléchargement si besoin
    filename = publication.file.name.split("/")[-1]
    return FileResponse(publication.file.open("rb"), as_attachment=True, filename=filename)

# 💕 Processus de don en 2 étapes
def donation_view(request):
    if request.method == 'POST':
        step = request.POST.get("step", "1")
        if step == "1":
            request.session['donation_data'] = {
                "amount": request.POST.get("amount"),
                "donor_name": request.POST.get("donor_name"),
                "email": request.POST.get("email"),
                "message": request.POST.get("message"),
                "project": request.POST.get("project"),
                "monthly": request.POST.get("monthly") == "on",
            }
            return render(request, "social/donation_payment_choice.html")
        elif step == "2":
            payment_method = request.POST.get("payment_method")
            data = request.session.get('donation_data')
            if not data:
                messages.error(request, _("Données manquantes, veuillez recommencer."))
                return redirect("social:donation")
            donation = Donation.objects.create(
                amount=data["amount"],
                donor_name=data["donor_name"],
                email=data["email"],
                message=data["message"],
                payment_method=payment_method,
                project_id=data.get("project") or None,
                monthly=data.get("monthly", False),
            )
            redirections = {
                "stripe": "social:stripe_checkout",
                "paypal": "social:paypal_checkout",
                "orange_money": "social:orange_money_checkout",
                "wave": "social:wave_checkout",
                "visa": "social:visa_checkout",
            }
            if payment_method in redirections:
                return redirect(redirections[payment_method], donation_id=donation.id)
            messages.error(request, _("Méthode de paiement non reconnue."))
            return redirect("social:donation")
    return render(request, "social/donation.html")

# 📜 Liste des dons publics
def public_donations_view(request):
    donations = Donation.objects.filter(status="paid").order_by("-created_at")[:100]
    return render(request, "social/public_donations.html", {"donations": donations})

# ✅ Paiement réussi
@login_required
def donation_success_view(request, donation_id=None):
    return render(request, "social/donation_success.html", {"donation_id": donation_id})

# ❌ Paiement annulé ou échoué
def donation_cancel_view(request):
    return render(request, "social/donation_cancel.html")

# 💪 Engagement bénévole
@login_required
def engagement_view(request):
    if request.method == 'POST':
        form = EngagementForm(request.POST)
        if form.is_valid():
            engagement = form.save(commit=False)
            engagement.user = request.user
            engagement.save()
            messages.success(request, _("Votre engagement a été enregistré. Merci !"))
            return redirect('dashboard:index')
    else:
        form = EngagementForm()
    return render(request, 'social/volunteers/become_volunteer.html', {'form': form})

# 📄 Génération de reçu PDF
def generate_receipt_pdf(donation):
    html = render_to_string("social/receipt_template.html", {"donation": donation})
    pdf_file = BytesIO()
    result = pisa.CreatePDF(html, dest=pdf_file)
    if not result.err:
        file_name = f"receipt_{slugify(donation.donor_name)}_{donation.created_at.date()}.pdf"
        donation.pdf_receipt.save(file_name, ContentFile(pdf_file.getvalue()))
        return True
    return False

# 💳 Simulations d'intégrations de paiement (remplace par intégration réelle si besoin)
@login_required
def stripe_checkout_view(request, donation_id):
    donation = get_object_or_404(Donation, id=donation_id)
    stripe_checkout_url = f"https://checkout.stripe.com/pay/mock_session?donation={donation.id}"
    return redirect(stripe_checkout_url)

@login_required
def paypal_checkout_view(request, donation_id):
    donation = get_object_or_404(Donation, id=donation_id)
    paypal_url = f"https://www.paypal.com/checkoutnow?amount={donation.amount}&donation_id={donation.id}"
    return redirect(paypal_url)

@login_required
def orange_money_checkout_view(request, donation_id):
    donation = get_object_or_404(Donation, id=donation_id)
    om_url = f"https://om.orange.sn/payment?amount={donation.amount}&ref={donation.id}"
    return redirect(om_url)

@login_required
def wave_checkout_view(request, donation_id):
    donation = get_object_or_404(Donation, id=donation_id)
    wave_url = f"https://pay.wave.com/sn/pay?amount={donation.amount}&reference={donation.id}"
    return redirect(wave_url)

@login_required
def visa_checkout_view(request, donation_id):
    donation = get_object_or_404(Donation, id=donation_id)
    visa_url = f"https://payment.visa.com/process?amount={donation.amount}&ref={donation.id}"
    return redirect(visa_url)

# 🔎 Moteur de recherche multi-modèles
def perform_search(query):
    projects = Project.objects.filter(Q(title__icontains=query) | Q(description__icontains=query))
    publications = Publication.objects.filter(Q(title__icontains=query) | Q(description__icontains=query))
    engagements = Engagement.objects.filter(Q(title__icontains=query) | Q(description__icontains=query))
    return {
        "projects": projects,
        "publications": publications,
        "engagements": engagements,
    }

def search_view(request):
    query = request.GET.get("q", "").strip()
    results = {"projects": [], "publications": [], "engagements": []}
    if query:
        results = perform_search(query)
    return render(request, "social/search_results.html", {
        "query": query,
        "project_results": results["projects"],
        "publication_results": results["publications"],
        "engagement_results": results["engagements"],
    })

# 🆕 Création d'un projet
@login_required
def create_projects_view(request):
    if request.method == "POST":
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, _("Projet créé avec succès."))
            return redirect("social:projects_list")
    else:
        form = ProjectForm()
    return render(request, "social/create_project.html", {"form": form})

# Liste des projets (publique ou dashboard selon les besoins)
def projects_list_view(request):
    projects = Project.objects.filter(is_active=True).order_by("-created_at")
    return render(request, "social/projects_list.html", {"projects": projects})

def project_detail_view(request, pk):
    project = get_object_or_404(Project, pk=pk, is_active=True)
    return render(request, "social/project_detail.html", {"project": project})



# # social/views.py

# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from django.utils.translation import gettext_lazy as _
# from django.db.models import Sum, Q
# from django.core.files.base import ContentFile
# from django.template.loader import render_to_string
# from django.utils.text import slugify
# from decimal import Decimal
# from io import BytesIO
# from xhtml2pdf import pisa
# from django.http import FileResponse, Http404

# from .forms import DonationForm, EngagementForm, ProjectForm
# from .models import Project, Donation, Engagement, Publication

# # 🏠 Page d'accueil sociale
# def soci_index_view(request):
#     total_raised = Donation.objects.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
#     goal = Project.objects.aggregate(goal=Sum('goal_amount'))['goal'] or Decimal('0.00')  # Correction ici
#     progress_percentage = round((total_raised / goal) * 100, 2) if goal else 0
#     publications = Publication.objects.filter(is_public=True)
#     projects = Project.objects.filter(is_active=True).order_by("-created_at")[:6]
#     context = {
#         "total_raised": total_raised,
#         "goal": goal,
#         "progress_percentage": progress_percentage,
#         "publications": publications,
#         "projects": projects,
#     }
#     return render(request, "social/soci_index.html", context)

# # 💕 Processus de don en 2 étapes
# def donation_view(request):
#     if request.method == 'POST':
#         step = request.POST.get("step", "1")
#         if step == "1":
#             request.session['donation_data'] = {
#                 "amount": request.POST.get("amount"),
#                 "donor_name": request.POST.get("donor_name"),
#                 "email": request.POST.get("email"),
#                 "message": request.POST.get("message"),
#                 "project": request.POST.get("project"),
#                 "monthly": request.POST.get("monthly") == "on",
#             }
#             return render(request, "social/donation_payment_choice.html")
#         elif step == "2":
#             payment_method = request.POST.get("payment_method")
#             data = request.session.get('donation_data')
#             if not data:
#                 messages.error(request, _("Données manquantes, veuillez recommencer."))
#                 return redirect("social:donation")
#             donation = Donation.objects.create(
#                 amount=data["amount"],
#                 donor_name=data["donor_name"],
#                 email=data["email"],
#                 message=data["message"],
#                 payment_method=payment_method,
#                 project_id=data.get("project") or None,
#                 monthly=data.get("monthly", False),
#             )
#             redirections = {
#                 "stripe": "social:stripe_checkout",
#                 "paypal": "social:paypal_checkout",
#                 "orange_money": "social:orange_money_checkout",
#                 "wave": "social:wave_checkout",
#                 "visa": "social:visa_checkout",
#             }
#             if payment_method in redirections:
#                 return redirect(redirections[payment_method], donation_id=donation.id)
#             messages.error(request, _("Méthode de paiement non reconnue."))
#             return redirect("social:donation")
#     return render(request, "social/donation.html")

# # 📜 Liste des dons publics
# def public_donations_view(request):
#     donations = Donation.objects.filter(status="paid").order_by("-created_at")[:100]
#     return render(request, "social/public_donations.html", {"donations": donations})

# # ✅ Paiement réussi
# @login_required
# def donation_success_view(request, donation_id=None):
#     return render(request, "social/donation_success.html", {"donation_id": donation_id})

# # ❌ Paiement annulé ou échoué
# def donation_cancel_view(request):
#     return render(request, "social/donation_cancel.html")

# # 💪 Engagement bénévole
# @login_required
# def engagement_view(request):
#     if request.method == 'POST':
#         form = EngagementForm(request.POST)
#         if form.is_valid():
#             engagement = form.save(commit=False)
#             engagement.user = request.user
#             engagement.save()
#             messages.success(request, _("Votre engagement a été enregistré. Merci !"))
#             return redirect('dashboard:index')
#     else:
#         form = EngagementForm()
#     return render(request, 'social/volunteers/become_volunteer.html', {'form': form})

# # 📄 Génération de reçu PDF
# def generate_receipt_pdf(donation):
#     html = render_to_string("social/receipt_template.html", {"donation": donation})
#     pdf_file = BytesIO()
#     result = pisa.CreatePDF(html, dest=pdf_file)
#     if not result.err:
#         file_name = f"receipt_{slugify(donation.donor_name)}_{donation.created_at.date()}.pdf"
#         donation.pdf_receipt.save(file_name, ContentFile(pdf_file.getvalue()))
#         return True
#     return False

# # 💳 Simulations d'intégrations de paiement (remplace par intégration réelle si besoin)
# @login_required
# def stripe_checkout_view(request, donation_id):
#     donation = get_object_or_404(Donation, id=donation_id)
#     stripe_checkout_url = f"https://checkout.stripe.com/pay/mock_session?donation={donation.id}"
#     return redirect(stripe_checkout_url)

# @login_required
# def paypal_checkout_view(request, donation_id):
#     donation = get_object_or_404(Donation, id=donation_id)
#     paypal_url = f"https://www.paypal.com/checkoutnow?amount={donation.amount}&donation_id={donation.id}"
#     return redirect(paypal_url)

# @login_required
# def orange_money_checkout_view(request, donation_id):
#     donation = get_object_or_404(Donation, id=donation_id)
#     om_url = f"https://om.orange.sn/payment?amount={donation.amount}&ref={donation.id}"
#     return redirect(om_url)

# @login_required
# def wave_checkout_view(request, donation_id):
#     donation = get_object_or_404(Donation, id=donation_id)
#     wave_url = f"https://pay.wave.com/sn/pay?amount={donation.amount}&reference={donation.id}"
#     return redirect(wave_url)

# @login_required
# def visa_checkout_view(request, donation_id):
#     donation = get_object_or_404(Donation, id=donation_id)
#     visa_url = f"https://payment.visa.com/process?amount={donation.amount}&ref={donation.id}"
#     return redirect(visa_url)

# # 🔎 Moteur de recherche multi-modèles
# def perform_search(query):
#     projects = Project.objects.filter(Q(title__icontains=query) | Q(description__icontains=query))
#     publications = Publication.objects.filter(Q(title__icontains=query) | Q(description__icontains=query))
#     engagements = Engagement.objects.filter(Q(title__icontains=query) | Q(description__icontains=query))
#     return {
#         "projects": projects,
#         "publications": publications,
#         "engagements": engagements,
#     }

# def search_view(request):
#     query = request.GET.get("q", "").strip()
#     results = {"projects": [], "publications": [], "engagements": []}
#     if query:
#         results = perform_search(query)
#     return render(request, "social/search_results.html", {
#         "query": query,
#         "project_results": results["projects"],
#         "publication_results": results["publications"],
#         "engagement_results": results["engagements"],
#     })

# # 🆕 Création d'un projet
# @login_required
# def create_projects_view(request):
#     if request.method == "POST":
#         form = ProjectForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             messages.success(request, _("Projet créé avec succès."))
#             return redirect("social:projects_list")
#     else:
#         form = ProjectForm()
#     return render(request, "social/create_project.html", {"form": form})

# # Liste des projets (publique ou dashboard selon les besoins)
# def projects_list_view(request):
#     projects = Project.objects.filter(is_active=True).order_by("-created_at")
#     return render(request, "social/projects_list.html", {"projects": projects})

# def project_detail_view(request, pk):
#     project = get_object_or_404(Project, pk=pk, is_active=True)
#     return render(request, "social/project_detail.html", {"project": project})


# @login_required
# def download_publication(request, pk):
#     pub = get_object_or_404(Publication, pk=pk)
#     if not pub.file:
#         raise Http404("Fichier non trouvé")
#     # Optionnel : logger le téléchargement, etc.
#     return FileResponse(pub.file.open(), as_attachment=True, filename=pub.file.name.split('/')[-1])