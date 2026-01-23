# accounts_users/views/password.py
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy
from django.contrib.auth.views import (
    PasswordResetView, PasswordResetConfirmView, PasswordResetDoneView,
    PasswordResetCompleteView, PasswordChangeView, PasswordChangeDoneView
)

from accounts_users.forms.password_forms import (
    CustomPasswordResetForm, CustomSetPasswordForm, CustomPasswordChangeForm
)


# ==================================================================
# 1. LOGIQUE : changement de mot de passe utilisateur connecté
# ==================================================================

@login_required
def change_password_logic(request):
    """
    Retourne (form, success: bool)
    Ne rend pas de template.
    """
    if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return form, True
        return form, False

    return PasswordChangeForm(user=request.user), None


# ==================================================================
# 2. CLASSES D'API (sans messages, sans UI)
# ==================================================================

class PasswordResetLogicView(PasswordResetView):
    form_class = CustomPasswordResetForm
    email_template_name = "accounts_users/registration/password_reset_email.html"
    subject_template_name = "accounts_users/registration/password_reset_subject.txt"
    success_url = reverse_lazy('accounts_users:web:password_reset_done')
    template_name = "accounts_users/registration/password_reset_form.html"


class PasswordResetDoneLogicView(PasswordResetDoneView):
    template_name = "accounts_users/registration/password_reset_done.html"


class PasswordResetConfirmLogicView(PasswordResetConfirmView):
    form_class = CustomSetPasswordForm
    success_url = reverse_lazy('accounts_users:web:password_reset_complete')
    template_name = "accounts_users/registration/password_reset_confirm.html"


class PasswordResetCompleteLogicView(PasswordResetCompleteView):
    template_name = "accounts_users/registration/password_reset_complete.html"


class PasswordChangeLogicView(PasswordChangeView):
    form_class = CustomPasswordChangeForm
    template_name = "accounts_users/registration/password_change_form.html"
    success_url = reverse_lazy('accounts_users:web:password_change_done')


class PasswordChangeDoneLogicView(PasswordChangeDoneView):
    template_name = "accounts_users/registration/password_change_done.html"





# # accounts_users/views/password.py 
# from django.contrib.auth.decorators import login_required
# from django.contrib.auth.forms import PasswordChangeForm
# from django.contrib.auth import update_session_auth_hash
# from django.shortcuts import render, redirect
# from django.contrib import messages
# from django.utils.translation import gettext_lazy as _
# from django.urls import reverse_lazy
# from django.contrib.auth.views import (
#     PasswordResetView, PasswordResetConfirmView, PasswordResetDoneView, PasswordResetCompleteView,
#     PasswordChangeView, PasswordChangeDoneView
# )

# # Formulaires personnalisés (assure-toi qu'ils existent)
# from accounts_users.forms.password_forms import (
#     CustomPasswordResetForm, CustomSetPasswordForm, CustomPasswordChangeForm
# )

# # --- Changement du mot de passe connecté : vue fonctionnelle ---
# @login_required
# def password_change_view(request):
#     """
#     Permet à l'utilisateur connecté de changer son mot de passe via un formulaire classique.
#     """
#     if request.method == "POST":
#         form = PasswordChangeForm(user=request.user, data=request.POST)
#         if form.is_valid():
#             user = form.save()
#             update_session_auth_hash(request, user)  # Évite la déconnexion après changement de mot de passe
#             messages.success(request, _("Votre mot de passe a été changé avec succès."))
#             return redirect("dashboard:profile")
#         else:
#             messages.error(request, _("Veuillez corriger les erreurs ci-dessous."))
#     else:
#         form = PasswordChangeForm(user=request.user)

#     return render(
#         request,
#         "accounts_users/registration/password_change_form.html",  # Convention Django
#         {"form": form}
#     )

# # --- Réinitialisation du mot de passe par email ---

# class CustomPasswordResetView(PasswordResetView):
#     email_template_name = "accounts_users/registration/password_reset_email.html"
#     subject_template_name = "accounts_users/registration/password_reset_subject.txt"
#     template_name = "accounts_users/registration/password_reset_form.html"
#     success_url = reverse_lazy('accounts_users_web:password_reset_done')
#     form_class = CustomPasswordResetForm

#     def form_valid(self, form):
#         messages.success(self.request, _("Si cette adresse existe, un email de réinitialisation a été envoyé."))
#         return super().form_valid(form)

# class CustomPasswordResetDoneView(PasswordResetDoneView):
#     template_name = "accounts_users/registration/password_reset_done.html"

# class CustomPasswordResetConfirmView(PasswordResetConfirmView):
#     template_name = "accounts_users/registration/password_reset_confirm.html"
#     success_url = reverse_lazy('accounts_users_web:password_reset_complete')
#     form_class = CustomSetPasswordForm

#     def form_valid(self, form):
#         messages.success(self.request, _("Votre mot de passe a bien été modifié !"))
#         return super().form_valid(form)

# class CustomPasswordResetCompleteView(PasswordResetCompleteView):
#     template_name = "accounts_users/registration/password_reset_complete.html"

# # --- Changement de mot de passe pour utilisateur connecté via vue basée sur classe ---

# class CustomPasswordChangeView(PasswordChangeView):
#     template_name = "accounts_users/registration/password_change_form.html"
#     success_url = reverse_lazy('accounts_users_web:password_change_done')
#     form_class = CustomPasswordChangeForm

#     def form_valid(self, form):
#         update_session_auth_hash(self.request, form.user)
#         messages.success(self.request, _("Votre mot de passe a bien été changé."))
#         return super().form_valid(form)

# class CustomPasswordChangeDoneView(PasswordChangeDoneView):
#     template_name = "accounts_users/registration/password_change_done.html"










# from django.contrib.auth.decorators import login_required
# from django.contrib.auth.forms import PasswordChangeForm
# from django.contrib.auth import update_session_auth_hash
# from django.shortcuts import render, redirect
# from django.contrib import messages
# from django.utils.translation import gettext_lazy as _


# @login_required
# def password_change_view(request):
#     if request.method == "POST":
#         form = PasswordChangeForm(user=request.user, data=request.POST)
#         if form.is_valid():
#             user = form.save()
#             update_session_auth_hash(request, user)
#             messages.success(request, _("Votre mot de passe a été changé avec succès."))
#             return redirect("dashboard:profile")
#         else:
#             messages.error(request, _("Veuillez corriger les erreurs."))
#     else:
#         form = PasswordChangeForm(user=request.user)

#     return render(request, "accounts_users/registration/password_change.html", {"form": form})




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
