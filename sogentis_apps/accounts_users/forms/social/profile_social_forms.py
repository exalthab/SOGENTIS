# # accounts_users/forms/profile_social_forms.py 21/12/2025 error
# from django import forms
# from django.utils.translation import gettext_lazy as _
# from django.contrib.auth import get_user_model

# from django_countries.widgets import CountrySelectWidget

# from accounts_users.models.users_economic_profile import UserProfile


# User = get_user_model()


# class UserProfileForm(forms.ModelForm):
#     """
#     Formulaire Profil utilisateur.
#     - Utilisé pour l'inscription ET l'édition de profil.
#     - CountryField sécurisé (ISO alpha-2 uniquement).
#     - Validation défensive serveur incluse.
#     """

#     terms = forms.BooleanField(
#         label=_("J'accepte les conditions générales"),
#         required=False,
#     )

#     class Meta:
#         model = UserProfile
#         fields = [
#             # =========================
#             # IDENTITÉ
#             # =========================
#             "last_name",
#             "first_name",
#             "middle_names",
#             "nickname",

#             # =========================
#             # NAISSANCE
#             # =========================
#             "date_of_birth",
#             "place_of_birth",
#             "country_of_birth",

#             # =========================
#             # RÉSIDENCE
#             # =========================
#             "country_of_residence",
#             "city_of_residence",
#             "address",

#             # =========================
#             # CONTACT / SOCIAL
#             # =========================
#             "phone",
#             "membership_role",

#             # =========================
#             # PIÈCES
#             # =========================
#             "profile_picture",
#             "judicial_record",

#             # =========================
#             # DIVERS
#             # =========================
#             "message",
#         ]

#         widgets = {
#             # -------- Identité --------
#             "last_name": forms.TextInput(attrs={
#                 "class": "form-control",
#                 "placeholder": _("Nom"),
#             }),
#             "first_name": forms.TextInput(attrs={
#                 "class": "form-control",
#                 "placeholder": _("Prénom"),
#             }),
#             "middle_names": forms.TextInput(attrs={
#                 "class": "form-control",
#                 "placeholder": _("Autres noms"),
#             }),
#             "nickname": forms.TextInput(attrs={
#                 "class": "form-control",
#                 "placeholder": _("Surnom"),
#             }),

#             # -------- Naissance --------
#             "date_of_birth": forms.DateInput(attrs={
#                 "type": "date",
#                 "class": "form-control",
#             }),
#             "place_of_birth": forms.TextInput(attrs={
#                 "class": "form-control",
#                 "placeholder": _("Lieu de naissance"),
#             }),
#             "country_of_birth": CountrySelectWidget(attrs={
#                 "class": "form-select",
#             }),

#             # -------- Résidence --------
#             "country_of_residence": CountrySelectWidget(attrs={
#                 "class": "form-select",
#             }),
#             "city_of_residence": forms.TextInput(attrs={
#                 "class": "form-control",
#                 "placeholder": _("Ville de résidence"),
#             }),
#             "address": forms.Textarea(attrs={
#                 "class": "form-control",
#                 "rows": 2,
#                 "placeholder": _("Adresse"),
#             }),

#             # -------- Contact --------
#             "phone": forms.TextInput(attrs={
#                 "class": "form-control",
#                 "placeholder": _("Téléphone"),
#             }),
#             "membership_role": forms.Select(attrs={
#                 "class": "form-select",
#             }),

#             # -------- Pièces --------
#             "profile_picture": forms.ClearableFileInput(attrs={
#                 "class": "form-control",
#             }),
#             "judicial_record": forms.ClearableFileInput(attrs={
#                 "class": "form-control",
#             }),

#             # -------- Divers --------
#             "message": forms.Textarea(attrs={
#                 "class": "form-control",
#                 "rows": 4,
#                 "placeholder": _("Message"),
#             }),
#         }

#     def __init__(self, *args, require_terms: bool = False, **kwargs):
#         """
#         require_terms=True => utilisé UNIQUEMENT à l'inscription.
#         """
#         super().__init__(*args, **kwargs)

#         if require_terms:
#             self.fields["terms"].required = True

#     # ======================================================
#     # VALIDATIONS DÉFENSIVES (CRITIQUE)
#     # ======================================================

#     def clean_country_of_birth(self):
#         value = self.cleaned_data.get("country_of_birth")
#         if value and len(value) != 2:
#             raise forms.ValidationError(_("Pays de naissance invalide."))
#         return value

#     def clean_country_of_residence(self):
#         value = self.cleaned_data.get("country_of_residence")
#         if value and len(value) != 2:
#             raise forms.ValidationError(_("Pays de résidence invalide."))
#         return value

#     def clean_judicial_record(self):
#         file = self.cleaned_data.get("judicial_record")
#         if file:
#             content_type = getattr(file, "content_type", "") or ""
#             if content_type != "application/pdf":
#                 raise forms.ValidationError(_("Le fichier doit être au format PDF."))
#             if file.size > 2 * 1024 * 1024:
#                 raise forms.ValidationError(_("Le fichier ne doit pas dépasser 2 Mo."))
#         return file









# # accounts_users/forms/profile_forms.py November 2025

# from django import forms
# from django.utils.translation import gettext_lazy as _
# from django.contrib.auth import get_user_model

# from accounts_users.models.users_profile import UserProfile


# class UserProfileForm(forms.ModelForm):
#     terms = forms.BooleanField(
#         label=_("J'accepte les conditions générales"),
#         required=True
#     )

#     class Meta:
#         model = UserProfile
#         fields = [
#             "full_name",
#             "phone",
#             # "country",
#             # "email",  # à activer si nécessaire
#             "membership_role",
#             "profile_picture",
#             "judicial_record",
#             "message",
#         ]
#         widgets = {
#             "full_name": forms.TextInput(
#                 attrs={"class": "form-control", "placeholder": _("Nom complet")}
#             ),
#             "phone": forms.TextInput(
#                 attrs={"class": "form-control", "placeholder": _("Téléphone")}
#             ),
#             "country": forms.TextInput(
#                 attrs={"class": "form-control", "placeholder": _("Pays")}
#             ),
#             "membership_role": forms.Select(
#                 attrs={"class": "form-select"}
#             ),
#             "profile_picture": forms.ClearableFileInput(
#                 attrs={"class": "form-control"}
#             ),
#             "judicial_record": forms.ClearableFileInput(
#                 attrs={"class": "form-control"}
#             ),
#             "message": forms.Textarea(
#                 attrs={
#                     "class": "form-control",
#                     "placeholder": _("Message"),
#                     "rows": 4,
#                 }
#             ),
#         }

#     def clean_judicial_record(self):
#         file = self.cleaned_data.get("judicial_record")
#         if file:
#             if file.content_type != "application/pdf":
#                 raise forms.ValidationError(
#                     _("Le fichier doit être au format PDF.")
#                 )
#             if file.size > 2 * 1024 * 1024:
#                 raise forms.ValidationError(
#                     _("Le fichier ne doit pas dépasser 2 Mo.")
#                 )
#         return file


# User = get_user_model()


# class UserProfileForm(forms.ModelForm):
#     class Meta:
#         model = UserProfile
#         fields = [
#             "full_name",
#             "phone",
#             # "country",
#             "membership_role",
#             "profile_picture",
#             "judicial_record",
#             "message",
#         ]








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