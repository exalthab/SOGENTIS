# economic/prestations/models/projects.py
from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class ProjectStatus(models.TextChoices):
    DRAFT = "DRAFT", _("Brouillon")
    PUBLISHED = "PUBLISHED", _("Publié")
    CLOSED = "CLOSED", _("Fermé")
    AWARDED = "AWARDED", _("Attribué")


class ProjectCall(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="project_calls")

    title = models.CharField(max_length=220)
    slug = models.SlugField(max_length=220, unique=True)
    summary = models.CharField(max_length=320, blank=True)
    description = models.TextField()

    currency = models.CharField(max_length=8, default="XOF")
    budget_min = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    budget_max = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    deadline = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=12, choices=ProjectStatus.choices, default=ProjectStatus.DRAFT)
    is_public = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(fields=["status", "is_public", "-created_at"]),
            models.Index(fields=["slug"]),
        ]

    def __str__(self) -> str:
        return self.title


class ProjectAttachment(models.Model):
    project = models.ForeignKey(ProjectCall, on_delete=models.CASCADE, related_name="attachments")
    file = models.FileField(upload_to="prestations/projects/%Y/%m/")
    label = models.CharField(max_length=120, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.label or self.file.name


class BidStatus(models.TextChoices):
    SENT = "SENT", _("Envoyée")
    SHORTLIST = "SHORTLIST", _("Pré-sélectionnée")
    REJECTED = "REJECTED", _("Refusée")
    ACCEPTED = "ACCEPTED", _("Acceptée")


class ProjectBid(models.Model):
    project = models.ForeignKey(ProjectCall, on_delete=models.CASCADE, related_name="bids")
    bidder = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="project_bids")

    message = models.TextField()
    amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=8, default="XOF")

    status = models.CharField(max_length=12, choices=BidStatus.choices, default=BidStatus.SENT)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(fields=["project", "status", "-created_at"]),
            models.Index(fields=["bidder", "-created_at"]),
        ]

    def __str__(self) -> str:
        return f"Bid #{self.id} ({self.project_id})"
