# accounting/models/audit.py
from __future__ import annotations

from typing import Any, Dict, Optional

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _


class AccountingAudit(models.Model):
    """
    Audit log comptable (QuickBooks-ish).
    Utilisation: posting, close period, corrections, imports, etc.
    """

    class Action(models.TextChoices):
        POST = "POST", _("Post entry")
        UNPOST = "UNPOST", _("Unpost entry")
        CLOSE_PERIOD = "CLOSE_PERIOD", _("Close period")
        OPEN_PERIOD = "OPEN_PERIOD", _("Open period")
        ADJUST = "ADJUST", _("Adjust / correction")
        IMPORT = "IMPORT", _("Import")
        OTHER = "OTHER", _("Other")

    action = models.CharField(max_length=32, choices=Action.choices, db_index=True)

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="accounting_audits",
    )

    # Generic target (optional)
    content_type = models.ForeignKey(ContentType, null=True, blank=True, on_delete=models.SET_NULL)
    object_id = models.CharField(max_length=64, blank=True, default="", db_index=True)
    content_object = GenericForeignKey("content_type", "object_id")

    pole = models.CharField(max_length=16, blank=True, default="", db_index=True)
    company_code = models.CharField(max_length=32, blank=True, default="", db_index=True)

    message = models.CharField(max_length=240, blank=True, default="")
    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(fields=["pole", "company_code", "created_at"]),
            models.Index(fields=["action", "created_at"]),
            models.Index(fields=["content_type", "object_id"]),
        ]

    def __str__(self) -> str:
        who = getattr(self.actor, "username", None) or "system"
        tgt = ""
        if self.content_type and self.object_id:
            tgt = f" {self.content_type.app_label}.{self.content_type.model}:{self.object_id}"
        scope = "/".join([p for p in [self.pole, self.company_code] if p]) or "GLOBAL"
        return f"[{scope}] {self.action} by {who}{tgt}"

    @classmethod
    def log(
        cls,
        *,
        action: str,
        actor=None,
        pole: str = "",
        company_code: str = "",
        obj=None,
        message: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "AccountingAudit":
        ct = None
        oid = ""
        if obj is not None:
            try:
                ct = ContentType.objects.get_for_model(obj.__class__)
                oid = str(getattr(obj, "pk", "") or "")
            except Exception:
                ct = None
                oid = ""
        return cls.objects.create(
            action=(action or cls.Action.OTHER),
            actor=actor,
            content_type=ct,
            object_id=oid,
            pole=(pole or "").strip().upper(),
            company_code=(company_code or "").strip().upper(),
            message=(message or "")[:240],
            metadata=metadata or {},
        )
