# accounts_users/forms/economic/economic_core_registration.py
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django_countries.widgets import CountrySelectWidget

from accounts_users.models.users_economic_profile import UserEconomicProfile


class UserProfileEconomicForm(forms.ModelForm):
    """
    Formulaire profil ÉCONOMIQUE (central)
    - terms obligatoire (non persisté)
    - identité + contact + résidence + pro + photo
    """

    terms = forms.BooleanField(
        required=True,
        label=_("J’accepte les conditions générales"),
        error_messages={"required": _("Vous devez accepter les conditions générales.")},
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    class Meta:
        model = UserEconomicProfile
        fields = [
            "first_name",
            "last_name",
            "country_of_residence",
            "phone",
            "city_of_residence",
            "profession",
            "function",
            "profile_picture",
        ]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control", "autocomplete": "given-name"}),
            "last_name": forms.TextInput(attrs={"class": "form-control", "autocomplete": "family-name"}),
            "country_of_residence": CountrySelectWidget(attrs={"class": "form-select"}),
            "phone": forms.TextInput(attrs={"class": "form-control", "autocomplete": "tel"}),
            "city_of_residence": forms.TextInput(attrs={"class": "form-control"}),
            "profession": forms.TextInput(attrs={"class": "form-control"}),
            "function": forms.TextInput(attrs={"class": "form-control"}),
            "profile_picture": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }

    def clean_phone(self):
        phone = (self.cleaned_data.get("phone") or "").strip()
        if not phone:
            return phone

        if phone.startswith("00"):
            phone = "+" + phone[2:]
        if not phone.startswith("+"):
            phone = "+" + phone

        digits = phone[1:]
        if not digits.isdigit() or not (8 <= len(digits) <= 15):
            raise ValidationError(_("Le numéro de téléphone est invalide."))

        return phone

    def clean_profile_picture(self):
        f = self.cleaned_data.get("profile_picture")
        if not f:
            return f

        max_mb = 5
        if f.size > max_mb * 1024 * 1024:
            raise ValidationError(_("Image trop lourde (max %(mb)sMB).") % {"mb": max_mb})

        content_type = getattr(f, "content_type", "") or ""
        allowed = {"image/jpeg", "image/png", "image/webp"}
        if content_type and content_type not in allowed:
            raise ValidationError(_("Format d’image non supporté (JPG/PNG/WEBP)."))

        return f

    def save(self, user=None, commit=True):
        instance = super().save(commit=False)
        if user is not None:
            instance.user = user

        if commit:
            instance.save()
            self.save_m2m()

        return instance