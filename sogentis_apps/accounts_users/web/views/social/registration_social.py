# from django.contrib import messages
# from django.shortcuts import render, redirect
# from django.utils.translation import gettext_lazy as _
# from django.views.decorators.http import require_http_methods
# from django.db import transaction

# from accounts_users.forms.social.signup_social_forms import (
#     UserSignupForm,
#     UserProfileForm,
# )


# @require_http_methods(["GET", "POST"])
# def register_social_view(request):
#     """
#     Inscription pôle SOCIAL
#     - Donateur
#     - Membre
#     - Volontaire
#     - Institution
#     """

#     # ======================================================
#     # INITIALISATION FORMULAIRES
#     # ======================================================
#     user_form = UserSignupForm(request.POST or None)
#     profile_form = UserProfileForm(
#         request.POST or None,
#         request.FILES or None,
#     )

#     # ======================================================
#     # TRAITEMENT POST
#     # ======================================================
#     if request.method == "POST":

#         if user_form.is_valid() and profile_form.is_valid():

#             try:
#                 with transaction.atomic():

#                     # -------------------------------
#                     # UTILISATEUR
#                     # -------------------------------
#                     user = user_form.save(commit=False)
#                     user.is_active = False  # activation après validation / email
#                     user.save()

#                     # -------------------------------
#                     # PROFIL SOCIAL
#                     # -------------------------------
#                     profile = profile_form.save(commit=False)
#                     profile.user = user
#                     profile.save()

#             except Exception:
#                 messages.error(
#                     request,
#                     _("Une erreur est survenue lors de la création du compte.")
#                 )
#                 return redirect("accounts_users_web:register_social")

#             messages.success(
#                 request,
#                 _(
#                     "Votre compte a été créé avec succès. "
#                     "Veuillez vérifier votre e-mail ou attendre la validation."
#                 ),
#             )
#             return redirect("accounts_users_web:login")

#         # --------------------------------------------------
#         # FORMULAIRES INVALIDES
#         # --------------------------------------------------
#         messages.error(request, _("Veuillez corriger les erreurs du formulaire."))

#     # ======================================================
#     # RENDU TEMPLATE
#     # ======================================================
#     return render(
#         request,
#         "accounts_users/registration/register_social_form.html",
#         {
#             "form": user_form,
#             "profile_form": profile_form,
#             "auth_pole": "social",
#         },
#     )





# from django.contrib import messages
# from django.shortcuts import render, redirect
# from django.utils.translation import gettext_lazy as _

# from accounts_users.forms.signup_forms import UserSignupForm

# def register_social_view(request):
#     if request.method == "POST":
#         form = UserSignupForm(request.POST)
#         if form.is_valid():
#             user = form.save(commit=False)
#             user.is_active = True
#             user.save()
#             messages.success(request, _("Compte créé avec succès."))
#             return redirect("accounts_users_web:login")
#     else:
#         form = UserSignupForm()

#     return render(
#         request,
#         "accounts_users/registration/register_social_form.html",
#         {"form": form}
#     )
