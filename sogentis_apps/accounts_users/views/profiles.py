# # accounts_users/views/profiles.py
# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render, redirect
# from django.utils.translation import gettext_lazy as _

# from accounts_users.forms.social.social_signup_forms import UserSignupForm
# from accounts_users.forms.user_forms import UserEmailUpdateForm


# @login_required
# def update_profile_logic(request):
#     """
#     Logique pure de mise à jour du profil utilisateur.
#     - Ne retourne PAS de HttpResponse
#     - Ne fait PAS de render()

#     Retourne :
#         form  : UserProfileForm
#         state :
#             True  -> profil mis à jour
#             False -> POST invalide
#             None  -> GET initial
#     """
#     profile = request.user.userprofile

#     if request.method == "POST":
#         form = UserSignupForm(
#             request.POST,
#             request.FILES,
#             instance=profile,
#         )
#         if form.is_valid():
#             form.save()
#             return form, True
#         return form, False

#     # GET : pré-remplissage
#     form = UserSignupForm(instance=profile)
#     return form, None


# @login_required
# def profile_edit_view(request):
#     user = request.user
#     profile = user.userprofile

#     if request.method == "POST":
#         profile_form = UserSignupForm(
#             request.POST,
#             request.FILES,
#             instance=profile,
#         )
#         email_form = UserEmailUpdateForm(
#             request.POST,
#             instance=user,
#         )

#         if profile_form.is_valid() and email_form.is_valid():
#             profile_form.save()
#             email_form.save()
#             messages.success(
#                 request,
#                 _("Profil mis à jour avec succès.")
#             )
#             return redirect("accounts_users:profile")
#     else:
#         profile_form = UserSignupForm(instance=profile)
#         email_form = UserEmailUpdateForm(instance=user)

#     return render(
#         request,
#         "accounts_users/profile_edit.html",
#         {
#             "profile_form": profile_form,
#             "email_form": email_form,
#         },
#     )





# # accounts_users/views/profiles.py

# from django.contrib.auth.decorators import login_required
# from django.utils.translation import gettext_lazy as _
# from accounts_users.forms.profile_forms import UserProfileForm


# @login_required
# def update_profile_logic(request):
#     """
#     Logique pure de mise à jour du profil.
#     Ne retourne *pas* de réponse HTTP.
#     Ne fait *pas* de render().
    
#     Retourne :
#         - form : UserProfileForm
#         - state :
#             True  -> profil mis à jour
#             False -> POST invalide
#             None  -> GET initial
#     """
#     profile = request.user.userprofile

#     if request.method == "POST":
#         form = UserProfileForm(
#             request.POST,
#             request.FILES,
#             instance=profile
#         )
#         if form.is_valid():
#             form.save()
#             return form, True
#         else:
#             return form, False

#     # GET : pré-remplissage
#     form = UserProfileForm(instance=profile)
#     return form, None




# # accounts_users/views/profiles.py
# from django.contrib.auth.decorators import login_required
# from django.utils.translation import gettext_lazy as _
# from accounts_users.forms.profile_forms import UserProfileForm

# @login_required
# def update_profile_logic(request):
#     """
#     Pure logique métier : ne rend pas de template.
#     Retourne (form, success: bool)
#     """
#     profile = request.user.userprofile

#     if request.method == "POST":
#         form = UserProfileForm(request.POST, request.FILES, instance=profile)
#         if form.is_valid():
#             form.save()
#             return form, True
#         return form, False

#     # GET request
#     form = UserProfileForm(instance=profile)
#     return form, None






# # accounts_users/views/profiles.py
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render, redirect
# from django.contrib import messages
# from django.utils.translation import gettext_lazy as _
# from accounts_users.forms.profile_forms import UserProfileForm


# @login_required
# def edit_profile_view(request):
#     profile = request.user.userprofile

#     if request.method == "POST":
#         form = UserProfileForm(request.POST, request.FILES, instance=profile)
#         if form.is_valid():
#             form.save()
#             messages.success(request, _("Profil mis à jour avec succès."))
#             return redirect("dashboard:profile")
#         else:
#             messages.error(request, _("Veuillez corriger les erreurs."))
#     else:
#         form = UserProfileForm(instance=profile)

#     return render(request, "accounts_users/registration/profile_edit.html", {"form": form})





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
