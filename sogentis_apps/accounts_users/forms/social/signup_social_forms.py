# # accounts_users/forms/social_signup_forms.py 21/12/2025
# from django import forms
# from django.utils.translation import gettext_lazy as _
# from django.core.exceptions import ValidationError

# from django_countries.widgets import CountrySelectWidget

# from accounts_users.models.custom_users import CustomUser
# from accounts_users.models.users_economic_profile import UserProfile


# # ======================================================
# # USER (AUTH)
# # ======================================================
# class UserSignupForm(forms.ModelForm):
#     password = forms.CharField(
#         label=_("Mot de passe"),
#         widget=forms.PasswordInput(attrs={"class": "form-control"}),
#     )
#     password_confirm = forms.CharField(
#         label=_("Confirmation du mot de passe"),
#         widget=forms.PasswordInput(attrs={"class": "form-control"}),
#     )

#     class Meta:
#         model = CustomUser
#         fields = ["email", "username"]
#         widgets = {
#             "email": forms.EmailInput(attrs={"class": "form-control"}),
#             "username": forms.TextInput(attrs={"class": "form-control"}),
#         }

#     def clean(self):
#         cleaned = super().clean()
#         if cleaned.get("password") != cleaned.get("password_confirm"):
#             raise ValidationError(_("Les mots de passe ne correspondent pas."))
#         return cleaned

#     def clean_email(self):
#         email = self.cleaned_data["email"]
#         if CustomUser.objects.filter(email=email).exists():
#             raise ValidationError(_("Cette adresse e-mail est déjà utilisée."))
#         return email

#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user.set_password(self.cleaned_data["password"])
#         if commit:
#             user.save()
#         return user


# # ======================================================
# # PROFIL SOCIAL (INSCRIPTION SOCIALE)
# # ======================================================
# class UserProfileForm(forms.ModelForm):
#     """
#     Formulaire Profil social.
#     - CountryField verrouillé ISO alpha-2
#     - Validation défensive serveur
#     """

#     terms = forms.BooleanField(
#         label=_("J’accepte les conditions générales"),
#         required=True,
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
#             # CONTACT / PRO
#             # =========================
#             "phone",
#             "profession",
#             "function",

#             # =========================
#             # SOCIAL
#             # =========================
#             "membership_role",

#             # =========================
#             # FICHIERS
#             # =========================
#             "profile_picture",
#             "judicial_record",

#             # =========================
#             # MESSAGE
#             # =========================
#             "message",
#         ]

#         widgets = {
#             # -------- Identité --------
#             "last_name": forms.TextInput(attrs={"class": "form-control"}),
#             "first_name": forms.TextInput(attrs={"class": "form-control"}),
#             "middle_names": forms.TextInput(attrs={"class": "form-control"}),
#             "nickname": forms.TextInput(attrs={"class": "form-control"}),

#             # -------- Naissance --------
#             "date_of_birth": forms.DateInput(attrs={
#                 "type": "date",
#                 "class": "form-control",
#             }),
#             "place_of_birth": forms.TextInput(attrs={"class": "form-control"}),
#             "country_of_birth": CountrySelectWidget(attrs={
#                 "class": "form-select",
#             }),

#             # -------- Résidence --------
#             "country_of_residence": CountrySelectWidget(attrs={
#                 "class": "form-select",
#             }),
#             "city_of_residence": forms.TextInput(attrs={"class": "form-control"}),
#             "address": forms.Textarea(attrs={
#                 "rows": 2,
#                 "class": "form-control",
#             }),

#             # -------- Contact / Pro --------
#             "phone": forms.TextInput(attrs={"class": "form-control"}),
#             "profession": forms.TextInput(attrs={"class": "form-control"}),
#             "function": forms.TextInput(attrs={"class": "form-control"}),

#             # -------- Social --------
#             "membership_role": forms.Select(attrs={"class": "form-select"}),

#             # -------- Fichiers --------
#             "profile_picture": forms.ClearableFileInput(attrs={"class": "form-control"}),
#             "judicial_record": forms.ClearableFileInput(attrs={"class": "form-control"}),

#             # -------- Message --------
#             "message": forms.Textarea(attrs={
#                 "rows": 3,
#                 "class": "form-control",
#             }),
#         }

#     # ======================================================
#     # VALIDATIONS DÉFENSIVES (CRITIQUES)
#     # ======================================================

#     def clean_country_of_birth(self):
#         value = self.cleaned_data.get("country_of_birth")
#         if value and len(value) != 2:
#             raise ValidationError(_("Pays de naissance invalide."))
#         return value

#     def clean_country_of_residence(self):
#         value = self.cleaned_data.get("country_of_residence")
#         if value and len(value) != 2:
#             raise ValidationError(_("Pays de résidence invalide."))
#         return value

#     def clean_judicial_record(self):
#         file = self.cleaned_data.get("judicial_record")
#         if file:
#             content_type = getattr(file, "content_type", "") or ""
#             if content_type != "application/pdf":
#                 raise ValidationError(_("Le fichier doit être un PDF."))
#             if file.size > 2 * 1024 * 1024:
#                 raise ValidationError(_("Le fichier ne doit pas dépasser 2 Mo."))
#         return file











# # accounts_users/forms/social_signup_forms.py November 2025
# from django import forms
# from django.utils.translation import gettext_lazy as _
# from django.core.exceptions import ValidationError

# from accounts_users.models.users import CustomUser
# from accounts_users.models.users_profile import UserProfile


# class UserSignupForm(forms.ModelForm):
#     username = forms.CharField(
#         label=_("Nom d'utilisateur"),
#         required=True,
#         widget=forms.TextInput(attrs={"class": "form-control", "placeholder": _("Nom d'utilisateur")}),
#     )
#     password = forms.CharField(
#         label=_("Créer un mot de passe"),
#         widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": _("Mot de passe")}),
#     )
#     password_confirm = forms.CharField(
#         label=_("Confirmer le mot de passe"),
#         widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": _("Confirmer le mot de passe")}),
#     )

#     class Meta:
#         model = CustomUser
#         fields = ["email", "username"]
#         widgets = {
#             "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": _("Adresse e-mail")}),
#         }

#     def clean(self):
#         cleaned_data = super().clean()
#         password = cleaned_data.get("password")
#         password_confirm = cleaned_data.get("password_confirm")
#         if password and password_confirm and password != password_confirm:
#             self.add_error("password_confirm", _("Les mots de passe ne correspondent pas."))
#         return cleaned_data

#     def clean_email(self):
#         email = self.cleaned_data.get("email")
#         if CustomUser.objects.filter(email=email).exists():
#             raise ValidationError(_("Un compte avec cette adresse e-mail existe déjà."))
#         return email

#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user.set_password(self.cleaned_data["password"])
#         if commit:
#             user.save()
#         return user


# class UserProfileForm(forms.ModelForm):
#     terms = forms.BooleanField(label=_("J'accepte les conditions générales"), required=True)

#     class Meta:
#         model = UserProfile
#         fields = [
#             "full_name",
#             "phone",
#             "country",
#             "membership_role",
#             "profile_picture",
#             "judicial_record",
#             "message",
#         ]
#         widgets = {
#             "full_name": forms.TextInput(attrs={"class": "form-control", "placeholder": _("Nom complet")}),
#             "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": _("Téléphone")}),
#             "membership_role": forms.Select(attrs={"class": "form-select"}),
#             "profile_picture": forms.ClearableFileInput(attrs={"class": "form-control"}),
#             "judicial_record": forms.ClearableFileInput(attrs={"class": "form-control"}),
#             "message": forms.Textarea(attrs={"class": "form-control", "placeholder": _("Message"), "rows": 4}),
#         }

#     def clean_judicial_record(self):
#         file = self.cleaned_data.get("judicial_record")
#         if file:
#             if file.content_type != "application/pdf":
#                 raise forms.ValidationError(_("Le fichier doit être au format PDF."))
#             if file.size > 2 * 1024 * 1024:
#                 raise forms.ValidationError(_("Le fichier ne doit pas dépasser 2 Mo."))
#         return file







# from django import forms
# from django.utils.translation import gettext_lazy as _
# from django.core.exceptions import ValidationError

# from accounts_users.models.users_profile import UserProfile


# class SocialProfileSignupForm(forms.ModelForm):
#     """
#     Formulaire STRICTEMENT réservé au pôle social.
#     Totalement isolé de l'économique.
#     """

#     terms = forms.BooleanField(
#         label=_("J'accepte les conditions générales"),
#         required=True
#     )

#     class Meta:
#         model = UserProfile
#         fields = [
#             "full_name",
#             "phone",
#             "country",
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
#                 raise ValidationError(_("Le fichier doit être au format PDF."))
#             if file.size > 2 * 1024 * 1024:
#                 raise ValidationError(_("Le fichier ne doit pas dépasser 2 Mo."))
#         return file
