# economic/prestations/views/entitlements.py
from __future__ import annotations

from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from ..models import PrestationEntitlement


@staff_member_required
def entitlements_admin_list_view(request: HttpRequest) -> HttpResponse:
    """
    Optionnel: mini vue back-office (si tu veux en plus de l'admin Django).
    """
    qs = (
        PrestationEntitlement.objects.select_related("user", "prestation_plan", "package_offer", "prestation", "package")
        .order_by("-created_at", "-id")
    )
    return render(request, "economic/prestations/dashboard/entitlements_list.html", {"entitlements": qs})
