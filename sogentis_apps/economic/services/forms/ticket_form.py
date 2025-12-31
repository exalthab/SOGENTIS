# economic/services/forms/ticket_form.py

from django import forms
from django.utils.translation import gettext_lazy as _

from economic.services.models import ServiceTicket  # adapte si ton chemin est différent


class ServiceTicketForm(forms.ModelForm):
    """
    Formulaire pour ouvrir une demande de service (ticket).
    - L'utilisateur est attaché dans la vue (request.user)
    - Le statut, la référence, les dates sont gérés en interne (modèle / signals / save)
    """

    class Meta:
        model = ServiceTicket

        # Champs visibles dans le formulaire (tu peux ajuster)
        fields = [
            "service",       # FK vers Service (optionnel)
            "subject",       # Sujet / titre de la demande
            "message",       # Description détaillée
            "priority",      # Niveau de priorité
        ]

        labels = {
            "service": _("Service concerné"),
            "subject": _("Sujet de la demande"),
            "message": _("Description détaillée"),
            "priority": _("Priorité"),
        }

        help_texts = {
            "service": _(
                "Choisissez le service concerné si vous le connaissez. "
                "Sinon, laissez vide et décrivez simplement votre besoin."
            ),
            "subject": _(
                "Donnez un titre clair à votre demande (ex : « Création d’un site vitrine »)."
            ),
            "message": _(
                "Expliquez votre besoin le plus précisément possible : contexte, objectifs, délais, budget approximatif..."
            ),
            "priority": _(
                "Indiquez l’importance de votre demande. Nous essayons de prioriser en conséquence."
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
            "priority": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
        }

    def clean_subject(self):
        subject = self.cleaned_data.get("subject", "").strip()
        if len(subject) < 5:
            raise forms.ValidationError(
                _("Le sujet doit contenir au moins 5 caractères.")
            )
        return subject

    def clean_message(self):
        message = self.cleaned_data.get("message", "").strip()
        if len(message) < 20:
            raise forms.ValidationError(
                _("Merci de détailler un peu plus votre demande (au moins 20 caractères).")
            )
        return message
