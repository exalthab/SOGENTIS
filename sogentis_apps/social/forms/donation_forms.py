# social/forms/donation_forms.py

from django import forms
from django.utils.translation import gettext_lazy as _
from social.models import Donation
from about.models.child import Child
from about.models.mother import Mother


class DonationForm(forms.ModelForm):
    """
    Formulaire de don avec champs supplémentaires :
    - child : Enfant à soutenir
    - mother : Mère à soutenir
    Ces champs ne sont PAS dans Donation mais accompagnent le flux.
    """

    child = forms.ModelChoiceField(
        queryset=Child.objects.all(),
        required=False,
        label=_("Enfant à soutenir"),
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    mother = forms.ModelChoiceField(
        queryset=Mother.objects.all(),
        required=False,
        label=_("Mère à soutenir"),
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Donation
        fields = [
            'donor_name',
            'email',
            'amount',
            'project',
            'message',
            'monthly',
        ]
        labels = {
            'donor_name': _("Nom du donateur"),
            'email': _("Adresse email"),
            'amount': _("Montant du don (FCFA)"),
            'project': _("Projet à soutenir"),
            'message': _("Message (optionnel)"),
            'monthly': _("Faire ce don chaque mois"),
        }
        widgets = {
            'donor_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _("Votre nom complet")
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': _("Votre adresse email")
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': _("Montant en FCFA")
            }),
            'project': forms.Select(attrs={
                'class': 'form-select'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _("Votre message (optionnel)")
            }),
            'monthly': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'id': 'id_monthly'
            }),
        }

    # ---------------------------------------------------------
    # Validation : on interdit le choix simultané child + mother
    # ---------------------------------------------------------
    def clean(self):
        cleaned_data = super().clean()
        child = cleaned_data.get("child")
        mother = cleaned_data.get("mother")

        if child and mother:
            raise forms.ValidationError(
                _("Vous ne pouvez soutenir qu'un enfant OU une mère, pas les deux.")
            )

        return cleaned_data
