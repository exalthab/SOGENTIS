# accounts_users/web/views/registration_choice.py (ou ton fichier actuel)

from django.shortcuts import render
from django.utils.http import url_has_allowed_host_and_scheme

def registration_choice_view(request):
    # next safe
    next_url = (request.GET.get("next") or request.POST.get("next") or "").strip()
    if next_url and not url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        next_url = ""

    # focus safe
    focus = (request.GET.get("focus") or request.GET.get("context") or "").strip().lower()
    if focus not in ("social", "economic"):
        focus = ""

    context = {
        "next_url": next_url,        # ✅ toujours défini
        "focus": focus,              # ✅ toujours défini
        "show_social": focus != "economic",
        "show_economic": focus != "social",
    }
    return render(request, "accounts_users/registration/choice.html", context)







# # accounts_users/web/views/registration_choice.py
# from __future__ import annotations

# from django.shortcuts import render
# from django.urls import reverse
# from django.utils.http import url_has_allowed_host_and_scheme
# from django.utils.translation import gettext_lazy as _


# def _safe_next(request) -> str:
#     nxt = (request.GET.get("next") or "").strip()
#     if nxt and url_has_allowed_host_and_scheme(
#         url=nxt,
#         allowed_hosts={request.get_host()},
#         require_https=request.is_secure(),
#     ):
#         return nxt
#     return ""


# def registration_choice_view(request):
#     """
#     Hub d’inscription
#     - affiche Social + Economic (par défaut)
#     - ou seulement Social / seulement Economic selon ?context=
#     - focus visuel via ?focus=social|economic
#     """
#     context_mode = (request.GET.get("context") or "").strip().lower()
#     focus = (request.GET.get("focus") or "").strip().lower()
#     next_url = _safe_next(request)

#     show_social = True
#     show_economic = True

#     if context_mode == "social":
#         show_economic = False
#         focus = focus or "social"
#     elif context_mode == "economic":
#         show_social = False
#         focus = focus or "economic"

#     return render(
#         request,
#         "accounts_users/registration/choice.html",
#         {
#             "page_title": _("Créer un compte"),
#             "focus": focus,
#             "show_social": show_social,
#             "show_economic": show_economic,
#             "next": next_url,
#         },
#     )






# # accounts_users/web/views/registration_choice.py
# from django.shortcuts import render
# from django.utils.translation import gettext_lazy as _

# def registration_choice_view(request):
#     # social only si ?context=social ou ?focus=social
#     ctx = (request.GET.get("focus") or request.GET.get("context") or "").strip().lower()

#     show_social = True
#     show_economic = (ctx != "social")

#     return render(
#         request,
#         "accounts_users/registration/choice.html",
#         {
#             "page_title": _("Créer un compte"),
#             "mode": "register",
#             "show_social": show_social,
#             "show_economic": show_economic,
#             "focus": ctx,  # pour surligner le bon bloc
#         },
#     )






# # accounts_users/web/views/registration_choice.py
# from django.shortcuts import render
# from django.utils.translation import gettext_lazy as _


# def registration_choice_view(request):
#     """
#     Page de choix du type d'inscription :
#     - Engagement social
#     - Pôle économique
#     """
#     return render(
#         request,
#         "accounts_users/registration/choice.html",
#         {
#             "page_title": _("Créer un compte"),
#             "mode": "register",
#         },
#     )








# # accounts_users/web/views/registration_choice.py 12-01-2026
# from django.shortcuts import render
# from django.utils.translation import gettext_lazy as _


# def registration_choice_view(request):
#     """
#     Page de choix du type d'inscription :
#     - Engagement social
#     - Pôle économique (client, vendeur, entreprise)
#     """
#     return render(
#         request,
#         "accounts_users/auth/choice.html",

#         {
#             "page_title": _("Créer un compte"),
#         }
#     )






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
    
    
    
    
    