# ✅ dashboard/views/profile.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from dashboard.forms.profile_form import ProfileUpdateForm
from django.utils.translation import gettext_lazy as _

@login_required
def dashboard_profile_view(request):
    profile = getattr(request.user, "userprofile", None)
    if not profile:
        messages.error(request, _("Aucun profil associé à ce compte."))
        return redirect("dashboard:index")  # Ou une vue d’accueil

    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, _("Profil mis à jour avec succès."))
            return redirect("dashboard:profile")
        else:
            messages.error(request, _("Veuillez corriger les erreurs du formulaire."))
    else:
        form = ProfileUpdateForm(instance=profile)

    context = {"form": form}
    return render(request, "dashboard/profile_edit.html", context)



# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render

# @login_required
# def dashboard_profile_view(request):
#     return render(request, "dashboard/profile.html")




