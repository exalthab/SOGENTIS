# economic/services/models/service_request.py
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from .service import Service


class ServiceRequest(models.Model):
    STATUS_CHOICES = [
        ("new", _("Nouvelle")),
        ("in_progress", _("En cours")),
        ("done", _("Terminée")),
        ("cancelled", _("Annulée")),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="service_requests",
        verbose_name=_("Utilisateur"),
    )

    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name="requests",
        verbose_name=_("Service"),
    )

    subject = models.CharField(
        max_length=255,
        verbose_name=_("Sujet"),
    )

    message = models.TextField(
        verbose_name=_("Besoin / description"),
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="new",
        verbose_name=_("Statut"),
    )

    created_at = models.DateTimeField(
        default=timezone.now,
        editable=False,
        verbose_name=_("Créé le"),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Mis à jour le"),
    )

    class Meta:
        verbose_name = _("Demande de service")
        verbose_name_plural = _("Demandes de service")
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return f"{self.user} → {self.service} ({self.get_status_display()})"








# # economic/services/models/service_request.py
# from django.db import models
# from django.conf import settings
# from django.utils.translation import gettext_lazy as _

# from .service import Service


# class ServiceRequest(models.Model):
#     STATUS_CHOICES = [
#         ("new", _("Nouveau")),
#         ("in_progress", _("En cours")),
#         ("done", _("Traité")),
#         ("cancelled", _("Annulé")),
#     ]

#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name="service_requests",
#         verbose_name=_("Utilisateur"),
#     )

#     service = models.ForeignKey(
#         Service,
#         on_delete=models.CASCADE,
#         related_name="requests",
#         verbose_name=_("Service"),
#     )

#     full_name = models.CharField(max_length=255, verbose_name=_("Nom complet"))
#     email = models.EmailField(verbose_name=_("Email"))
#     phone = models.CharField(max_length=50, blank=True, verbose_name=_("Téléphone"))

#     message = models.TextField(verbose_name=_("Message / Besoin"))
#     status = models.CharField(
#         max_length=20,
#         choices=STATUS_CHOICES,
#         default="new",
#         verbose_name=_("Statut"),
#     )

#     created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Créé le"))
#     updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Mis à jour le"))

#     class Meta:
#         verbose_name = _("Demande de service")
#         verbose_name_plural = _("Demandes de services")
#         ordering = ["-created_at"]

#     def __str__(self):
#         return f"{self.full_name} → {self.service}"
