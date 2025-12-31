# accounts_users/forms/auth_forms.py
from django import forms
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _

class AuthenticationEmailForm(forms.Form):
    email = forms.EmailField(
        label=_("Adresse e-mail"),
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": _("Adresse e-mail"),
            "autocomplete": "username",
            "inputmode": "email",
        }),
        error_messages={"required": _("Ce champ est obligatoire.")},
    )
    password = forms.CharField(
        label=_("Mot de passe"),
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": _("Mot de passe"),
            "autocomplete": "current-password",
        }),
        error_messages={"required": _("Ce champ est obligatoire.")},
        strip=False,
    )
    remember_me = forms.BooleanField(
        label=_("Se souvenir de moi"),
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    error_messages = {
        "invalid_login": _("Adresse e-mail et/ou mot de passe invalide."),
        "inactive": _("Ce compte est inactif."),
    }

    def __init__(self, *args, **kwargs):
        # permet d'utiliser request dans clean()
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

    def clean_email(self):
        # normalise l'email (évite les faux négatifs)
        return self.cleaned_data["email"].strip().casefold()

    def clean(self):
        cleaned = super().clean()
        email = cleaned.get("email")
        password = cleaned.get("password")
        if not email or not password:
            return cleaned

        user = authenticate(self.request, email=email, password=password)
        if user is None:
            raise forms.ValidationError(self.error_messages["invalid_login"])
        if not user.is_active:
            raise forms.ValidationError(self.error_messages["inactive"])

        cleaned["user"] = user
        return cleaned

    # appel dans la vue après form_valid pour gérer "remember me"
    def apply_session_persistence(self, request):
        if self.cleaned_data.get("remember_me"):
            # session persiste (utilise SESSION_COOKIE_AGE)
            request.session.set_expiry(None)
        else:
            # expire à la fermeture du navigateur
            request.session.set_expiry(0)





# # accounts_users/forms/auth_forms.py
# from django import forms
# from django.contrib.auth import authenticate
# from django.utils.translation import gettext_lazy as _

# class AuthenticationEmailForm(forms.Form):
#     email = forms.EmailField(
#         label=_("Adresse e-mail"),
#         widget=forms.EmailInput(attrs={
#             "class": "form-control",
#             "placeholder": _("Adresse e-mail"),
#             "autocomplete": "username",
#         }),
#         error_messages={"required": _("Ce champ est obligatoire.")}
#     )
#     password = forms.CharField(
#         label=_("Mot de passe"),
#         widget=forms.PasswordInput(attrs={
#             "class": "form-control",
#             "placeholder": _("Mot de passe"),
#             "autocomplete": "current-password",
#         }),
#         error_messages={"required": _("Ce champ est obligatoire.")}
#     )
#     remember_me = forms.BooleanField(
#         label=_("Se souvenir de moi"),
#         required=False,
#         widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
#     )

#     error_messages = {
#         "invalid_login": _(
#             "Adresse e-mail et/ou mot de passe invalide."
#         ),
#         "inactive": _("Ce compte est inactif."),
#     }

#     def clean(self):
#         cleaned = super().clean()
#         email = cleaned.get("email")
#         password = cleaned.get("password")
#         if not email or not password:
#             return cleaned

#         # On laisse le backend gérer la recherche par e-mail (voir §2).
#         user = authenticate(self.request, email=email, password=password)
#         if user is None:
#             raise forms.ValidationError(self.error_messages["invalid_login"])
#         if not user.is_active:
#             raise forms.ValidationError(self.error_messages["inactive"])

#         cleaned["user"] = user
#         return cleaned

#     # Pour pouvoir accéder request dans clean()
#     def __init__(self, *args, **kwargs):
#         self.request = kwargs.pop("request", None)
#         super().__init__(*args, **kwargs)




# # accounts_users/forms/auth_forms.py
# from django import forms
# from django.utils.translation import gettext_lazy as _

# class AuthenticationEmailForm(forms.Form):
#     email = forms.EmailField(
#         label=_("Adresse e-mail"),
#         widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": _("Adresse e-mail")}),
#     )
#     password = forms.CharField(
#         label=_("Mot de passe"),
#         widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": _("Mot de passe")}),
#     )





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
