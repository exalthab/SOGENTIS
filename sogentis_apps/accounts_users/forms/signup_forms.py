from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from accounts_users.models.users import CustomUser
from accounts_users.models.users_profile import UserProfile

class UserSignupForm(forms.ModelForm):
    username = forms.CharField(
        label=_("Nom d'utilisateur"),
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": _("Nom d'utilisateur")}),
    )
    password = forms.CharField(
        label=_("Créer un mot de passe"),
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": _("Mot de passe")}),
    )
    password_confirm = forms.CharField(
        label=_("Confirmer le mot de passe"),
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": _("Confirmer le mot de passe")}),
    )

    class Meta:
        model = CustomUser
        fields = ["email", "username"]
        widgets = {
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": _("Adresse e-mail")}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        if password and password_confirm and password != password_confirm:
            self.add_error("password_confirm", _("Les mots de passe ne correspondent pas."))
        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError(_("Un compte avec cette adresse e-mail existe déjà."))
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


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
            "country",            # <-- Laisse ce champ ici, mais SANS widget spécifique
            "membership_role",
            "profile_picture",
            "judicial_record",
            "message",
        ]
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control", "placeholder": _("Nom complet")}),
            "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": _("Téléphone")}),
            # SUPPRIME CETTE LIGNE car sinon la liste ne s'affichera PAS :
            # "country": forms.TextInput(attrs={"class": "form-control", "placeholder": _("Pays")}),
            "membership_role": forms.Select(attrs={"class": "form-select"}),
            "profile_picture": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "judicial_record": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "message": forms.Textarea(attrs={"class": "form-control", "placeholder": _("Message"), "rows": 4}),
        }

    def clean_judicial_record(self):
        file = self.cleaned_data.get('judicial_record')
        if file:
            if file.content_type != 'application/pdf':
                raise forms.ValidationError(_("Le fichier doit être au format PDF."))
            if file.size > 2 * 1024 * 1024:
                raise forms.ValidationError(_("Le fichier ne doit pas dépasser 2 Mo."))
        return file





# # accounts_users/forms/signup_forms.py

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
#             "full_name": forms.TextInput(attrs={"class": "form-control", "placeholder": _("Nom complet")}),
#             "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": _("Téléphone")}),
#             "country": forms.TextInput(attrs={"class": "form-control", "placeholder": _("Pays")}),
#             "membership_role": forms.Select(attrs={"class": "form-select"}),
#             "profile_picture": forms.ClearableFileInput(attrs={"class": "form-control"}),
#             "judicial_record": forms.ClearableFileInput(attrs={"class": "form-control"}),
#             "message": forms.Textarea(attrs={"class": "form-control", "placeholder": _("Message"), "rows": 4}),
#         }

#     def clean_judicial_record(self):
#         file = self.cleaned_data.get('judicial_record')
#         if file:
#             if file.content_type != 'application/pdf':
#                 raise forms.ValidationError(_("Le fichier doit être au format PDF."))
#             if file.size > 2 * 1024 * 1024:
#                 raise forms.ValidationError(_("Le fichier ne doit pas dépasser 2 Mo."))
#         return file




##accounts_users/forms/signup_forms -> 01/07
# from django import forms
# from django.utils.translation import gettext_lazy as _
# from accounts_users.models.users import CustomUser
# from accounts_users.models.users_profile import UserProfile


# class UserSignupForm(forms.ModelForm):
#     username = forms.CharField(
#         label=_("Nom d'utilisateur"),
#         max_length=150,
#         widget=forms.TextInput(attrs={"class": "form-control", "placeholder": _("Nom d'utilisateur")})
#     )

#     password = forms.CharField(
#         label=_("Mot de passe"),
#         widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": _("Mot de passe")})
#     )
#     password_confirm = forms.CharField(
#         label=_("Confirmer le mot de passe"),
#         widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": _("Confirmer le mot de passe")})
#     )

#     class Meta:
#         model = CustomUser
#         fields = ["username", "email"]
#         widgets = {
#             "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": _("Adresse e-mail")}),
#         }

#     def clean(self):
#         cleaned_data = super().clean()
#         password = cleaned_data.get("password")
#         confirm = cleaned_data.get("password_confirm")

#         if password and confirm and password != confirm:
#             self.add_error("password_confirm", _("Les mots de passe ne correspondent pas."))

#         return cleaned_data

#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user.set_password(self.cleaned_data["password"])
#         if commit:
#             user.save()
#         return user


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
#             "country",
#             "membership_role",
#             "profile_picture",
#             "judicial_record",
#             "message",
#         ]
#         widgets = {
#             "full_name": forms.TextInput(attrs={"class": "form-control", "placeholder": _("Nom complet")}),
#             "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": _("Téléphone")}),
#             "country": forms.TextInput(attrs={"class": "form-control", "placeholder": _("Pays")}),
#             "membership_role": forms.Select(attrs={"class": "form-select"}),
#             "profile_picture": forms.ClearableFileInput(attrs={"class": "form-control"}),
#             "judicial_record": forms.ClearableFileInput(attrs={"class": "form-control"}),
#             "message": forms.Textarea(attrs={"class": "form-control", "placeholder": _("Message"), "rows": 4}),
#         }

#     def clean_judicial_record(self):
#         file = self.cleaned_data.get('judicial_record')
#         if file:
#             if file.content_type != 'application/pdf':
#                 raise forms.ValidationError("Le fichier doit être au format PDF.")
#             if file.size > 2 * 1024 * 1024:
#                 raise forms.ValidationError("Le fichier ne doit pas dépasser 2 Mo.")
#         return file







# from django import forms
# from django.utils.translation import gettext_lazy as _
# from accounts_users.models.users import CustomUser
# from accounts_users.models.users_profile import UserProfile
# from accounts_users.models.membership_role import MembershipRole

# class UserSignupForm(forms.ModelForm):
#     password = forms.CharField(
#         label=_("Mot de passe"),
#         widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": _("Mot de passe")})
#     )
#     password_confirm = forms.CharField(
#         label=_("Confirmer le mot de passe"),
#         widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": _("Confirmer le mot de passe")})
#     )

#     class Meta:
#         model = CustomUser
#         fields = ["email"]
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

#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user.set_password(self.cleaned_data["password"])
#         if commit:
#             user.save()
#         return user


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
#             "country",
#             "membership_role",
#             "profile_picture",
#             "judicial_record",
#             "message",
#         ]
#         widgets = {
#             "full_name": forms.TextInput(attrs={"class": "form-control", "placeholder": _("Nom complet")}),
#             "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": _("Téléphone")}),
#             "country": forms.TextInput(attrs={"class": "form-control", "placeholder": _("Pays")}),
#             "membership_role": forms.Select(attrs={"class": "form-select"}),
#             "profile_picture": forms.ClearableFileInput(attrs={"class": "form-control"}),
#             "judicial_record": forms.ClearableFileInput(attrs={"class": "form-control"}),
#             "message": forms.Textarea(attrs={"class": "form-control", "placeholder": _("Message"), "rows": 4}),
#         }



# from django import forms
# from django.utils.translation import gettext_lazy as _

# from accounts_users.models.users import CustomUser
# from accounts_users.models.users_profile import UserProfile


# class UserSignupForm(forms.ModelForm):
#     password1 = forms.CharField(
#         label=_("Mot de passe"),
#         widget=forms.PasswordInput(attrs={"class": "form-control"}),
#     )
#     password2 = forms.CharField(
#         label=_("Confirmer le mot de passe"),
#         widget=forms.PasswordInput(attrs={"class": "form-control"}),
#     )
#     terms = forms.BooleanField(
#         label=_("J'accepte les conditions générales"),
#         required=True
#     )

#     class Meta:
#         model = CustomUser
#         fields = ["username", "email"]
#         widgets = {
#             "username": forms.TextInput(attrs={"class": "form-control", "placeholder": _("Nom d'utilisateur")}),
#             "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": _("Adresse e-mail")}),
#         }

#     def clean(self):
#         cleaned_data = super().clean()
#         password1 = cleaned_data.get("password1")
#         password2 = cleaned_data.get("password2")

#         if password1 and password2 and password1 != password2:
#             self.add_error("password2", _("Les mots de passe ne correspondent pas."))

#         return cleaned_data

#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user.set_password(self.cleaned_data["password1"])
#         if commit:
#             user.save()
#         return user


# class UserProfileForm(forms.ModelForm):
#     class Meta:
#         model = UserProfile
#         fields = ["full_name", "phone", "country", "profile_picture", "message", "judicial_record", "role"]
#         widgets = {
#             "full_name": forms.TextInput(attrs={"class": "form-control", "placeholder": _("Nom complet")}),
#             "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": _("Téléphone")}),
#             "country": forms.TextInput(attrs={"class": "form-control", "placeholder": _("Pays")}),
#             "profile_picture": forms.ClearableFileInput(attrs={"class": "form-control"}),
#             "message": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": _("Message")}),
#             "judicial_record": forms.ClearableFileInput(attrs={"class": "form-control"}),
#             "role": forms.Select(attrs={"class": "form-select"}),
#         }
