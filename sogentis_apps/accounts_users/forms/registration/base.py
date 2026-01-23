from __future__ import annotations

from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

try:
    from phonenumber_field.formfields import PhoneNumberField
except Exception:
    PhoneNumberField = None  # fallback


UserModel = get_user_model()


class BaseRegistrationV2Form(forms.Form):
    # Identité utilisateur (comme tes anciens formulaires)
    first_name = forms.CharField(label=_("Prénom"), max_length=150, required=True)
    last_name = forms.CharField(label=_("Nom"), max_length=150, required=True)
    email = forms.EmailField(label=_("Email"), required=True)

    if PhoneNumberField:
        phone_number = PhoneNumberField(label=_("Téléphone"), required=True, help_text=_("Format international, ex: +221771234567"))
    else:
        phone_number = forms.CharField(label=_("Téléphone"), required=True)

    country = forms.CharField(label=_("Pays"), max_length=2, required=False, help_text=_("Code pays (ex: SN, FR)"))

    password1 = forms.CharField(label=_("Mot de passe"), widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(label=_("Confirmer le mot de passe"), widget=forms.PasswordInput, required=True)

    judicial_record = forms.BooleanField(
        label=_("Casier judiciaire"),
        required=False,
        help_text=_("Optionnel (selon votre catégorie)."),
    )

    terms = forms.BooleanField(
        label=_("J’accepte les conditions générales"),
        required=True,
    )

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip().lower()
        if UserModel.objects.filter(email=email).exists():
            raise forms.ValidationError(_("Un compte existe déjà avec cet email."))
        return email

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", _("Les mots de passe ne correspondent pas."))
        return cleaned
