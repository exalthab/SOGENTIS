# common/middleware.py
from django.contrib import messages
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin


class ProfileStatusMiddleware(MiddlewareMixin):
    """
    Empêche l'accès au dashboard si :
    - compte non activé (email non confirmé)
    - profil en attente
    - profil refusé
    """

    EXEMPT_URLS = [
        # Auth
        "accounts_users_web:login",
        "accounts_users_web:logout",
        "accounts_users_web:signup",
        "accounts_users_web:activate",
        "accounts_users_web:resend_activation",
        "accounts_users_web:password_reset",
        "accounts_users_web:password_reset_done",
        "accounts_users_web:password_reset_confirm",
        "accounts_users_web:password_reset_complete",

        # Pages info
        "accounts_users_web:profile_pending_notice",
        "accounts_users_web:profile_refused_notice",
    ]

    def process_view(self, request, view_func, view_args, view_kwargs):
        user = request.user

        # Pas connecté -> rien à faire
        if not user.is_authenticated:
            return None

        # Resolver match
        rm = getattr(request, "resolver_match", None)
        if not rm:
            return None

        current_view = getattr(rm, "view_name", "") or ""

        # ✅ Ne bloque QUE le dashboard
        # (tu peux adapter si ton dashboard a un autre namespace)
        is_dashboard = current_view.startswith("dashboard:") or ("dashboard" in (rm.namespaces or []))
        if not is_dashboard:
            return None

        # Exemptions (login, notices, reset password, etc.)
        if current_view in self.EXEMPT_URLS:
            return None

        # Option : laisser passer staff/superuser
        # (décommente si tu veux)
        # if user.is_staff or user.is_superuser:
        #     return None

        # 1) Compte non activé
        if not user.is_active:
            messages.warning(request, "Veuillez activer votre compte par e-mail.")
            return redirect("accounts_users_web:login")

        # 2) Profil associé (supporte user.profile OU user.userprofile)
        profile = getattr(user, "profile", None) or getattr(user, "userprofile", None)
        if not profile:
            return None

        status = getattr(profile, "status", None)
        if not status:
            return None

        # 3) Pending
        if status == "pending":
            messages.info(request, "Votre profil est toujours en attente de validation.")
            return redirect("accounts_users_web:profile_pending_notice")

        # 4) Refused
        if status == "refused":
            messages.error(request, "Votre profil a été refusé.")
            return redirect("accounts_users_web:profile_refused_notice")

        return None












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
