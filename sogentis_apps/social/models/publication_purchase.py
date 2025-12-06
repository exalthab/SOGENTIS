# social/models/publication_purchase.py
from django.db import models, transaction
from django.db.models import F
from django.utils import timezone
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from .purchase_counter import PublicationPurchaseCounter

class PublicationPurchase(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="publication_purchases",
        verbose_name=_("Acheteur"),
    )
    document = models.ForeignKey(
        "social.Publication",
        on_delete=models.PROTECT,
        related_name="purchases",              # ✅ reverse accessor officiel
        related_query_name="purchase",
        verbose_name=_("Document"),
    )
    copy_number = models.PositiveIntegerField(_("Numéro de copie"))
    created_at = models.DateTimeField(_("Acheté le"), default=timezone.now)

    class Meta:
        unique_together = (("document", "copy_number"),)
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.document_id}#{self.copy_number} par {self.user_id}"

    @classmethod
    def create_with_next_number(cls, *, user, document) -> "PublicationPurchase":
        with transaction.atomic():
            counter, _ = PublicationPurchaseCounter.objects.select_for_update().get_or_create(
                document=document, defaults={"last_number": 0}
            )
            PublicationPurchaseCounter.objects.filter(pk=counter.pk).update(last_number=F("last_number") + 1)
            counter.refresh_from_db(fields=["last_number"])
            return cls.objects.create(user=user, document=document, copy_number=counter.last_number)
