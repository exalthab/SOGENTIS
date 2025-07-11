# accounts_users/forms/profile_forms.py
from django import forms
from django.utils.translation import gettext_lazy as _
from accounts_users.models.users_profile import UserProfile

class UserProfileForm(forms.ModelForm):
    terms = forms.BooleanField(
        label=_("J'accepte les conditions générales"),
        required=True
    )

    class Meta:
        model = UserProfile
        fields = [
            "full_name",
            "phone",
            "country",
            "membership_role",
            "profile_picture",
            "judicial_record",
            "message",
        ]
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control", "placeholder": _("Nom complet")}),
            "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": _("Téléphone")}),
            # "country": forms.TextInput(attrs={"class": "form-control", "placeholder": _("Pays")}),
            "membership_role": forms.Select(attrs={"class": "form-select"}),
            "profile_picture": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "judicial_record": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "message": forms.Textarea(attrs={"class": "form-control", "placeholder": _("Message"), "rows": 4}),
        }

    def clean_judicial_record(self):
        file = self.cleaned_data.get("judicial_record")
        if file:
            if file.content_type != "application/pdf":
                raise forms.ValidationError(_("Le fichier doit être au format PDF."))
            if file.size > 2 * 1024 * 1024:
                raise forms.ValidationError(_("Le fichier ne doit pas dépasser 2 Mo."))
        return file









# # accounts_users/forms/profile_forms.py
# from django import forms
# from accounts_users.models.users_profile import UserProfile


# class UserProfileForm(forms.ModelForm):
#     judicial_record = forms.FileField(
#         required=True,
#         label="Casier judiciaire (PDF, max 2 Mo)",
#         help_text="Format PDF uniquement. Taille maximale : 2 Mo.",
#         widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
#     )

#     class Meta:
#         model = UserProfile
#         fields = [
#             'full_name',
#             'phone',
#             'country',
#             'message',
#             'judicial_record',
#             'role',
#             'membership_role'
#         ]
#         widgets = {
#             'full_name': forms.TextInput(attrs={'placeholder': 'Nom complet', 'class': 'form-control'}),
#             'phone': forms.TextInput(attrs={'placeholder': 'Téléphone', 'class': 'form-control'}),
#             'country': forms.TextInput(attrs={'placeholder': 'Pays', 'class': 'form-control'}),
#             'message': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Message', 'class': 'form-control'}),
#             'role': forms.Select(attrs={'class': 'form-select'}),
#             'membership_role': forms.Select(attrs={'class': 'form-select'}),
#         }

#     def clean_judicial_record(self):
#         file = self.cleaned_data.get('judicial_record')
#         if file:
#             if file.content_type != 'application/pdf':
#                 raise forms.ValidationError("Le fichier doit être au format PDF.")
#             if file.size > 2 * 1024 * 1024:
#                 raise forms.ValidationError("Le fichier ne doit pas dépasser 2 Mo.")
#         return file








# # from django import forms
# # from accounts_users.models.users_profile import UserProfile


# # class UserProfileForm(forms.ModelForm):
# #     judicial_record = forms.FileField(
# #         required=True,
# #         label="Casier judiciaire (PDF, max 2 Mo)",
# #         help_text="Format PDF uniquement. Taille maximale : 2 Mo."
# #     )

# #     class Meta:
# #         model = UserProfile
# #         fields = [
# #             'full_name',
# #             'phone',
# #             'country',
# #             'message',
# #             'judicial_record',
# #             'role',
# #             'membership_role'
# #         ]
# #         widgets = {
# #             'full_name': forms.TextInput(attrs={'placeholder': 'Nom complet', 'class': 'form-control'}),
# #             'phone': forms.TextInput(attrs={'placeholder': 'Téléphone', 'class': 'form-control'}),
# #             'country': forms.TextInput(attrs={'placeholder': 'Pays', 'class': 'form-control'}),
# #             'message': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Message', 'class': 'form-control'}),
# #             'role': forms.Select(attrs={'class': 'form-select'}),
# #             'membership_role': forms.Select(attrs={'class': 'form-select'}),
# #         }

# #     def clean_judicial_record(self):
# #         file = self.cleaned_data.get('judicial_record')
# #         if file:
# #             if file.content_type != 'application/pdf':
# #                 raise forms.ValidationError("Le fichier doit être au format PDF.")
# #             if file.size > 2 * 1024 * 1024:  # 2 Mo
# #                 raise forms.ValidationError("Le fichier ne doit pas dépasser 2 Mo.")
# #         return file



# # from django import forms
# # from accounts_users.models.users_profile import UserProfile

# # class UserProfileForm(forms.ModelForm):
# #     class Meta:
# #         model = UserProfile
# #         fields = ['full_name', 'phone', 'country', 'message', 'judicial_record', 'role', 'membership_role']
# #         widgets = {
# #             'full_name': forms.TextInput(attrs={'placeholder': 'Nom complet', 'class': 'form-control'}),
# #             'phone': forms.TextInput(attrs={'placeholder': 'Téléphone', 'class': 'form-control'}),
# #             'country': forms.TextInput(attrs={'placeholder': 'Pays', 'class': 'form-control'}),
# #             'message': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Message', 'class': 'form-control'}),
# #             # 'judicial_record': forms.ClearableFileInput(attrs={'class': 'form-control'}),
# #             'judicial_record': forms.FileField(required=True, label="Casier judiciaire"),
# #             'role': forms.Select(attrs={'class': 'form-select'}),
# #             'membership_role': forms.Select(attrs={'class': 'form-select'}),

# #         }