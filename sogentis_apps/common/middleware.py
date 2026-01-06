# common/middleware.py
from __future__ import annotations

from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import NoReverseMatch, reverse
from django.utils.deprecation import MiddlewareMixin


class DomainMiddleware(MiddlewareMixin):
    """
    Déduit le type de site par domaine + redirige la racine vers le bon pôle
    si DOMAIN_REDIRECT_ROOT=True.

    Hub accessible via /hub/ (et /fr/hub/ si i18n).
    """

    def process_request(self, request):
        host = (request.get_host() or "").split(":")[0].lower().strip()
        bare = host[4:] if host.startswith("www.") else host

        request.site_host = host
        request.site_bare_host = bare

        site_type = self._resolve_site_type(bare)
        request.site_type = site_type

        # Bypass (admin, static, hub, etc.)
        path = request.path_info or "/"
        if self._is_bypassed(path):
            return None

        # Redirige uniquement "/" et "/<lang>/"
        if not getattr(settings, "DOMAIN_REDIRECT_ROOT", False):
            return None

        roots = {"/"}
        for code, _ in getattr(settings, "LANGUAGES", []):
            roots.add(f"/{code}/")

        if path not in roots:
            return None

        # Calcul home cible selon site_type
        target_urlname = self._home_urlname_for(site_type)
        target_path = self._safe_reverse(target_urlname) or "/"

        if target_path and target_path != path:
            permanent = bool(getattr(settings, "DOMAIN_REDIRECT_PERMANENT", False))
            return redirect(target_path, permanent=permanent)

        return None

    def _is_bypassed(self, path: str) -> bool:
        prefixes = getattr(settings, "DOMAIN_BYPASS_PREFIXES", ()) or ()
        return any(path.startswith(p) for p in prefixes)

    def _resolve_site_type(self, bare_host: str) -> str:
        mapping = getattr(settings, "DOMAIN_SITE_MAP", {}) or {}
        if bare_host in mapping:
            return mapping[bare_host]

        if bare_host.endswith(".org"):
            return "social"
        if bare_host.endswith(".com"):
            return "business"
        if bare_host.endswith(".sn"):
            return "institution"
        return "default"

    def _home_urlname_for(self, site_type: str) -> str:
        if site_type == "business":
            return getattr(settings, "BUSINESS_HOME_URLNAME", "economic:index")
        if site_type == "social":
            return getattr(settings, "SOCIAL_HOME_URLNAME", "social:index")
        if site_type == "institution":
            return getattr(settings, "SN_HOME_URLNAME", "institution:index")
        return getattr(settings, "DEFAULT_HOME_URLNAME", "core:home")

    def _safe_reverse(self, urlname: str) -> str:
        try:
            return reverse(urlname)
        except NoReverseMatch:
            return "/"


class ProfileStatusMiddleware(MiddlewareMixin):
    EXEMPT_URLS = [
        "accounts_users_web:login",
        "accounts_users_web:logout",
        "accounts_users_web:signup",
        "accounts_users_web:activate",
        "accounts_users_web:resend_activation",
        "accounts_users_web:password_reset",
        "accounts_users_web:password_reset_done",
        "accounts_users_web:password_reset_confirm",
        "accounts_users_web:password_reset_complete",
        "accounts_users_web:profile_pending_notice",
        "accounts_users_web:profile_refused_notice",
    ]

    def process_view(self, request, view_func, view_args, view_kwargs):
        user = request.user
        if not user.is_authenticated:
            return None

        try:
            current_url_name = request.resolver_match.view_name
        except Exception:
            return None

        if current_url_name in self.EXEMPT_URLS:
            return None

        if not user.is_active:
            messages.warning(request, "Veuillez activer votre compte par e-mail.")
            return redirect("accounts_users_web:login")

        profile = getattr(user, "userprofile", None)
        if not profile:
            return None

        status = getattr(profile, "status", "")
        if status == "pending":
            messages.info(request, "Votre profil est toujours en attente de validation.")
            return redirect("accounts_users_web:profile_pending_notice")

        if status == "refused":
            messages.error(request, "Votre profil a été refusé.")
            return redirect("accounts_users_web:profile_refused_notice")

        return None




# # common/middleware.py
# from __future__ import annotations

# from django.conf import settings
# from django.contrib import messages
# from django.shortcuts import redirect
# from django.urls import NoReverseMatch, reverse
# from django.utils.deprecation import MiddlewareMixin


# class DomainMiddleware(MiddlewareMixin):
#     """
#     Déduit le type de site selon le domaine et peut rediriger la racine vers
#     la "home" correspondante.

#     - .com -> business
#     - .org -> social
#     - .sn  -> institution
#     """

#     def process_request(self, request):
#         host = (request.get_host() or "").split(":")[0].lower().strip()
#         bare = host[4:] if host.startswith("www.") else host

#         # 1) Déterminer site_type
#         site_type = self._resolve_site_type(bare)
#         request.site_type = site_type
#         request.site_host = host
#         request.site_bare_host = bare

#         # 2) Calculer la home (path) correspondante
#         home_urlname = self._home_urlname_for(site_type)
#         home_path = self._safe_reverse(home_urlname) if home_urlname else "/"
#         request.site_home_urlname = home_urlname
#         request.site_home_path = home_path

#         # 3) Redirection automatique de la racine (option)
#         if getattr(settings, "DOMAIN_REDIRECT_ROOT", False) is True:
#             # Racines possibles: "/" + "/<lang>/"
#             roots = {"/"}
#             try:
#                 for code, _ in getattr(settings, "LANGUAGES", []):
#                     roots.add(f"/{code}/")
#             except Exception:
#                 pass

#             path = request.path_info or "/"
#             if path in roots and home_path and home_path != path:
#                 # 302 par défaut (évite cache agressif). Tu peux forcer 301 via setting.
#                 permanent = bool(getattr(settings, "DOMAIN_REDIRECT_PERMANENT", False))
#                 return redirect(home_path, permanent=permanent)

#         return None

#     def _resolve_site_type(self, bare_host: str) -> str:
#         # mapping précis (prioritaire)
#         site_map = getattr(settings, "DOMAIN_SITE_MAP", {}) or {}
#         if bare_host in site_map:
#             return site_map[bare_host]

#         # fallback par TLD
#         if bare_host.endswith(".org"):
#             return "social"
#         if bare_host.endswith(".com"):
#             return "business"
#         if bare_host.endswith(".sn"):
#             return "institution"
#         return "default"

#     def _home_urlname_for(self, site_type: str) -> str:
#         # réglable dans settings
#         if site_type == "business":
#             return getattr(settings, "BUSINESS_HOME_URLNAME", "economic:index")
#         if site_type == "social":
#             return getattr(settings, "SOCIAL_HOME_URLNAME", "social:index")
#         if site_type == "institution":
#             return getattr(settings, "SN_HOME_URLNAME", "institution:index")
#         return getattr(settings, "DEFAULT_HOME_URLNAME", "core:home")

#     def _safe_reverse(self, urlname: str) -> str:
#         try:
#             return reverse(urlname)
#         except NoReverseMatch:
#             return "/"


# class ProfileStatusMiddleware(MiddlewareMixin):
#     """
#     Empêche l'accès au dashboard si :
#     - le compte n'est pas activé (email non confirmé)
#     - le profil est en attente de validation
#     - le profil est refusé
#     """

#     EXEMPT_URLS = [
#         # Auth
#         "accounts_users_web:login",
#         "accounts_users_web:logout",
#         "accounts_users_web:signup",
#         "accounts_users_web:activate",
#         "accounts_users_web:resend_activation",
#         "accounts_users_web:password_reset",
#         "accounts_users_web:password_reset_done",
#         "accounts_users_web:password_reset_confirm",
#         "accounts_users_web:password_reset_complete",

#         # Pages info
#         "accounts_users_web:profile_pending_notice",
#         "accounts_users_web:profile_refused_notice",
#     ]

#     def process_view(self, request, view_func, view_args, view_kwargs):
#         user = request.user

#         if not user.is_authenticated:
#             return None

#         try:
#             current_url_name = request.resolver_match.view_name
#         except Exception:
#             return None

#         if current_url_name in self.EXEMPT_URLS:
#             return None

#         if not user.is_active:
#             messages.warning(request, "Veuillez activer votre compte par e-mail.")
#             return redirect("accounts_users_web:login")

#         profile = getattr(user, "userprofile", None)
#         if not profile:
#             return None

#         if getattr(profile, "status", "") == "pending":
#             messages.info(request, "Votre profil est toujours en attente de validation.")
#             return redirect("accounts_users_web:profile_pending_notice")

#         if getattr(profile, "status", "") == "refused":
#             messages.error(request, "Votre profil a été refusé.")
#             return redirect("accounts_users_web:profile_refused_notice")

#         return None












# # common/middleware.py 05/01/2026
# from django.shortcuts import redirect
# from django.urls import reverse
# from django.contrib import messages
# from django.utils.deprecation import MiddlewareMixin

# class ProfileStatusMiddleware(MiddlewareMixin):
#     """
#     Empêche l'accès au dashboard si :
#     - le compte n'est pas activé (email non confirmé)
#     - le profil est en attente de validation
#     - le profil est refusé
#     """

#     EXEMPT_URLS = [
#         # Auth
#         "accounts_users_web:login",
#         "accounts_users_web:logout",
#         "accounts_users_web:signup",
#         "accounts_users_web:activate",
#         "accounts_users_web:resend_activation",
#         "accounts_users_web:password_reset",
#         "accounts_users_web:password_reset_done",
#         "accounts_users_web:password_reset_confirm",
#         "accounts_users_web:password_reset_complete",

#         # Pages info
#         "accounts_users_web:profile_pending_notice",
#         "accounts_users_web:profile_refused_notice",
#     ]

#     def process_view(self, request, view_func, view_args, view_kwargs):

#         user = request.user

#         # Si l'utilisateur n'est pas connecté → rien à bloquer
#         if not user.is_authenticated:
#             return None

#         # Vérifie exemption
#         try:
#             current_url_name = request.resolver_match.view_name
#         except Exception:
#             return None

#         if current_url_name in self.EXEMPT_URLS:
#             return None

#         # 1) Compte non activé = email pas confirmé
#         if not user.is_active:
#             messages.warning(request, "Veuillez activer votre compte par e-mail.")
#             return redirect("accounts_users_web:login")

#         # 2) Profil associé
#         profile = getattr(user, "userprofile", None)
#         if not profile:
#             return None  # aucun profil → on laisse passer

#         # 3) Profil en attente
#         if profile.status == "pending":
#             messages.info(request, "Votre profil est toujours en attente de validation.")
#             return redirect("accounts_users_web:profile_pending_notice")

#         # 4) Profil refusé
#         if profile.status == "refused":
#             messages.error(request, "Votre profil a été refusé.")
#             return redirect("accounts_users_web:profile_refused_notice")

#         return None
