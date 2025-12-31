# accounts_users/views/auth.py
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from accounts_users.forms.login_forms import CustomLoginForm


def _i18n_reverse(name, request, **kwargs):
    """
    Convertit un nom de vue en URL tenant compte du namespace linguistique.
    (Dans ton projet : /fr/... ou /en/...)
    """
    return reverse(name, kwargs=kwargs or None)


class WebLoginCBV(LoginView):
    """
    Version class-based de la connexion (rarement utilisée par toi,
    car tu préfères une vue fonctionnelle → auth_web_views.py).
    Gardée pour API, tests, futur usage.
    """

    template_name = "accounts_users/registration/login.html"
    authentication_form = CustomLoginForm
    redirect_authenticated_user = True

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.setdefault("request", self.request)
        return kwargs

    def form_valid(self, form):
        user = form.get_user()

        if not user.is_active:
            messages.error(self.request, _("Votre compte n'est pas encore activé."))
            return self.form_invalid(form)

        login(self.request, user)

        remember = getattr(form, "cleaned_data", {}).get("remember_me")
        if remember is True:
            self.request.session.set_expiry(None)  # durée normale
        elif remember is False:
            self.request.session.set_expiry(0)     # expire à fermeture

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        nxt = self.request.POST.get("next") or self.request.GET.get("next")
        return nxt or _i18n_reverse("dashboard:index", self.request)


class WebLogoutCBV(LogoutView):
    """
    Déconnexion propre, sans template.
    """

    def get_next_page(self):
        return _i18n_reverse("accounts_users_web:login", self.request)






# # accounts_users/views/auth.py
# from django.contrib import messages
# from django.contrib.auth import login
# from django.contrib.auth.views import LoginView, LogoutView
# from django.http import HttpResponseRedirect
# from django.urls import reverse
# from django.utils.translation import gettext_lazy as _

# from accounts_users.forms.login_forms import CustomLoginForm
# # from accounts_users.forms.auth_forms import AuthenticationEmailForm  # si tu veux login via e-mail

# def _i18n_reverse(name, request, **kwargs):
#     return reverse(name, kwargs=kwargs or None)

# class WebLoginCBV(LoginView):
#     template_name = "accounts_users/registration/login.html"
#     authentication_form = CustomLoginForm          # ou AuthenticationEmailForm
#     redirect_authenticated_user = True

#     def get_form_kwargs(self):
#         kw = super().get_form_kwargs()
#         kw.setdefault("request", self.request)     # utile pour certains forms
#         return kw

#     def form_valid(self, form):
#         user = form.get_user()
#         if not user.is_active:
#             messages.error(self.request, _("Votre compte n'est pas encore activé."))
#             return self.form_invalid(form)

#         login(self.request, user)

#         remember = getattr(form, "cleaned_data", {}).get("remember_me")
#         if remember is True:
#             self.request.session.set_expiry(None)  # utilise SESSION_COOKIE_AGE
#         elif remember is False:
#             self.request.session.set_expiry(0)     # expire à la fermeture

#         return HttpResponseRedirect(self.get_success_url())

#     def get_success_url(self):
#         nxt = self.request.POST.get("next") or self.request.GET.get("next")
#         return nxt or _i18n_reverse("dashboard:home", self.request)


# class WebLogoutCBV(LogoutView):
#     def get_next_page(self):
#         return _i18n_reverse("accounts_users_web:login", self.request)





# # accounts_users/views/auth.py 
# from django.contrib.auth import authenticate, login, logout
# from django.shortcuts import render, redirect
# from django.contrib import messages
# from django.utils.translation import gettext_lazy as _
# from django.contrib.auth.views import LoginView, LogoutView

# from accounts_users.forms.auth_forms import LoginForm
# from accounts_users.forms.login_forms import CustomLoginForm

# def login_view(request):
#     if request.user.is_authenticated:
#         return redirect('dashboard:index')  # Redirige l'utilisateur déjà connecté

#     if request.method == "POST":
#         form = LoginForm(request, data=request.POST)
#         if form.is_valid():
#             user = form.get_user()
#             if not user.is_active:
#                 messages.error(request, _("Votre compte n'est pas encore activé."))
#                 return render(request, "accounts_users/registration/login.html", {"form": form})
#             login(request, user)
#             return redirect('dashboard:index')
#         else:
#             messages.error(request, _("Identifiants invalides."))
#     else:
#         form = LoginForm()

#     return render(request, "accounts_users/registration/login.html", {"form": form})


# def logout_view(request):
#     logout(request)
#     return redirect("accounts_users_web:login")  # Namespace correct pour la vue login


# class CustomLoginView(LoginView):
#     authentication_form = CustomLoginForm  # Django >= 4.x préfère authentication_form à form_class
#     template_name = 'accounts_users/registration/login.html'


# class CustomLogoutView(LogoutView):
#     next_page = 'accounts_users_web:login'  # Namespace correct pour la vue login





# from django.contrib.auth import authenticate, login, logout
# from django.shortcuts import render, redirect
# from django.contrib import messages
# from django.utils.translation import gettext_lazy as _
# from django.contrib.auth.views import LoginView, LogoutView

# from accounts_users.forms.auth_forms import LoginForm
# from accounts_users.forms.login_forms import CustomLoginForm


# def login_view(request):
#     if request.user.is_authenticated:
#         return redirect('dashboard:index')

#     if request.method == "POST":
#         form = LoginForm(request, data=request.POST)
#         if form.is_valid():
#             user = form.get_user()
#             login(request, user)
#             return redirect('dashboard:index')
#         else:
#             messages.error(request, _("Identifiants invalides."))
#     else:
#         form = LoginForm()

#     return render(request, "accounts_users/registration/login.html", {"form": form})


# def logout_view(request):
#     logout(request)
#     return redirect("accounts_users_web:login")


# class CustomLoginView(LoginView):
#     form_class = CustomLoginForm
#     template_name = 'accounts_users/registration/login.html'


# class CustomLogoutView(LogoutView):
#     next_page = 'accounts_users:login'



# accounts_users/views/auth.py 01/07 
# from django.contrib.auth.views import LoginView, LogoutView
# from accounts_users.forms.login_forms import CustomLoginForm

# class CustomLoginView(LoginView):
#     form_class = CustomLoginForm
#     template_name = 'accounts_users/registration/login.html'


# class CustomLogoutView(LogoutView):
#     next_page = 'accounts_users:login'
