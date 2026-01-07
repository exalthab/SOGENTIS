# common/middlewares/cross_domain_redirect.py
from django.conf import settings
from django.http import HttpResponsePermanentRedirect

REDIRECT_PREFIXES = {
    # depuis .org => economic -> .com ; institution -> .sn ; app -> app.
    "sogentis.org": [
        ("/economic/", "COMMERCIAL"),
        ("/institution/", "INSTITUTION"),
        ("/dashboard/", "APP"),
        ("/accounts/", "APP"),
        ("/admin/", "APP"),
    ],
    "www.sogentis.org": [
        ("/economic/", "COMMERCIAL"),
        ("/institution/", "INSTITUTION"),
        ("/dashboard/", "APP"),
        ("/accounts/", "APP"),
        ("/admin/", "APP"),
    ],

    # depuis .sn => economic -> .com ; social -> .org ; app -> app.
    "sogentis.sn": [
        ("/economic/", "COMMERCIAL"),
        ("/social/", "SOCIAL"),
        ("/dashboard/", "APP"),
        ("/accounts/", "APP"),
        ("/admin/", "APP"),
    ],
    "www.sogentis.sn": [
        ("/economic/", "COMMERCIAL"),
        ("/social/", "SOCIAL"),
        ("/dashboard/", "APP"),
        ("/accounts/", "APP"),
        ("/admin/", "APP"),
    ],

    # depuis .com => social -> .org ; institution -> .sn ; app -> app.
    "sogentis.com": [
        ("/social/", "SOCIAL"),
        ("/institution/", "INSTITUTION"),
        ("/dashboard/", "APP"),
        ("/accounts/", "APP"),
        ("/admin/", "APP"),
    ],
    "www.sogentis.com": [
        ("/social/", "SOCIAL"),
        ("/institution/", "INSTITUTION"),
        ("/dashboard/", "APP"),
        ("/accounts/", "APP"),
        ("/admin/", "APP"),
    ],
}


def _split_lang_prefix(path: str):
    """
    Support i18n_patterns: /fr/... /en/...
    Retourne (lang_prefix, rest)
      - lang_prefix: '' ou '/fr' ou '/en'
      - rest: commence par '/'
    """
    codes = [c for c, _ in getattr(settings, "LANGUAGES", [])]
    for code in codes:
        prefix = f"/{code}/"
        if path.startswith(prefix):
            return f"/{code}", path[len(f"/{code}"):]  # rest commence par '/'
    return "", path


class CrossDomainRedirectMiddleware:
    """
    Force l'ouverture de certains préfixes sur un domaine cible.
    Exemple : /economic/... -> toujours sur sogentis.com
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = (request.get_host() or "").split(":")[0].lower()

        # On conserve les query params
        full_path = request.get_full_path() or "/"
        path_only = request.path or "/"
        query_string = request.META.get("QUERY_STRING", "")

        lang_prefix, rest = _split_lang_prefix(path_only)

        for prefix, target_key in REDIRECT_PREFIXES.get(host, []):
            if rest.startswith(prefix):
                base = getattr(settings, f"{target_key}_BASE_URL", "").rstrip("/")
                if not base:
                    break

                redirect_url = base + lang_prefix + rest
                if query_string:
                    redirect_url += "?" + query_string
                return HttpResponsePermanentRedirect(redirect_url)

        return self.get_response(request)