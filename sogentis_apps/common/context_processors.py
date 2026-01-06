# common/domain_middleware.py
from __future__ import annotations

from django.conf import settings
from django.shortcuts import redirect
from django.urls import NoReverseMatch, reverse


def _clean_host(raw_host: str) -> str:
    host = (raw_host or "").split(":")[0].strip().lower()
    if host.startswith("www."):
        host = host[4:]
    return host


class DomainSiteMiddleware:
    """
    - définit request.site_type selon le host
    - redirige '/' ET '/<lang>/' vers la home du site (sauf localhost/loop)
    - respecte DOMAIN_BYPASS_PREFIXES
    """

    LOCAL_HOSTS = {"localhost", "127.0.0.1", "0.0.0.0"}

    def __init__(self, get_response):
        self.get_response = get_response
        self.redirect_root = bool(getattr(settings, "DOMAIN_REDIRECT_ROOT", True))
        self.redirect_permanent = bool(getattr(settings, "DOMAIN_REDIRECT_PERMANENT", False))

        self.bypass_prefixes = tuple(
            getattr(
                settings,
                "DOMAIN_BYPASS_PREFIXES",
                ("/admin/", "/accounts/", "/dashboard/", "/i18n/", "/static/", "/media/"),
            )
        )

        # Racines à rediriger ("/" et "/fr/" etc.)
        roots = {"/"}
        for code, _ in getattr(settings, "LANGUAGES", []):
            roots.add(f"/{code}/")
        self.redirect_roots = roots

    def __call__(self, request):
        host = _clean_host(request.get_host())
        path = request.path_info or "/"

        # ✅ Local/dev : pas de redirection par domaine
        if host in self.LOCAL_HOSTS:
            request.site_type = "default"
            request.site_host = host
            request.site_bare_host = host
            return self.get_response(request)

        # ✅ site_type via mapping exact
        domain_map = getattr(settings, "DOMAIN_SITE_MAP", {}) or {}
        site_type = domain_map.get(host)

        # ✅ fallback via TLD
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
        request.site_bare_host = host

        # bypass (admin/static/i18n/etc.)
        if any(path.startswith(p) for p in self.bypass_prefixes):
            return self.get_response(request)

        # redirige seulement '/' et '/<lang>/' si activé
        if self.redirect_root and path in self.redirect_roots:
            target = self._resolve_target(site_type)

            # default => ne redirige pas (évite / -> /)
            if not target:
                return self.get_response(request)

            # anti-boucle
            if target == path:
                return self.get_response(request)

            return redirect(target, permanent=self.redirect_permanent)

        return self.get_response(request)

    def _resolve_target(self, site_type: str) -> str | None:
        if site_type == "business":
            urlname = getattr(settings, "BUSINESS_HOME_URLNAME", "economic:index")
        elif site_type == "social":
            urlname = getattr(settings, "SOCIAL_HOME_URLNAME", "social:index")
        elif site_type == "institution":
            urlname = getattr(settings, "SN_HOME_URLNAME", "institution:index")
        else:
            # default: ne redirige pas
            return None

        try:
            return reverse(urlname)
        except NoReverseMatch:
            return None
