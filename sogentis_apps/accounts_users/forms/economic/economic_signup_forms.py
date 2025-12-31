# accounts_users/forms/economic/economic_signup_forms.py
from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from accounts_users.models.economic.client_profile import ClientProfile
from accounts_users.models.economic.vendor_profile import VendorProfile
from accounts_users.models.economic.company_profile import CompanyProfile


# ======================================================
# HELPERS (prod)
# ======================================================

def validate_pdf(file, *, max_mb=2, required=False, label=_("Le fichier")):
    if not file:
        if required:
            raise ValidationError(_("%(label)s est requis.") % {"label": label})
        return file

    content_type = getattr(file, "content_type", "") or ""
    # certains serveurs peuvent ne pas renseigner content_type -> on tolère
    if content_type and content_type != "application/pdf":
        raise ValidationError(_("Le fichier doit être un PDF."))

    if file.size > max_mb * 1024 * 1024:
        raise ValidationError(_("Le fichier ne doit pas dépasser %(mb)s Mo.") % {"mb": max_mb})

    return file


# ======================================================
# CLIENT (B2C)
# ======================================================

class ClientSignupForm(forms.ModelForm):
    class Meta:
        model = ClientProfile
        fields = ["address", "city", "postal_code"]
        labels = {
            "address": _("Adresse"),
            "city": _("Ville"),
            "postal_code": _("Code postal"),
        }
        widgets = {
            "address": forms.TextInput(attrs={"class": "form-control"}),
            "city": forms.TextInput(attrs={"class": "form-control"}),
            "postal_code": forms.TextInput(attrs={"class": "form-control"}),
        }


# ======================================================
# VENDEUR
# ======================================================

class VendorSignupForm(forms.ModelForm):
    class Meta:
        model = VendorProfile
        fields = [
            "business_name",
            "ninea",
            "business_address",
            "postal_code",
            "trade_register_document",
        ]
        labels = {
            "business_name": _("Nom commercial"),
            "ninea": _("NINEA / Identifiant commercial"),
            "business_address": _("Adresse de l’activité"),
            "postal_code": _("Code postal"),
            "trade_register_document": _("Registre de commerce / document légal"),
        }
        widgets = {
            "business_name": forms.TextInput(attrs={"class": "form-control"}),
            "ninea": forms.TextInput(attrs={"class": "form-control", "autocomplete": "off"}),
            "business_address": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "postal_code": forms.TextInput(attrs={"class": "form-control"}),
            "trade_register_document": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }

    def clean_ninea(self):
        ninea = (self.cleaned_data.get("ninea") or "").strip().upper().replace(" ", "")
        if not ninea:
            raise ValidationError(_("Le NINEA est requis."))
        return ninea

    def clean_trade_register_document(self):
        f = self.cleaned_data.get("trade_register_document")
        return validate_pdf(f, max_mb=2, required=True, label=_("Le registre de commerce"))


# ======================================================
# ENTREPRISE / B2B
# ======================================================

class CompanySignupForm(forms.ModelForm):
    class Meta:
        model = CompanyProfile
        fields = [
            "company_name",
            "owner_name",
            "company_address",
            "postal_code",
            "registration_document",
            "financial_document",
        ]
        labels = {
            "company_name": _("Nom de la société"),
            "owner_name": _("Représentant légal"),
            "company_address": _("Adresse de la société"),
            "postal_code": _("Code postal"),
            "registration_document": _("Document d’enregistrement légal"),
            "financial_document": _("Attestation financière / Good standing"),
        }
        widgets = {
            "company_name": forms.TextInput(attrs={"class": "form-control"}),
            "owner_name": forms.TextInput(attrs={"class": "form-control"}),
            "company_address": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "postal_code": forms.TextInput(attrs={"class": "form-control"}),
            "registration_document": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "financial_document": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }

    def clean_registration_document(self):
        f = self.cleaned_data.get("registration_document")
        return validate_pdf(f, max_mb=2, required=True, label=_("Le document d’enregistrement"))

    def clean_financial_document(self):
        f = self.cleaned_data.get("financial_document")
        return validate_pdf(f, max_mb=2, required=False, label=_("Le document financier"))









# # accounts_users/forms/economic/economic_signup_forms.py 30/12/2025
# from django import forms
# from django.utils.translation import gettext_lazy as _

# from django.core.exceptions import ValidationError
# import re

# from accounts_users.models.economic.client_profile import ClientProfile
# from accounts_users.models.economic.vendor_profile import VendorProfile
# from accounts_users.models.economic.company_profile import CompanyProfile


# # ======================================================
# # CLIENT (B2C)
# # ======================================================

# class ClientSignupForm(forms.ModelForm):
#     password = forms.CharField(
#         widget=forms.PasswordInput(attrs={"class": "form-control"}),
#         label=_("Mot de passe"),
#         min_length=8,  # Optionnel, mais recommandé
#     )
#     confirm_password = forms.CharField(
#         widget=forms.PasswordInput(attrs={"class": "form-control"}),
#         label=_("Confirmer le mot de passe"),
#     )

#     class Meta:
#         model = ClientProfile
#         fields = [
#             # "address",
#             # "city_of_residence",
#             # "postal_code",
#         ]

#         labels = {
#             "address": _("Adresse"),
#             "city": _("Ville"),
#             "postal_code": _("Code postal"),
#         }

#         widgets = {
#             "address": forms.TextInput(attrs={"class": "form-control"}),
#             "city": forms.TextInput(attrs={"class": "form-control"}),
#             "postal_code": forms.TextInput(attrs={"class": "form-control"}),
#         }

#     def clean(self):
#         cleaned = super().clean()
#         if cleaned.get("password") != cleaned.get("password_confirm"):
#             raise ValidationError(_("Les mots de passe ne correspondent pas."))
#         return cleaned

#     def clean_email(self):
#         email = self.cleaned_data["email"]
#         if ClientProfile.objects.filter(email=email).exists():
#             raise ValidationError(_("Cette adresse e-mail est déjà utilisée."))
#         return email

#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user.set_password(self.cleaned_data["password"])
#         if commit:
#             user.save()
#         return user

# # ======================================================
# # VENDEUR
# # ======================================================

# class VendorSignupForm(forms.ModelForm):
#     password = forms.CharField(
#         widget=forms.PasswordInput(attrs={"class": "form-control"}),
#         label=_("Mot de passe"),
#         min_length=8,
#     )
#     confirm_password = forms.CharField(
#         widget=forms.PasswordInput(attrs={"class": "form-control"}),
#         label=_("Confirmer le mot de passe"),
#     )

#     class Meta:
#         model = VendorProfile
#         fields = [
#             "business_name",
#             "ninea",
#             "business_address",
#             "postal_code",
#             "trade_register_document",
#         ]

#         labels = {
#             "business_name": _("Nom commercial"),
#             "ninea": _("NINEA / Identifiant commercial"),
#             "business_address": _("Adresse de l’activité"),
#             "postal_code": _("Code postal"),
#             "trade_register_document": _("Registre de commerce"),
#         }

#         widgets = {
#             "business_name": forms.TextInput(attrs={"class": "form-control"}),
#             "ninea": forms.TextInput(attrs={"class": "form-control"}),
#             "business_address": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
#             "postal_code": forms.TextInput(attrs={"class": "form-control"}),
#             "trade_register_document": forms.ClearableFileInput(attrs={"class": "form-control"}),
#         }

#     def clean(self):
#         cleaned_data = super().clean()
#         password = cleaned_data.get("password")
#         confirm_password = cleaned_data.get("confirm_password")

#         if password != confirm_password:
#             raise forms.ValidationError(_("Les mots de passe ne correspondent pas."))

#         return cleaned_data

    
#     def clean_trade_register_document(self):
#         file = self.cleaned_data.get("trade_register_document")
#         if file:
#             content_type = getattr(file, "content_type", "") or ""
#             if content_type != "application/pdf":
#                 raise ValidationError(_("Le fichier doit être un PDF."))
#             if file.size > 2 * 1024 * 1024:
#                 raise ValidationError(_("Le fichier ne doit pas dépasser 2 Mo."))
#         return file


# # ======================================================
# # ENTREPRISE / B2B
# # ======================================================

# class CompanySignupForm(forms.ModelForm):
#     password = forms.CharField(
#         widget=forms.PasswordInput(attrs={"class": "form-control"}),
#         label=_("Mot de passe"),
#         min_length=8,
#     )
#     confirm_password = forms.CharField(
#         widget=forms.PasswordInput(attrs={"class": "form-control"}),
#         label=_("Confirmer le mot de passe"),
#     )

#     class Meta:
#         model = CompanyProfile
#         fields = [
#             "company_name",
#             "owner_name",
#             "company_address",
#             "postal_code",
#             "registration_document",
#             "financial_document",
#         ]

#         labels = {
#             "company_name": _("Nom de la société"),
#             "owner_name": _("Représentant légal"),
#             "company_address": _("Adresse de la société"),
#             "postal_code": _("Code postal"),
#             "registration_document": _("Document d’enregistrement"),
#             "financial_document": _("Attestation financière / Good standing"),
#         }

#         widgets = {
#             "company_name": forms.TextInput(attrs={"class": "form-control"}),
#             "owner_name": forms.TextInput(attrs={"class": "form-control"}),
#             "company_address": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
#             "postal_code": forms.TextInput(attrs={"class": "form-control"}),
#             "registration_document": forms.ClearableFileInput(attrs={"class": "form-control"}),
#             "financial_document": forms.ClearableFileInput(attrs={"class": "form-control"}),
#         }

#     def clean(self):
#         cleaned_data = super().clean()
#         password = cleaned_data.get("password")
#         confirm_password = cleaned_data.get("confirm_password")

#         if password != confirm_password:
#             raise forms.ValidationError(_("Les mots de passe ne correspondent pas."))

#         return cleaned_data
    
#     def clean_financial_document(self):
#         file = self.cleaned_data.get("financial_document")
#         if file:
#             content_type = getattr(file, "content_type", "") or ""
#             if content_type != "application/pdf":
#                 raise ValidationError(_("Le fichier doit être un PDF."))
#             if file.size > 2 * 1024 * 1024:
#                 raise ValidationError(_("Le fichier ne doit pas dépasser 2 Mo."))
#         return file


#     def clean_registration_document(self):
#         file = self.cleaned_data.get("registration_document")
#         if file:
#             content_type = getattr(file, "content_type", "") or ""
#             if content_type != "application/pdf":
#                 raise ValidationError(_("Le fichier doit être un PDF."))
#             if file.size > 2 * 1024 * 1024:
#                 raise ValidationError(_("Le fichier ne doit pas dépasser 2 Mo."))
#         return file





# # accounts_users/forms/economic_signup_forms.py
# from django import forms
# from django.utils.translation import gettext_lazy as _

# from accounts_users.models.economic.client_profile import ClientProfile
# from accounts_users.models.economic.vendor_profile import VendorProfile
# from accounts_users.models.economic.company_profile import CompanyProfile


# # ======================================================
# # CLIENT (B2C)
# # ======================================================

# class ClientSignupForm(forms.ModelForm):
#     class Meta:
#         model = ClientProfile
#         fields = [
#             "address",
#             "city",
#             "postal_code",
#         ]

#         labels = {
#             "address": _("Adresse"),
#             "city": _("Ville"),
#             "postal_code": _("Code postal"),
#         }

#         widgets = {
#             "address": forms.TextInput(
#                 attrs={"class": "form-control"}
#             ),
#             "city": forms.TextInput(
#                 attrs={"class": "form-control"}
#             ),
#             "postal_code": forms.TextInput(
#                 attrs={"class": "form-control"}
#             ),
#         }


# # ======================================================
# # VENDEUR
# # ======================================================

# class VendorSignupForm(forms.ModelForm):
#     class Meta:
#         model = VendorProfile
#         fields = [
#             "business_name",
#             "ninea",
#             "business_address",
#             "postal_code",
#             "trade_register_document",
#         ]

#         labels = {
#             "business_name": _("Nom commercial"),
#             "ninea": _("NINEA / Identifiant commercial"),
#             "business_address": _("Adresse de l’activité"),
#             "postal_code": _("Code postal"),
#             "trade_register_document": _("Registre de commerce"),
#         }

#         widgets = {
#             "business_name": forms.TextInput(attrs={"class": "form-control"}),
#             "ninea": forms.TextInput(attrs={"class": "form-control"}),
#             "business_address": forms.Textarea(
#                 attrs={"class": "form-control", "rows": 3}
#             ),
#             "postal_code": forms.TextInput(
#                 attrs={"class": "form-control"}
#             ),
#             "trade_register_document": forms.ClearableFileInput(
#                 attrs={"class": "form-control"}
#             ),
#         }

#     def clean_ninea(self):
#         ninea = (self.cleaned_data.get("ninea") or "").strip()
#         if len(ninea) < 8:
#             raise forms.ValidationError(_("NINEA invalide."))
#         return ninea


# # ======================================================
# # ENTREPRISE / B2B
# # ======================================================

# class CompanySignupForm(forms.ModelForm):
#     class Meta:
#         model = CompanyProfile
#         fields = [
#             "company_name",
#             "owner_name",
#             "company_address",
#             "postal_code",                  # ✅ AJOUT
#             "registration_document",
#             "financial_document",
#         ]

#         labels = {
#             "company_name": _("Nom de la société"),
#             "owner_name": _("Représentant légal"),
#             "company_address": _("Adresse de la société"),
#             "postal_code": _("Code postal"),
#             "registration_document": _("Document d’enregistrement"),
#             "financial_document": _("Attestation financière / Good standing"),
#         }

#         widgets = {
#             "company_name": forms.TextInput(attrs={"class": "form-control"}),
#             "owner_name": forms.TextInput(attrs={"class": "form-control"}),
#             "company_address": forms.Textarea(
#                 attrs={"class": "form-control", "rows": 3}
#             ),
#             "postal_code": forms.TextInput(
#                 attrs={"class": "form-control"}
#             ),
#             "registration_document": forms.ClearableFileInput(
#                 attrs={"class": "form-control"}
#             ),
#             "financial_document": forms.ClearableFileInput(
#                 attrs={"class": "form-control"}
#             ),
#         }








# # accounts_users/forms/economic_signup_forms.py 21/12/2025 error
# from django import forms
# from django.utils.translation import gettext_lazy as _

# from accounts_users.models.economic.client_profile import ClientProfile
# from accounts_users.models.economic.vendor_profile import VendorProfile
# from accounts_users.models.economic.company_profile import CompanyProfile


# # ======================================================
# # CLIENT (B2C)
# # ======================================================

# class ClientSignupForm(forms.ModelForm):
#     class Meta:
#         model = ClientProfile
#         fields = [
#             "address",
#             "city",
#             "postal_code",
#         ]

#         labels = {
#             "address": _("Adresse"),
#             "city": _("Ville"),
#             "postal_code": _("Code postal"),
#         }

#         widgets = {
#             "address": forms.TextInput(
#                 attrs={"class": "form-control", "placeholder": _("Adresse complète")}
#             ),
#             "city": forms.TextInput(
#                 attrs={"class": "form-control", "placeholder": _("Ville")}
#             ),
#             "postal_code": forms.TextInput(
#                 attrs={"class": "form-control", "placeholder": _("Code postal")}
#             ),
#         }


# # ======================================================
# # VENDEUR
# # ======================================================

# class VendorSignupForm(forms.ModelForm):
#     class Meta:
#         model = VendorProfile
#         fields = [
#             "business_name",
#             "ninea",
#             "business_address",
#             "trade_register_document",
#         ]

#         labels = {
#             "business_name": _("Nom commercial"),
#             "ninea": _("NINEA / Identifiant commercial"),
#             "business_address": _("Adresse de l’activité"),
#             "trade_register_document": _("Registre de commerce"),
#         }

#         widgets = {
#             "business_name": forms.TextInput(
#                 attrs={"class": "form-control"}
#             ),
#             "ninea": forms.TextInput(
#                 attrs={"class": "form-control"}
#             ),
#             "business_address": forms.Textarea(
#                 attrs={"class": "form-control", "rows": 3}
#             ),
#             "trade_register_document": forms.ClearableFileInput(
#                 attrs={"class": "form-control"}
#             ),
#         }

#     def clean_ninea(self):
#         ninea = (self.cleaned_data.get("ninea") or "").strip()
#         if len(ninea) < 8:
#             raise forms.ValidationError(_("NINEA invalide."))
#         return ninea


# # ======================================================
# # ENTREPRISE / B2B
# # ======================================================

# class CompanySignupForm(forms.ModelForm):
#     class Meta:
#         model = CompanyProfile
#         fields = [
#             "company_name",
#             "owner_name",
#             "company_address",
#             "registration_document",
#             "financial_document",
#         ]

#         labels = {
#             "company_name": _("Nom de la société"),
#             "owner_name": _("Représentant légal"),
#             "company_address": _("Adresse de la société"),
#             "registration_document": _("Document d’enregistrement"),
#             "financial_document": _("Attestation financière / Good standing"),
#         }

#         widgets = {
#             "company_name": forms.TextInput(
#                 attrs={"class": "form-control"}
#             ),
#             "owner_name": forms.TextInput(
#                 attrs={"class": "form-control"}
#             ),
#             "company_address": forms.Textarea(
#                 attrs={"class": "form-control", "rows": 3}
#             ),
#             "registration_document": forms.ClearableFileInput(
#                 attrs={"class": "form-control"}
#             ),
#             "financial_document": forms.ClearableFileInput(
#                 attrs={"class": "form-control"}
#             ),
#         }











# # accounts_users/forms/economic_signup_forms.py Novembre 2025
# from django import forms
# from django.utils.translation import gettext_lazy as _

# from accounts_users.models.economic.client_profile import ClientProfile
# from accounts_users.models.economic.vendor_profile import VendorProfile
# from accounts_users.models.economic.company_profile import CompanyProfile


# class ClientSignupForm(forms.ModelForm):
#     class Meta:
#         model = ClientProfile
#         fields = [
#             "address",
#             "city",
#             "postal_code",
#         ]

#         labels = {
#             "address": _("Adresse"),
#             "city": _("Ville"),
#             "postal_code": _("Code postal"),
#         }

#         widgets = {
#             "address": forms.TextInput(attrs={"placeholder": _("Adresse complète")}),
#             "city": forms.TextInput(attrs={"placeholder": _("Ville")}),
#             "postal_code": forms.TextInput(attrs={"placeholder": _("Code postal")}),
#         }

# from django import forms
# from django.utils.translation import gettext_lazy as _

# from accounts_users.models.economic.vendor_profile import VendorProfile


# class VendorSignupForm(forms.ModelForm):
#     class Meta:
#         model = VendorProfile
#         fields = [
#             "business_name",
#             "ninea",
#             "business_address",
#             "trade_register_document",  # ✅ IMPORTANT : nom réel du modèle
#         ]
#         labels = {
#             "business_name": _("Nom commercial"),
#             "ninea": _("NINEA / Identifiant commercial"),
#             "business_address": _("Adresse de l’activité"),
#             "trade_register_document": _("Registre de commerce"),
#         }
#         widgets = {
#             "business_name": forms.TextInput(attrs={"class": "form-control"}),
#             "ninea": forms.TextInput(attrs={"class": "form-control"}),
#             "business_address": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
#             "trade_register_document": forms.ClearableFileInput(attrs={"class": "form-control"}),
#         }

#     def clean_ninea(self):
#         ninea = (self.cleaned_data.get("ninea") or "").strip()
#         if len(ninea) < 8:
#             raise forms.ValidationError(_("NINEA invalide."))
#         return ninea


# class CompanySignupForm(forms.ModelForm):
#     class Meta:
#         model = CompanyProfile
#         fields = [
#             "company_name",
#             "owner_name",
#             "company_address",
#             "registration_document",
#             "financial_document",
#         ]

#         labels = {
#             "company_name": _("Nom de la société"),
#             "owner_name": _("Propriétaire / Gérant"),
#             "company_address": _("Adresse de la société"),
#             "registration_document": _("Document d’enregistrement"),
#             "financial_document": _("Attestation financière"),
#         }

#         widgets = {
#             "company_name": forms.TextInput(),
#             "owner_name": forms.TextInput(),
#             "company_address": forms.Textarea(attrs={"rows": 3}),
#         }    







