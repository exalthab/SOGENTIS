# core/models.py

from django.db import models
from django.utils.translation import gettext_lazy as _

class ContactMessage(models.Model):
    name = models.CharField(_("Nom"), max_length=255)
    email = models.EmailField(_("Adresse email"))
    message = models.TextField(_("Message"))
    created_at = models.DateTimeField(_("Envoyé le"), auto_now_add=True)  # Bonne pratique

    class Meta:
        verbose_name = _("Message de contact")
        verbose_name_plural = _("Messages de contact")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} <{self.email}> - {self.created_at:%d/%m/%Y %H:%M}"

# #core/models.py
# from django.db import models
# from django.utils import timezone


# class ContactMessage(models.Model):
#     name = models.CharField(max_length=255)
#     email = models.EmailField()
#     message = models.TextField()
#     created_at = models.DateTimeField(default=timezone.now)

#     def __str__(self):
#         return f"Message from {self.name} <{self.email}>"
