from django.contrib import messages
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from accounts_users.forms.login_forms import LoginForm


def login_view(request):
    """
    Vue de connexion UI (unique).
    - Un seul formulaire
    - Supporte ?next=
    - Supporte ?context=social|economic|generic
    - Redirige vers dashboard hub après succès
    """

    # Déjà connecté → dashboard hub
    if request.user.is_authenticated:
        messages.info(request, _("Vous êtes déjà connecté."))
        return redirect("dashboard:hub")

    # Contexte UX (UNIQUEMENT visuel)
    auth_pole = request.GET.get("context", "generic")
    if auth_pole not in ("social", "economic", "generic"):
        auth_pole = "generic"

    # URL de redirection après login
    next_url = (
        request.POST.get("next")
        or request.GET.get("next")
        or reverse("dashboard:hub")
    )

    form = LoginForm(request, data=request.POST or None)

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

                # Remember me (sécurisé)
                remember = form.cleaned_data.get("remember_me", False)
                request.session.set_expiry(None if remember else 0)

                return redirect(next_url)
        else:
            messages.error(request, _("Identifiants invalides. Veuillez réessayer."))

    return render(
        request,
        "accounts_users/registration/login.html",
        {
            "form": form,
            "next": next_url,
            "auth_pole": auth_pole,
        },
    )


def logout_view(request):
    """
    Déconnexion utilisateur (UI).
    """
    logout(request)
    messages.success(request, _("Vous avez été déconnecté avec succès."))
    return redirect("accounts_users_web:login")







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

