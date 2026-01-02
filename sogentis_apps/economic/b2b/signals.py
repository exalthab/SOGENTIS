# economic/b2b/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from economic.b2b.models import BulkOrderItem
from economic.b2b.services.bulk_order_service import recalculate_bulk_order_total


@receiver(post_save, sender=BulkOrderItem)
def _item_saved(sender, instance, **kwargs):
    recalculate_bulk_order_total(instance.bulk_order)


@receiver(post_delete, sender=BulkOrderItem)
def _item_deleted(sender, instance, **kwargs):
    recalculate_bulk_order_total(instance.bulk_order)
