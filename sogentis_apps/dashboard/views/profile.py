# dashboard/views/profile.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from dashboard.forms.profile_form import ProfileUpdateForm


@login_required
def dashboard_profile_view(request):
    """Page d'affichage du profil (économique)."""
    profile = getattr(request.user, "economic_profile", None)

    if not profile:
        messages.error(request, _("Aucun profil associé à ce compte."))
        return redirect("dashboard:router")  # ✅ existe

    return render(request, "dashboard/profile/profile.html", {"profile": profile})


@login_required
def dashboard_profile_edit_view(request):
    """Page d'édition du profil (économique)."""
    profile = getattr(request.user, "economic_profile", None)

    if not profile:
        messages.error(request, _("Aucun profil associé à ce compte."))
        return redirect("dashboard:router")  # ✅ existe

    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, _("Profil mis à jour avec succès."))
            return redirect("dashboard:profile")  # ✅ route profile
        messages.error(request, _("Veuillez corriger les erreurs du formulaire."))
    else:
        form = ProfileUpdateForm(instance=profile)

    return render(
        request,
        "dashboard/profile/profile_edit.html",
        {"form": form, "profile": profile},
    )






# # ✅ dashboard/views/profile.py
# from django.shortcuts import render, redirect
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages
# from dashboard.forms.profile_form import ProfileUpdateForm
# from django.utils.translation import gettext_lazy as _


# @login_required
# def dashboard_profile_view(request):
#     """ Page d'affichage du profil """
#     profile = getattr(request.user, "userprofile", None)

#     if not profile:
#         messages.error(request, _("Aucun profil associé à ce compte."))
#         return redirect("dashboard:index")

#     context = {"profile": profile}
#     return render(request, "dashboard/profile/profile.html", context)


# @login_required
# def dashboard_profile_edit_view(request):
#     """ Page d'édition du profil """
#     profile = getattr(request.user, "userprofile", None)

#     if not profile:
#         messages.error(request, _("Aucun profil associé à ce compte."))
#         return redirect("dashboard:index")

#     if request.method == "POST":
#         form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
#         if form.is_valid():
#             form.save()
#             messages.success(request, _("Profil mis à jour avec succès."))
#             return redirect("dashboard:profile")
#         else:
#             messages.error(request, _("Veuillez corriger les erreurs du formulaire."))
#     else:
#         form = ProfileUpdateForm(instance=profile)

#     return render(request, "dashboard/profile/profile_edit.html", {"form": form, "profile": profile})






# # ✅ dashboard/views/profile.py
# from django.shortcuts import render, redirect
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages
# from dashboard.forms.profile_form import ProfileUpdateForm
# from django.utils.translation import gettext_lazy as _

# @login_required
# def dashboard_profile_view(request):
#     profile = getattr(request.user, "userprofile", None)
#     if not profile:
#         messages.error(request, _("Aucun profil associé à ce compte."))
#         return redirect("dashboard:index")  # Ou une vue d’accueil

#     if request.method == "POST":
#         form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
#         if form.is_valid():
#             form.save()
#             messages.success(request, _("Profil mis à jour avec succès."))
#             return redirect("dashboard:profile")
#         else:
#             messages.error(request, _("Veuillez corriger les erreurs du formulaire."))
#     else:
#         form = ProfileUpdateForm(instance=profile)

#     context = {"form": form}
#     return render(request, "dashboard/profile/profile.html", context)



# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render

# @login_required
# def dashboard_profile_view(request):
#     return render(request, "dashboard/profile.html")




