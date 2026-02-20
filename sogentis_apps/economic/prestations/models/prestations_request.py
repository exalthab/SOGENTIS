# economic/prestations/models/prestations_request.py
from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .prestations import Prestation
from .prestations_package import PrestationPackage


class PrestationRequest(models.Model):
    class Status(models.TextChoices):
        NEW = "new", _("Nouvelle")
        IN_PROGRESS = "in_progress", _("En cours")
        DONE = "done", _("Terminée")
        CANCELLED = "cancelled", _("Annulée")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="prestation_requests",
        verbose_name=_("Utilisateur"),
    )

    prestation = models.ForeignKey(
        Prestation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="requests",
        verbose_name=_("Prestation"),
    )

    package = models.ForeignKey(
        PrestationPackage,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="requests",
        verbose_name=_("Pack"),
    )

    subject = models.CharField(max_length=255, verbose_name=_("Sujet"))
    message = models.TextField(verbose_name=_("Besoin / description"))

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
        verbose_name=_("Statut"),
        db_index=True,
    )

    created_at = models.DateTimeField(default=timezone.now, editable=False, verbose_name=_("Créé le"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Mis à jour le"))

    class Meta:
        verbose_name = _("Demande de prestation")
        verbose_name_plural = _("Demandes de prestations")
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(fields=["user", "status", "created_at"]),
            models.Index(fields=["prestation", "created_at"]),
            models.Index(fields=["package", "created_at"]),
        ]
        constraints = [
            models.CheckConstraint(
                name="prestation_xor_package",
                condition=(
                    (Q(prestation__isnull=False) & Q(package__isnull=True))
                    | (Q(prestation__isnull=True) & Q(package__isnull=False))
                ),
            ),
        ]

    def clean(self):
        super().clean()

        if self.prestation and self.package:
            raise ValidationError(_("Une demande ne peut pas référencer à la fois une prestation et un pack."))

        if not self.prestation and not self.package:
            raise ValidationError(_("Une demande doit référencer une prestation ou un pack."))

    def __str__(self) -> str:
        target = self.prestation or self.package
        return f"{self.user} → {target} ({self.get_status_display()})"





# # economic/prestations/models/prestations_request.py
# from __future__ import annotations

# from django.conf import settings
# from django.core.exceptions import ValidationError
# from django.db import models
# from django.db.models import Q
# from django.utils import timezone
# from django.utils.translation import gettext_lazy as _

# from .prestations import Service
# from .prestations_package import ServicePackage


# class ServiceRequest(models.Model):
#     class Status(models.TextChoices):
#         NEW = "new", _("Nouvelle")
#         IN_PROGRESS = "in_progress", _("En cours")
#         DONE = "done", _("Terminée")
#         CANCELLED = "cancelled", _("Annulée")

#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name="service_requests",
#         verbose_name=_("Utilisateur"),
#     )

#     service = models.ForeignKey(
#         Service,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name="requests",
#         verbose_name=_("Service"),
#     )

#     package = models.ForeignKey(
#         ServicePackage,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name="requests",
#         verbose_name=_("Pack"),
#     )

#     subject = models.CharField(
#         max_length=255,
#         verbose_name=_("Sujet"),
#     )

#     message = models.TextField(
#         verbose_name=_("Besoin / description"),
#     )

#     status = models.CharField(
#         max_length=20,
#         choices=Status.choices,
#         default=Status.NEW,
#         verbose_name=_("Statut"),
#         db_index=True,
#     )

#     created_at = models.DateTimeField(
#         default=timezone.now,
#         editable=False,
#         verbose_name=_("Créé le"),
#     )

#     updated_at = models.DateTimeField(
#         auto_now=True,
#         verbose_name=_("Mis à jour le"),
#     )

#     class Meta:
#         verbose_name = _("Demande de service")
#         verbose_name_plural = _("Demandes de service")
#         ordering = ["-created_at", "-id"]

#         indexes = [
#             models.Index(fields=["user", "status", "created_at"]),
#             models.Index(fields=["service", "created_at"]),
#             models.Index(fields=["package", "created_at"]),
#         ]

#         constraints = [
#             # ✅ EXACTEMENT un des deux : service OU package
#             models.CheckConstraint(
#                 name="service_xor_package",
#                 check=(
#                     (Q(service__isnull=False) & Q(package__isnull=True)) |
#                     (Q(service__isnull=True) & Q(package__isnull=False))
#                 ),
#             ),
#         ]

#     # ✅ Validation applicative (API, admin, forms)
#     def clean(self):
#         super().clean()

#         if self.service and self.package:
#             raise ValidationError(
#                 _("Une demande ne peut pas référencer à la fois un service et un pack.")
#             )

#         if not self.service and not self.package:
#             raise ValidationError(
#                 _("Une demande doit référencer un service ou un pack.")
#             )

#     def __str__(self) -> str:
#         target = self.service or self.package
#         return f"{self.user} → {target} ({self.get_status_display()})"






# # economic/services/models/service_request.py
# from django.db import models
# from django.conf import settings
# from django.utils.translation import gettext_lazy as _
# from django.utils import timezone

# from .service import Service


# class ServiceRequest(models.Model):
#     STATUS_CHOICES = [
#         ("new", _("Nouvelle")),
#         ("in_progress", _("En cours")),
#         ("done", _("Terminée")),
#         ("cancelled", _("Annulée")),
#     ]

#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name="service_requests",
#         verbose_name=_("Utilisateur"),
#     )

#     service = models.ForeignKey(
#         Service,
#         on_delete=models.CASCADE,
#         related_name="requests",
#         verbose_name=_("Service"),
#     )

#     subject = models.CharField(
#         max_length=255,
#         verbose_name=_("Sujet"),
#     )

#     message = models.TextField(
#         verbose_name=_("Besoin / description"),
#     )

#     status = models.CharField(
#         max_length=20,
#         choices=STATUS_CHOICES,
#         default="new",
#         verbose_name=_("Statut"),
#     )

#     created_at = models.DateTimeField(
#         default=timezone.now,
#         editable=False,
#         verbose_name=_("Créé le"),
#     )
#     updated_at = models.DateTimeField(
#         auto_now=True,
#         verbose_name=_("Mis à jour le"),
#     )

#     class Meta:
#         verbose_name = _("Demande de service")
#         verbose_name_plural = _("Demandes de service")
#         ordering = ["-created_at", "-id"]

#     def __str__(self):
#         return f"{self.user} → {self.service} ({self.get_status_display()})"








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
