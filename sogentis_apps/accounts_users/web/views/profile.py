# accounts_users/web/views/profile.py
from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _


def _get_best_profile(user):
    profile = getattr(user, "userprofile", None)
    if profile is not None:
        return profile, "userprofile"

    try:
        from accounts_users.models.social.social_profile import SocialProfile
        sp = SocialProfile.objects.filter(user=user).first()
        if sp:
            return sp, "social"
    except Exception:
        pass

    try:
        from accounts_users.models.users_economic_profile import UserEconomicProfile
        ep = UserEconomicProfile.objects.filter(user=user).first()
        if ep:
            return ep, "economic"
    except Exception:
        pass

    return None, None


@login_required
def myprofile_view(request):
    profile, profile_kind = _get_best_profile(request.user)

    return render(
        request,
        "dashboard/profile/profile.html",
        {
            "page_title": _("Mon profil"),
            "dashboard_menu": "dashboard/user/_menu.html",
            "profile": profile,
            "profile_kind": profile_kind,
        },
    )







# # accounts_users/web/views/profile.py
# from __future__ import annotations

# from django.contrib.auth.decorators import login_required
# from django.shortcuts import redirect, render
# from django.utils.translation import gettext_lazy as _


# def _get_best_profile(user):
#     """
#     Récupère un profil "best effort" sans casser :
#     - UserProfile central (si existe)
#     - SocialProfile (si existe)
#     - UserEconomicProfile (si existe)
#     """
#     # 1) UserProfile (central)
#     try:
#         from accounts_users.models.users_profile import UserProfile
#         up = UserProfile.objects.filter(user=user).first()
#         if up:
#             return up, "userprofile"
#     except Exception:
#         pass

#     # 2) SocialProfile
#     try:
#         from accounts_users.models.social.social_profile import SocialProfile
#         sp = SocialProfile.objects.filter(user=user).first()
#         if sp:
#             return sp, "social"
#     except Exception:
#         pass

#     # 3) Economic profile
#     try:
#         from accounts_users.models.users_economic_profile import UserEconomicProfile
#         ep = UserEconomicProfile.objects.filter(user=user).first()
#         if ep:
#             return ep, "economic"
#     except Exception:
#         pass

#     return None, None


# @login_required
# def myprofile_view(request):
#     user = request.user
#     profile, profile_kind = _get_best_profile(user)

#     # Si aucun profil trouvé, on ne plante pas.
#     # Tu peux rediriger vers profile_edit pour "créer/compléter".
#     if profile is None:
#         return render(
#             request,
#             "dashboard/profile/profile.html",
#             {
#                 "page_title": _("Mon profil"),
#                 "dashboard_menu": "dashboard/user/_menu.html",
#                 "profile": None,
#                 "profile_kind": None,
#                 "notice": _("Aucun profil n’est encore renseigné. Veuillez compléter votre profil."),
#             },
#         )

#     return render(
#         request,
#         "dashboard/profile/profile.html",  # tu gardes ton template dashboard
#         {
#             "page_title": _("Mon profil"),
#             "dashboard_menu": "dashboard/user/_menu.html",
#             "profile": profile,
#             "profile_kind": profile_kind,  # utile pour afficher un badge/sections conditionnelles
#         },
#     )






# # accounts_users/web/views/profile.py
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render
# from django.utils.translation import gettext as _

# from accounts_users.models.users_profile import UserProfile


# @login_required
# def myprofile_view(request):
#     user = request.user

#     # Récupérer le profil sans faire planter si inexistant
#     profile = (
#         UserProfile.objects.filter(user=user).first()
#     )

#     return render(
#         request,
#         "dashboard/profile/profile.html",  # on utilise le template dashboard/profile/profile.html
#         {
#             "page_title": _("Mon profil"),
#             "dashboard_menu": "dashboard/user/_menu.html",
#             "profile": profile,
#         },
#     )









# # accounts_users/web/views/profile.py
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render
# from django.utils.translation import gettext as _


# @login_required
# def myprofile_view(request):
#     return render(
#         request,
#         "accounts_users/profile.html",
#         {
#             "page_title": _("Mon profil"),
#         },
#     )
