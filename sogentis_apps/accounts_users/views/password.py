# accounts_users/views/password.py 
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _


@login_required
def password_change_view(request):
    if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, _("Votre mot de passe a été changé avec succès."))
            return redirect("dashboard:profile")
        else:
            messages.error(request, _("Veuillez corriger les erreurs."))
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, "accounts_users/registration/password_change.html", {"form": form})




## accounts_users/views/password.py -> 01/07
# from django.contrib.auth.views import (
#     PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView,
#     PasswordChangeView, PasswordChangeDoneView
# )
# from accounts_users.forms.password_forms import (
#     CustomPasswordResetForm, CustomSetPasswordForm, CustomPasswordChangeForm
# )

# # --- Reset password (oubli) ---
# class CustomPasswordResetView(PasswordResetView):
#     template_name = 'accounts_users/registration/password_reset.html'
#     form_class = CustomPasswordResetForm
#     email_template_name = 'accounts_users/registration/password_reset_email.html'
#     subject_template_name = 'accounts_users/registration/password_reset_subject.txt'
#     success_url = '/accounts/password-reset/done/'


# class CustomPasswordResetDoneView(PasswordResetDoneView):
#     template_name = 'accounts_users/registration/password_reset_done.html'


# class CustomPasswordResetConfirmView(PasswordResetConfirmView):
#     template_name = 'accounts_users/registration/password_reset_confirm.html'
#     form_class = CustomSetPasswordForm
#     success_url = '/accounts/password-reset/complete/'


# class CustomPasswordResetCompleteView(PasswordResetCompleteView):
#     template_name = 'accounts_users/registration/password_reset_complete.html'

# # --- Changement de mot de passe connecté ---
# class CustomPasswordChangeView(PasswordChangeView):
#     template_name = 'accounts_users/registration/password_change.html'
#     form_class = CustomPasswordChangeForm
#     success_url = '/accounts/password-change/done/'


# class CustomPasswordChangeDoneView(PasswordChangeDoneView):
#     template_name = 'accounts_users/registration/password_change_done.html'
