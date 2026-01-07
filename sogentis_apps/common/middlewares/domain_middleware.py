# common/middlewares/domain_middleware.py
from django.conf import settings

def _clean_host(raw_host: str) -> str:
    host = (raw_host or "").split(":")[0].strip().lower()
    if host.startswith("www."):
        host = host[4:]
    return host


class DomainSiteMiddleware:
    """
    Détermine request.site_type selon le domaine.
    IMPORTANT: ne redirige pas. La homepage hub reste accessible sur "/".
    """
    LOCAL_HOSTS = {"localhost", "127.0.0.1", "0.0.0.0"}

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = _clean_host(request.get_host())

        if host in self.LOCAL_HOSTS:
            request.site_type = "default"
            request.site_host = host
            return self.get_response(request)

        domain_map = getattr(settings, "DOMAIN_SITE_MAP", {}) or {}
        site_type = domain_map.get(host)

        if not site_type:
            if host.endswith(".org"):
                site_type = "social"
            elif host.endswith(".com"):
                site_type = "business"
            elif host.endswith(".sn"):
                site_type = "institution"
            else:
                site_type = "default"

        request.site_type = site_type
        request.site_host = host
        return self.get_response(request)
