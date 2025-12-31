# economic/ecommerce/models/invoice.py
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _

from .order import Order


class Invoice(models.Model):
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        verbose_name=_("UUID"),
    )

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="invoice",
        verbose_name=_("Commande"),
    )

    file = models.FileField(
        upload_to="invoices/%Y/%m/",
        verbose_name=_("Fichier PDF"),
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Créée le"),
    )

    class Meta:
        verbose_name = _("Facture")
        verbose_name_plural = _("Factures")

    def __str__(self):
        return f"Facture {self.uuid}"
