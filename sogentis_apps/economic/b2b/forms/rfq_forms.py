# economic/b2b/forms/rfq_forms.py
from django import forms
from economic.b2b.models import RFQ, Offer


class RFQForm(forms.ModelForm):
    class Meta:
        model = RFQ
        fields = [
            "title", "description",
            "quantity", "unit",
            "budget_min", "budget_max", "currency",
            "deadline", "status",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "quantity": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "unit": forms.TextInput(attrs={"class": "form-control"}),
            "budget_min": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "budget_max": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "currency": forms.TextInput(attrs={"class": "form-control"}),
            "deadline": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }


class OfferForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = ["message", "price_total", "currency", "delivery_days"]
        widgets = {
            "message": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "price_total": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "currency": forms.TextInput(attrs={"class": "form-control"}),
            "delivery_days": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
        }
