# accounts_users/forms/auth_forms.py
from django import forms
from django.utils.translation import gettext_lazy as _

class AuthenticationEmailForm(forms.Form):
    email = forms.EmailField(
        label=_("Adresse e-mail"),
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": _("Adresse e-mail")}),
    )
    password = forms.CharField(
        label=_("Mot de passe"),
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": _("Mot de passe")}),
    )





# #accounts_users/forms/auth_forms.py -> 01/07
# from django import forms
# from django.contrib.auth.forms import UserCreationForm, UserChangeForm
# from django.contrib.auth import get_user_model

# User = get_user_model()

# class CustomUserCreationForm(UserCreationForm):
#     class Meta:
#         model = User
#         fields = ['email']


# class CustomUserChangeForm(UserChangeForm):
#     class Meta:
#         model = User
#         fields = ['email']
