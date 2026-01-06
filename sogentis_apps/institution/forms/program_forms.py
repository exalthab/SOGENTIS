from django import forms

from institution.models.program import Program


class ProgramForm(forms.ModelForm):
    class Meta:
        model = Program
        fields = (
            "facility",
            "title",
            "summary",
            "content",
            "start_date",
            "end_date",
            "is_active",
        )
