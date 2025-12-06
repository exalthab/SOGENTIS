# social/models/purchase_counter.py
from django.db import models
from django.utils.translation import gettext_lazy as _

class PublicationPurchaseCounter(models.Model):
    document = models.OneToOneField(
        "social.Publication",
        on_delete=models.CASCADE,
        related_name="purchase_counter",
        verbose_name=_("Document"),
    )
    last_number = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = _("Compteur d’achats (document)")
        verbose_name_plural = _("Compteurs d’achats (document)")
