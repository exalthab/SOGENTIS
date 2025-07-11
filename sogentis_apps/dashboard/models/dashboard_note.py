
# #dashboard/models/dashboard_note.py
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class DashboardNote(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="dashboard_notes",
        verbose_name=_("Auteur"),
        null=True, blank=True  # Ajoute ceci

    )
    title = models.CharField(_("Titre"), max_length=200)
    content = models.TextField(_("Contenu"))
    is_public = models.BooleanField(_("Visible au public"), default=False)
    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)

    class Meta:
        verbose_name = _("Note")
        verbose_name_plural = _("Notes")
        ordering = ['-created_at']

    def __str__(self):
        # Option 1 : Juste le titre
        # return self.title
        # Option 2 : Titre + auteur
        return f"{self.title} ({self.author})"




# #dashboard/models/dashboard_note.py
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





