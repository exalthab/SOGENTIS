# economic/services/forms/service_request_form.py

from django import forms
from django.utils.translation import gettext_lazy as _

from ..models.service_request import ServiceRequest


class ServiceRequestForm(forms.ModelForm):
    """
    Formulaire générique pour ouvrir une demande de service
    depuis la page /services/tickets/.
    """

    class Meta:
        model = ServiceRequest

        # On utilise les champs réellement présents dans le modèle
        fields = ["service", "subject", "message"]

        labels = {
            "service": _("Service concerné"),
            "subject": _("Sujet de la demande"),
            "message": _("Besoin / description"),
        }

        help_texts = {
            "service": _(
                "Choisissez le service concerné. "
                "Cela nous permet de mieux orienter votre demande."
            ),
            "subject": _(
                "Donnez un titre clair à votre demande (ex : « Création d’un site vitrine »)."
            ),
            "message": _(
                "Expliquez votre besoin le plus précisément possible : contexte, objectifs, délais, budget approximatif..."
            ),
        }

        widgets = {
            "service": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "subject": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("Ex : Site vitrine pour association"),
                }
            ),
            "message": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": _(
                        "Décrivez votre projet, vos attentes, les délais souhaités, etc."
                    ),
                }
            ),
        }

    def clean_subject(self):
        subject = (self.cleaned_data.get("subject") or "").strip()
        if len(subject) < 5:
            raise forms.ValidationError(
                _("Le sujet doit contenir au moins 5 caractères.")
            )
        return subject

    def clean_message(self):
        message = (self.cleaned_data.get("message") or "").strip()
        if len(message) < 20:
            raise forms.ValidationError(
                _("Merci de détailler un peu plus votre demande (au moins 20 caractères).")
            )
        return message


class QuoteRequestForm(forms.ModelForm):
    """
    Formulaire de devis pour un service donné (route /<slug>/quote/).
    - Le service est fixé dans la vue à partir du slug.
    - On ne montre que sujet + message.
    """

    class Meta:
        model = ServiceRequest
        fields = ["subject", "message"]

        labels = {
            "subject": _("Sujet de la demande"),
            "message": _("Besoin / description"),
        }

        help_texts = {
            "subject": _(
                "Donnez un titre clair à votre demande de devis."
            ),
            "message": _(
                "Expliquez précisément votre besoin pour ce service."
            ),
        }

        widgets = {
            "subject": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("Ex : Devis pour maintenance annuelle"),
                }
            ),
            "message": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                }
            ),
        }

    def clean_subject(self):
        subject = (self.cleaned_data.get("subject") or "").strip()
        if len(subject) < 5:
            raise forms.ValidationError(
                _("Le sujet doit contenir au moins 5 caractères.")
            )
        return subject

    def clean_message(self):
        message = (self.cleaned_data.get("message") or "").strip()
        if len(message) < 20:
            raise forms.ValidationError(
                _("Merci de détailler un peu plus votre demande (au moins 20 caractères).")
            )
        return message
