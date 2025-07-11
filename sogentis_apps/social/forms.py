# social/forms.py
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Donation, Engagement

class DonationForm(forms.ModelForm):
    monthly = forms.BooleanField(
        required=False,
        label=_("Faire un don mensuel récurrent"),
        widget=forms.CheckboxInput(attrs={
            "class": "form-check-input"
        })
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
            # Ajoute ici 'payment_method' si tu veux proposer le choix direct dans ce formulaire
        ]
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
                'placeholder': _("Montant du don"),
                'min': '1'
            }),
            'project': forms.Select(attrs={
                'class': 'form-select'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _("Message (optionnel)")
            }),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is not None and amount <= 0:
            raise forms.ValidationError(_("Le montant doit être positif."))
        return amount

class EngagementForm(forms.ModelForm):
    class Meta:
        model = Engagement
        fields = ['title', 'description', 'date']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _("Titre de l’engagement")
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': _("Description de votre engagement")
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }