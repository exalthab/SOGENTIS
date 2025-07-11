# accounts_users/views/auth.py 
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.views import LoginView, LogoutView

from accounts_users.forms.auth_forms import LoginForm
from accounts_users.forms.login_forms import CustomLoginForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard:index')
        else:
            messages.error(request, _("Identifiants invalides."))
    else:
        form = LoginForm()

    return render(request, "accounts_users/registration/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("accounts_users_web:login")


class CustomLoginView(LoginView):
    form_class = CustomLoginForm
    template_name = 'accounts_users/registration/login.html'


class CustomLogoutView(LogoutView):
    next_page = 'accounts_users:login'



# accounts_users/views/auth.py 01/07 
# from django.contrib.auth.views import LoginView, LogoutView
# from accounts_users.forms.login_forms import CustomLoginForm

# class CustomLoginView(LoginView):
#     form_class = CustomLoginForm
#     template_name = 'accounts_users/registration/login.html'


# class CustomLogoutView(LogoutView):
#     next_page = 'accounts_users:login'
