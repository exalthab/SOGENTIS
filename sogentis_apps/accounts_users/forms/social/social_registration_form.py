from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from django_countries.widgets import CountrySelectWidget
from phonenumber_field.formfields import PhoneNumberField

from accounts_users.models.social.social_profile import SocialProfile


class SocialRegistrationForm(forms.ModelForm):
    """
    Formulaire PUBLIC d’inscription sociale SOGENTIS
    """

    # ==================================================
    # CHAMPS NON-MODÈLE
    # ==================================================
    terms = forms.BooleanField(
        label=_("J’accepte les conditions générales"),
        required=True,
        help_text=_("Vous devez accepter les conditions générales pour poursuivre l’inscription."),
    )

    # Téléphone (lié au pays/indicatif via la lib)
    phone_number = PhoneNumberField(
        label=_("Téléphone"),
        required=True,
        help_text=_("Format international requis, ex : +221771234567"),
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    class Meta:
        model = SocialProfile

        # 🔥 CRITIQUE : on EXCLUT le champ modèle "phone" pour éviter tout doublon
        exclude = (
            "phone",
            "user",
            "status",
            "is_active_member",
            "is_validated",
            "validated_at",
            "created_at",
            "updated_at",
        )

        help_texts = {
            "last_name": _("Nom de famille tel qu’indiqué sur vos documents officiels."),
            "first_name": _("Prénom officiel."),
            "middle_names": _("Autres prénoms (si applicable)."),
            "nickname": _("Nom usuel ou surnom (facultatif)."),
            "date_of_birth": _("Date de naissance."),
            "place_of_birth": _("Lieu de naissance (ville, pays)."),
            "country_of_birth": _("Pays de naissance."),
            "country_of_residence": _("Pays de résidence actuelle."),
            "city_of_residence": _("Ville de résidence actuelle."),
            "address": _("Adresse complète de résidence."),
            "profession": _("Votre profession actuelle."),
            "function": _("Fonction ou poste occupé."),
            "profile_picture": _("Photo de profil (format image)."),
            "judicial_record": _("Casier judiciaire obligatoire au format PDF (max 2 Mo)."),
            "membership_role": _("Type d’adhésion sociale souhaitée."),
            "membership_date": _("Date d’adhésion (auto si vide)."),
            "motivation": _("Expliquez votre motivation (au moins 20 caractères)."),
            "availability": _("Vos disponibilités pour les activités."),
            "skills": _("Compétences ou domaines d’expertise."),
        }

        widgets = {
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "middle_names": forms.TextInput(attrs={"class": "form-control"}),
            "nickname": forms.TextInput(attrs={"class": "form-control"}),

            "date_of_birth": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "place_of_birth": forms.TextInput(attrs={"class": "form-control"}),
            "country_of_birth": CountrySelectWidget(attrs={"class": "form-select"}),

            "country_of_residence": CountrySelectWidget(attrs={"class": "form-select"}),
            "city_of_residence": forms.TextInput(attrs={"class": "form-control"}),
            "address": forms.Textarea(attrs={"rows": 2, "class": "form-control"}),

            "profession": forms.TextInput(attrs={"class": "form-control"}),
            "function": forms.TextInput(attrs={"class": "form-control"}),

            "profile_picture": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "judicial_record": forms.ClearableFileInput(attrs={"class": "form-control"}),

            "membership_role": forms.Select(attrs={"class": "form-select"}),
            "membership_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),

            "motivation": forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
            "availability": forms.TextInput(attrs={"class": "form-control"}),
            "skills": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ==================================================
        # ✅ LISTE BLANCHE : seuls ces champs doivent être visibles côté PUBLIC
        # - On se base sur tes champs déclarés dans widgets/help_texts (donc sans casser ton form)
        # - On garde aussi les non-modèle : terms + phone_number
        # ==================================================
        allowed_model_fields = set(self.Meta.widgets.keys()) | set(self.Meta.help_texts.keys())

        allowed_extra_fields = {"terms", "phone_number"}
        allowed_all = allowed_model_fields | allowed_extra_fields

        # On retire tout le reste (y compris "Téléphone vérifié", "Téléphone vérifié le", etc.)
        for name in list(self.fields.keys()):
            if name not in allowed_all:
                self.fields.pop(name, None)

        # Optionnel : si instance existe et a phone, préremplir phone_number
        if getattr(self.instance, "phone", None) and "phone_number" in self.fields:
            self.fields["phone_number"].initial = self.instance.phone

    # ==================================================
    # VALIDATIONS
    # ==================================================
    def clean_membership_role(self):
        role = self.cleaned_data.get("membership_role")
        if not role:
            raise ValidationError(_("Veuillez sélectionner un type d’adhésion sociale."))
        return role

    def clean_motivation(self):
        motivation = (self.cleaned_data.get("motivation") or "").strip()
        if len(motivation) < 20:
            raise ValidationError(_("La motivation doit contenir au moins 20 caractères."))
        return motivation

    def clean_phone_number(self):
        phone = self.cleaned_data.get("phone_number")
        if not phone:
            raise ValidationError(_("Le numéro de téléphone est obligatoire."))
        return phone

    def clean_judicial_record(self):
        file = self.cleaned_data.get("judicial_record")

        if not file:
            raise ValidationError(_("Le casier judiciaire est obligatoire."))

        if getattr(file, "content_type", "") != "application/pdf":
            raise ValidationError(_("Le fichier doit être un PDF."))

        if file.size > 2 * 1024 * 1024:
            raise ValidationError(_("Le fichier ne doit pas dépasser 2 Mo."))

        return file

    # ==================================================
    # SAVE (signature voulue : save(user=...))
    # ==================================================
    def save(self, user, commit=True):
        instance = super().save(commit=False)
        instance.user = user

        # 🔗 mapping : champ form phone_number -> champ modèle phone
        instance.phone = self.cleaned_data.get("phone_number")

        if not instance.membership_date:
            instance.membership_date = timezone.now().date()

        instance.is_active_member = False
        instance.is_validated = False
        instance.validated_at = None

        if commit:
            instance.save()
            self.save_m2m()

        return instance






# # accounts_users/forms/social/social_registration_form.py
# from django import forms
# from django.core.exceptions import ValidationError
# from django.utils.translation import gettext_lazy as _
# from django.utils import timezone

# from django_countries.widgets import CountrySelectWidget
# from phonenumber_field.formfields import PhoneNumberField

# from accounts_users.models.social.social_profile import SocialProfile


# class SocialRegistrationForm(forms.ModelForm):
#     """
#     Formulaire PUBLIC d’inscription sociale SOGENTIS
#     """

#     # ==================================================
#     # CHAMPS NON-MODÈLE
#     # ==================================================
#     terms = forms.BooleanField(
#         label=_("J’accepte les conditions générales"),
#         required=True,
#         help_text=_("Vous devez accepter les conditions générales pour poursuivre l’inscription."),
#     )

#     # Téléphone (lié au pays/indicatif via la lib)
#     phone_number = PhoneNumberField(
#         label=_("Téléphone"),
#         required=True,
#         help_text=_("Format international requis, ex : +221771234567"),
#         widget=forms.TextInput(attrs={"class": "form-control"}),
#     )

#     class Meta:
#         model = SocialProfile

#         # 🔥 CRITIQUE : on EXCLUT le champ modèle "phone" pour éviter tout doublon
#         exclude = (
#             "phone",
#             "user",
#             "status",
#             "is_active_member",
#             "is_validated",
#             "validated_at",
#             "created_at",
#             "updated_at",
#         )

#         help_texts = {
#             "last_name": _("Nom de famille tel qu’indiqué sur vos documents officiels."),
#             "first_name": _("Prénom officiel."),
#             "middle_names": _("Autres prénoms (si applicable)."),
#             "nickname": _("Nom usuel ou surnom (facultatif)."),
#             "date_of_birth": _("Date de naissance."),
#             "place_of_birth": _("Lieu de naissance (ville, pays)."),
#             "country_of_birth": _("Pays de naissance."),
#             "country_of_residence": _("Pays de résidence actuelle."),
#             "city_of_residence": _("Ville de résidence actuelle."),
#             "address": _("Adresse complète de résidence."),
#             "profession": _("Votre profession actuelle."),
#             "function": _("Fonction ou poste occupé."),
#             "profile_picture": _("Photo de profil (format image)."),
#             "judicial_record": _("Casier judiciaire obligatoire au format PDF (max 2 Mo)."),
#             "membership_role": _("Type d’adhésion sociale souhaitée."),
#             "membership_date": _("Date d’adhésion (auto si vide)."),
#             "motivation": _("Expliquez votre motivation (au moins 20 caractères)."),
#             "availability": _("Vos disponibilités pour les activités."),
#             "skills": _("Compétences ou domaines d’expertise."),
#         }

#         widgets = {
#             "last_name": forms.TextInput(attrs={"class": "form-control"}),
#             "first_name": forms.TextInput(attrs={"class": "form-control"}),
#             "middle_names": forms.TextInput(attrs={"class": "form-control"}),
#             "nickname": forms.TextInput(attrs={"class": "form-control"}),

#             "date_of_birth": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
#             "place_of_birth": forms.TextInput(attrs={"class": "form-control"}),
#             "country_of_birth": CountrySelectWidget(attrs={"class": "form-select"}),

#             "country_of_residence": CountrySelectWidget(attrs={"class": "form-select"}),
#             "city_of_residence": forms.TextInput(attrs={"class": "form-control"}),
#             "address": forms.Textarea(attrs={"rows": 2, "class": "form-control"}),

#             "profession": forms.TextInput(attrs={"class": "form-control"}),
#             "function": forms.TextInput(attrs={"class": "form-control"}),

#             "profile_picture": forms.ClearableFileInput(attrs={"class": "form-control"}),
#             "judicial_record": forms.ClearableFileInput(attrs={"class": "form-control"}),

#             "membership_role": forms.Select(attrs={"class": "form-select"}),
#             "membership_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),

#             "motivation": forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
#             "availability": forms.TextInput(attrs={"class": "form-control"}),
#             "skills": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
#         }

#     # ==================================================
#     # VALIDATIONS
#     # ==================================================
#     def clean_membership_role(self):
#         role = self.cleaned_data.get("membership_role")
#         if not role:
#             raise ValidationError(_("Veuillez sélectionner un type d’adhésion sociale."))
#         return role

#     def clean_motivation(self):
#         motivation = (self.cleaned_data.get("motivation") or "").strip()
#         if len(motivation) < 20:
#             raise ValidationError(_("La motivation doit contenir au moins 20 caractères."))
#         return motivation

#     def clean_phone_number(self):
#         phone = self.cleaned_data.get("phone_number")
#         if not phone:
#             raise ValidationError(_("Le numéro de téléphone est obligatoire."))
#         return phone

#     def clean_judicial_record(self):
#         file = self.cleaned_data.get("judicial_record")

#         if not file:
#             raise ValidationError(_("Le casier judiciaire est obligatoire."))

#         if getattr(file, "content_type", "") != "application/pdf":
#             raise ValidationError(_("Le fichier doit être un PDF."))

#         if file.size > 2 * 1024 * 1024:
#             raise ValidationError(_("Le fichier ne doit pas dépasser 2 Mo."))

#         return file

#     # ==================================================
#     # SAVE (signature voulue : save(user=...))
#     # ==================================================
#     def save(self, user, commit=True):
#         instance = super().save(commit=False)
#         instance.user = user

#         # 🔗 mapping : champ form phone_number -> champ modèle phone
#         instance.phone = self.cleaned_data.get("phone_number")

#         if not instance.membership_date:
#             instance.membership_date = timezone.now().date()

#         instance.is_active_member = False
#         instance.is_validated = False
#         instance.validated_at = None

#         if commit:
#             instance.save()
#             self.save_m2m()

#         return instance





# # accounts_users/forms/social/social_registration_form.py

# from django import forms
# from django.core.exceptions import ValidationError
# from django.utils.translation import gettext_lazy as _
# from django.utils import timezone

# from django_countries.widgets import CountrySelectWidget
# from phonenumber_field.formfields import PhoneNumberField

# from accounts_users.models.social.social_profile import SocialProfile


# class SocialRegistrationForm(forms.ModelForm):
#     """
#     Formulaire PUBLIC d’inscription sociale SOGENTIS
#     """

#     # ==================================================
#     # CHAMP NON-MODÈLE
#     # ==================================================
#     terms = forms.BooleanField(
#         label=_("J’accepte les conditions générales"),
#         required=True,
#         help_text=_(
#             "Vous devez accepter les conditions générales pour poursuivre l’inscription."
#         ),
#     )

#     # TÉLÉPHONE
#     phone_number = PhoneNumberField(
#         label=_("Téléphone"),
#         required=True,
#         help_text=_("Format international requis, ex : +221771234567"),
#         widget=forms.TextInput(attrs={"class": "form-control"}),
#     )

#     class Meta:
#         model = SocialProfile

#         exclude = (
#             "user",
#             "status",
#             "is_active_member",
#             "is_validated",
#             "validated_at",
#             "created_at",
#             "updated_at",
#         )

#         # ✅ HELP TEXTS RESTAURÉS
#         help_texts = {
#             "last_name": _("Nom de famille tel qu’indiqué sur vos documents officiels."),
#             "first_name": _("Prénom officiel."),
#             "middle_names": _("Autres prénoms (si applicable)."),
#             "nickname": _("Nom usuel ou surnom (facultatif)."),
#             "date_of_birth": _("Date de naissance."),
#             "place_of_birth": _("Lieu de naissance (ville, pays)."),
#             "country_of_birth": _("Pays de naissance."),
#             "country_of_residence": _("Pays de résidence actuelle."),
#             "city_of_residence": _("Ville de résidence actuelle."),
#             "address": _("Adresse complète de résidence."),
#             "profession": _("Votre profession actuelle."),
#             "function": _("Fonction ou poste occupé."),
#             "profile_picture": _("Photo de profil (format image)."),
#             "judicial_record": _("Casier judiciaire obligatoire au format PDF (max 2 Mo)."),
#             "membership_role": _("Type d’adhésion sociale souhaitée."),
#             "membership_date": _("Date d’adhésion (auto si vide)."),
#             "motivation": _("Expliquez votre motivation (au moins 20 caractères)."),
#             "availability": _("Vos disponibilités pour les activités."),
#             "skills": _("Compétences ou domaines d’expertise."),
#         }

#         widgets = {
#             # Identité
#             "last_name": forms.TextInput(attrs={"class": "form-control"}),
#             "first_name": forms.TextInput(attrs={"class": "form-control"}),
#             "middle_names": forms.TextInput(attrs={"class": "form-control"}),
#             "nickname": forms.TextInput(attrs={"class": "form-control"}),

#             # Naissance
#             "date_of_birth": forms.DateInput(
#                 attrs={"type": "date", "class": "form-control"}
#             ),
#             "place_of_birth": forms.TextInput(attrs={"class": "form-control"}),
#             "country_of_birth": CountrySelectWidget(
#                 attrs={"class": "form-select"}
#             ),

#             # Résidence
#             "country_of_residence": CountrySelectWidget(
#                 attrs={"class": "form-select"}
#             ),
#             "city_of_residence": forms.TextInput(attrs={"class": "form-control"}),
#             "address": forms.Textarea(
#                 attrs={"rows": 2, "class": "form-control"}
#             ),

#             # Profession
#             "profession": forms.TextInput(attrs={"class": "form-control"}),
#             "function": forms.TextInput(attrs={"class": "form-control"}),

#             # Documents
#             "profile_picture": forms.ClearableFileInput(
#                 attrs={"class": "form-control"}
#             ),
#             "judicial_record": forms.ClearableFileInput(
#                 attrs={"class": "form-control"}
#             ),

#             # Social
#             "membership_role": forms.Select(attrs={"class": "form-select"}),
#             "membership_date": forms.DateInput(
#                 attrs={"type": "date", "class": "form-control"}
#             ),

#             # Engagement
#             "motivation": forms.Textarea(
#                 attrs={"rows": 4, "class": "form-control"}
#             ),
#             "availability": forms.TextInput(attrs={"class": "form-control"}),
#             "skills": forms.Textarea(
#                 attrs={"rows": 3, "class": "form-control"}
#             ),
#         }

#     # ==================================================
#     # VALIDATIONS
#     # ==================================================
#     def clean_membership_role(self):
#         role = self.cleaned_data.get("membership_role")
#         if not role:
#             raise ValidationError(
#                 _("Veuillez sélectionner un type d’adhésion sociale.")
#             )
#         return role

#     def clean_motivation(self):
#         motivation = (self.cleaned_data.get("motivation") or "").strip()
#         if len(motivation) < 20:
#             raise ValidationError(
#                 _("La motivation doit contenir au moins 20 caractères.")
#             )
#         return motivation

#     def clean_judicial_record(self):
#         file = self.cleaned_data.get("judicial_record")

#         if not file:
#             raise ValidationError(_("Le casier judiciaire est obligatoire."))

#         if getattr(file, "content_type", "") != "application/pdf":
#             raise ValidationError(_("Le fichier doit être un PDF."))

#         if file.size > 2 * 1024 * 1024:
#             raise ValidationError(_("Le fichier ne doit pas dépasser 2 Mo."))

#         return file

#     # ==================================================
#     # SAVE
#     # ==================================================
#     def save(self, user, commit=True):
#         instance = super().save(commit=False)
#         instance.user = user

#         if not instance.membership_date:
#             instance.membership_date = timezone.now().date()

#         instance.is_active_member = False
#         instance.is_validated = False
#         instance.validated_at = None

#         if commit:
#             instance.save()
#             self.save_m2m()

#         return instance






# # accounts_users/forms/social/social_registration_form.py

# from django import forms
# from django.core.exceptions import ValidationError
# from django.utils.translation import gettext_lazy as _
# from django.utils import timezone

# from django_countries.widgets import CountrySelectWidget
# from phonenumber_field.formfields import PhoneNumberField
# from phonenumber_field.widgets import PhoneNumberPrefixWidget

# from accounts_users.models.social.social_profile import SocialProfile


# class SocialRegistrationForm(forms.ModelForm):
#     """
#     Formulaire PUBLIC d’inscription sociale SOGENTIS

#     - Crée un SocialProfile (liaison User faite dans la vue)
#     - Toutes les validations métier sont réalisées côté serveur
#     - Compatible avec social_signup.html
#     """
#     # Utilisation de PhoneNumberField avec son widget par défaut
#     phone_number = PhoneNumberField(
#         required=False,
#         widget=forms.TextInput(attrs={'placeholder': _('Numéro de téléphone'), 'class': 'form-control'})
#     )

#     # ==================================================
#     # CHAMPS NON-MODÈLE
#     # ==================================================
#     model = SocialProfile
#     fields = ['phone_number']
    
#     terms = forms.BooleanField(
#         label=_("J’accepte les conditions générales"),
#         required=True,
#         help_text=_(
#             "Vous devez accepter les conditions générales pour poursuivre l’inscription."
#         ),
#     )

#     # ==================================================
#     # CONFIGURATION MODÈLE
#     # ==================================================
#     class Meta:
#         model = SocialProfile

#         # Champs système exclus (gérés serveur / admin)
#         exclude = (
#             "user",
#             "status",              # ← OBLIGATOIRE
#             "is_active_member",
#             "is_validated",
#             "validated_at",
#             "created_at",
#             "updated_at",
#         )

#         # ==================================================
#         # WIDGETS
#         # ==================================================
#         widgets = {
#             # -------------------------
#             # IDENTITÉ
#             # -------------------------
#             "last_name": forms.TextInput(attrs={"class": "form-control"}),
#             "first_name": forms.TextInput(attrs={"class": "form-control"}),
#             "middle_names": forms.TextInput(attrs={"class": "form-control"}),
#             "nickname": forms.TextInput(attrs={"class": "form-control"}),

#             # -------------------------
#             # NAISSANCE
#             # -------------------------
#             "date_of_birth": forms.DateInput(
#                 attrs={"type": "date", "class": "form-control"}
#             ),
#             "place_of_birth": forms.TextInput(attrs={"class": "form-control"}),
#             "country_of_birth": CountrySelectWidget(
#                 attrs={"class": "form-select"}
#             ),

#             # -------------------------
#             # RÉSIDENCE
#             # -------------------------
#             "country_of_residence": CountrySelectWidget(
#                 attrs={"class": "form-select"}
#             ),
#             "city_of_residence": forms.TextInput(attrs={"class": "form-control"}),
#             "address": forms.Textarea(
#                 attrs={"rows": 2, "class": "form-control"}
#             ),

#             # -------------------------
#             # CONTACT / PROFESSION
#             # -------------------------
#             "profession": forms.TextInput(attrs={"class": "form-control"}),
#             "function": forms.TextInput(attrs={"class": "form-control"}),

#             # -------------------------
#             # DOCUMENTS
#             # -------------------------
#             "profile_picture": forms.ClearableFileInput(
#                 attrs={"class": "form-control"}
#             ),
#             "judicial_record": forms.ClearableFileInput(
#                 attrs={"class": "form-control"}
#             ),

#             # -------------------------
#             # ADHÉSION SOCIALE
#             # -------------------------
#             "membership_role": forms.Select(attrs={"class": "form-select"}),
#             "membership_date": forms.DateInput(
#                 attrs={"type": "date", "class": "form-control"}
#             ),

#             # -------------------------
#             # ENGAGEMENT
#             # -------------------------
#             "motivation": forms.Textarea(
#                 attrs={"rows": 4, "class": "form-control"}
#             ),
#             "availability": forms.TextInput(attrs={"class": "form-control"}),
#             "skills": forms.Textarea(
#                 attrs={"rows": 3, "class": "form-control"}
#             ),
#         }

#         # ==================================================
#         # HELP TEXTS (COMPLETS)
#         # ==================================================
#         help_texts = {
#             # -------------------------
#             # IDENTITÉ
#             # -------------------------
#             "last_name": _("Votre nom de famille officiel."),
#             "first_name": _("Votre prénom officiel."),
#             "middle_names": _("Autres prénoms éventuels (facultatif)."),
#             "nickname": _("Surnom ou nom usuel (facultatif)."),

#             # -------------------------
#             # NAISSANCE
#             # -------------------------
#             "date_of_birth": _("Votre date de naissance."),
#             "place_of_birth": _("Ville ou localité de naissance."),
#             "country_of_birth": _("Pays dans lequel vous êtes né(e)."),

#             # -------------------------
#             # RÉSIDENCE
#             # -------------------------
#             "country_of_residence": _("Pays où vous résidez actuellement."),
#             "city_of_residence": _("Ville de résidence actuelle."),
#             "address": _("Adresse complète de résidence."),

#             # -------------------------
#             # CONTACT / PROFESSION
#             # -------------------------
#             "profession": _("Votre profession actuelle (facultatif)."),
#             "function": _("Fonction ou poste occupé (facultatif)."),

#             # -------------------------
#             # DOCUMENTS
#             # -------------------------
#             "profile_picture": _("Photo de profil (facultatif)."),
#             "judicial_record": _(
#                 "Casier judiciaire OBLIGATOIRE au format PDF "
#                 "(taille maximale : 2 Mo)."
#             ),

#             # -------------------------
#             # ADHÉSION SOCIALE
#             # -------------------------
#             "membership_role": _("Type d’adhésion sociale souhaité."),
#             "membership_date": _(
#                 "Laissez vide : la date sera renseignée automatiquement."
#             ),

#             # -------------------------
#             # ENGAGEMENT
#             # -------------------------
#             "motivation": _(
#                 "Expliquez votre motivation à rejoindre SOGENTIS "
#                 "(au moins 20 caractères)."
#             ),
#             "availability": _(
#                 "Votre disponibilité pour les activités sociales "
#                 "(ex : week-end, temps partiel, temps plein)."
#             ),
#             "skills": _(
#                 "Compétences ou expériences utiles pour les actions sociales."
#             ),
#         }

#     # ==================================================
#     # VALIDATIONS MÉTIER
#     # ==================================================
#     def clean_membership_role(self):
#         role = self.cleaned_data.get("membership_role")
#         if not role:
#             raise ValidationError(
#                 _("Veuillez sélectionner un type d’adhésion sociale.")
#             )
#         return role

#     def clean_motivation(self):
#         motivation = (self.cleaned_data.get("motivation") or "").strip()
#         if len(motivation) < 20:
#             raise ValidationError(
#                 _("La motivation doit contenir au moins 20 caractères.")
#             )
#         return motivation

#     def clean_judicial_record(self):
#         file = self.cleaned_data.get("judicial_record")

#         # 🔴 OBLIGATOIRE
#         if not file:
#             raise ValidationError(
#                 _("Le casier judiciaire est obligatoire.")
#             )

#         content_type = getattr(file, "content_type", "") or ""
#         if content_type != "application/pdf":
#             raise ValidationError(_("Le fichier doit être un PDF."))

#         if file.size > 2 * 1024 * 1024:
#             raise ValidationError(_("Le fichier ne doit pas dépasser 2 Mo."))

#         return file

#     # ==================================================
#     # SAVE STANDARD (PAS DE USER ICI)
#     # ==================================================
#     def save(self, commit=True):
#         """
#         Sauvegarde standard :
#         - le rattachement au User est effectué dans la vue
#         - statut par défaut : en attente de validation
#         """
#         instance = super().save(commit=False)

#         if not instance.membership_date:
#             instance.membership_date = timezone.now().date()

#         instance.is_active_member = False
#         instance.is_validated = False
#         instance.validated_at = None

#         if commit:
#             instance.save()
#             self.save_m2m()

#         return instance





# # accounts_users/forms/social/social_registration_form.py

# from django import forms
# from django.core.exceptions import ValidationError
# from django.utils.translation import gettext_lazy as _
# from django.utils import timezone

# from django_countries.widgets import CountrySelectWidget
# from phonenumber_field.formfields import PhoneNumberField


# from accounts_users.models.social.social_profile import SocialProfile


# class SocialRegistrationForm(forms.ModelForm):
#     """
#     Formulaire PUBLIC d’inscription sociale SOGENTIS

#     - Crée un SocialProfile (liaison User faite dans la vue)
#     - Toutes les validations métier sont réalisées côté serveur
#     - Compatible avec social_signup.html
#     """
#     phone_number = PhoneNumberField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Numéro de téléphone'}))

#     # ==================================================
#     # CHAMPS NON-MODÈLE
#     # ==================================================
#     model = SocialProfile
#     fields = ['phone_number']
#     # phone = PhoneNumberField(
#     #     label=_("Téléphone"),
#     #     required=True,
#     #     help_text=_(
#     #         "Numéro de téléphone valide avec indicatif international. "
#     #         "Exemple : +221 77 123 45 67"
#     #     ),
#     # )

#     terms = forms.BooleanField(
#         label=_("J’accepte les conditions générales"),
#         required=True,
#         help_text=_(
#             "Vous devez accepter les conditions générales pour poursuivre l’inscription."
#         ),
#     )

#     # ==================================================
#     # CONFIGURATION MODÈLE
#     # ==================================================
#     class Meta:
#         model = SocialProfile

#         # Champs système exclus (gérés serveur / admin)
#         exclude = (
#             "user",
#             "status",              # ← OBLIGATOIRE
#             "is_active_member",
#             "is_validated",
#             "validated_at",
#             "created_at",
#             "updated_at",
#         )

#         # ==================================================
#         # WIDGETS
#         # ==================================================
#         widgets = {
#             # -------------------------
#             # IDENTITÉ
#             # -------------------------
#             "last_name": forms.TextInput(attrs={"class": "form-control"}),
#             "first_name": forms.TextInput(attrs={"class": "form-control"}),
#             "middle_names": forms.TextInput(attrs={"class": "form-control"}),
#             "nickname": forms.TextInput(attrs={"class": "form-control"}),

#             # -------------------------
#             # NAISSANCE
#             # -------------------------
#             "date_of_birth": forms.DateInput(
#                 attrs={"type": "date", "class": "form-control"}
#             ),
#             "place_of_birth": forms.TextInput(attrs={"class": "form-control"}),
#             "country_of_birth": CountrySelectWidget(
#                 attrs={"class": "form-select"}
#             ),

#             # -------------------------
#             # RÉSIDENCE
#             # -------------------------
#             "country_of_residence": CountrySelectWidget(
#                 attrs={"class": "form-select"}
#             ),
#             "city_of_residence": forms.TextInput(attrs={"class": "form-control"}),
#             "address": forms.Textarea(
#                 attrs={"rows": 2, "class": "form-control"}
#             ),

#             # -------------------------
#             # CONTACT / PROFESSION
#             # -------------------------
#             "profession": forms.TextInput(attrs={"class": "form-control"}),
#             "function": forms.TextInput(attrs={"class": "form-control"}),

#             # -------------------------
#             # DOCUMENTS
#             # -------------------------
#             "profile_picture": forms.ClearableFileInput(
#                 attrs={"class": "form-control"}
#             ),
#             "judicial_record": forms.ClearableFileInput(
#                 attrs={"class": "form-control"}
#             ),

#             # -------------------------
#             # ADHÉSION SOCIALE
#             # -------------------------
#             "membership_role": forms.Select(attrs={"class": "form-select"}),
#             "membership_date": forms.DateInput(
#                 attrs={"type": "date", "class": "form-control"}
#             ),

#             # -------------------------
#             # ENGAGEMENT
#             # -------------------------
#             "motivation": forms.Textarea(
#                 attrs={"rows": 4, "class": "form-control"}
#             ),
#             "availability": forms.TextInput(attrs={"class": "form-control"}),
#             "skills": forms.Textarea(
#                 attrs={"rows": 3, "class": "form-control"}
#             ),
#         }

#         # ==================================================
#         # HELP TEXTS (COMPLETS)
#         # ==================================================
#         help_texts = {
#             # -------------------------
#             # IDENTITÉ
#             # -------------------------
#             "last_name": _("Votre nom de famille officiel."),
#             "first_name": _("Votre prénom officiel."),
#             "middle_names": _("Autres prénoms éventuels (facultatif)."),
#             "nickname": _("Surnom ou nom usuel (facultatif)."),

#             # -------------------------
#             # NAISSANCE
#             # -------------------------
#             "date_of_birth": _("Votre date de naissance."),
#             "place_of_birth": _("Ville ou localité de naissance."),
#             "country_of_birth": _("Pays dans lequel vous êtes né(e)."),

#             # -------------------------
#             # RÉSIDENCE
#             # -------------------------
#             "country_of_residence": _("Pays où vous résidez actuellement."),
#             "city_of_residence": _("Ville de résidence actuelle."),
#             "address": _("Adresse complète de résidence."),

#             # -------------------------
#             # CONTACT / PROFESSION
#             # -------------------------
#             "profession": _("Votre profession actuelle (facultatif)."),
#             "function": _("Fonction ou poste occupé (facultatif)."),

#             # -------------------------
#             # DOCUMENTS
#             # -------------------------
#             "profile_picture": _("Photo de profil (facultatif)."),
#             "judicial_record": _(
#                 "Casier judiciaire OBLIGATOIRE au format PDF "
#                 "(taille maximale : 2 Mo)."
#             ),

#             # -------------------------
#             # ADHÉSION SOCIALE
#             # -------------------------
#             "membership_role": _("Type d’adhésion sociale souhaité."),
#             "membership_date": _(
#                 "Laissez vide : la date sera renseignée automatiquement."
#             ),

#             # -------------------------
#             # ENGAGEMENT
#             # -------------------------
#             "motivation": _(
#                 "Expliquez votre motivation à rejoindre SOGENTIS "
#                 "(au moins 20 caractères)."
#             ),
#             "availability": _(
#                 "Votre disponibilité pour les activités sociales "
#                 "(ex : week-end, temps partiel, temps plein)."
#             ),
#             "skills": _(
#                 "Compétences ou expériences utiles pour les actions sociales."
#             ),
#         }

#     # ==================================================
#     # VALIDATIONS MÉTIER
#     # ==================================================
#     def clean_membership_role(self):
#         role = self.cleaned_data.get("membership_role")
#         if not role:
#             raise ValidationError(
#                 _("Veuillez sélectionner un type d’adhésion sociale.")
#             )
#         return role

#     def clean_motivation(self):
#         motivation = (self.cleaned_data.get("motivation") or "").strip()
#         if len(motivation) < 20:
#             raise ValidationError(
#                 _("La motivation doit contenir au moins 20 caractères.")
#             )
#         return motivation

#     def clean_judicial_record(self):
#         file = self.cleaned_data.get("judicial_record")

#         # 🔴 OBLIGATOIRE
#         if not file:
#             raise ValidationError(
#                 _("Le casier judiciaire est obligatoire.")
#             )

#         content_type = getattr(file, "content_type", "") or ""
#         if content_type != "application/pdf":
#             raise ValidationError(_("Le fichier doit être un PDF."))

#         if file.size > 2 * 1024 * 1024:
#             raise ValidationError(_("Le fichier ne doit pas dépasser 2 Mo."))

#         return file

#     # ==================================================
#     # SAVE STANDARD (PAS DE USER ICI)
#     # ==================================================
#     def save(self, commit=True):
#         """
#         Sauvegarde standard :
#         - le rattachement au User est effectué dans la vue
#         - statut par défaut : en attente de validation
#         """
#         instance = super().save(commit=False)

#         if not instance.membership_date:
#             instance.membership_date = timezone.now().date()

#         instance.is_active_member = False
#         instance.is_validated = False
#         instance.validated_at = None

#         if commit:
#             instance.save()
#             self.save_m2m()

#         return instance







# # accounts_users/forms/social/social_registration_form.py
# from django import forms
# from django.core.exceptions import ValidationError
# from django.utils.translation import gettext_lazy as _
# from django.utils import timezone

# from django_countries.widgets import CountrySelectWidget
# from phonenumber_field.formfields import PhoneNumberField

# from accounts_users.models.social.social_profile import SocialProfile


# class SocialRegistrationForm(forms.ModelForm):
#     """
#     Formulaire PUBLIC d’inscription sociale SOGENTIS

#     - Crée un SocialProfile lié à un User (OneToOne)
#     - Utilisé pour l’inscription sociale publique
#     - Compatible avec social_register_form.html
#     - Tous les champs métier sont validés côté serveur
#     """

#     # ==================================================
#     # CHAMPS NON-MODÈLE
#     # ==================================================
#     phone = PhoneNumberField(
#         label=_("Téléphone"),
#         required=True,
#         help_text=_(
#             "Numéro de téléphone valide avec indicatif international. "
#             "Exemple : +221 77 123 45 67"
#         ),
#     )

#     terms = forms.BooleanField(
#         label=_("J’accepte les conditions générales"),
#         required=True,
#         help_text=_(
#             "Vous devez accepter les conditions générales pour poursuivre l’inscription."
#         ),
#     )

#     # ==================================================
#     # CONFIGURATION MODÈLE
#     # ==================================================
#     class Meta:
#         model = SocialProfile

#         # ⚠️ user, is_validated, validated_at, created_at, updated_at
#         # sont gérés côté serveur / admin
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
#             # CONTACT / PROFESSION
#             # =========================
#             "phone",
#             "profession",
#             "function",

#             # =========================
#             # DOCUMENTS
#             # =========================
#             "profile_picture",
#             "judicial_record",

#             # =========================
#             # ADHÉSION SOCIALE
#             # =========================
#             "membership_role",
#             "membership_date",

#             # =========================
#             # ENGAGEMENT
#             # =========================
#             "motivation",
#             "availability",
#             "skills",
#         ]

#         # ==================================================
#         # WIDGETS
#         # ==================================================
#         widgets = {
#             # Identité
#             "last_name": forms.TextInput(attrs={"class": "form-control"}),
#             "first_name": forms.TextInput(attrs={"class": "form-control"}),
#             "middle_names": forms.TextInput(attrs={"class": "form-control"}),
#             "nickname": forms.TextInput(attrs={"class": "form-control"}),

#             # Naissance
#             "date_of_birth": forms.DateInput(
#                 attrs={"type": "date", "class": "form-control"}
#             ),
#             "place_of_birth": forms.TextInput(attrs={"class": "form-control"}),
#             "country_of_birth": CountrySelectWidget(
#                 attrs={"class": "form-select"}
#             ),

#             # Résidence
#             "country_of_residence": CountrySelectWidget(
#                 attrs={"class": "form-select"}
#             ),
#             "city_of_residence": forms.TextInput(attrs={"class": "form-control"}),
#             "address": forms.Textarea(
#                 attrs={"rows": 2, "class": "form-control"}
#             ),

#             # Profession
#             "profession": forms.TextInput(attrs={"class": "form-control"}),
#             "function": forms.TextInput(attrs={"class": "form-control"}),

#             # Documents
#             "profile_picture": forms.ClearableFileInput(
#                 attrs={"class": "form-control"}
#             ),
#             "judicial_record": forms.ClearableFileInput(
#                 attrs={"class": "form-control"}
#             ),

#             # Social
#             "membership_role": forms.Select(attrs={"class": "form-select"}),
#             "membership_date": forms.DateInput(
#                 attrs={"type": "date", "class": "form-control"}
#             ),

#             # Engagement
#             "motivation": forms.Textarea(
#                 attrs={"rows": 4, "class": "form-control"}
#             ),
#             "availability": forms.TextInput(attrs={"class": "form-control"}),
#             "skills": forms.Textarea(
#                 attrs={"rows": 3, "class": "form-control"}
#             ),
#         }

#         # ==================================================
#         # HELP TEXTS (COMPLETS)
#         # ==================================================
#         help_texts = {
#             # Identité
#             "last_name": _("Votre nom de famille officiel."),
#             "first_name": _("Votre prénom officiel."),
#             "middle_names": _("Autres prénoms éventuels (facultatif)."),
#             "nickname": _("Surnom ou nom usuel (facultatif)."),

#             # Naissance
#             "date_of_birth": _("Votre date de naissance."),
#             "place_of_birth": _("Ville ou localité de naissance."),
#             "country_of_birth": _("Pays dans lequel vous êtes né(e)."),

#             # Résidence
#             "country_of_residence": _("Pays où vous résidez actuellement."),
#             "city_of_residence": _("Ville de résidence actuelle."),
#             "address": _("Adresse complète de résidence."),

#             # Contact / Profession
#             "profession": _("Votre profession actuelle (facultatif)."),
#             "function": _("Fonction ou poste occupé (facultatif)."),

#             # Documents
#             "profile_picture": _("Photo de profil (facultatif)."),
#             "judicial_record": _(
#                 "Casier judiciaire OBLIGATOIRE au format PDF "
#                 "(taille maximale : 2 Mo)."
#             ),

#             # Social
#             "membership_role": _("Type d’adhésion sociale souhaité."),
#             "membership_date": _(
#                 "Laissez vide : la date sera renseignée automatiquement."
#             ),

#             # Engagement
#             "motivation": _(
#                 "Expliquez votre motivation à rejoindre SOGENTIS "
#                 "(au moins 20 caractères)."
#             ),
#             "availability": _(
#                 "Votre disponibilité pour les activités sociales "
#                 "(ex : week-end, temps partiel, temps plein)."
#             ),
#             "skills": _(
#                 "Compétences ou expériences utiles pour les actions sociales."
#             ),
#         }

#     # ==================================================
#     # VALIDATIONS MÉTIER
#     # ==================================================
#     def clean_membership_role(self):
#         role = self.cleaned_data.get("membership_role")
#         if not role:
#             raise ValidationError(
#                 _("Veuillez sélectionner un type d’adhésion sociale.")
#             )
#         return role

#     def clean_motivation(self):
#         motivation = (self.cleaned_data.get("motivation") or "").strip()
#         if len(motivation) < 20:
#             raise ValidationError(
#                 _("La motivation doit contenir au moins 20 caractères.")
#             )
#         return motivation

#     def clean_judicial_record(self):
#         file = self.cleaned_data.get("judicial_record")

#         # 🔴 OBLIGATOIRE
#         if not file:
#             raise ValidationError(
#                 _("Le casier judiciaire est obligatoire.")
#             )

#         content_type = getattr(file, "content_type", "") or ""
#         if content_type != "application/pdf":
#             raise ValidationError(_("Le fichier doit être un PDF."))

#         if file.size > 2 * 1024 * 1024:
#             raise ValidationError(_("Le fichier ne doit pas dépasser 2 Mo."))

#         return file

#     # ==================================================
#     # SAVE (AVEC USER)
#     # ==================================================
#     def save(self, user, commit=True):
#         """
#         Sauvegarde sécurisée du SocialProfile :
#         - liaison OneToOne avec User
#         - statut en attente de validation
#         """
#         instance = super().save(commit=False)

#         instance.user = user

#         if not instance.membership_date:
#             instance.membership_date = timezone.now().date()

#         instance.is_active_member = False
#         instance.is_validated = False
#         instance.validated_at = None

#         if commit:
#             existing = SocialProfile.objects.filter(user=user).first()
#             if existing:
#                 instance.pk = existing.pk
#             instance.save()
#             self.save_m2m()

#         return instance
