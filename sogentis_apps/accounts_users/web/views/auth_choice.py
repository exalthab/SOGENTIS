from django.shortcuts import render
from django.utils.translation import gettext_lazy as _


def auth_choice_view(request):
    """
    Page de choix d’accès :
    - Connexion ou inscription
    - Social ou Économique
    """
    return render(
        request,
        "accounts_users/auth/choice.html",
        {
            "page_title": _("Accéder à votre espace"),
        }
    )







# # accounts_users/web/views/auth_choice.py
# from django.shortcuts import render
# from django.utils.translation import gettext_lazy as _

# def auth_choice_view(request):
#     return render(
#         request,
#         "accounts_users/auth/choice.html",
#         {
#             "page_title": _("Accéder à votre espace"),
#         }
#     )
