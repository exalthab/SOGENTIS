
# # dashboard/forms/note_form.py
from django import forms
from dashboard.models.dashboard_note import DashboardNote
from django.utils.translation import gettext_lazy as _

class DashboardNoteForm(forms.ModelForm):
    class Meta:
        model = DashboardNote
        fields = ['title', 'content', 'is_public']
        labels = {
            'title': _("Titre de la note"),
            'content': _("Contenu de la note"),
            'is_public': _("Note publique ?")
        }
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _("Titre de la note"),
                'maxlength': 200
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': _("Écris ta note ici…")
            }),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_title(self):
        title = self.cleaned_data.get("title", "").strip()
        if not title:
            raise forms.ValidationError(_("Le titre ne peut pas être vide."))
        if len(title) > 200:
            raise forms.ValidationError(_("Le titre ne doit pas dépasser 200 caractères."))
        return title

    def clean_content(self):
        content = self.cleaned_data.get("content", "").strip()
        if not content:
            raise forms.ValidationError(_("Le contenu ne peut pas être vide."))
        return content




# from django.conf import settings
# from django.db import models
# from django.utils import timezone

# class DashboardNote(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='dashboard_notes')
#     title = models.CharField(max_length=255)
#     content = models.TextField()
#     created_at = models.DateTimeField(default=timezone.now)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         verbose_name = "Dashboard Note"
#         verbose_name_plural = "Dashboard Notes"
#         ordering = ['-created_at']

#     def __str__(self):
#         return self.title

