# dashboard/views/b2b/users.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from dashboard.permissions import is_b2b_manager

from economic.b2b.models import CompanyUser
from dashboard.forms.b2b.company_user_form import CompanyUserForm


@login_required
def b2b_users(request):
    users = CompanyUser.objects.filter(company=request.user.company_user.company)
    return render(request, "dashboard/b2b/users.html", {"users": users})

@login_required
def b2b_users_list_view(request):
    if not is_b2b_manager(request.user):
        return render(request, "dashboard/errors/not_authorized.html", status=403)

    company = request.user.company_user.company
    users = CompanyUser.objects.filter(company=company)

    return render(request, "dashboard/b2b/users_list.html", {
        "company": company,
        "users": users,
    })


@login_required
def b2b_user_create_view(request):
    if not is_b2b_manager(request.user):
        return render(request, "dashboard/errors/not_authorized.html", status=403)

    company = request.user.company_user.company
    form = CompanyUserForm(request.POST or None)

    if form.is_valid():
        company_user = form.save(commit=False)
        company_user.company = company
        company_user.save()
        return redirect("dashboard:b2b:users")

    return render(request, "dashboard/b2b/user_form.html", {
        "form": form,
        "title": "Ajouter un utilisateur",
    })


@login_required
def b2b_user_update_view(request, pk):
    if not is_b2b_manager(request.user):
        return render(request, "dashboard/errors/not_authorized.html", status=403)

    company = request.user.company_user.company
    company_user = get_object_or_404(
        CompanyUser,
        pk=pk,
        company=company,
    )

    form = CompanyUserForm(request.POST or None, instance=company_user)

    if form.is_valid():
        form.save()
        return redirect("dashboard:b2b:users")

    return render(request, "dashboard/b2b/user_form.html", {
        "form": form,
        "title": "Modifier l’utilisateur",
    })
