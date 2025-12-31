# sogentis_apps/economic/b2b/services/bulk_order_service.py

from django.db.models import Sum
from economic.b2b.models.bulk_order import BulkOrder


def recalculate_bulk_order_total(bulk_order: BulkOrder):
    total = bulk_order.items.aggregate(
        total=Sum("total_price")
    )["total"] or 0

    bulk_order.total_amount = total
    bulk_order.save(update_fields=["total_amount"])
