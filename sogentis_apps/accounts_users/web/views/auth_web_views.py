# accounts_users/web/views/auth_web_views.py
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from accounts_users.forms.login_forms import LoginForm
from django.utils.translation import gettext_lazy as _

def login_view(request):
    form = LoginForm(data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)

        next_url = request.GET.get("next") or "dashboard:index"
        return redirect(next_url)

    return render(request, "accounts_users/registration/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("accounts_users_web:login")




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

