# common/middlewares/domain_middleware.py

from django.conf import settings

def _clean_host(raw_host: str) -> str:
    """Retourne le host en minuscules, sans port ni espaces"""
    if not raw_host:
        return ""
    return raw_host.split(":")[0].strip().lower()

def _bare_host(host: str) -> str:
    """Supprime le préfixe www. si présent"""
    return host.removeprefix("www.")


class DomainSiteMiddleware:
    """
    Middleware qui enrichit request avec les informations de domaine :
      - request.site_host : host complet (ex: www.sogentis.org)
      - request.site_bare_host : host sans www. (ex: sogentis.org)
      - request.site_type : type de site selon domaine (social/business/institution/default)

    Ne fait aucune redirection.
    """
    LOCAL_HOSTS = {"localhost", "127.0.0.1", "0.0.0.0"}

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        raw_host = getattr(request, "get_host", lambda: "")()
        host = _clean_host(raw_host)
        bare = _bare_host(host)

        request.site_host = host
        request.site_bare_host = bare

        # localhost / IP
        if bare in self.LOCAL_HOSTS:
            request.site_type = "default"
            return self.get_response(request)

        # Map définie dans settings
        domain_map = getattr(settings, "DOMAIN_SITE_MAP", {}) or {}
        site_type = domain_map.get(bare)

        # Détection automatique par suffixe
        if not site_type:
            if bare.endswith(".org"):
                site_type = "social"
            elif bare.endswith(".com"):
                site_type = "business"
            elif bare.endswith(".sn"):
                site_type = "institution"
            else:
                site_type = "default"

        request.site_type = site_type
        return self.get_response(request)







# # common/middlewares/domain_middleware.py 10/01/2026
# from django.conf import settings

# def _clean_host(raw_host: str) -> str:
#     host = (raw_host or "").split(":")[0].strip().lower()
#     return host

# def _bare_host(host: str) -> str:
#     return host[4:] if host.startswith("www.") else host


# class DomainSiteMiddleware:
#     """
#     Détermine request.site_type selon le domaine.
#     IMPORTANT: ne redirige pas.
#     """
#     LOCAL_HOSTS = {"localhost", "127.0.0.1", "0.0.0.0"}

#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         host = _clean_host(request.get_host())
#         bare = _bare_host(host)

#         request.site_host = host
#         request.site_bare_host = bare

#         if bare in self.LOCAL_HOSTS:
#             request.site_type = "default"
#             return self.get_response(request)

#         domain_map = getattr(settings, "DOMAIN_SITE_MAP", {}) or {}
#         site_type = domain_map.get(bare)

#         if not site_type:
#             if bare.endswith(".org"):
#                 site_type = "social"
#             elif bare.endswith(".com"):
#                 site_type = "business"
#             elif bare.endswith(".sn"):
#                 site_type = "institution"
#             else:
#                 site_type = "default"

#         request.site_type = site_type
#         return self.get_response(request)








# # common/middlewares/domain_middleware.py 09/01/2026
# from django.conf import settings

# def _clean_host(raw_host: str) -> str:
#     host = (raw_host or "").split(":")[0].strip().lower()
#     if host.startswith("www."):
#         host = host[4:]
#     return host


# class DomainSiteMiddleware:
#     """
#     Détermine request.site_type selon le domaine.
#     IMPORTANT: ne redirige pas. La homepage hub reste accessible sur "/".
#     """
#     LOCAL_HOSTS = {"localhost", "127.0.0.1", "0.0.0.0"}

#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         host = _clean_host(request.get_host())

#         if host in self.LOCAL_HOSTS:
#             request.site_type = "default"
#             request.site_host = host
#             return self.get_response(request)

#         domain_map = getattr(settings, "DOMAIN_SITE_MAP", {}) or {}
#         site_type = domain_map.get(host)

#         if not site_type:
#             if host.endswith(".org"):
#                 site_type = "social"
#             elif host.endswith(".com"):
#                 site_type = "business"
#             elif host.endswith(".sn"):
#                 site_type = "institution"
#             else:
#                 site_type = "default"

#         request.site_type = site_type
#         request.site_host = host
#         return self.get_response(request)
