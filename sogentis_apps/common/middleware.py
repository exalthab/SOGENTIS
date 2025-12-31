# common/middleware.py
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.utils.deprecation import MiddlewareMixin

class ProfileStatusMiddleware(MiddlewareMixin):
    """
    Empêche l'accès au dashboard si :
    - le compte n'est pas activé (email non confirmé)
    - le profil est en attente de validation
    - le profil est refusé
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

        # Si l'utilisateur n'est pas connecté → rien à bloquer
        if not user.is_authenticated:
            return None

        # Vérifie exemption
        try:
            current_url_name = request.resolver_match.view_name
        except Exception:
            return None

        if current_url_name in self.EXEMPT_URLS:
            return None

        # 1) Compte non activé = email pas confirmé
        if not user.is_active:
            messages.warning(request, "Veuillez activer votre compte par e-mail.")
            return redirect("accounts_users_web:login")

        # 2) Profil associé
        profile = getattr(user, "userprofile", None)
        if not profile:
            return None  # aucun profil → on laisse passer

        # 3) Profil en attente
        if profile.status == "pending":
            messages.info(request, "Votre profil est toujours en attente de validation.")
            return redirect("accounts_users_web:profile_pending_notice")

        # 4) Profil refusé
        if profile.status == "refused":
            messages.error(request, "Votre profil a été refusé.")
            return redirect("accounts_users_web:profile_refused_notice")

        return None
