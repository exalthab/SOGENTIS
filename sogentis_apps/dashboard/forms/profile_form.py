# # ✅ 1. dashboard/forms/profile_form.py
from django import forms
from accounts_users.models.users_profile import UserProfile
from django.utils.translation import gettext_lazy as _

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            "full_name",
            "phone",
            "country",
            "message",
            "judicial_record",
            "profile_picture",
            "membership_role",
        ]
        labels = {
            "full_name": _("Nom complet"),
            "phone": _("Téléphone"),
            "country": _("Pays"),
            "message": _("Message personnel"),
            "judicial_record": _("Casier judiciaire (PDF)"),
            "profile_picture": _("Photo de profil"),
            "membership_role": _("Type d’adhésion"),
        }
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control", "placeholder": _("Nom complet")}),
            "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": _("Téléphone")}),
            "country": forms.TextInput(attrs={"class": "form-control", "placeholder": _("Pays")}),
            "message": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": _("Quelques mots sur vous")}),
            "judicial_record": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "profile_picture": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "membership_role": forms.Select(attrs={"class": "form-select"}),
        }

    def clean_judicial_record(self):
        record = self.cleaned_data.get("judicial_record")
        if record:
            if not record.name.lower().endswith('.pdf'):
                raise forms.ValidationError(_("Le document doit être un fichier PDF."))
            if record.size > 2 * 1024 * 1024:
                raise forms.ValidationError(_("Le fichier ne doit pas dépasser 2 Mo."))
        return record

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "")
        if phone and not phone.isdigit():
            raise forms.ValidationError(_("Le téléphone doit contenir uniquement des chiffres."))
        return phone





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