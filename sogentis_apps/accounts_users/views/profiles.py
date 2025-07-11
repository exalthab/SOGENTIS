# accounts_users/views/profiles.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from accounts_users.forms.profile_forms import UserProfileForm


@login_required
def edit_profile_view(request):
    profile = request.user.userprofile

    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, _("Profil mis à jour avec succès."))
            return redirect("dashboard:profile")
        else:
            messages.error(request, _("Veuillez corriger les erreurs."))
    else:
        form = UserProfileForm(instance=profile)

    return render(request, "accounts_users/registration/profile_edit.html", {"form": form})





## accounts_users/views/profiles.py
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib import messages
# from django.utils.translation import gettext_lazy as _

# from accounts_users.forms.profile_forms import UserProfileForm
# from accounts_users.models.users_profile import UserProfile


# @login_required
# def edit_profile_view(request):
#     profile = get_object_or_404(UserProfile, user=request.user)

#     if request.method == 'POST':
#         form = UserProfileForm(request.POST, request.FILES, instance=profile)
#         if form.is_valid():
#             form.save()
#             messages.success(request, _("Profil mis à jour avec succès."))
#             return redirect('dashboard:profile')
#         else:
#             messages.error(request, _("Merci de corriger les erreurs ci-dessous."))
#     else:
#         form = UserProfileForm(instance=profile)

#     return render(request, 'accounts_users/registration/profile_edit.html', {'form': form})





# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render, redirect
# from accounts_users.forms.profile_forms import UserProfileForm

# @login_required
# def edit_profile_view(request):
#     profile = request.user.userprofile
#     if request.method == 'POST':
#         form = UserProfileForm(request.POST, request.FILES, instance=profile)
#         if form.is_valid():
#             form.save()
#             return redirect('dashboard:profile')
#     else:
#         form = UserProfileForm(instance=profile)
#     return render(request, 'accounts_users/registration/profile_edit.html', {'form': form})
