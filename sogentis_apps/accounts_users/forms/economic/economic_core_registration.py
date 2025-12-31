# accounts_users/forms/economic/economic_core_registration.py
from django import forms
from django.utils.translation import gettext_lazy as _
from django_countries.widgets import CountrySelectWidget
from django.core.exceptions import ValidationError

from accounts_users.models.users_economic_profile import UserEconomicProfile


class UserProfileEconomicForm(forms.ModelForm):
    """
    Formulaire profil ÉCONOMIQUE (central)
    - terms obligatoire (non persisté)
    - champs limités (identité + contact + résidence + pro + photo)
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
            "phone",
            "country_of_residence",
            "city_of_residence",
            "profession",
            "function",
            "profile_picture",
        ]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control", "autocomplete": "given-name"}),
            "last_name": forms.TextInput(attrs={"class": "form-control", "autocomplete": "family-name"}),
            "phone": forms.TextInput(attrs={"class": "form-control", "autocomplete": "tel"}),
            "country_of_residence": CountrySelectWidget(attrs={"class": "form-select"}),
            "city_of_residence": forms.TextInput(attrs={"class": "form-control"}),
            "profession": forms.TextInput(attrs={"class": "form-control"}),
            "function": forms.TextInput(attrs={"class": "form-control"}),
            "profile_picture": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }

    def clean_phone(self):
        """
        - Si ton modèle est PhoneNumberField: la validation se fera déjà.
        - Si ton modèle est CharField: on sécurise ici.
        """
        phone = (self.cleaned_data.get("phone") or "").strip()
        if not phone:
            return phone

        # Validation E.164 simple (prod)
        # +221771234567 ou 221771234567 (on force +)
        if phone.startswith("00"):
            phone = "+" + phone[2:]
        if not phone.startswith("+"):
            phone = "+" + phone

        # E.164: + + 8..15 digits
        digits = phone[1:]
        if not digits.isdigit() or not (8 <= len(digits) <= 15):
            raise ValidationError(_("Le numéro de téléphone est invalide."))

        return phone

    def clean_profile_picture(self):
        f = self.cleaned_data.get("profile_picture")
        if not f:
            return f

        # limites production
        max_mb = 5
        if f.size > max_mb * 1024 * 1024:
            raise ValidationError(_("Image trop lourde (max %(mb)sMB).") % {"mb": max_mb})

        content_type = getattr(f, "content_type", "") or ""
        allowed = {"image/jpeg", "image/png", "image/webp"}
        if content_type and content_type not in allowed:
            raise ValidationError(_("Format d’image non supporté (JPG/PNG/WEBP)."))

        return f







# # accounts_users/forms/economic/economic_core_registration.py 30/12/2025
# from django import forms
# from django.utils.translation import gettext_lazy as _
# from django_countries.widgets import CountrySelectWidget
# from django.core.exceptions import ValidationError
# import re

# from accounts_users.models.users_economic_profile import UserEconomicProfile


# class UserProfileEconomicForm(forms.ModelForm):
#     """
#     Formulaire profil ÉCONOMIQUE
#     - Photo de profil autorisée
#     - Pas d’adhésion sociale
#     - Conditions générales obligatoires
#     """

#     # ======================================================
#     # CONDITIONS GÉNÉRALES (NON PERSISTÉ)
#     # ======================================================
#     terms = forms.BooleanField(
#         required=True,
#         label=_("J’accepte les conditions générales"),
#         error_messages={
#             "required": _("Vous devez accepter les conditions générales."),
#         },
#     )

#     class Meta:
#         model = UserEconomicProfile
#         fields = [
#             # Identité
#             "first_name",
#             "last_name",

#             # Contact
#             "phone",

#             # Résidence
#             "country_of_residence",
#             "city_of_residence",

#             # Professionnel
#             "profession",
#             "function",

#             # 📸 Photo de profil
#             "profile_picture",
#         ]

#         widgets = {
#             "first_name": forms.TextInput(attrs={"class": "form-control"}),
#             "last_name": forms.TextInput(attrs={"class": "form-control"}),

#             "phone": forms.TextInput(attrs={"class": "form-control"}),

#             "country_of_residence": CountrySelectWidget(
#                 attrs={"class": "form-select"}
#             ),
#             "city_of_residence": forms.TextInput(attrs={"class": "form-control"}),

#             "profession": forms.TextInput(attrs={"class": "form-control"}),
#             "function": forms.TextInput(attrs={"class": "form-control"}),

#             "profile_picture": forms.ClearableFileInput(
#                 attrs={"class": "form-control"}
#             ),
#         }

#     # ======================================================
#     # VALIDATIONS
#     # ======================================================

#     def clean_phone(self):
#         phone = self.cleaned_data.get("phone")
#         if phone and not re.match(r"^\+?[1-9]\d{1,14}$", phone):
#             raise ValidationError(_("Le numéro de téléphone est invalide."))
#         return phone











# # accounts_users/forms/profile_economic_forms.py
# from django import forms
# from django_countries.widgets import CountrySelectWidget
# from django.utils.translation import gettext_lazy as _

# from django.core.exceptions import ValidationError
# import re

# from accounts_users.models.users_economic_profile import UserProfile


# class UserProfileEconomicForm(forms.ModelForm):
#     """
#     Formulaire profil ÉCONOMIQUE
#     - Photo de profil autorisée
#     - Pas d’adhésion sociale obligatoire
#     - Conditions générales obligatoires
#     """

#     # ======================================================
#     # CONDITIONS GÉNÉRALES (NON PERSISTÉ)
#     # ======================================================
#     terms = forms.BooleanField(
#         required=True,
#         label=_("J’accepte les conditions générales"),
#         error_messages={
#             "required": _("Vous devez accepter les conditions générales."),
#         },
#     )

#     class Meta:
#         model = UserProfile
#         fields = [
#             # Identité
#             "first_name",
#             "last_name",

#             # Contact
#             "phone",

#             # Résidence
#             "country_of_residence",
#             "city_of_residence",
#             # "address",

#             # Professionnel
#             "profession",
#             "function",

#             # 📸 Photo de profil
#             "profile_picture",
#         ]

#         widgets = {
#             "first_name": forms.TextInput(attrs={"class": "form-control"}),
#             "last_name": forms.TextInput(attrs={"class": "form-control"}),

#             "phone": forms.TextInput(attrs={"class": "form-control"}),

#             "country_of_residence": CountrySelectWidget(
#                 attrs={"class": "form-select"}
#             ),
#             "city_of_residence": forms.TextInput(attrs={"class": "form-control"}),
#             "address": forms.Textarea(
#                 attrs={"rows": 2, "class": "form-control"}
#             ),

#             "profession": forms.TextInput(attrs={"class": "form-control"}),
#             "function": forms.TextInput(attrs={"class": "form-control"}),

#             "profile_picture": forms.ClearableFileInput(
#                 attrs={"class": "form-control"}
#             ),
#         }
    
#     # ======================================================
#     # VALIDATIONS DÉFENSIVES (CRITIQUES)
#     # ======================================================


#     def clean_phone(self):
#         phone = self.cleaned_data.get("phone")
#         # Validation pour un format de numéro spécifique (ex : seulement chiffres, longueur fixe, etc.)
#         if not re.match(r"^\+?[1-9]\d{1,14}$", phone):
#             raise ValidationError(_("Le numéro de téléphone est invalide."))
#         return phone

#     def clean_country_of_residence(self):
#         value = self.cleaned_data.get("country_of_residence")
#         if value and len(value) != 2:
#             raise ValidationError(_("Pays de résidence invalide."))
#         return value




# # accounts_users/forms/profile_economic_forms.py
# from django import forms
# from django_countries.widgets import CountrySelectWidget
# from django.utils.translation import gettext_lazy as _

# from accounts_users.models.users_profile import UserProfile


# class UserProfileEconomicForm(forms.ModelForm):
#     """
#     Formulaire profil ÉCONOMIQUE
#     - Photo de profil autorisée
#     - Pas d’adhésion sociale obligatoire
#     - Pas de casier judiciaire
#     """

#     class Meta:
#         model = UserProfile
#         fields = [
#             # Identité
#             "first_name",
#             "last_name",

#             # Contact
#             "phone",

#             # Résidence
#             "country_of_residence",
#             "city_of_residence",
#             "address",

#             # Professionnel
#             "profession",
#             "function",

#             # 📸 Photo de profil
#             "profile_picture",
#         ]

#         widgets = {
#             "first_name": forms.TextInput(attrs={"class": "form-control"}),
#             "last_name": forms.TextInput(attrs={"class": "form-control"}),

#             "phone": forms.TextInput(attrs={"class": "form-control"}),

#             "country_of_residence": CountrySelectWidget(
#                 attrs={"class": "form-select"}
#             ),
#             "city_of_residence": forms.TextInput(attrs={"class": "form-control"}),
#             "address": forms.Textarea(
#                 attrs={"rows": 2, "class": "form-control"}
#             ),

#             "profession": forms.TextInput(attrs={"class": "form-control"}),
#             "function": forms.TextInput(attrs={"class": "form-control"}),

#             "profile_picture": forms.ClearableFileInput(
#                 attrs={"class": "form-control"}
#             ),
#         }




# from django import forms
# from django.utils.translation import gettext_lazy as _
# from django_countries.widgets import CountrySelectWidget

# from accounts_users.models.users_profile import UserProfile


# class UserProfileEconomicForm(forms.ModelForm):
#     """
#     Formulaire profil ÉCONOMIQUE
#     - Pas d’adhésion sociale obligatoire
#     - Pas de casier judiciaire
#     - Pas de CGU sociales
#     """

#     class Meta:
#         model = UserProfile
#         fields = [
#             "first_name",
#             "last_name",
#             "phone",
#             "country_of_residence",
#             "city_of_residence",
#             "address",
#             "profession",
#             "function",
#         ]

#         widgets = {
#             "first_name": forms.TextInput(attrs={"class": "form-control"}),
#             "last_name": forms.TextInput(attrs={"class": "form-control"}),
#             "phone": forms.TextInput(attrs={"class": "form-control"}),

#             "country_of_residence": CountrySelectWidget(
#                 attrs={"class": "form-select"}
#             ),
#             "city_of_residence": forms.TextInput(attrs={"class": "form-control"}),
#             "address": forms.Textarea(
#                 attrs={"rows": 2, "class": "form-control"}
#             ),

#             "profession": forms.TextInput(attrs={"class": "form-control"}),
#             "function": forms.TextInput(attrs={"class": "form-control"}),
#         }
