# social/forms/project_forms.py

from django import forms
from social.models import Project

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["title", "description", "goal", "image", "is_active"]  # 👈 correction ici

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})
