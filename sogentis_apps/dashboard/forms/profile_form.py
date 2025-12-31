from django import forms
from django.utils.translation import gettext_lazy as _

from accounts_users.models.users_economic_profile import UserEconomicProfile


class ProfileUpdateForm(forms.ModelForm):
    """
    Formulaire de mise à jour du profil utilisateur (Dashboard).
    Aligné avec UserEconomicProfile (profil économique).
    """

    class Meta:
        model = UserEconomicProfile
        fields = [
            # Identité
            "first_name",
            "last_name",
            "middle_names",
            "nickname",
            "date_of_birth",
            "place_of_birth",

            # Résidence
            "country_of_residence",
            "city_of_residence",
            "address",
            "country_of_birth",

            # Contact / profession
            "phone",
            "profession",
            "function",
            "message",

            # Rôle économique
            "economic_role",

            # Photo
            "profile_picture",
        ]

        labels = {
            "first_name": _("Prénom"),
            "last_name": _("Nom"),
            "middle_names": _("Autres noms"),
            "nickname": _("Surnom"),
            "date_of_birth": _("Date de naissance"),
            "place_of_birth": _("Lieu de naissance"),

            "country_of_residence": _("Pays de résidence"),
            "city_of_residence": _("Ville de résidence"),
            "address": _("Adresse"),
            "country_of_birth": _("Pays de naissance"),

            "phone": _("Téléphone"),
            "profession": _("Profession"),
            "function": _("Fonction"),
            "message": _("Message"),

            "economic_role": _("Rôle économique"),
            "profile_picture": _("Photo de profil"),
        }

        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control", "placeholder": _("Prénom")}),
            "last_name": forms.TextInput(attrs={"class": "form-control", "placeholder": _("Nom")}),
            "middle_names": forms.TextInput(attrs={"class": "form-control", "placeholder": _("Autres noms")}),
            "nickname": forms.TextInput(attrs={"class": "form-control", "placeholder": _("Surnom")}),
            "date_of_birth": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "place_of_birth": forms.TextInput(attrs={"class": "form-control", "placeholder": _("Lieu de naissance")}),

            "country_of_residence": forms.Select(attrs={"class": "form-select"}),
            "city_of_residence": forms.TextInput(attrs={"class": "form-control", "placeholder": _("Ville")}),
            "address": forms.Textarea(attrs={"class": "form-control", "rows": 2, "placeholder": _("Adresse")}),
            "country_of_birth": forms.Select(attrs={"class": "form-select"}),

            "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": _("Téléphone")}),
            "profession": forms.TextInput(attrs={"class": "form-control", "placeholder": _("Profession")}),
            "function": forms.TextInput(attrs={"class": "form-control", "placeholder": _("Fonction")}),
            "message": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": _("Quelques mots")}),

            "economic_role": forms.Select(attrs={"class": "form-select"}),

            "profile_picture": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }

    # --------------------------------------------------
    # VALIDATIONS
    # --------------------------------------------------
    def clean_phone(self):
        phone = (self.cleaned_data.get("phone") or "").strip()
        if phone and not phone.replace("+", "").replace(" ", "").isdigit():
            raise forms.ValidationError(_("Le téléphone doit contenir uniquement des chiffres."))
        return phone







# # dashboard/forms/profile_form.py
# from django import forms
# from django.utils.translation import gettext_lazy as _

# from accounts_users.models.users_economic_profile import UserProfile


# class ProfileUpdateForm(forms.ModelForm):
#     """
#     Formulaire de mise à jour du profil utilisateur (Dashboard).
#     Aligné STRICTEMENT avec le modèle UserProfile réel.
#     """

#     class Meta:
#         model = UserProfile
#         fields = [
#             # Identité
#             "first_name",
#             "last_name",

#             # Contact
#             "phone",

#             # Pays (ISO alpha-2)
#             "country_of_residence",

#             # Divers
#             "message",

#             # Fichiers
#             "judicial_record",
#             "profile_picture",

#             # Social
#             "membership_role",
#         ]

#         labels = {
#             "first_name": _("Prénom"),
#             "last_name": _("Nom"),
#             "phone": _("Téléphone"),
#             "country_of_residence": _("Pays de résidence"),
#             "message": _("Message personnel"),
#             "judicial_record": _("Casier judiciaire (PDF)"),
#             "profile_picture": _("Photo de profil"),
#             "membership_role": _("Type d’adhésion"),
#         }

#         widgets = {
#             "first_name": forms.TextInput(
#                 attrs={"class": "form-control", "placeholder": _("Prénom")}
#             ),
#             "last_name": forms.TextInput(
#                 attrs={"class": "form-control", "placeholder": _("Nom")}
#             ),
#             "phone": forms.TextInput(
#                 attrs={"class": "form-control", "placeholder": _("Téléphone")}
#             ),
#             # CountryField → Select ISO (django-countries)
#             "country_of_residence": forms.Select(
#                 attrs={"class": "form-select"}
#             ),
#             "message": forms.Textarea(
#                 attrs={
#                     "class": "form-control",
#                     "rows": 4,
#                     "placeholder": _("Quelques mots sur vous"),
#                 }
#             ),
#             "judicial_record": forms.ClearableFileInput(
#                 attrs={"class": "form-control"}
#             ),
#             "profile_picture": forms.ClearableFileInput(
#                 attrs={"class": "form-control"}
#             ),
#             "membership_role": forms.Select(
#                 attrs={"class": "form-select"}
#             ),
#         }

#     # --------------------------------------------------
#     # VALIDATIONS
#     # --------------------------------------------------
#     def clean_judicial_record(self):
#         record = self.cleaned_data.get("judicial_record")
#         if record:
#             if not record.name.lower().endswith(".pdf"):
#                 raise forms.ValidationError(_("Le document doit être un fichier PDF."))
#             if record.size > 2 * 1024 * 1024:
#                 raise forms.ValidationError(_("Le fichier ne doit pas dépasser 2 Mo."))
#         return record

#     def clean_phone(self):
#         phone = self.cleaned_data.get("phone", "")
#         if phone and not phone.replace("+", "").isdigit():
#             raise forms.ValidationError(
#                 _("Le téléphone doit contenir uniquement des chiffres.")
#             )
#         return phone






# # # ✅ 1. dashboard/forms/profile_form.py
# from django import forms
# from accounts_users.models.users_profile import UserProfile
# from django.utils.translation import gettext_lazy as _

# class ProfileUpdateForm(forms.ModelForm):
#     class Meta:
#         model = UserProfile
#         fields = [
#             "full_name",
#             "phone",
#             "country",
#             "message",
#             "judicial_record",
#             "profile_picture",
#             "membership_role",
#         ]
#         labels = {
#             "full_name": _("Nom complet"),
#             "phone": _("Téléphone"),
#             "country": _("Pays"),
#             "message": _("Message personnel"),
#             "judicial_record": _("Casier judiciaire (PDF)"),
#             "profile_picture": _("Photo de profil"),
#             "membership_role": _("Type d’adhésion"),
#         }
#         widgets = {
#             "full_name": forms.TextInput(attrs={"class": "form-control", "placeholder": _("Nom complet")}),
#             "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": _("Téléphone")}),
#             "country": forms.TextInput(attrs={"class": "form-control", "placeholder": _("Pays")}),
#             "message": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": _("Quelques mots sur vous")}),
#             "judicial_record": forms.ClearableFileInput(attrs={"class": "form-control"}),
#             "profile_picture": forms.ClearableFileInput(attrs={"class": "form-control"}),
#             "membership_role": forms.Select(attrs={"class": "form-select"}),
#         }

#     def clean_judicial_record(self):
#         record = self.cleaned_data.get("judicial_record")
#         if record:
#             if not record.name.lower().endswith('.pdf'):
#                 raise forms.ValidationError(_("Le document doit être un fichier PDF."))
#             if record.size > 2 * 1024 * 1024:
#                 raise forms.ValidationError(_("Le fichier ne doit pas dépasser 2 Mo."))
#         return record

#     def clean_phone(self):
#         phone = self.cleaned_data.get("phone", "")
#         if phone and not phone.isdigit():
#             raise forms.ValidationError(_("Le téléphone doit contenir uniquement des chiffres."))
#         return phone





# from django import forms
# from accounts_users.models.users_profile import UserProfile
# from django.utils.translation import gettext_lazy as _

# class ProfileUpdateForm(forms.ModelForm):
#     class Meta:
#         model = UserProfile
#         fields = [
#             "full_name", "phone", "country", "message",
#             "judicial_record", "profile_picture", "membership_role"
#         ]
#         widgets = {
#             "full_name": forms.TextInput(attrs={"class": "form-control"}),
#             "phone": forms.TextInput(attrs={"class": "form-control"}),
#             "country": forms.TextInput(attrs={"class": "form-control"}),
#             "message": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
#             "judicial_record": forms.ClearableFileInput(attrs={"class": "form-control"}),
#             "profile_picture": forms.ClearableFileInput(attrs={"class": "form-control"}),
#             "membership_role": forms.Select(attrs={"class": "form-select"}),
#         }