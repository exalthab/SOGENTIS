# economic/prestations/views/projects.py
from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _

from ..models import ProjectBid, ProjectCall
from ..models.projects import ProjectStatus


def projects_list_view(request: HttpRequest) -> HttpResponse:
    qs = ProjectCall.objects.filter(status=ProjectStatus.PUBLISHED, is_public=True).order_by("-created_at", "-id")
    return render(request, "economic/prestations/projects/projects_list.html", {"projects": qs})


def project_detail_view(request: HttpRequest, slug: str) -> HttpResponse:
    project = get_object_or_404(ProjectCall.objects.filter(is_public=True), slug=slug)
    return render(request, "economic/prestations/projects/project_detail.html", {"project": project})


@login_required
def project_create_view(request: HttpRequest) -> HttpResponse:
    """
    Minimal (si tu veux un flux plus complet, on branchera un ModelForm).
    """
    if request.method == "POST":
        title = (request.POST.get("title") or "").strip()
        desc = (request.POST.get("description") or "").strip()
        if len(title) < 5 or len(desc) < 40:
            messages.error(request, _("Titre ou description insuffisants."))
            return redirect("economic:prestations:projects_create")

        obj = ProjectCall.objects.create(
            created_by=request.user,
            title=title,
            slug=title.lower().replace(" ", "-")[:220],
            description=desc,
            status=ProjectStatus.PUBLISHED,
            is_public=True,
        )
        messages.success(request, _("Projet publié."))
        return redirect("economic:prestations:projects_detail", slug=obj.slug)

    return render(request, "economic/prestations/projects/project_create.html")


@login_required
def project_bid_view(request: HttpRequest, slug: str) -> HttpResponse:
    project = get_object_or_404(ProjectCall.objects.filter(status=ProjectStatus.PUBLISHED, is_public=True), slug=slug)

    if request.method == "POST":
        msg = (request.POST.get("message") or "").strip()
        if len(msg) < 40:
            messages.error(request, _("Message trop court."))
            return redirect("economic:prestations:projects_detail", slug=project.slug)

        ProjectBid.objects.create(project=project, bidder=request.user, message=msg)
        messages.success(request, _("Votre proposition a été envoyée."))
        return redirect("economic:prestations:projects_detail", slug=project.slug)

    return redirect("economic:prestations:projects_detail", slug=project.slug)
