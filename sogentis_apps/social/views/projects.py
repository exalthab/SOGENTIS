# social/views/projects.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from social.models import Project
from social.forms.project_forms import ProjectForm

def projects_list_view(request):
    """
    Affiche la liste des projets actifs
    """
    projects = Project.objects.filter(is_active=True).order_by("-created_at")
    return render(request, "social/projects_list.html", {"projects": projects})

@login_required
def create_project_view(request):
    """
    Créer un nouveau projet
    """
    if request.method == "POST":
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, _("Projet créé avec succès."))
            return redirect("social:projects_list")
    else:
        form = ProjectForm()
    return render(request, "social/create_project.html", {"form": form})

@login_required
def update_project_view(request, pk):
    """
    Modifier un projet existant
    """
    project = get_object_or_404(Project, pk=pk)
    form = ProjectForm(request.POST or None, request.FILES or None, instance=project)
    if form.is_valid():
        form.save()
        messages.success(request, _("Projet mis à jour."))
        return redirect("social:projects_list")
    return render(request, "social/update_project.html", {"form": form, "project": project})

@login_required
def delete_project_view(request, pk):
    """
    Supprimer un projet
    """
    project = get_object_or_404(Project, pk=pk)
    if request.method == "POST":
        project.delete()
        messages.success(request, _("Projet supprimé."))
        return redirect("social:projects_list")
    return render(request, "social/delete_project.html", {"project": project})

def project_detail_view(request, pk):
    """
    Afficher les détails d’un projet
    """
    project = get_object_or_404(Project, pk=pk, is_active=True)
    return render(request, "social/project_detail.html", {"project": project})
