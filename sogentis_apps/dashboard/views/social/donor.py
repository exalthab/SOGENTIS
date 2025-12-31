# dashboard/views/social/donor.py
from django.db import models
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import FileResponse, Http404
from django.shortcuts import render

from donations.models import Donation
from dashboard.services.social_donor_impact_service import DonorImpactService


@login_required
def donor_home_view(request):
    return render(request, "dashboard/social/donor/home.html")


@login_required
def donor_donations_list_view(request):
    """
    Liste complète des dons du donateur connecté
    (par défaut : dons complétés)
    """
    qs = (
        Donation.objects.filter(
            user=request.user,
            status=Donation.STATUS_COMPLETED,  # ✅ correct
        )
        .select_related("project")
        .order_by("-created_at")
    )

    # Filtres
    project_id = request.GET.get("project")
    if project_id:
        qs = qs.filter(project_id=project_id)

    date_from = request.GET.get("date")
    if date_from:
        qs = qs.filter(created_at__date__gte=date_from)

    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    # Liste projets pour select (si ton template affiche un select)
    projects = (
        Donation.objects.filter(user=request.user, project__isnull=False)
        .select_related("project")
        .values_list("project_id", "project__title")
        .distinct()
    )

    return render(
        request,
        "dashboard/social/donor/donations_list.html",
        {
            "dons": page_obj,                 # ✅ si ton template attend "dons"
            "page_obj": page_obj,             # ✅ si ton template attend "page_obj"
            "projects": [{"id": pid, "title": title} for pid, title in projects],
            "project_filter": project_id or "",
            "date_filter": date_from or "",
        },
    )


@login_required
def donor_receipt_download_view(request, donation_id):
    """
    Téléchargement sécurisé du reçu PDF
    - seul le propriétaire du don peut y accéder
    """
    try:
        donation = Donation.objects.get(
            id=donation_id,
            user=request.user,
            status=Donation.STATUS_COMPLETED,  # ✅ correct
        )
    except Donation.DoesNotExist:
        raise Http404("Reçu introuvable")

    if not donation.receipt_pdf:
        raise Http404("Aucun reçu disponible")

    return FileResponse(
        donation.receipt_pdf.open("rb"),
        as_attachment=True,
        filename=f"recu-don-{donation.id}.pdf",
    )


@login_required
def donor_impact_view(request):
    impact = DonorImpactService.by_project(request.user)
    return render(request, "dashboard/social/donor/impact.html", {"impact": impact})

@login_required
def donation_history_view(request):
    # Compat : anciens dons par email + nouveaux dons liés au user
    donations = Donation.objects.filter(
        models.Q(user=request.user) | models.Q(user__isnull=True, email=request.user.email)
    ).order_by("-created_at")
    return render(request, "social/donation_history.html", {"donations": donations})







# # dashboard/views/social/donor.py
# from django.contrib.auth.decorators import login_required
# from django.core.paginator import Paginator
# from django.shortcuts import render
# from dashboard.services.social_donor_service import DonorDashboardService
# from django.http import FileResponse, Http404
# from dashboard.services.social_donor_impact_service import DonorImpactService

# from donations.models import Donation


# @login_required
# def donor_home_view(request):
#     return render(request, "dashboard/social/donor/home.html")

# @login_required
# def donor_donations_list_view(request):
#     """
#     Liste complète des dons du donateur connecté
#     """

#     qs = Donation.objects.filter(
#         user=request.user,
#         status="CONFIRMED"
#     ).select_related("project").order_by("-created_at")

#     # 🔍 Filtres simples
#     project = request.GET.get("project")
#     if project:
#         qs = qs.filter(project__name__icontains=project)

#     paginator = Paginator(qs, 10)
#     page_number = request.GET.get("page")
#     page_obj = paginator.get_page(page_number)

#     return render(
#         request,
#         "dashboard/social/donor/donations_list.html",
#         {
#             "page_obj": page_obj,
#         }
#     )
    
    
# @login_required
# def donor_receipt_download_view(request, donation_id):
#     """
#     Téléchargement sécurisé du reçu PDF
#     - seul le propriétaire du don peut y accéder
#     """

#     try:
#         donation = Donation.objects.get(
#             id=donation_id,
#             user=request.user,
#             status="CONFIRMED",
#         )
#     except Donation.DoesNotExist:
#         raise Http404("Reçu introuvable")

#     if not donation.receipt_pdf:
#         raise Http404("Aucun reçu disponible")

#     return FileResponse(
#         donation.receipt_pdf.open("rb"),
#         as_attachment=True,
#         filename=f"recu-don-{donation.id}.pdf",
#     )
    
# @login_required
# def donor_impact_view(request):
#         impact = DonorImpactService.by_project(request.user)

#         return render(
#             request,
#             "dashboard/social/donor/impact.html",
#             {"impact": impact},
#         )
        











# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render

# from dashboard.services.social_donor_service import DonorDashboardService

# @login_required
# def donor_home_view(request):
#     return render(request, "dashboard/social/donor/home.html")
