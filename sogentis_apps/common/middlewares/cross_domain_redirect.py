# common/middlewares/cross_domain_redirect.py

from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponsePermanentRedirect


REDIRECT_PREFIXES = {
    "sogentis.org": [
        ("/economic/", "COMMERCIAL"),
        ("/institution/", "INSTITUTION"),
    ],
    "www.sogentis.org": [
        ("/economic/", "COMMERCIAL"),
        ("/institution/", "INSTITUTION"),
    ],
    "sogentis.sn": [
        ("/economic/", "COMMERCIAL"),
        ("/social/", "SOCIAL"),
    ],
    "www.sogentis.sn": [
        ("/economic/", "COMMERCIAL"),
        ("/social/", "SOCIAL"),
    ],
    "sogentis.com": [
        ("/social/", "SOCIAL"),
        ("/institution/", "INSTITUTION"),
    ],
    "www.sogentis.com": [
        ("/social/", "SOCIAL"),
        ("/institution/", "INSTITUTION"),
    ],
}


def _split_lang_prefix(path: str):
    """
    Support i18n_patterns: /fr/... /en/...
    Retourne (lang_prefix, rest)
    """
    codes = [code for code, _ in getattr(settings, "LANGUAGES", [])]
    for code in codes:
        prefix = f"/{code}/"
        if path.startswith(prefix):
            return f"/{code}", path[len(f"/{code}"):]
    return "", path


class CrossDomainRedirectMiddleware:
    """
    Force certains préfixes d'URL à être servis
    sur un domaine cible spécifique.
    """

    SAFE_METHODS = {"GET", "HEAD"}

    def __init__(self, get_response):
        self.get_response = get_response
        self.permanent = bool(
            getattr(settings, "CROSS_DOMAIN_REDIRECT_PERMANENT", False)
        )

    def __call__(self, request):
        # Ne jamais rediriger les méthodes non sûres
        if request.method not in self.SAFE_METHODS:
            return self.get_response(request)

        host = (request.get_host() or "").split(":")[0].lower()
        path = request.path or "/"
        query_string = request.META.get("QUERY_STRING", "")

        lang_prefix, rest = _split_lang_prefix(path)

        for prefix, target_key in REDIRECT_PREFIXES.get(host, []):
            if not rest.startswith(prefix):
                continue

            base_url = getattr(
                settings, f"{target_key}_BASE_URL", ""
            ).rstrip("/")

            # Base invalide ou absente → pas de redirection
            if not base_url.startswith(("http://", "https://")):
                return self.get_response(request)

            # Évite les boucles (déjà sur le bon domaine)
            if host in base_url:
                return self.get_response(request)

            redirect_url = f"{base_url}{lang_prefix}{rest}"
            if query_string:
                redirect_url = f"{redirect_url}?{query_string}"

            if self.permanent:
                return HttpResponsePermanentRedirect(redirect_url)

            return HttpResponseRedirect(redirect_url)

        return self.get_response(request)






# # common/middlewares/cross_domain_redirect.py 10/01/2026
# from django.conf import settings
# from django.http import HttpResponseRedirect, HttpResponsePermanentRedirect

# REDIRECT_PREFIXES = {
#     # depuis .org => economic -> .com ; institution -> .sn
#     "sogentis.org": [
#         ("/economic/", "COMMERCIAL"),
#         ("/institution/", "INSTITUTION"),
#     ],
#     "www.sogentis.org": [
#         ("/economic/", "COMMERCIAL"),
#         ("/institution/", "INSTITUTION"),
#     ],

#     # depuis .sn => economic -> .com ; social -> .org
#     "sogentis.sn": [
#         ("/economic/", "COMMERCIAL"),
#         ("/social/", "SOCIAL"),
#     ],
#     "www.sogentis.sn": [
#         ("/economic/", "COMMERCIAL"),
#         ("/social/", "SOCIAL"),
#     ],

#     # depuis .com => social -> .org ; institution -> .sn
#     "sogentis.com": [
#         ("/social/", "SOCIAL"),
#         ("/institution/", "INSTITUTION"),
#     ],
#     "www.sogentis.com": [
#         ("/social/", "SOCIAL"),
#         ("/institution/", "INSTITUTION"),
#     ],
# }


# def _split_lang_prefix(path: str):
#     """
#     Support i18n_patterns: /fr/... /en/...
#     Retourne (lang_prefix, rest)
#     """
#     codes = [c for c, _ in getattr(settings, "LANGUAGES", [])]
#     for code in codes:
#         prefix = f"/{code}/"
#         if path.startswith(prefix):
#             return f"/{code}", path[len(f"/{code}"):]
#     return "", path


# class CrossDomainRedirectMiddleware:
#     """
#     Force l'ouverture de certains préfixes sur un domaine cible.
#     Exemple : /economic/... -> toujours sur COMMERCIAL_BASE_URL
#     """

#     SAFE_METHODS = {"GET", "HEAD"}

#     def __init__(self, get_response):
#         self.get_response = get_response
#         self.permanent = bool(getattr(settings, "CROSS_DOMAIN_REDIRECT_PERMANENT", False))

#     def __call__(self, request):
#         # ⚠️ ne redirige pas les POST/PUT/... (sinon perte de payload / CSRF)
#         if request.method not in self.SAFE_METHODS:
#             return self.get_response(request)

#         host = (request.get_host() or "").split(":")[0].lower()
#         path_only = request.path or "/"
#         query_string = request.META.get("QUERY_STRING", "")

#         lang_prefix, rest = _split_lang_prefix(path_only)

#         for prefix, target_key in REDIRECT_PREFIXES.get(host, []):
#             if rest.startswith(prefix):
#                 base = getattr(settings, f"{target_key}_BASE_URL", "").rstrip("/")
#                 if not base:
#                     # si la base n'est pas définie, on ne redirige pas
#                     return self.get_response(request)

#                 redirect_url = base + lang_prefix + rest
#                 if query_string:
#                     redirect_url += "?" + query_string

#                 if self.permanent:
#                     return HttpResponsePermanentRedirect(redirect_url)
#                 return HttpResponseRedirect(redirect_url)

#         return self.get_response(request)






# # common/middlewares/cross_domain_redirect.py 09/01/2026
# from django.conf import settings
# from django.http import HttpResponsePermanentRedirect

# REDIRECT_PREFIXES = {
#     # depuis .org => economic -> .com ; institution -> .sn
#     "sogentis.org": [
#         ("/economic/", "COMMERCIAL"),
#         ("/institution/", "INSTITUTION"),
#     ],
#     "www.sogentis.org": [
#         ("/economic/", "COMMERCIAL"),
#         ("/institution/", "INSTITUTION"),
#     ],

#     # depuis .sn => economic -> .com ; social -> .org
#     "sogentis.sn": [
#         ("/economic/", "COMMERCIAL"),
#         ("/social/", "SOCIAL"),
#     ],
#     "www.sogentis.sn": [
#         ("/economic/", "COMMERCIAL"),
#         ("/social/", "SOCIAL"),
#     ],

#     # depuis .com => social -> .org ; institution -> .sn
#     "sogentis.com": [
#         ("/social/", "SOCIAL"),
#         ("/institution/", "INSTITUTION"),
#     ],
#     "www.sogentis.com": [
#         ("/social/", "SOCIAL"),
#         ("/institution/", "INSTITUTION"),
#     ],
# }


# def _split_lang_prefix(path: str):
#     """
#     Support i18n_patterns: /fr/... /en/...
#     Retourne (lang_prefix, rest)
#     """
#     codes = [c for c, _ in getattr(settings, "LANGUAGES", [])]
#     for code in codes:
#         prefix = f"/{code}/"
#         if path.startswith(prefix):
#             return f"/{code}", path[len(f"/{code}"):]
#     return "", path


# class CrossDomainRedirectMiddleware:
#     """
#     Force l'ouverture de certains préfixes sur un domaine cible.
#     Exemple : /economic/... -> toujours sur sogentis.com
#     """

#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         host = (request.get_host() or "").split(":")[0].lower()

#         path_only = request.path or "/"
#         query_string = request.META.get("QUERY_STRING", "")

#         lang_prefix, rest = _split_lang_prefix(path_only)

#         for prefix, target_key in REDIRECT_PREFIXES.get(host, []):
#             if rest.startswith(prefix):
#                 base = getattr(settings, f"{target_key}_BASE_URL", "").rstrip("/")
#                 if not base:
#                     break

#                 redirect_url = base + lang_prefix + rest
#                 if query_string:
#                     redirect_url += "?" + query_string
#                 return HttpResponsePermanentRedirect(redirect_url)

#         return self.get_response(request)
