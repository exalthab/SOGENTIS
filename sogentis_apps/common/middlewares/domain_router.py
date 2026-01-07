# common/middlewares/domain_router.py

from django.http import Http404
from django.urls import set_urlconf, clear_urlconf

# Tu peux ajuster le mapping selon tes domaines réels
DOMAIN_URLCONF = {
    # SOCIAL
    "sogentis.org": "config.urls_social",
    "www.sogentis.org": "config.urls_social",

    # COMMERCIAL
    "sogentis.com": "config.urls_commercial",
    "www.sogentis.com": "config.urls_commercial",

    # INSTITUTION
    "sogentis.sn": "config.urls_institution",
    "www.sogentis.sn": "config.urls_institution",

    # (Optionnel) APP
    "app.sogentis.org": "config.urls_app",
}

DEFAULT_URLCONF = "config.urls_social"
STRICT_HOST = False  # mets True si tu veux 404 sur host inconnu


class DomainRouterMiddleware:
    """
    Middleware multi-domaines: choisit un URLConf selon le host.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = (request.get_host() or "").split(":")[0].lower()

        urlconf = DOMAIN_URLCONF.get(host)
        if not urlconf:
            if STRICT_HOST:
                raise Http404("Unknown host")
            urlconf = DEFAULT_URLCONF

        request.domain_host = host
        request.domain_urlconf = urlconf

        set_urlconf(urlconf)
        try:
            response = self.get_response(request)
        finally:
            clear_urlconf()

        return response
