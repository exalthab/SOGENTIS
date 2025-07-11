# accounts_users/forms/login_forms.py
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label=_("Nom d'utilisateur"),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _("Nom d'utilisateur")})
    )
    password = forms.CharField(
        label=_("Mot de passe"),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': _("Mot de passe")})
    )

    error_messages = {
        'invalid_login': _("Nom d'utilisateur ou mot de passe incorrect."),
        'inactive': _("Ce compte est inactif."),
    }

    def __init__(self, *args, **kwargs):
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if username and password:
            self.user_cache = authenticate(username=username, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                )
            elif not self.user_cache.is_active:
                raise forms.ValidationError(
                    self.error_messages['inactive'],
                    code='inactive',
                )
        return self.cleaned_data

    def get_user(self):
        return self.user_cache






# # accounts_users/forms/login_forms.py 01/07
# from django import forms
# from django.contrib.auth.forms import AuthenticationForm

# class CustomLoginForm(AuthenticationForm):
#     username = forms.EmailField(
#         label="Email",
#         widget=forms.EmailInput(attrs={
#             'class': 'form-control',
#             'placeholder': 'Entrez votre adresse email'
#         })
#     )
#     password = forms.CharField(
#         label="Mot de passe",
#         strip=False,
#         widget=forms.PasswordInput(attrs={
#             'class': 'form-control',
#             'placeholder': 'Entrez votre mot de passe'
#         }),
#     )
