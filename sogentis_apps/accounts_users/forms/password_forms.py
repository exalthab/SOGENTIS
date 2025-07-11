# accounts_users/forms/password_forms.py
from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm, PasswordResetForm

class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(label="Votre email", max_length=254, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Entrez votre adresse email'
    }))

class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label=_("Ancien mot de passe"),
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": _("Ancien mot de passe")}),
    )
    new_password1 = forms.CharField(
        label=_("Nouveau mot de passe"),
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": _("Nouveau mot de passe")}),
    )
    new_password2 = forms.CharField(
        label=_("Confirmer le nouveau mot de passe"),
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": _("Confirmer le mot de passe")}),
    )


class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label=_("Nouveau mot de passe"),
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": _("Nouveau mot de passe")}),
    )
    new_password2 = forms.CharField(
        label=_("Confirmer le mot de passe"),
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": _("Confirmer le mot de passe")}),
    )




# #accounts_users/forms/password_forms.py -> 01/07
# from django import forms
# from django.contrib.auth.forms import (
#     PasswordResetForm, SetPasswordForm, PasswordChangeForm
# )

# class CustomPasswordResetForm(PasswordResetForm):
#     email = forms.EmailField(label="Votre email", max_length=254, widget=forms.EmailInput(attrs={
#         'class': 'form-control',
#         'placeholder': 'Entrez votre adresse email'
#     }))


# class CustomSetPasswordForm(SetPasswordForm):
#     new_password1 = forms.CharField(
#         label="Nouveau mot de passe",
#         widget=forms.PasswordInput(attrs={'class': 'form-control'}),
#     )
#     new_password2 = forms.CharField(
#         label="Confirmez le mot de passe",
#         widget=forms.PasswordInput(attrs={'class': 'form-control'}),
#     )


# class CustomPasswordChangeForm(PasswordChangeForm):
#     old_password = forms.CharField(
#         label="Mot de passe actuel",
#         strip=False,
#         widget=forms.PasswordInput(attrs={'class': 'form-control'}),
#     )
#     new_password1 = forms.CharField(
#         label="Nouveau mot de passe",
#         strip=False,
#         widget=forms.PasswordInput(attrs={'class': 'form-control'}),
#     )
#     new_password2 = forms.CharField(
#         label="Confirmez le nouveau mot de passe",
#         strip=False,
#         widget=forms.PasswordInput(attrs={'class': 'form-control'}),
#     )
