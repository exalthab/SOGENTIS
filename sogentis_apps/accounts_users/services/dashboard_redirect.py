from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.conf import settings
from django.utils.translation import get_language


def get_dashboard_home_url(request):
    """
    Retourne l'URL correcte du dashboard en tenant compte :
    - du namespace "dashboard"
    - de i18n_patterns (/fr/, /en/, etc.)
    """

    try:
        return reverse("dashboard:index")
    except Exception:
        # Fallback absolu (ne devrait jamais arriver)
        lang = get_language() or settings.LANGUAGE_CODE
        return f"/{lang}/dashboard/"


def get_redirect_after_login(request):
    """
    Détermine la redirection après connexion.
    Priorité :
    1. `next` sécurisé (POST ou GET)
    2. Dashboard
    """

    next_url = request.POST.get("next") or request.GET.get("next")

    if next_url and url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return next_url

    return get_dashboard_home_url(request)








# # accounts_users/services/dashboard_redirect.py

# from django.urls import reverse


# def get_dashboard_home_url(request):
#     """
#     Retourne l'URL correcte du dashboard en tenant compte :
#     - du namespace "dashboard"
#     - de la configuration i18n_patterns qui ajoute automatiquement /fr/ ou /en/
#     """

#     try:
#         return reverse("dashboard:index")
#     except Exception:
#         # Cas extrême : namespace absent
#         # On retombe sur une URL par défaut
#         return "/dashboard/"


# def get_redirect_after_login(request):
#     """
#     Détermine la redirection après connexion.
#     Priorité :
#     1. `next` dans POST
#     2. `next` dans GET
#     3. Dashboard
#     """

#     next_url = request.POST.get("next") or request.GET.get("next")

#     if next_url:
#         return next_url

#     return get_dashboard_home_url(request)
