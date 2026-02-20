# economic/prestations/forms/prestation_request_form.py
from __future__ import annotations

from django import forms
from django.utils.translation import gettext_lazy as _

# Import robuste mais contrôlé
try:
    from ..models import PrestationRequest
except ImportError:  # refactor ou split de models
    from ..models.prestations_request import PrestationRequest


# -------------------------------------------------------------------
# Helpers de validation (faciles à tester)
# -------------------------------------------------------------------

def _clean_min_length(value: str, min_len: int, message: str) -> str:
    value = (value or "").strip()
    if len(value) < min_len:
        raise forms.ValidationError(message)
    return value


# -------------------------------------------------------------------
# Mixin de validation partagée
# -------------------------------------------------------------------

class SubjectMessageValidationMixin:
    """
    Mixin de validation pour les formulaires de demande
    (sujet + message).
    """

    subject_min_length = 5
    message_min_length = 20

    def clean_subject(self) -> str:
        return _clean_min_length(
            self.cleaned_data.get("subject"),
            self.subject_min_length,
            _("Le sujet doit contenir au moins %(min)d caractères.")
            % {"min": self.subject_min_length},
        )

    def clean_message(self) -> str:
        return _clean_min_length(
            self.cleaned_data.get("message"),
            self.message_min_length,
            _("Merci de détailler un peu plus votre demande (au moins %(min)d caractères).")
            % {"min": self.message_min_length},
        )


# -------------------------------------------------------------------
# Formulaire générique de demande de prestation
# -------------------------------------------------------------------

class PrestationRequestForm(SubjectMessageValidationMixin, forms.ModelForm):
    """
    Formulaire générique pour ouvrir une demande de prestation.

    Utilisé notamment sur :
    - /prestations/tickets/
    """

    class Meta:
        model = PrestationRequest
        fields = ["prestation", "subject", "message"]

        labels = {
            "prestation": _("Prestation concernée"),
            "subject": _("Sujet de la demande"),
            "message": _("Besoin / description"),
        }

        help_texts = {
            "prestation": _(
                "Choisissez la prestation concernée afin de mieux orienter votre demande."
            ),
            "subject": _(
                "Donnez un titre clair à votre demande (ex : « Création d’un site vitrine »)."
            ),
            "message": _(
                "Expliquez votre besoin le plus précisément possible : "
                "contexte, objectifs, délais, budget approximatif…"
            ),
        }

        widgets = {
            "prestation": forms.Select(attrs={"class": "form-select"}),
            "subject": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("Ex : Site vitrine pour association"),
                    "autocomplete": "off",
                }
            ),
            "message": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": _("Décrivez votre projet, vos attentes, les délais souhaités, etc."),
                }
            ),
        }


# -------------------------------------------------------------------
# Formulaire de demande de devis (prestation imposée)
# -------------------------------------------------------------------

class QuoteRequestForm(SubjectMessageValidationMixin, forms.ModelForm):
    """
    Formulaire de demande de devis pour une prestation donnée.

    - La prestation est fixée dans la vue (via slug ou ID)
    - L'utilisateur ne renseigne que sujet + message
    """

    class Meta:
        model = PrestationRequest
        fields = ["subject", "message"]

        labels = {
            "subject": _("Sujet de la demande"),
            "message": _("Besoin / description"),
        }

        help_texts = {
            "subject": _("Donnez un titre clair à votre demande de devis."),
            "message": _("Expliquez précisément votre besoin pour cette prestation."),
        }

        widgets = {
            "subject": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("Ex : Devis pour maintenance annuelle"),
                    "autocomplete": "off",
                }
            ),
            "message": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                }
            ),
        }






# # economic/prestations/forms/prestation_request_form.py -good
# from __future__ import annotations

# from django import forms
# from django.utils.translation import gettext_lazy as _

# from ..models import PrestationRequest


# class PrestationRequestForm(forms.ModelForm):
#     """
#     Formulaire générique pour ouvrir une demande de prestation
#     depuis la page /prestations/tickets/.
#     """

#     class Meta:
#         model = PrestationRequest

#         # On garde la logique: sélection prestation + sujet + message
#         fields = ["prestation", "subject", "message"]

#         labels = {
#             "prestation": _("Prestation concernée"),
#             "subject": _("Sujet de la demande"),
#             "message": _("Besoin / description"),
#         }

#         help_texts = {
#             "prestation": _(
#                 "Choisissez la prestation concernée. "
#                 "Cela nous permet de mieux orienter votre demande."
#             ),
#             "subject": _(
#                 "Donnez un titre clair à votre demande (ex : « Création d’un site vitrine »)."
#             ),
#             "message": _(
#                 "Expliquez votre besoin le plus précisément possible : contexte, objectifs, délais, budget approximatif..."
#             ),
#         }

#         widgets = {
#             "prestation": forms.Select(attrs={"class": "form-select"}),
#             "subject": forms.TextInput(
#                 attrs={
#                     "class": "form-control",
#                     "placeholder": _("Ex : Site vitrine pour association"),
#                 }
#             ),
#             "message": forms.Textarea(
#                 attrs={
#                     "class": "form-control",
#                     "rows": 5,
#                     "placeholder": _("Décrivez votre projet, vos attentes, les délais souhaités, etc."),
#                 }
#             ),
#         }

#     def clean_subject(self):
#         subject = (self.cleaned_data.get("subject") or "").strip()
#         if len(subject) < 5:
#             raise forms.ValidationError(_("Le sujet doit contenir au moins 5 caractères."))
#         return subject

#     def clean_message(self):
#         message = (self.cleaned_data.get("message") or "").strip()
#         if len(message) < 20:
#             raise forms.ValidationError(_("Merci de détailler un peu plus votre demande (au moins 20 caractères)."))
#         return message


# class QuoteRequestForm(forms.ModelForm):
#     """
#     Formulaire de devis pour une prestation donnée (route /<slug>/quote/).
#     - la prestation est fixée dans la vue à partir du slug
#     - on ne montre que sujet + message
#     """

#     class Meta:
#         model = PrestationRequest
#         fields = ["subject", "message"]

#         labels = {
#             "subject": _("Sujet de la demande"),
#             "message": _("Besoin / description"),
#         }

#         help_texts = {
#             "subject": _("Donnez un titre clair à votre demande de devis."),
#             "message": _("Expliquez précisément votre besoin pour cette prestation."),
#         }

#         widgets = {
#             "subject": forms.TextInput(
#                 attrs={
#                     "class": "form-control",
#                     "placeholder": _("Ex : Devis pour maintenance annuelle"),
#                 }
#             ),
#             "message": forms.Textarea(
#                 attrs={
#                     "class": "form-control",
#                     "rows": 5,
#                 }
#             ),
#         }

#     def clean_subject(self):
#         subject = (self.cleaned_data.get("subject") or "").strip()
#         if len(subject) < 5:
#             raise forms.ValidationError(_("Le sujet doit contenir au moins 5 caractères."))
#         return subject

#     def clean_message(self):
#         message = (self.cleaned_data.get("message") or "").strip()
#         if len(message) < 20:
#             raise forms.ValidationError(_("Merci de détailler un peu plus votre demande (au moins 20 caractères)."))
#         return message






# # economic/prestations/forms/prestation_request_form.py

# from django import forms
# from django.utils.translation import gettext_lazy as _

# from ..models.prestations_request import ServiceRequest


# class ServiceRequestForm(forms.ModelForm):
#     """
#     Formulaire générique pour ouvrir une demande de service
#     depuis la page /services/tickets/.
#     """

#     class Meta:
#         model = ServiceRequest

#         # On utilise les champs réellement présents dans le modèle
#         fields = ["service", "subject", "message"]

#         labels = {
#             "service": _("Service concerné"),
#             "subject": _("Sujet de la demande"),
#             "message": _("Besoin / description"),
#         }

#         help_texts = {
#             "service": _(
#                 "Choisissez le service concerné. "
#                 "Cela nous permet de mieux orienter votre demande."
#             ),
#             "subject": _(
#                 "Donnez un titre clair à votre demande (ex : « Création d’un site vitrine »)."
#             ),
#             "message": _(
#                 "Expliquez votre besoin le plus précisément possible : contexte, objectifs, délais, budget approximatif..."
#             ),
#         }

#         widgets = {
#             "service": forms.Select(
#                 attrs={
#                     "class": "form-select",
#                 }
#             ),
#             "subject": forms.TextInput(
#                 attrs={
#                     "class": "form-control",
#                     "placeholder": _("Ex : Site vitrine pour association"),
#                 }
#             ),
#             "message": forms.Textarea(
#                 attrs={
#                     "class": "form-control",
#                     "rows": 5,
#                     "placeholder": _(
#                         "Décrivez votre projet, vos attentes, les délais souhaités, etc."
#                     ),
#                 }
#             ),
#         }

#     def clean_subject(self):
#         subject = (self.cleaned_data.get("subject") or "").strip()
#         if len(subject) < 5:
#             raise forms.ValidationError(
#                 _("Le sujet doit contenir au moins 5 caractères.")
#             )
#         return subject

#     def clean_message(self):
#         message = (self.cleaned_data.get("message") or "").strip()
#         if len(message) < 20:
#             raise forms.ValidationError(
#                 _("Merci de détailler un peu plus votre demande (au moins 20 caractères).")
#             )
#         return message


# class QuoteRequestForm(forms.ModelForm):
#     """
#     Formulaire de devis pour un service donné (route /<slug>/quote/).
#     - Le service est fixé dans la vue à partir du slug.
#     - On ne montre que sujet + message.
#     """

#     class Meta:
#         model = ServiceRequest
#         fields = ["subject", "message"]

#         labels = {
#             "subject": _("Sujet de la demande"),
#             "message": _("Besoin / description"),
#         }

#         help_texts = {
#             "subject": _(
#                 "Donnez un titre clair à votre demande de devis."
#             ),
#             "message": _(
#                 "Expliquez précisément votre besoin pour ce service."
#             ),
#         }

#         widgets = {
#             "subject": forms.TextInput(
#                 attrs={
#                     "class": "form-control",
#                     "placeholder": _("Ex : Devis pour maintenance annuelle"),
#                 }
#             ),
#             "message": forms.Textarea(
#                 attrs={
#                     "class": "form-control",
#                     "rows": 5,
#                 }
#             ),
#         }

#     def clean_subject(self):
#         subject = (self.cleaned_data.get("subject") or "").strip()
#         if len(subject) < 5:
#             raise forms.ValidationError(
#                 _("Le sujet doit contenir au moins 5 caractères.")
#             )
#         return subject

#     def clean_message(self):
#         message = (self.cleaned_data.get("message") or "").strip()
#         if len(message) < 20:
#             raise forms.ValidationError(
#                 _("Merci de détailler un peu plus votre demande (au moins 20 caractères).")
#             )
#         return message
