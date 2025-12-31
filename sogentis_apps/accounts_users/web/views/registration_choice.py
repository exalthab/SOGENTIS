from django.shortcuts import render
from django.utils.translation import gettext_lazy as _


def registration_choice_view(request):
    """
    Page de choix du type d'inscription :
    - Engagement social
    - Pôle économique (client, vendeur, entreprise)
    """
    return render(
        request,
        "accounts_users/registration/choice.html",
        {
            "page_title": _("Créer un compte"),
        }
    )






# from django.shortcuts import render
# from django.utils.translation import gettext_lazy as _

# def registration_choice_view(request):
#     """
#     Page de choix du type d'inscription :
#     - Sociale
#     - Économique
#     """
#     return render(
#         request,
#         "accounts_users/registration/choice.html",
#         {
#             "page_title": _("Créer un compte"),
#         }
#     )
    
    
    
    
    