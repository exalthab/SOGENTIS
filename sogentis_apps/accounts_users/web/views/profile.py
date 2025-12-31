# accounts_users/web/views/profile.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.translation import gettext as _

from accounts_users.models.users_profile import UserProfile


@login_required
def myprofile_view(request):
    user = request.user

    # Récupérer le profil sans faire planter si inexistant
    profile = (
        UserProfile.objects.filter(user=user).first()
    )

    return render(
        request,
        "dashboard/profile/profile.html",  # on utilise le template dashboard/profile/profile.html
        {
            "page_title": _("Mon profil"),
            "dashboard_menu": "dashboard/user/_menu.html",
            "profile": profile,
        },
    )









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
