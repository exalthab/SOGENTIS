# accounts_users/web/views/auth_login_choice.py
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

def auth_choice_view(request):
    # si tu veux cacher l’éco quand context=social
    ctx = (request.GET.get("context") or "").strip().lower()
    show_social = True
    show_economic = (ctx != "social")  # social only si context=social

    return render(
        request,
        "accounts_users/auth/choice.html",
        {
            "page_title": _("Accéder à votre espace"),
            "mode": "auth",
            "show_social": show_social,
            "show_economic": show_economic,
            "login_context": ctx or "generic",
        },
    )






# # accounts_users/web/views/auth_login_choice.py
# from django.shortcuts import render
# from django.utils.translation import gettext_lazy as _


# def auth_choice_view(request):
#     """
#     Hub Auth:
#     - Connexion ou inscription
#     - Social ou Économique
#     """
#     return render(
#         request,
#         "accounts_users/auth/choice.html",
#         {
#             "page_title": _("Accéder à votre espace"),
#             "mode": "auth",
#         },
#     )






# # accounts_users/web/views/auth_login_choice.py
# from django.shortcuts import render
# from django.utils.translation import gettext_lazy as _


# def auth_choice_view(request):
#     """
#     Page de choix d’accès :
#     - Connexion ou inscription
#     - Social ou Économique
#     """
#     return render(
#         request,
#         "accounts_users/auth/register_choice.html",
#         {
#             "page_title": _("Accéder à votre espace"),
#             "mode": "auth",
#         },
#     )







# # accounts_users/web/views/auth_choice.py 12-01-2026
# from django.shortcuts import render
# from django.utils.translation import gettext_lazy as _


# def auth_choice_view(request):
#     """
#     Page de choix d’accès :
#     - Connexion ou inscription
#     - Social ou Économique
#     """
#     return render(
#         request,
#         "accounts_users/auth/choice.html",
#         {
#             "page_title": _("Accéder à votre espace"),
#         }
#     )







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
