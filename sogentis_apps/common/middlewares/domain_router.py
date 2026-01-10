# common/middlewares/domain_router.py

from django.conf import settings
from django.http import Http404
from django.urls import set_urlconf, clear_urlconf


class DomainRouterMiddleware:
    """
    Middleware multi-domaines : choisit un URLConf selon le host.
    ⚠️ À utiliser seul (idéalement sans CrossDomainRedirectMiddleware).

    Attributs ajoutés à request :
      - request.domain_host : host complet (ex: www.sogentis.org)
      - request.domain_urlconf : URLConf utilisé
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.domain_urlconf = getattr(settings, "DOMAIN_URLCONF", {}) or {}
        self.default_urlconf = getattr(settings, "DEFAULT_DOMAIN_URLCONF", settings.ROOT_URLCONF)
        self.strict_host = bool(getattr(settings, "DOMAIN_ROUTER_STRICT_HOST", False))

    def __call__(self, request):
        raw_host = getattr(request, "get_host", lambda: "")()
        host = (raw_host or "").split(":")[0].strip().lower()
        bare_host = host.removeprefix("www.")

        # Recherche URLConf : priorité host complet, fallback bare_host
        urlconf = self.domain_urlconf.get(host) or self.domain_urlconf.get(bare_host)

        if not urlconf:
            if self.strict_host:
                raise Http404(f"Unknown host: {host}")
            urlconf = self.default_urlconf

        request.domain_host = host
        request.domain_urlconf = urlconf

        # Set URLConf pour cette requête uniquement
        set_urlconf(urlconf)
        try:
            response = self.get_response(request)
        finally:
            clear_urlconf()  # Nettoyage pour les requêtes suivantes

        return response







# # common/middlewares/domain_router.py 10/01/2026
# from django.conf import settings
# from django.http import Http404
# from django.urls import set_urlconf, clear_urlconf


# class DomainRouterMiddleware:
#     """
#     Middleware multi-domaines: choisit un URLConf selon le host.
#     ⚠️ À utiliser SEUL (idéalement sans CrossDomainRedirectMiddleware).
#     """

#     def __init__(self, get_response):
#         self.get_response = get_response
#         self.domain_urlconf = getattr(settings, "DOMAIN_URLCONF", {}) or {}
#         self.default_urlconf = getattr(settings, "DEFAULT_DOMAIN_URLCONF", settings.ROOT_URLCONF)
#         self.strict_host = bool(getattr(settings, "DOMAIN_ROUTER_STRICT_HOST", False))

#     def __call__(self, request):
#         host = (request.get_host() or "").split(":")[0].lower()
#         urlconf = self.domain_urlconf.get(host) or self.domain_urlconf.get(host[4:] if host.startswith("www.") else host)

#         if not urlconf:
#             if self.strict_host:
#                 raise Http404("Unknown host")
#             urlconf = self.default_urlconf

#         request.domain_host = host
#         request.domain_urlconf = urlconf

#         set_urlconf(urlconf)
#         try:
#             return self.get_response(request)
#         finally:
#             clear_urlconf()







# # common/middlewares/domain_router.py 09/01/2026

# from django.http import Http404
# from django.urls import set_urlconf, clear_urlconf

# # Tu peux ajuster le mapping selon tes domaines réels
# DOMAIN_URLCONF = {
#     # SOCIAL
#     "sogentis.org": "config.urls_social",
#     "www.sogentis.org": "config.urls_social",

#     # COMMERCIAL
#     "sogentis.com": "config.urls_commercial",
#     "www.sogentis.com": "config.urls_commercial",

#     # INSTITUTION
#     "sogentis.sn": "config.urls_institution",
#     "www.sogentis.sn": "config.urls_institution",

#     # (Optionnel) APP
#     "app.sogentis.org": "config.urls_app",
# }

# DEFAULT_URLCONF = "config.urls_social"
# STRICT_HOST = False  # mets True si tu veux 404 sur host inconnu


# class DomainRouterMiddleware:
#     """
#     Middleware multi-domaines: choisit un URLConf selon le host.
#     """

#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         host = (request.get_host() or "").split(":")[0].lower()

#         urlconf = DOMAIN_URLCONF.get(host)
#         if not urlconf:
#             if STRICT_HOST:
#                 raise Http404("Unknown host")
#             urlconf = DEFAULT_URLCONF

#         request.domain_host = host
#         request.domain_urlconf = urlconf

#         set_urlconf(urlconf)
#         try:
#             response = self.get_response(request)
#         finally:
#             clear_urlconf()

#         return response
