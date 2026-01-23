# accounts_users/web/views/auth_login_web_views.py
from __future__ import annotations

from django.contrib import messages
from django.contrib.auth import login, logout
from django.shortcuts import redirect, render
from django.urls import NoReverseMatch, reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext_lazy as _

from accounts_users.forms.login_forms import CustomLoginForm


def _reverse_first(*names: str, fallback: str = "/") -> str:
    """
    Reverse "best effort" pour éviter les erreurs si un nom a changé
    (ex: auth:choice vs auth:auth_choice).
    """
    for name in names:
        try:
            return reverse(name)
        except NoReverseMatch:
            continue
    return fallback


def _resolve_auth_pole(request) -> str:
    """
    Retourne : 'social' | 'economic' | 'generic'
    """
    qp = (request.GET.get("context") or request.POST.get("context") or "").strip().lower()
    if qp in ("social", "economic", "generic"):
        return qp

    path = (request.path or "").lower()
    # tolérance sur différentes variantes d'URL
    if "login/social" in path or "/social/" in path:
        return "social"
    if "login/economic" in path or "/economic/" in path:
        return "economic"

    return "generic"


def _safe_next(request) -> str:
    """
    Retourne un next SAFE (ou "" si invalide).
    IMPORTANT: on ne force pas le hub ici, pour pouvoir l'afficher proprement côté template.
    """
    nxt = (request.POST.get("next") or request.GET.get("next") or "").strip()
    if nxt and url_has_allowed_host_and_scheme(
        url=nxt,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return nxt
    return ""


def login_view(request):
    if request.user.is_authenticated:
        messages.info(request, _("Vous êtes déjà connecté."))
        return redirect("dashboard:hub")

    auth_pole = _resolve_auth_pole(request)  # social|economic|generic
    next_url = _safe_next(request)           # "" ou url safe
    request_path = request.path or ""

    # Pour les templates : pole doit être "" ou social/economic (pas "generic")
    pole = auth_pole if auth_pole in ("social", "economic") else ""

    # Auth form (Django standard)
    form = CustomLoginForm(request, data=request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            user = form.get_user()

            if not user.is_active:
                messages.error(
                    request,
                    _(
                        "Votre compte n'est pas encore activé. "
                        "Vérifiez votre e-mail ou contactez l’administrateur."
                    ),
                )
            else:
                login(request, user)

                # remember_me optionnel
                remember = bool(form.cleaned_data.get("remember_me", False))
                request.session.set_expiry(None if remember else 0)

                # Redirection : next_url si fourni, sinon hub
                return redirect(next_url or reverse("dashboard:hub"))
        else:
            messages.error(request, _("Identifiants invalides. Veuillez réessayer."))

    return render(
        request,
        "accounts_users/auth/login.html",
        {
            # ✅ anciens templates
            "form": form,
            "next": next_url,
            "auth_pole": auth_pole,
            "login_context": auth_pole,

            # ✅ nouveaux templates (robustes, sans request.GET.*)
            "pole": pole,
            "next_url": next_url,
            "request_path": request_path,
        },
    )


def logout_view(request):
    logout(request)
    messages.success(request, _("Vous avez été déconnecté avec succès."))

    # supporte les 2 noms possibles
    return redirect(
        _reverse_first(
            "accounts_users:web:auth:choice",
            "accounts_users:web:auth:auth_choice",
            fallback="/",
        )
    )







# # accounts_users/web/views/auth_login_web_views.py
# from __future__ import annotations

# from django.contrib import messages
# from django.contrib.auth import login, logout
# from django.shortcuts import redirect, render
# from django.urls import NoReverseMatch, reverse
# from django.utils.http import url_has_allowed_host_and_scheme
# from django.utils.translation import gettext_lazy as _

# from accounts_users.forms.login_forms import CustomLoginForm


# def _reverse_first(*names: str, fallback: str = "/") -> str:
#     """
#     Reverse "best effort" pour éviter les erreurs si un nom a changé
#     (ex: auth:choice vs auth:auth_choice).
#     """
#     for name in names:
#         try:
#             return reverse(name)
#         except NoReverseMatch:
#             continue
#     return fallback


# def _resolve_auth_pole(request) -> str:
#     """
#     Retourne : 'social' | 'economic' | 'generic'
#     """
#     qp = (request.GET.get("context") or request.POST.get("context") or "").strip().lower()
#     if qp in ("social", "economic", "generic"):
#         return qp

#     path = (request.path or "").lower()
#     # tolérance sur différentes variantes d'URL
#     if "login/social" in path or "/social/" in path:
#         return "social"
#     if "login/economic" in path or "/economic/" in path:
#         return "economic"

#     return "generic"


# def _safe_next(request) -> str:
#     """
#     Retourne un next SAFE (ou "" si invalide).
#     IMPORTANT: on ne force pas le hub ici, pour pouvoir l'afficher proprement côté template.
#     """
#     nxt = (request.POST.get("next") or request.GET.get("next") or "").strip()
#     if nxt and url_has_allowed_host_and_scheme(
#         url=nxt,
#         allowed_hosts={request.get_host()},
#         require_https=request.is_secure(),
#     ):
#         return nxt
#     return ""


# def login_view(request):
#     if request.user.is_authenticated:
#         messages.info(request, _("Vous êtes déjà connecté."))
#         return redirect("dashboard:hub")

#     auth_pole = _resolve_auth_pole(request)  # social|economic|generic
#     next_url = _safe_next(request)           # "" ou url safe
#     request_path = request.path or ""

#     # Pour les templates : pole doit être "" ou social/economic (pas "generic")
#     pole = auth_pole if auth_pole in ("social", "economic") else ""

#     # Auth form (Django standard)
#     form = CustomLoginForm(request, data=request.POST or None)

#     if request.method == "POST":
#         if form.is_valid():
#             user = form.get_user()

#             if not user.is_active:
#                 messages.error(
#                     request,
#                     _(
#                         "Votre compte n'est pas encore activé. "
#                         "Vérifiez votre e-mail ou contactez l’administrateur."
#                     ),
#                 )
#             else:
#                 login(request, user)

#                 # remember_me optionnel
#                 remember = bool(form.cleaned_data.get("remember_me", False))
#                 request.session.set_expiry(None if remember else 0)

#                 # Redirection : next_url si fourni, sinon hub
#                 return redirect(next_url or reverse("dashboard:hub"))
#         else:
#             messages.error(request, _("Identifiants invalides. Veuillez réessayer."))

#     return render(
#         request,
#         "accounts_users/auth/login.html",
#         {
#             # ✅ anciens templates
#             "form": form,
#             "next": next_url,
#             "auth_pole": auth_pole,
#             "login_context": auth_pole,

#             # ✅ nouveaux templates (robustes, sans request.GET.*)
#             "pole": pole,
#             "next_url": next_url,
#             "request_path": request_path,
#         },
#     )


# def logout_view(request):
#     logout(request)
#     messages.success(request, _("Vous avez été déconnecté avec succès."))

#     # supporte les 2 noms possibles
#     return redirect(
#         _reverse_first(
#             "accounts_users:web:auth:choice",
#             "accounts_users:web:auth:auth_choice",
#             fallback="/",
#         )
#     )







# # accounts_users/web/views/auth_login_web_views.py
# from __future__ import annotations

# from django.contrib import messages
# from django.contrib.auth import login, logout
# from django.shortcuts import redirect, render
# from django.urls import reverse
# from django.utils.http import url_has_allowed_host_and_scheme
# from django.utils.translation import gettext_lazy as _

# from accounts_users.forms.login_forms import CustomLoginForm


# def _resolve_auth_pole(request) -> str:
#     qp = (request.GET.get("context") or request.POST.get("context") or "").strip().lower()
#     if qp in ("social", "economic", "generic"):
#         return qp

#     path = (request.path or "").lower()
#     if "/login/social" in path:
#         return "social"
#     if "/login/economic" in path:
#         return "economic"

#     return "generic"


# def _safe_next(request) -> str:
#     nxt = (request.POST.get("next") or request.GET.get("next") or "").strip()
#     if nxt and url_has_allowed_host_and_scheme(
#         url=nxt,
#         allowed_hosts={request.get_host()},
#         require_https=request.is_secure(),
#     ):
#         return nxt
#     return reverse("dashboard:hub")


# def login_view(request):
#     if request.user.is_authenticated:
#         messages.info(request, _("Vous êtes déjà connecté."))
#         return redirect("dashboard:hub")

#     auth_pole = _resolve_auth_pole(request)
#     next_url = _safe_next(request)

#     form = CustomLoginForm(request, data=request.POST or None)

#     if request.method == "POST":
#         if form.is_valid():
#             user = form.get_user()

#             if not user.is_active:
#                 messages.error(
#                     request,
#                     _(
#                         "Votre compte n'est pas encore activé. "
#                         "Vérifiez votre e-mail ou contactez l’administrateur."
#                     ),
#                 )
#             else:
#                 login(request, user)

#                 remember = form.cleaned_data.get("remember_me", False)
#                 request.session.set_expiry(None if remember else 0)

#                 return redirect(next_url)
#         else:
#             messages.error(request, _("Identifiants invalides. Veuillez réessayer."))

#     return render(
#         request,
#         "accounts_users/auth/login.html",
#         {
#             "form": form,
#             "next": next_url,
#             "auth_pole": auth_pole,
#             "login_context": auth_pole,
#         },
#     )


# def logout_view(request):
#     logout(request)
#     messages.success(request, _("Vous avez été déconnecté avec succès."))
#     return redirect("accounts_users:web:auth:auth_choice")





# # accounts_users/web/views/auth_login_web_views.py
# from __future__ import annotations

# from django.contrib import messages
# from django.contrib.auth import login, logout
# from django.shortcuts import redirect, render
# from django.urls import reverse
# from django.utils.http import url_has_allowed_host_and_scheme
# from django.utils.translation import gettext_lazy as _

# from accounts_users.forms.login_forms import CustomLoginForm


# def _resolve_auth_pole(request) -> str:
#     """
#     Déduit le pôle d'auth:
#     1) ?context=social|economic|generic
#     2) chemin URL (…/login/social/ ou …/login/economic/)
#     3) fallback generic
#     """
#     qp = (request.GET.get("context") or "").strip().lower()
#     if qp in ("social", "economic", "generic"):
#         return qp

#     path = (request.path or "").lower()
#     if "/login/social" in path:
#         return "social"
#     if "/login/economic" in path:
#         return "economic"

#     return "generic"


# def _safe_next(request) -> str:
#     """
#     Sécurise next pour éviter open redirect.
#     Fallback -> dashboard:hub
#     """
#     nxt = (request.POST.get("next") or request.GET.get("next") or "").strip()
#     if nxt and url_has_allowed_host_and_scheme(
#         url=nxt,
#         allowed_hosts={request.get_host()},
#         require_https=request.is_secure(),
#     ):
#         return nxt
#     return reverse("dashboard:hub")


# def login_view(request):
#     """
#     Vue de connexion UI (unique).
#     - Un seul formulaire
#     - Supporte ?next=
#     - Supporte ?context=social|economic|generic
#     - Supporte /login/social/ et /login/economic/ sans querystring
#     """
#     if request.user.is_authenticated:
#         messages.info(request, _("Vous êtes déjà connecté."))
#         return redirect("dashboard:hub")

#     auth_pole = _resolve_auth_pole(request)
#     next_url = _safe_next(request)

#     form = CustomLoginForm(request, data=request.POST or None)

#     if request.method == "POST":
#         if form.is_valid():
#             user = form.get_user()

#             if not user.is_active:
#                 messages.error(
#                     request,
#                     _(
#                         "Votre compte n'est pas encore activé. "
#                         "Vérifiez votre e-mail ou contactez l’administrateur."
#                     ),
#                 )
#             else:
#                 login(request, user)

#                 remember = form.cleaned_data.get("remember_me", False)
#                 request.session.set_expiry(None if remember else 0)

#                 return redirect(next_url)
#         else:
#             messages.error(request, _("Identifiants invalides. Veuillez réessayer."))

#     return render(
#         request,
#         "accounts_users/auth/login.html",
#         {
#             "form": form,
#             "next": next_url,
#             "auth_pole": auth_pole,
#             "login_context": auth_pole,
#         },
#     )


# def logout_view(request):
#     logout(request)
#     messages.success(request, _("Vous avez été déconnecté avec succès."))
#     return redirect("accounts_users:web:auth:login")






# # accounts_users/web/views/auth_web_views.py 12-01-2026
# from __future__ import annotations

# from django.contrib import messages
# from django.contrib.auth import login, logout
# from django.shortcuts import render, redirect
# from django.urls import reverse
# from django.utils.http import url_has_allowed_host_and_scheme
# from django.utils.translation import gettext_lazy as _

# from accounts_users.forms.login_forms import CustomLoginForm


# def _resolve_auth_pole(request) -> str:
#     """
#     Déduit le pôle d'auth:
#     1) ?context=social|economic|generic
#     2) chemin URL (…/login/social/ ou …/login/economic/)
#     3) fallback generic
#     """
#     qp = (request.GET.get("context") or "").strip().lower()
#     if qp in ("social", "economic", "generic"):
#         return qp

#     path = (request.path or "").lower()
#     if "/login/social" in path:
#         return "social"
#     if "/login/economic" in path:
#         return "economic"

#     return "generic"


# def _safe_next(request) -> str:
#     """
#     Sécurise next pour éviter open redirect.
#     Fallback -> dashboard:hub
#     """
#     nxt = (request.POST.get("next") or request.GET.get("next") or "").strip()
#     if nxt and url_has_allowed_host_and_scheme(
#         url=nxt,
#         allowed_hosts={request.get_host()},
#         require_https=request.is_secure(),
#     ):
#         return nxt
#     return reverse("dashboard:hub")


# def login_view(request):
#     """
#     Vue de connexion UI (unique).
#     - Un seul formulaire
#     - Supporte ?next=
#     - Supporte ?context=social|economic|generic
#     - Supporte /login/social/ et /login/economicS/conomic/ sans querystring
#     - Redirige vers dashboard hub après succès
#     """
#     if request.user.is_authenticated:
#         messages.info(request, _("Vous êtes déjà connecté."))
#         return redirect("dashboard:hub")

#     auth_pole = _resolve_auth_pole(request)
#     next_url = _safe_next(request)

#     form = CustomLoginForm(request, data=request.POST or None)

#     if request.method == "POST":
#         if form.is_valid():
#             user = form.get_user()

#             if not user.is_active:
#                 messages.error(
#                     request,
#                     _(
#                         "Votre compte n'est pas encore activé. "
#                         "Vérifiez votre e-mail ou contactez l’administrateur."
#                     ),
#                 )
#             else:
#                 login(request, user)

#                 remember = form.cleaned_data.get("remember_me", False)
#                 request.session.set_expiry(None if remember else 0)

#                 return redirect(next_url)

#         else:
#             messages.error(request, _("Identifiants invalides. Veuillez réessayer."))

#     return render(
#         request,
#         "accounts_users/registration/login.html",
#         {
#             "form": form,
#             "next": next_url,
#             "auth_pole": auth_pole,         # ✅ pour BG
#             "login_context": auth_pole,     # ✅ optionnel mais pratique
#         },
#     )


# def logout_view(request):
#     logout(request)
#     messages.success(request, _("Vous avez été déconnecté avec succès."))
#     return redirect("accounts_users_web:login")









# # accounts_users/web/views/auth_web_views.py
# from django.contrib import messages
# from django.contrib.auth import login, logout
# from django.shortcuts import render, redirect
# from django.urls import reverse
# from django.utils.translation import gettext_lazy as _

# from accounts_users.forms.login_forms import CustomLoginForm


# def login_view(request):
#     """
#     Vue de connexion UI (unique).
#     - Un seul formulaire
#     - Supporte ?next=
#     - Supporte ?context=social|economic|generic
#     - Redirige vers dashboard hub après succès
#     """

#     # Déjà connecté → dashboard hub
#     if request.user.is_authenticated:
#         messages.info(request, _("Vous êtes déjà connecté."))
#         return redirect("dashboard:hub")

#     # Contexte UX (UNIQUEMENT visuel)
#     auth_pole = request.GET.get("context", "generic")
#     if auth_pole not in ("social", "economic", "generic"):
#         auth_pole = "generic"

#     # URL de redirection après login
#     next_url = (
#         request.POST.get("next")
#         or request.GET.get("next")
#         or reverse("dashboard:hub")
#     )

#     form = CustomLoginForm(request, data=request.POST or None)

#     if request.method == "POST":
#         if form.is_valid():
#             user = form.get_user()

#             if not user.is_active:
#                 messages.error(
#                     request,
#                     _(
#                         "Votre compte n'est pas encore activé. "
#                         "Vérifiez votre e-mail ou contactez l’administrateur."
#                     ),
#                 )
#             else:
#                 login(request, user)

#                 # Remember me (sécurisé)
#                 remember = form.cleaned_data.get("remember_me", False)
#                 request.session.set_expiry(None if remember else 0)

#                 return redirect(next_url)
#         else:
#             messages.error(request, _("Identifiants invalides. Veuillez réessayer."))

#     return render(
#         request,
#         "accounts_users/registration/login.html",
#         {
#             "form": form,
#             "next": next_url,
#             "auth_pole": auth_pole,
#         },
#     )


# def logout_view(request):
#     """
#     Déconnexion utilisateur (UI).
#     """
#     logout(request)
#     messages.success(request, _("Vous avez été déconnecté avec succès."))
#     return redirect("accounts_users_web:login")







# # accounts_users/web/views/auth_web_views.py
# from django.contrib import messages
# from django.contrib.auth import login, logout
# from django.shortcuts import render, redirect
# from django.urls import reverse
# from django.utils.translation import gettext_lazy as _

# from accounts_users.forms.login_forms import LoginForm


# def login_view(request):
#     """
#     Vue de connexion UI (unique).
#     - Un seul formulaire
#     - Supporte ?next=
#     - Supporte ?context=social|economic|generic
#     - Redirige vers dashboard hub après succès
#     """

#     # Déjà connecté → dashboard hub
#     if request.user.is_authenticated:
#         messages.info(request, _("Vous êtes déjà connecté."))
#         return redirect("dashboard:hub")

#     # Contexte UX (PAS métier)
#     auth_pole = request.GET.get("context", "generic")

#     # URL de redirection après login
#     next_url = (
#         request.POST.get("next")
#         or request.GET.get("next")
#         or reverse("dashboard:hub")
#     )

#     form = LoginForm(request, data=request.POST or None)

#     if request.method == "POST":
#         if form.is_valid():
#             user = form.get_user()

#             if not user.is_active:
#                 messages.error(
#                     request,
#                     _(
#                         "Votre compte n'est pas encore activé. "
#                         "Vérifiez votre e-mail ou contactez l’administrateur."
#                     ),
#                 )
#             else:
#                 login(request, user)

#                 # Remember me
#                 remember = form.cleaned_data.get("remember_me")
#                 request.session.set_expiry(None if remember else 0)

#                 return redirect(next_url)

#         messages.error(request, _("Identifiants invalides. Veuillez réessayer."))

#     return render(
#         request,
#         "accounts_users/registration/login.html",
#         {
#             "form": form,
#             "next": next_url,
#             "auth_pole": auth_pole,
#         },
#     )


# def logout_view(request):
#     """
#     Déconnexion utilisateur (UI).
#     """
#     logout(request)
#     messages.success(request, _("Vous avez été déconnecté avec succès."))
#     return redirect("accounts_users_web:login")











# # accounts_users/web/views/auth_web_views.py
# from django.contrib import messages
# from django.contrib.auth import login, logout
# from django.shortcuts import render, redirect
# from django.urls import reverse
# from django.utils.translation import gettext_lazy as _

# from accounts_users.forms.login_forms import LoginForm


# def login_view(request):
#     """
#     Vue de connexion UI.
#     - Gère login
#     - Respecte ?next=
#     - Redirige TOUJOURS vers le dashboard hub par défaut
#     - Différencie les contextes : social, economic, generic
#     """

#     # Déjà connecté → dashboard
#     if request.user.is_authenticated:
#         messages.info(request, _("Vous êtes déjà connecté."))
#         return redirect("dashboard:hub")

#     # URL de redirection après login
#     next_url = (
#         request.POST.get("next")
#         or request.GET.get("next")
#         or reverse("dashboard:hub")
#     )

#     # Déterminer le contexte pour adapter le template/UI
#     if request.path.endswith("/social/"):
#         login_context = "social"
#     elif request.path.endswith("/economic/"):
#         login_context = "economic"
#     else:
#         login_context = "generic"

#     form = LoginForm(request, data=request.POST or None)

#     if request.method == "POST":
#         if form.is_valid():
#             user = form.get_user()

#             if not user.is_active:
#                 messages.error(
#                     request,
#                     _(
#                         "Votre compte n'est pas encore activé. "
#                         "Vérifiez votre e-mail ou contactez l’administrateur."
#                     ),
#                 )
#                 return render(
#                     request,
#                     "accounts_users/registration/login.html",
#                     {"form": form, "next": next_url, "login_context": login_context},
#                 )

#             # Connexion
#             login(request, user)

#             # Gestion du "remember me"
#             remember = form.cleaned_data.get("remember_me")
#             request.session.set_expiry(None if remember else 0)

#             return redirect(next_url)

#         messages.error(request, _("Identifiants invalides. Veuillez réessayer."))

#     return render(
#         request,
#         "accounts_users/registration/login.html",
#         {"form": form, "next": next_url, "login_context": login_context},
#     )


# def logout_view(request):
#     """
#     Déconnexion utilisateur (UI).
#     """
#     logout(request)
#     messages.success(request, _("Vous avez été déconnecté avec succès."))
#     return redirect("accounts_users_web:login")





# # accounts_users/web/views/auth_web_views.py
# from django.contrib import messages
# from django.contrib.auth import login, logout
# from django.shortcuts import render, redirect
# from django.urls import reverse
# from django.utils.translation import gettext_lazy as _

# from accounts_users.forms.login_forms import LoginForm


# def login_view(request):
#     """
#     Vue de connexion UI.
#     - Gère login
#     - Respecte ?next=
#     - Redirige TOUJOURS vers le dashboard hub par défaut
#     """

#     # Déjà connecté → dashboard
#     if request.user.is_authenticated:
#         messages.info(request, _("Vous êtes déjà connecté."))
#         return redirect("dashboard:hub")

#     # URL de redirection après login
#     next_url = (
#         request.POST.get("next")
#         or request.GET.get("next")
#         or reverse("dashboard:hub")
#     )

#     form = LoginForm(request, data=request.POST or None)

#     if request.method == "POST":

#         if form.is_valid():
#             user = form.get_user()

#             if not user.is_active:
#                 messages.error(
#                     request,
#                     _(
#                         "Votre compte n'est pas encore activé. "
#                         "Vérifiez votre e-mail ou contactez l’administrateur."
#                     )
#                 )
#                 return render(
#                     request,
#                     "accounts_users/registration/login.html",
#                     {"form": form, "next": next_url},
#                 )

#             # Connexion
#             login(request, user)

#             # Gestion du "remember me"
#             remember = form.cleaned_data.get("remember_me")
#             if remember:
#                 request.session.set_expiry(None)   # session persistante
#             else:
#                 request.session.set_expiry(0)      # session navigateur

#             return redirect(next_url)

#         messages.error(request, _("Identifiants invalides. Veuillez réessayer."))

#     return render(
#         request,
#         "accounts_users/registration/login.html",
#         {
#             "form": form,
#             "next": next_url,
#         },
#     )


# def logout_view(request):
#     """
#     Déconnexion utilisateur (UI).
#     """
#     logout(request)
#     messages.success(request, _("Vous avez été déconnecté avec succès."))
#     return redirect("accounts_users_web:login")





# # accounts_users/web/views/auth_web_views.py
# from django.contrib import messages
# from django.contrib.auth import login, logout
# from django.shortcuts import render, redirect
# from django.urls import reverse
# from django.utils.translation import gettext_lazy as _

# from accounts_users.forms.login_forms import LoginForm


# def _i18n_reverse(name, request, **kwargs):
#     """
#     Génère une URL locale dans le namespace linguistique courant.
#     """
#     return reverse(name, kwargs=kwargs or None)


# def login_view(request):
#     """
#     Version fonctionnelle : la seule réellement utilisée dans l'UI.
#     Gère template, messages, redirection, remember_me.
#     """

#     if request.user.is_authenticated:
#         messages.info(request, _("Vous êtes déjà connecté."))
#         return redirect(_i18n_reverse("dashboard:index", request))

#     next_url = (
#         request.POST.get("next")
#         or request.GET.get("next")
#         or _i18n_reverse("dashboard:index", request)
#     )

#     form = LoginForm(request, data=request.POST or None)

#     if request.method == "POST":
#         if form.is_valid():
#             user = form.get_user()

#             if not user.is_active:
#                 messages.error(
#                     request,
#                     _("Votre compte n'est pas encore activé. Vérifiez votre e-mail ou contactez l’administrateur.")
#                 )
#                 return render(request, "accounts_users/registration/login.html", {"form": form, "next": next_url})

#             login(request, user)

#             # Gestion "remember me"
#             remember = getattr(form, "cleaned_data", {}).get("remember_me")
#             if remember is True:
#                 request.session.set_expiry(None)
#             elif remember is False:
#                 request.session.set_expiry(0)

#             return redirect(next_url)

#         else:
#             messages.error(request, _("Identifiants invalides. Veuillez réessayer."))

#     return render(request, "accounts_users/registration/login.html", {
#         "form": form,
#         "next": request.GET.get("next", ""),
#     })


# def logout_view(request):
#     """
#     Déconnexion via UI utilisateur.
#     """
#     logout(request)
#     messages.success(request, _("Vous avez été déconnecté avec succès."))
#     return redirect(_i18n_reverse("accounts_users_web:login", request))






# # accounts_users/web/views/auth_web_views.py
# from django.contrib import messages
# from django.contrib.auth import login, logout
# from django.shortcuts import render, redirect
# from django.urls import reverse
# from django.utils.translation import gettext_lazy as _

# from accounts_users.forms.login_forms import LoginForm
# # from accounts_users.forms.auth_forms import AuthenticationEmailForm  # si e-mail

# def _i18n_reverse(name, request, **kwargs):
#     return reverse(name, kwargs=kwargs or None)

# def login_view(request):
#     if request.user.is_authenticated:
#         messages.info(request, _("Vous êtes déjà connecté."))
#         return redirect(_i18n_reverse("dashboard:home", request))

#     # next: priorité POST > GET > fallback
#     next_url = request.POST.get("next") or request.GET.get("next") or _i18n_reverse("dashboard:home", request)

#     # Choisis le form réellement utilisé :
#     form = LoginForm(request, data=request.POST or None)
#     # form = AuthenticationEmailForm(request=request, data=request.POST or None)

#     if request.method == "POST":
#         if form.is_valid():
#             user = form.get_user()
#             if not user.is_active:
#                 messages.error(
#                     request,
#                     _("Votre compte n'est pas encore activé. Vérifiez votre e-mail ou contactez l’administrateur.")
#                 )
#                 return render(request, "accounts_users/registration/login.html", {"form": form, "next": next_url})

#             login(request, user)

#             # Se souvenir de moi si présent
#             remember = getattr(form, "cleaned_data", {}).get("remember_me")
#             if remember is True:
#                 request.session.set_expiry(None)
#             elif remember is False:
#                 request.session.set_expiry(0)

#             return redirect(next_url)
#         else:
#             messages.error(request, _("Identifiants invalides. Veuillez réessayer."))

#     return render(request, "accounts_users/registration/login.html", {
#         "form": form,
#         "next": request.GET.get("next", ""),  # pour le template
#     })


# def logout_view(request):
#     logout(request)
#     messages.success(request, _("Vous avez été déconnecté avec succès."))
#     return redirect(_i18n_reverse("accounts_users_web:login", request))








# # accounts_users/web/views/auth_web_views.py
# from django.contrib.auth import login, logout
# from django.shortcuts import render, redirect
# from django.utils.translation import gettext_lazy as _
# from django.contrib import messages
# from accounts_users.forms.login_forms import LoginForm

# def login_view(request):
#     if request.user.is_authenticated:
#         messages.info(request, _("Vous êtes déjà connecté."))
#         return redirect("dashboard:index")

#     # Toujours tenir compte du "next" en GET ou POST
#     next_url = request.POST.get("next") or request.GET.get("next") or "dashboard:index"
#     form = LoginForm(data=request.POST or None)

#     if request.method == "POST":
#         if form.is_valid():
#             user = form.get_user()
#             if not user.is_active:
#                 messages.error(request, _("Votre compte n'est pas encore activé. Vérifiez votre email ou contactez l’administrateur."))
#                 return render(request, "accounts_users/registration/login.html", {"form": form, "next": next_url})
#             login(request, user)
#             return redirect(next_url)
#         else:
#             messages.error(request, _("Identifiants invalides. Veuillez réessayer."))

#     context = {
#         "form": form,
#         "next": request.GET.get("next", ""),  # Pour le template, priorité au GET (ex : accès direct à /login?next=...)
#     }
#     return render(request, "accounts_users/registration/login.html", context)


# def logout_view(request):
#     logout(request)
#     messages.success(request, _("Vous avez été déconnecté avec succès."))
#     return redirect("accounts_users_web:login")












# from django.contrib.auth import login, logout
# from django.shortcuts import render, redirect
# from accounts_users.forms.login_forms import LoginForm
# from django.utils.translation import gettext_lazy as _

# def login_view(request):
#     form = LoginForm(data=request.POST or None)

#     if request.method == "POST" and form.is_valid():
#         user = form.get_user()
#         login(request, user)

#         next_url = request.GET.get("next") or "dashboard:index"
#         return redirect(next_url)

#     return render(request, "accounts_users/registration/login.html", {"form": form})


# def logout_view(request):
#     logout(request)
#     return redirect("accounts_users_web:login")




# #accounts_users/web/views/auth_web_views.py
# from django.contrib.auth import login, logout, authenticate
# from django.shortcuts import render, redirect
# # from accounts_users.forms.login_forms import CustomLoginForm
# from accounts_users.forms.login_forms import LoginForm

# def login_view(request):
#     # form = CustomLoginForm(data=request.POST or None)
#     form = LoginForm(data=request.POST or None)

#     if request.method == "POST" and form.is_valid():
#         user = form.get_user()
#         login(request, user)
#         return redirect('dashboard:index')
#     return render(request, "accounts_users/registration/login.html", {"form": form})


# def logout_view(request):
#     logout(request)
#     return redirect("accounts_users_web:login")

