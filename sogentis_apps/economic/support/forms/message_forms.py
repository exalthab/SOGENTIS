from django import forms
from django.utils.translation import gettext_lazy as _

from economic.support.models import TicketMessage


class TicketMessageForm(forms.ModelForm):
    class Meta:
        model = TicketMessage
        fields = ["message", "attachment"]

        widgets = {
            "message": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": _("Votre message...")}),
        }

    def clean_attachment(self):
        f = self.cleaned_data.get("attachment")
        if not f:
            return f
        max_mb = 10
        if f.size > max_mb * 1024 * 1024:
            raise forms.ValidationError(_("Fichier trop lourd (max %(mb)s MB).") % {"mb": max_mb})
        return f
