from django import forms
from django.utils.translation import gettext_lazy as _

from economic.support.models import SupportTicket


class TicketCreateForm(forms.ModelForm):
    class Meta:
        model = SupportTicket
        fields = ["subject", "description", "priority", "order_ref"]

        widgets = {
            "subject": forms.TextInput(attrs={"class": "form-control", "placeholder": _("Sujet")}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 5, "placeholder": _("Décrivez votre problème...")}),
            "priority": forms.Select(attrs={"class": "form-select"}),
            "order_ref": forms.TextInput(attrs={"class": "form-control", "placeholder": _("Ex: ORD-2025-0001")}),
        }
