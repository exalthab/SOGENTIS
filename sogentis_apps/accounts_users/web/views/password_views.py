# accounts_users/web/views/password_views.py
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from django.contrib.auth.views import (
    PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView,
    PasswordResetCompleteView
)

from accounts_users.forms.password_forms import CustomPasswordResetForm, CustomSetPasswordForm


# ==================================================================
# 1. Demande de réinitialisation par email
# ==================================================================

class CustomPasswordResetView(PasswordResetView):
    template_name = "accounts_users/registration/password_reset_form.html"
    email_template_name = "accounts_users/registration/password_reset_email.html"
    subject_template_name = "accounts_users/registration/password_reset_subject.txt"
    success_url = reverse_lazy('accounts_users_web:password_reset_done')
    form_class = CustomPasswordResetForm

    def form_valid(self, form):
        messages.success(
            self.request,
            _("Si cette adresse existe, un email de réinitialisation a été envoyé.")
        )
        return super().form_valid(form)


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = "accounts_users/registration/password_reset_done.html"


# ==================================================================
# 2. Saisie du nouveau mot de passe
# ==================================================================

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "accounts_users/registration/password_reset_confirm.html"
    form_class = CustomSetPasswordForm
    success_url = reverse_lazy('accounts_users_web:password_reset_complete')

    def form_valid(self, form):
        messages.success(self.request, _("Votre mot de passe a bien été modifié !"))
        return super().form_valid(form)


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "accounts_users/registration/password_reset_complete.html"








# # accounts_users/web/views/password_views.py
# from django.contrib.auth.views import (
#     PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
# )
# from django.urls import reverse_lazy
# from django.contrib import messages
# from accounts_users.forms.password_forms import CustomPasswordResetForm, CustomSetPasswordForm
# from django.utils.translation import gettext_lazy as _

# # Demande de reset (étape 1)
# class CustomPasswordResetView(PasswordResetView):
#     email_template_name = "accounts_users/registration/password_reset_email.html"
#     subject_template_name = "accounts_users/registration/password_reset_subject.txt"
#     template_name = "accounts_users/registration/password_reset_form.html"
#     success_url = reverse_lazy('accounts_users_web:password_reset_done')
#     form_class = CustomPasswordResetForm

#     def form_valid(self, form):
#         messages.success(
#             self.request,
#             _("Si cette adresse existe, un email de réinitialisation a été envoyé. Vérifiez vos spams si besoin.")
#         )
#         return super().form_valid(form)

# # Confirmation lien envoyé
# class CustomPasswordResetDoneView(PasswordResetDoneView):
#     template_name = "accounts_users/registration/password_reset_done.html"

# # Saisie nouveau mot de passe (après clic sur lien email)
# class CustomPasswordResetConfirmView(PasswordResetConfirmView):
#     template_name = "accounts_users/registration/password_reset_confirm.html"
#     form_class = CustomSetPasswordForm
#     success_url = reverse_lazy('accounts_users_web:password_reset_complete')

#     def form_valid(self, form):
#         messages.success(self.request, _("Votre mot de passe a été modifié avec succès !"))
#         return super().form_valid(form)

# # Confirmation fin de process
# class CustomPasswordResetCompleteView(PasswordResetCompleteView):
#     template_name = "accounts_users/registration/password_reset_complete.html"







# from django.shortcuts import render, redirect
# from django.contrib import messages
# from accounts_users.forms.password_forms import CustomPasswordResetForm
# from django.contrib.auth.tokens import default_token_generator
# from django.contrib.auth import get_user_model
# from django.core.mail import send_mail
# from django.template.loader import render_to_string
# from django.utils.http import urlsafe_base64_encode
# from django.utils.encoding import force_bytes
# from django.conf import settings
# from django.utils.translation import gettext_lazy as _

# def password_reset_request(request):
#     """
#     Vue pour demander la réinitialisation du mot de passe (étape 1).
#     Compatible avec /accounts/web/password_reset/
#     """
#     form = CustomPasswordResetForm(request.POST or None)

#     if request.method == "POST" and form.is_valid():
#         email = form.cleaned_data["email"]
#         User = get_user_model()
#         users = User.objects.filter(email=email, is_active=True)
#         # On affiche TOUJOURS le même message pour des raisons de sécurité
#         messages.success(
#             request,
#             _("Si cette adresse existe, un email de réinitialisation a été envoyé. Vérifiez vos spams si besoin.")
#         )
#         if users.exists():
#             for user in users:
#                 context = {
#                     "email": user.email,
#                     "domain": request.get_host(),
#                     "site_name": "Sogentis",
#                     "uid": urlsafe_base64_encode(force_bytes(user.pk)),
#                     "user": user,
#                     "token": default_token_generator.make_token(user),
#                     "protocol": "https" if request.is_secure() else "http",
#                 }
#                 subject = render_to_string("accounts_users/registration/password_reset_subject.txt", context)
#                 subject = "".join(subject.splitlines())
#                 email_body = render_to_string("accounts_users/registration/password_reset_email.html", context)
#                 send_mail(
#                     subject,
#                     email_body,
#                     settings.DEFAULT_FROM_EMAIL,
#                     [user.email],
#                     fail_silently=False,
#                 )
#         # Toujours rediriger après POST (Post/Redirect/Get)
#         return redirect("accounts_users_web:password_reset_done")

#     return render(
#         request,
#         "accounts_users/registration/password_reset_form.html",
#         {"form": form}
#     )




# #/accounts_users/web/views/password_views.py
# from django.shortcuts import render
# from accounts_users.forms.password_forms import CustomPasswordResetForm
# from django.contrib.auth.tokens import default_token_generator
# # from django.contrib.auth.models import User
# from django.contrib.auth import get_user_model
# from django.core.mail import send_mail
# from django.template.loader import render_to_string
# from django.utils.http import urlsafe_base64_encode
# from django.utils.encoding import force_bytes
# from django.conf import settings

# def password_reset_request(request):
#     if request.method == "POST":
#         form = CustomPasswordResetForm(request.POST)
#         if form.is_valid():
#             email = form.cleaned_data["email"]
#             User = get_user_model()  # Use the custom user model
#             users = User.objects.filter(email=email)
#             for user in users:
#                 context = {
#                     "email": user.email,
#                     "domain": request.get_host(),
#                     "site_name": "Sogentis",
#                     "uid": urlsafe_base64_encode(force_bytes(user.pk)),
#                     "user": user,
#                     "token": default_token_generator.make_token(user),
#                     "protocol": "https" if request.is_secure() else "http",
#                 }
#                 subject = render_to_string("accounts_users/registration/password_reset_subject.txt", context)
#                 subject = "".join(subject.splitlines())
#                 email_body = render_to_string("accounts_users/registration/password_reset_email.html", context)
#                 send_mail(subject, email_body, settings.DEFAULT_FROM_EMAIL, [user.email])
#     else:
#         form = CustomPasswordResetForm()
#     return render(request, "accounts_users/registration/password_reset.html", {"form": form})
