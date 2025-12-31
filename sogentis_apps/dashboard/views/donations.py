# dashboard/views/donations.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum
from django.db.models.functions import ExtractMonth
from social.models import Donation


@login_required
def dashboard_donations_view(request):
    user = request.user

    # =============================
    # 1. FILTRES
    # =============================
    status = request.GET.get("status", "")
    donation_type = request.GET.get("type", "")

    donations_qs = Donation.objects.filter(user=user).order_by("-created_at")

    if status:
        donations_qs = donations_qs.filter(status=status)

    if donation_type:
        donations_qs = donations_qs.filter(donation_type=donation_type)

    # Totaux AVANT pagination
    donations_count = donations_qs.count()
    receipts_count = donations_qs.filter(pdf_receipt__isnull=False).count()  # <-- corrigé ici
    total_amount = donations_qs.aggregate(total=Sum("amount"))["total"] or 0

    # =============================
    # 2. PAGINATION
    # =============================
    paginator = Paginator(donations_qs, 10)
    page_number = request.GET.get("page")
    donations_page = paginator.get_page(page_number)

    # =============================
    # 3. GRAPHIQUE : mensualisation propre
    # =============================
    monthly = (
        donations_qs.annotate(month=ExtractMonth("created_at"))
        .values("month")
        .annotate(total=Sum("amount"))
        .order_by("month")
    )

    chart_labels = []
    chart_amounts = []

    for m in monthly:
        month_num = m.get("month")
        amount = m.get("total") or 0

        if month_num:
            chart_labels.append(_("Mois ") + str(month_num))
            chart_amounts.append(amount)

    # =============================
    # 4. CONTEXTE
    # =============================
    context = {
        "donations": donations_page,
        "total_donations": total_amount,
        "donations_count": donations_count,
        "receipts_count": receipts_count,
        "filter_status": status,
        "filter_type": donation_type,
        "chart_labels": chart_labels,
        "chart_amounts": chart_amounts,
    }

    return render(request, "dashboard/donations.html", context)



# # dashboard/views/donations.py
# from django.shortcuts import render
# from django.contrib.auth.decorators import login_required

# @login_required
# def donations_view(request):

#     donations = [
#         {"donor": "John", "amount": 15000, "date": "2025-02-10"},
#         {"donor": "Fatou", "amount": 20000, "date": "2025-02-11"},
#     ]

#     return render(request, "dashboard/donations.html", {"donations": donations})
