# # accounts_users/forms/social/social_signup_forms.py

# from django import forms
# from django.utils.translation import gettext_lazy as _
# from django.core.exceptions import ValidationError

# from accounts_users.models.custom_users import CustomUser

# # ======================================================
# # FORMULAIRE UTILISATEUR (AUTH / INSCRIPTION PUBLIQUE)
# # ======================================================
# class UserSignupForm(forms.ModelForm):
#     """
#     Formulaire de création de COMPTE UTILISATEUR.
#     - Utilisé pour :
#         • inscription sociale (publique)
#         • inscription économique
#     - Ne gère PAS les profils (social / économique)
#     """

#     password = forms.CharField(
#         label=_("Mot de passe"),
#         widget=forms.PasswordInput(
#             attrs={
#                 "class": "form-control",
#                 "placeholder": _("Mot de passe"),
#                 "autocomplete": "new-password",
#             } 
#         ),
#         strip=False,
#     )

#     password_confirm = forms.CharField(
#         label=_("Confirmation du mot de passe"),
#         widget=forms.PasswordInput(
#             attrs={
#                 "class": "form-control",
#                 "placeholder": _("Confirmer le mot de passe"),
#                 "autocomplete": "new-password",
#             }
#         ),
#         strip=False,
#     )

#     class Meta:
#         model = CustomUser
#         fields = [
#             "email",
#             "username",
#         ]

#         widgets = {
#             "email": forms.EmailInput(
#                 attrs={
#                     "class": "form-control",
#                     "placeholder": _("Adresse e-mail"),
#                     "autocomplete": "email",
#                 }
#             ),
#             "username": forms.TextInput(
#                 attrs={
#                     "class": "form-control",
#                     "placeholder": _("Nom d’utilisateur"),
#                     "autocomplete": "username",
#                 }
#             ),
#         }

#     # ==================================================
#     # VALIDATIONS
#     # ==================================================
#     def clean(self):
#         """
#         Validation croisée des mots de passe.
#         """
#         cleaned_data = super().clean()

#         password = cleaned_data.get("password")
#         password_confirm = cleaned_data.get("password_confirm")

#         if password and password_confirm and password != password_confirm:
#             self.add_error(
#                 "password_confirm",
#                 _("Les mots de passe ne correspondent pas.")
#             )

#         return cleaned_data

#     def clean_email(self):
#         """
#         Email obligatoire, unique et normalisé.
#         """
#         email = self.cleaned_data.get("email")

#         if not email:
#             raise ValidationError(_("L’adresse e-mail est obligatoire."))

#         email = email.lower().strip()

#         if CustomUser.objects.filter(email=email).exists():
#             raise ValidationError(
#                 _("Cette adresse e-mail est déjà utilisée.")
#             )

#         return email

#     def clean_username(self):
#         """
#         Nom d'utilisateur obligatoire et unique.
#         """
#         username = self.cleaned_data.get("username")

#         if not username:
#             raise ValidationError(_("Le nom d’utilisateur est obligatoire."))

#         if CustomUser.objects.filter(username=username).exists():
#             raise ValidationError(
#                 _("Ce nom d’utilisateur est déjà utilisé.")
#             )

#         return username

#     # ==================================================
#     # SAVE
#     # ==================================================
#     def save(self, commit=True):
#         """
#         - Crée l’utilisateur
#         - Hash le mot de passe
#         - Aucune logique métier (social / économique)
#         """
#         user = super().save(commit=False)
#         user.set_password(self.cleaned_data["password"])

#         if commit:
#             user.save()

#         return user
