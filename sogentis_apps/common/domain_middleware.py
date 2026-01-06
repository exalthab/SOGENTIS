# /common/domain_middleware.py
# common/domain_middleware.py
from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse


def _clean_host(raw_host: str) -> str:
    host = (raw_host or "").split(":")[0].strip().lower()
    if host.startswith("www."):
        host = host[4:]
    return host


class DomainSiteMiddleware:
    """
    - définit request.site_type selon le host
    - redirige '/' vers la home du site (sauf localhost/loop)
    """

    LOCAL_HOSTS = {"localhost", "127.0.0.1", "0.0.0.0"}

    def __init__(self, get_response):
        self.get_response = get_response
        self.redirect_root = bool(getattr(settings, "DOMAIN_REDIRECT_ROOT", True))
        self.bypass_prefixes = tuple(
            getattr(
                settings,
                "DOMAIN_BYPASS_PREFIXES",
                ("/admin/", "/accounts/", "/dashboard/", "/i18n/", "/static/", "/media/"),
            )
        )

    def __call__(self, request):
        host = _clean_host(request.get_host())
        path = request.path_info or "/"

        # ✅ Local/dev : pas de redirection par domaine
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
                site_type = "sn"
            else:
                site_type = "default"

        request.site_type = site_type
        request.site_host = host

        # bypass (admin/static/i18n/etc.)
        if any(path.startswith(p) for p in self.bypass_prefixes):
            return self.get_response(request)

        # redirige seulement '/' et seulement si activé
        if self.redirect_root and path == "/":
            if site_type == "business":
                target = reverse(getattr(settings, "BUSINESS_HOME_URLNAME", "economic:index"))
            elif site_type == "social":
                target = reverse(getattr(settings, "SOCIAL_HOME_URLNAME", "social:index"))
            elif site_type == "sn":
                target = reverse(getattr(settings, "SN_HOME_URLNAME", "core:home"))
            else:
                # ✅ default => ne redirige pas (évite / -> /)
                return self.get_response(request)

            # ✅ anti-boucle : si la cible == path actuel, on ne redirige pas
            if target == path:
                return self.get_response(request)

            return redirect(target)

        return self.get_response(request)

