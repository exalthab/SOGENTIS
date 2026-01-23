# accounts_users/forms/registration/user_signup_form.py
from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from accounts_users.models.custom_users import CustomUser


class UserSignupForm(forms.ModelForm):
    password = forms.CharField(
        label=_("Mot de passe"),
        widget=forms.PasswordInput(attrs={"class": "form-control", "autocomplete": "new-password"}),
        strip=False,
    )
    password_confirm = forms.CharField(
        label=_("Confirmation du mot de passe"),
        widget=forms.PasswordInput(attrs={"class": "form-control", "autocomplete": "new-password"}),
        strip=False,
    )

    class Meta:
        model = CustomUser
        fields = ["email", "username"]
        widgets = {
            "email": forms.EmailInput(attrs={"class": "form-control", "autocomplete": "email"}),
            "username": forms.TextInput(attrs={"class": "form-control", "autocomplete": "username"}),
        }

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password")
        p2 = cleaned.get("password_confirm")
        if p1 and p2 and p1 != p2:
            self.add_error("password_confirm", _("Les mots de passe ne correspondent pas."))
        return cleaned

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").lower().strip()
        if not email:
            raise ValidationError(_("L’adresse e-mail est obligatoire."))
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError(_("Cette adresse e-mail est déjà utilisée."))
        return email

    def clean_username(self):
        username = (self.cleaned_data.get("username") or "").strip()
        if not username:
            raise ValidationError(_("Le nom d’utilisateur est obligatoire."))
        if CustomUser.objects.filter(username=username).exists():
            raise ValidationError(_("Ce nom d’utilisateur est déjà utilisé."))
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user
