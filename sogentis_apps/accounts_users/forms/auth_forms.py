# accounts_users/forms/auth_forms.py
from __future__ import annotations

from typing import Any

from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

User = get_user_model()


# =====================================================
# Helpers (safe)
# =====================================================
def _has_field(model, field_name: str) -> bool:
    try:
        model._meta.get_field(field_name)
        return True
    except Exception:
        return False


def _normalize_email(value: str) -> str:
    return (value or "").strip().casefold()


def _user_exists_with_email(email: str, *, exclude_pk: int | None = None) -> bool:
    if not email:
        return False
    qs = User._default_manager.filter(email__iexact=email)
    if exclude_pk:
        qs = qs.exclude(pk=exclude_pk)
    return qs.exists()


# =====================================================
# Authentication (email)
# =====================================================
class AuthenticationEmailForm(forms.Form):
    """
    Form de login par email, robuste:
    - normalise email (strip + casefold)
    - authenticate(email=...) puis fallback authenticate(username=...)
    - expose `cleaned_data["user"]`
    - gère remember_me via apply_session_persistence()
    """

    email = forms.EmailField(
        label=_("Adresse e-mail"),
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Adresse e-mail"),
                "autocomplete": "username",
                "inputmode": "email",
            }
        ),
        error_messages={"required": _("Ce champ est obligatoire.")},
    )

    password = forms.CharField(
        label=_("Mot de passe"),
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Mot de passe"),
                "autocomplete": "current-password",
            }
        ),
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

    def __init__(self, *args: Any, **kwargs: Any):
        # Permet d'utiliser request dans clean()
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

    def clean_email(self) -> str:
        return _normalize_email(self.cleaned_data.get("email", ""))

    def _do_authenticate(self, *, email: str, password: str):
        """
        1) essaie authenticate(email=..., password=...)
        2) fallback authenticate(username=email, password=...) (utile si backend classique)
        """
        user = authenticate(self.request, email=email, password=password)
        if user is None:
            user = authenticate(self.request, username=email, password=password)
        return user

    def clean(self):
        cleaned = super().clean()
        email = cleaned.get("email")
        password = cleaned.get("password")

        if not email or not password:
            return cleaned

        user = self._do_authenticate(email=email, password=password)

        if user is None:
            raise ValidationError(self.error_messages["invalid_login"], code="invalid_login")

        if not getattr(user, "is_active", True):
            raise ValidationError(self.error_messages["inactive"], code="inactive")

        cleaned["user"] = user
        return cleaned

    def apply_session_persistence(self, request):
        """
        À appeler dans la vue après login() si tu veux gérer remember_me.
        - remember_me=True : session persistante (expire selon SESSION_COOKIE_AGE)
        - remember_me=False : expire à la fermeture du navigateur
        """
        remember = bool(self.cleaned_data.get("remember_me"))
        request.session.set_expiry(None if remember else 0)


# =====================================================
# Custom user creation / change forms (admin-safe)
# =====================================================
class CustomUserCreationForm(UserCreationForm):
    """
    Form admin de création: inclut email + username si présent.
    Valide l'unicité de l'email si non gérée côté modèle.
    """

    class Meta:
        model = User
        fields = tuple([f for f in ("email", "username", "first_name", "last_name") if _has_field(User, f)])

    def clean_email(self):
        email = _normalize_email(self.cleaned_data.get("email", ""))
        if not email:
            raise ValidationError(_("Adresse e-mail obligatoire."))

        # si le modèle a unique=True sur email, ceci double-check mais ne gêne pas
        if _user_exists_with_email(email):
            raise ValidationError(_("Un compte avec cette adresse e-mail existe déjà."))
        return email


class CustomUserChangeForm(UserChangeForm):
    """
    Form admin d'édition: inclut email + username si présent.
    Valide l'unicité de l'email hors instance courante.
    """

    class Meta:
        model = User
        fields = tuple([f for f in ("email", "username", "first_name", "last_name") if _has_field(User, f)])

    def clean_email(self):
        email = _normalize_email(self.cleaned_data.get("email", ""))
        if not email:
            raise ValidationError(_("Adresse e-mail obligatoire."))

        pk = getattr(self.instance, "pk", None)
        if _user_exists_with_email(email, exclude_pk=pk):
            raise ValidationError(_("Un autre compte utilise déjà cette adresse e-mail."))
        return email





# # accounts_users/forms/auth_forms.py

# from django import forms
# from django.contrib.auth import authenticate, get_user_model
# from django.contrib.auth.forms import UserCreationForm, UserChangeForm
# from django.utils.translation import gettext_lazy as _


# class AuthenticationEmailForm(forms.Form):
#     email = forms.EmailField(
#         label=_("Adresse e-mail"),
#         widget=forms.EmailInput(
#             attrs={
#                 "class": "form-control",
#                 "placeholder": _("Adresse e-mail"),
#                 "autocomplete": "username",
#                 "inputmode": "email",
#             }
#         ),
#         error_messages={"required": _("Ce champ est obligatoire.")},
#     )

#     password = forms.CharField(
#         label=_("Mot de passe"),
#         widget=forms.PasswordInput(
#             attrs={
#                 "class": "form-control",
#                 "placeholder": _("Mot de passe"),
#                 "autocomplete": "current-password",
#             }
#         ),
#         error_messages={"required": _("Ce champ est obligatoire.")},
#         strip=False,
#     )

#     remember_me = forms.BooleanField(
#         label=_("Se souvenir de moi"),
#         required=False,
#         widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
#     )

#     error_messages = {
#         "invalid_login": _("Adresse e-mail et/ou mot de passe invalide."),
#         "inactive": _("Ce compte est inactif."),
#     }

#     def __init__(self, *args, **kwargs):
#         # Permet d'utiliser request dans clean()
#         self.request = kwargs.pop("request", None)
#         super().__init__(*args, **kwargs)

#     def clean_email(self):
#         # Normalise l'email (évite les faux négatifs)
#         return self.cleaned_data["email"].strip().casefold()

#     def clean(self):
#         cleaned = super().clean()
#         email = cleaned.get("email")
#         password = cleaned.get("password")

#         if not email or not password:
#             return cleaned

#         user = authenticate(self.request, email=email, password=password)

#         if user is None:
#             raise forms.ValidationError(self.error_messages["invalid_login"])

#         if not user.is_active:
#             raise forms.ValidationError(self.error_messages["inactive"])

#         cleaned["user"] = user
#         return cleaned

#     def apply_session_persistence(self, request):
#         """
#         À appeler dans la vue après form_valid
#         pour gérer l'option "Se souvenir de moi"
#         """
#         if self.cleaned_data.get("remember_me"):
#             # Session persistante (SESSION_COOKIE_AGE)
#             request.session.set_expiry(None)
#         else:
#             # Expire à la fermeture du navigateur
#             request.session.set_expiry(0)


# User = get_user_model()


# class CustomUserCreationForm(UserCreationForm):
#     class Meta:
#         model = User
#         fields = ["email"]


# class CustomUserChangeForm(UserChangeForm):
#     class Meta:
#         model = User
#         fields = ["email"]






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
#             "inputmode": "email",
#         }),
#         error_messages={"required": _("Ce champ est obligatoire.")},
#     )
#     password = forms.CharField(
#         label=_("Mot de passe"),
#         widget=forms.PasswordInput(attrs={
#             "class": "form-control",
#             "placeholder": _("Mot de passe"),
#             "autocomplete": "current-password",
#         }),
#         error_messages={"required": _("Ce champ est obligatoire.")},
#         strip=False,
#     )
#     remember_me = forms.BooleanField(
#         label=_("Se souvenir de moi"),
#         required=False,
#         widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
#     )

#     error_messages = {
#         "invalid_login": _("Adresse e-mail et/ou mot de passe invalide."),
#         "inactive": _("Ce compte est inactif."),
#     }

#     def __init__(self, *args, **kwargs):
#         # permet d'utiliser request dans clean()
#         self.request = kwargs.pop("request", None)
#         super().__init__(*args, **kwargs)

#     def clean_email(self):
#         # normalise l'email (évite les faux négatifs)
#         return self.cleaned_data["email"].strip().casefold()

#     def clean(self):
#         cleaned = super().clean()
#         email = cleaned.get("email")
#         password = cleaned.get("password")
#         if not email or not password:
#             return cleaned

#         user = authenticate(self.request, email=email, password=password)
#         if user is None:
#             raise forms.ValidationError(self.error_messages["invalid_login"])
#         if not user.is_active:
#             raise forms.ValidationError(self.error_messages["inactive"])

#         cleaned["user"] = user
#         return cleaned

#     # appel dans la vue après form_valid pour gérer "remember me"
#     def apply_session_persistence(self, request):
#         if self.cleaned_data.get("remember_me"):
#             # session persiste (utilise SESSION_COOKIE_AGE)
#             request.session.set_expiry(None)
#         else:
#             # expire à la fermeture du navigateur
#             request.session.set_expiry(0)





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
