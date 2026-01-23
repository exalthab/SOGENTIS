# accounts_users/forms/signup_forms.py
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class UserSignupForm(forms.ModelForm):
    """
    Formulaire inscription :
    - email + mot de passe
    - OTP email (validé dans la vue, pas ici)
    """

    password1 = forms.CharField(
        label=_("Mot de passe"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control password-strong",
                "autocomplete": "new-password",
            }
        ),
    )

    password2 = forms.CharField(
        label=_("Confirmer le mot de passe"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control password-confirm",
                "autocomplete": "new-password",
            }
        ),
    )

    email_otp_code = forms.CharField(
        label=_("Code OTP email"),
        max_length=6,
        required=True,
        help_text=_("Entrez le code que vous avez reçu par email (6 chiffres)."),
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "autocomplete": "one-time-code",
                "inputmode": "numeric",
                "pattern": "[0-9]{6}",
                "maxlength": "6",
            }
        ),
    )

    class Meta:
        model = User
        fields = ("email",)
        widgets = {
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "autocomplete": "email",
                }
            )
        }

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip().lower()
        if not email:
            raise ValidationError(_("Email requis."))
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError(_("Un compte avec cet email existe déjà."))
        return email

    def clean_email_otp_code(self):
        """
        Normalisation légère : on garde uniquement les chiffres, max 6.
        La validation en base (match + expiry + attempts) se fait dans la vue.
        """
        code = (self.cleaned_data.get("email_otp_code") or "").strip()
        code = "".join(ch for ch in code if ch.isdigit())
        return code[:6]

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")

        if p1 and p2 and p1 != p2:
            self.add_error("password2", _("Les mots de passe ne correspondent pas."))

        if p1:
            try:
                validate_password(p1)
            except ValidationError as e:
                self.add_error("password1", e)

        # OTP validé en base dans la vue (pas ici)
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user






# # accounts_users/forms/signup_forms.py
# from django import forms
# from django.contrib.auth import get_user_model
# from django.contrib.auth.password_validation import validate_password
# from django.core.exceptions import ValidationError
# from django.utils.translation import gettext_lazy as _

# User = get_user_model()


# class UserSignupForm(forms.ModelForm):
#     """
#     Formulaire inscription :
#     - email + mot de passe
#     - OTP email (validé en vue)
#     """

#     password1 = forms.CharField(
#         label=_("Mot de passe"),
#         widget=forms.PasswordInput(attrs={"class": "form-control", "autocomplete": "new-password"}),
#         strip=False,
#     )
#     password2 = forms.CharField(
#         label=_("Confirmer le mot de passe"),
#         widget=forms.PasswordInput(attrs={"class": "form-control", "autocomplete": "new-password"}),
#         strip=False,
#     )

#     email_otp_code = forms.CharField(
#         label=_("Code OTP email"),
#         max_length=6,
#         required=True,
#         help_text=_("Entrez le code que vous avez reçu par email (6 chiffres)."),
#         widget=forms.TextInput(attrs={"class": "form-control", "autocomplete": "one-time-code"}),
#     )

#     class Meta:
#         model = User
#         fields = ("email",)
#         widgets = {
#             "email": forms.EmailInput(attrs={"class": "form-control", "autocomplete": "email"}),
#         }

#     def clean_email(self):
#         email = (self.cleaned_data.get("email") or "").strip().lower()
#         if not email:
#             raise ValidationError(_("Email requis."))
#         if User.objects.filter(email__iexact=email).exists():
#             raise ValidationError(_("Un compte avec cet email existe déjà."))
#         return email

#     def clean(self):
#         cleaned = super().clean()
#         p1 = cleaned.get("password1")
#         p2 = cleaned.get("password2")

#         if p1 and p2 and p1 != p2:
#             self.add_error("password2", _("Les mots de passe ne correspondent pas."))

#         if p1:
#             try:
#                 validate_password(p1)
#             except ValidationError as e:
#                 self.add_error("password1", e)

#         # OTP validé en base dans la vue (pas ici)
#         return cleaned

#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user.email = self.cleaned_data["email"]
#         user.set_password(self.cleaned_data["password1"])
#         if commit:
#             user.save()
#         return user





# # accounts_users/forms/signup_forms.py
# from django import forms
# from django.contrib.auth import get_user_model
# from django.contrib.auth.password_validation import validate_password
# from django.core.exceptions import ValidationError
# from django.utils.translation import gettext_lazy as _

# User = get_user_model()

# class UserSignupForm(forms.ModelForm):
#     password1 = forms.CharField(
#         label=_("Mot de passe"),
#         widget=forms.PasswordInput(attrs={"class": "form-control", "autocomplete": "new-password"}),
#         strip=False,
#     )
#     password2 = forms.CharField(
#         label=_("Confirmer le mot de passe"),
#         widget=forms.PasswordInput(attrs={"class": "form-control", "autocomplete": "new-password"}),
#         strip=False,
#     )
#     email_otp_code = forms.CharField(
#         label=_("Code OTP email"),
#         max_length=6,
#         required=True,
#         help_text=_("Entrez le code que vous avez reçu par email."),
#         widget=forms.TextInput(attrs={"class": "form-control"}),
#     )

#     class Meta:
#         model = User
#         fields = ("email",)
#         widgets = {
#             "email": forms.EmailInput(attrs={"class": "form-control", "autocomplete": "email"}),
#         }

#     def clean_email(self):
#         email = (self.cleaned_data.get("email") or "").strip().lower()
#         if not email:
#             raise ValidationError(_("Email requis."))
#         if User.objects.filter(email__iexact=email).exists():
#             raise ValidationError(_("Un compte avec cet email existe déjà."))
#         return email

#     def clean(self):
#         cleaned = super().clean()
#         p1 = cleaned.get("password1")
#         p2 = cleaned.get("password2")

#         if p1 and p2 and p1 != p2:
#             self.add_error("password2", _("Les mots de passe ne correspondent pas."))

#         if p1:
#             try:
#                 validate_password(p1)
#             except ValidationError as e:
#                 self.add_error("password1", e)

#         # La validation du code OTP se fait dans la vue

#         return cleaned

#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user.email = self.cleaned_data["email"]
#         user.set_password(self.cleaned_data["password1"])
#         if commit:
#             user.save()
#         return user




# # accounts_users/forms/signup_forms.py
# from django import forms
# from django.contrib.auth import get_user_model
# from django.contrib.auth.password_validation import validate_password
# from django.core.exceptions import ValidationError
# from django.utils.translation import gettext_lazy as _

# User = get_user_model()


# class UserSignupForm(forms.ModelForm):
#     password1 = forms.CharField(
#         label=_("Mot de passe"),
#         widget=forms.PasswordInput(attrs={"class": "form-control", "autocomplete": "new-password"}),
#         strip=False,
#     )
#     password2 = forms.CharField(
#         label=_("Confirmer le mot de passe"),
#         widget=forms.PasswordInput(attrs={"class": "form-control", "autocomplete": "new-password"}),
#         strip=False,
#     )

#     class Meta:
#         model = User
#         fields = ("email",)
#         widgets = {
#             "email": forms.EmailInput(attrs={"class": "form-control", "autocomplete": "email"}),
#         }

#     def clean_email(self):
#         email = (self.cleaned_data.get("email") or "").strip().lower()
#         if not email:
#             raise ValidationError(_("Email requis."))
#         if User.objects.filter(email__iexact=email).exists():
#             raise ValidationError(_("Un compte avec cet email existe déjà."))
#         return email

#     def clean(self):
#         cleaned = super().clean()
#         p1 = cleaned.get("password1")
#         p2 = cleaned.get("password2")

#         if p1 and p2 and p1 != p2:
#             self.add_error("password2", _("Les mots de passe ne correspondent pas."))

#         if p1:
#             try:
#                 validate_password(p1)
#             except ValidationError as e:
#                 self.add_error("password1", e)

#         return cleaned

#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user.email = self.cleaned_data["email"]
#         user.set_password(self.cleaned_data["password1"])
#         if commit:
#             user.save()
#         return user






# # accounts_users/forms/signup_forms.py 30/12/2025
# from django import forms
# from django.core.exceptions import ValidationError
# from django.utils.translation import gettext_lazy as _

# from accounts_users.models.custom_users import CustomUser


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




# # accounts_users/forms/signup_forms.py 21/12/2025

# from django import forms
# from django.utils.translation import gettext_lazy as _
# from django.core.exceptions import ValidationError

# from django_countries.widgets import CountrySelectWidget

# from accounts_users.models.users import CustomUser
# from accounts_users.models.users_profile import UserProfile


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
# # PROFIL SOCIAL (INSCRIPTION)
# # ======================================================
# class UserProfileForm(forms.ModelForm):
#     """
#     Formulaire Profil utilisé UNIQUEMENT à l'inscription.
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










# # accounts_users/forms/signup_forms.py November 2025

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
#             # "country",
#             "membership_role",
#             "profile_picture",
#             "judicial_record",
#             "message",
#         ]
#         widgets = {
#             "full_name": forms.TextInput(attrs={"class": "form-control", "placeholder": _("Nom complet")}),
#             "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": _("Téléphone")}),
#             # "country": forms.TextInput(attrs={"class": "form-control", "placeholder": _("Pays")}),
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









# # accounts_users/forms/signup_forms.py
# from django import forms
# from django.utils.translation import gettext_lazy as _
# from django.core.exceptions import ValidationError

# from accounts_users.models.users import CustomUser
# from accounts_users.models.users_profile import UserProfile


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
# # PROFIL SOCIAL
# # ======================================================
# class UserProfileForm(forms.ModelForm):
#     terms = forms.BooleanField(
#         label=_("J’accepte les conditions générales"),
#         required=True
#     )

#     class Meta:
#         model = UserProfile
#         fields = [
#             # Identité
#             "last_name",
#             "first_name",
#             "middle_names",
#             "nickname",

#             # Naissance
#             "date_of_birth",
#             "place_of_birth",
#             "country_of_birth",

#             # Résidence
#             "country_of_residence",
#             "city_of_residence",
#             "address",

#             # Contact / pro
#             "phone",
#             "profession",
#             "function",

#             # Social
#             "membership_role",

#             # Fichiers
#             "profile_picture",
#             "judicial_record",

#             "message",
#         ]

#         widgets = {
#             "last_name": forms.TextInput(attrs={"class": "form-control"}),
#             "first_name": forms.TextInput(attrs={"class": "form-control"}),
#             "middle_names": forms.TextInput(attrs={"class": "form-control"}),
#             "nickname": forms.TextInput(attrs={"class": "form-control"}),

#             "date_of_birth": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
#             "place_of_birth": forms.TextInput(attrs={"class": "form-control"}),

#             "city_of_residence": forms.TextInput(attrs={"class": "form-control"}),
#             "address": forms.Textarea(attrs={"rows": 2, "class": "form-control"}),

#             "phone": forms.TextInput(attrs={"class": "form-control"}),
#             "profession": forms.TextInput(attrs={"class": "form-control"}),
#             "function": forms.TextInput(attrs={"class": "form-control"}),

#             "membership_role": forms.Select(attrs={"class": "form-select"}),

#             "profile_picture": forms.ClearableFileInput(attrs={"class": "form-control"}),
#             "judicial_record": forms.ClearableFileInput(attrs={"class": "form-control"}),

#             "message": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
#         }

#     def clean_judicial_record(self):
#         file = self.cleaned_data.get("judicial_record")
#         if file:
#             if file.content_type != "application/pdf":
#                 raise ValidationError(_("Le fichier doit être un PDF."))
#             if file.size > 2 * 1024 * 1024:
#                 raise ValidationError(_("Le fichier ne doit pas dépasser 2 Mo."))
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
