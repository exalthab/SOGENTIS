# accounts_users/web/views/profile_web_views.py

from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils.translation import gettext_lazy as _

from accounts_users.models.users_economic_profile import UserEconomicProfile
from accounts_users.views.profiles import update_profile_logic


# ==========================================================
# 1. VUE UTILISATEUR : Modifier son propre profil
# ==========================================================
@login_required
def profile_edit_view(request):
    """
    Vue utilisateur pour modifier SON propre profil.
    - Appelle la logique métier pure update_profile_logic()
    - Affiche messages de succès/erreur
    - Rend le template du dashboard (logique, cohérent)
    """
    form, success = update_profile_logic(request)

    if success is True:
        messages.success(request, _("Votre profil a été mis à jour avec succès."))
        return redirect("dashboard:profile")  # la bonne URL dashboard

    elif success is False:
        messages.error(request, _("Veuillez corriger les erreurs."))

    return render(request, "dashboard/profile/profile_edit.html", {
        "form": form,
        "profile": request.user.userprofile,
    })


# ==========================================================
# 2. VUE ADMIN : liste des profils en attente
# ==========================================================
@staff_member_required
def list_pending_profiles(request):
    """
    Liste les profils utilisateurs encore en état 'pending'.
    Réservé aux administrateurs.
    """
    profiles = UserEconomicProfile.objects.filter(status="pending")

    return render(request, "accounts_users/profiles/pending_list.html", {
        "profiles": profiles
    })


# ==========================================================
# 3. VUE UTILISATEUR : Notification “profil en attente”
# ==========================================================
@login_required
def profile_pending_notice(request):
    """
    Affiche un écran d'avertissement au user dont le profil
    n’est pas encore validé/activé dans le système interne.
    """
    return render(
        request,
        "accounts_users/registration/profile_pending_notice.html"
    )









# # accounts_users/web/views/profile_web_views.py
# from django.contrib.auth.decorators import login_required
# from django.contrib.admin.views.decorators import staff_member_required
# from django.contrib import messages
# from django.shortcuts import render, redirect
# from django.utils.translation import gettext_lazy as _

# from accounts_users.models.users_profile import UserProfile
# from accounts_users.views.profiles import update_profile_logic


# # ==========================================================
# # 1. VUE USER : Modifier son propre profil
# # ==========================================================
# @login_required
# def profile_edit_view(request):
#     """
#     Vue complète : rend le template, affiche les messages.
#     """
#     form, success = update_profile_logic(request)

#     if success is True:
#         messages.success(request, _("Votre profil a été mis à jour avec succès."))
#         return redirect("dashboard:profile")
#     elif success is False:
#         messages.error(request, _("Veuillez corriger les erreurs."))

#     return render(request, "accounts_users/registration/profile_edit.html", {
#         "form": form,
#         "profile": request.user.userprofile,
#     })


# # ==========================================================
# # 2. VUE ADMIN : liste des profils en attente
# # ==========================================================
# @staff_member_required
# def list_pending_profiles(request):
#     profiles = UserProfile.objects.filter(status="pending")
#     return render(request, "accounts_users/profiles/pending_list.html", {
#         "profiles": profiles
#     })


# # ==========================================================
# # 3. VUE USER : Notification “profil en attente”
# # ==========================================================
# @login_required
# def profile_pending_notice(request):
#     return render(request, "accounts_users/registration/profile_pending_notice.html")





# # accounts_users/web/views/profile_views.py
# from django.contrib.admin.views.decorators import staff_member_required
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render
# from accounts_users.models.users_profile import UserProfile

# @staff_member_required
# def list_pending_profiles(request):
#     """
#     Vue admin : liste les profils utilisateur en attente de validation.
#     """
#     profiles = UserProfile.objects.filter(status='pending')
#     return render(request, 'accounts_users/profiles/pending_list.html', {'profiles': profiles})

# @login_required
# def profile_pending_notice(request):
#     """
#     Affiche un message au user dont le profil est en attente de validation.
#     """
#     return render(request, "accounts_users/registration/profile_pending_notice.html")





# # accounts_users/web/views/profile_views.py
# from django.contrib.admin.views.decorators import staff_member_required
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render
# from accounts_users.models.users_profile import UserProfile

# @staff_member_required
# def list_pending_profiles(request):
#     profiles = UserProfile.objects.filter(status='pending')
#     return render(request, 'accounts_users/profiles/pending_list.html', {'profiles': profiles})

# @login_required
# def profile_pending_notice(request):
#     return render(request, "accounts_users/registration/profile_pending_notice.html")

