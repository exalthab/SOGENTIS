# accounts_users/web/views/auth_web_views.py
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from accounts_users.forms.login_forms import LoginForm

def login_view(request):
    if request.user.is_authenticated:
        messages.info(request, _("Vous êtes déjà connecté."))
        return redirect("dashboard:index")

    # Toujours tenir compte du "next" en GET ou POST
    next_url = request.POST.get("next") or request.GET.get("next") or "dashboard:index"
    form = LoginForm(data=request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            user = form.get_user()
            if not user.is_active:
                messages.error(request, _("Votre compte n'est pas encore activé. Vérifiez votre email ou contactez l’administrateur."))
                return render(request, "accounts_users/registration/login.html", {"form": form, "next": next_url})
            login(request, user)
            return redirect(next_url)
        else:
            messages.error(request, _("Identifiants invalides. Veuillez réessayer."))

    context = {
        "form": form,
        "next": request.GET.get("next", ""),  # Pour le template, priorité au GET (ex : accès direct à /login?next=...)
    }
    return render(request, "accounts_users/registration/login.html", context)


def logout_view(request):
    logout(request)
    messages.success(request, _("Vous avez été déconnecté avec succès."))
    return redirect("accounts_users_web:login")












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

