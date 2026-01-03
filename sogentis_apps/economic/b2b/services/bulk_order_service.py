# economic/b2b/services/bulk_order_service.py
from decimal import Decimal

from django.db.models import Sum

from economic.b2b.models import BulkOrder


def recalculate_bulk_order_total(bulk_order: BulkOrder) -> Decimal:
    total = bulk_order.items.aggregate(total=Sum("total_price"))["total"] or Decimal("0.00")
    bulk_order.total_amount = total
    bulk_order.save(update_fields=["total_amount", "updated_at"])
    return total





# # economic/b2b/services/bulk_order_service.py
# from decimal import Decimal

# from django.db.models import Sum
# from django.db.models.functions import Coalesce

# from economic.b2b.models.bulk_order import BulkOrder
# from economic.ecommerce.models.product import Product


# def get_product_unit_price(product: Product) -> Decimal:
#     """
#     Retourne un prix unitaire fiable pour la commande en gros.
#     Adapte si tu as un champ différent dans Product.
#     """
#     # Priorité : promo_price -> price -> 0
#     for field in ("promo_price", "sale_price", "price", "unit_price"):
#         if hasattr(product, field):
#             val = getattr(product, field)
#             if val is not None:
#                 return Decimal(val)
#     return Decimal("0.00")


# def recalculate_bulk_order_total(bulk_order: BulkOrder) -> Decimal:
#     """
#     Recalcule total_amount depuis les items.total_price.
#     """
#     total = bulk_order.items.aggregate(
#         total=Coalesce(Sum("total_price"), Decimal("0.00"))
#     )["total"] or Decimal("0.00")

#     bulk_order.total_amount = total
#     # updated_at auto si tu as auto_now=True (sinon ignore)
#     bulk_order.save(update_fields=["total_amount", "updated_at"] if hasattr(bulk_order, "updated_at") else ["total_amount"])
#     return total







# # /economic/b2b/services/bulk_order_service.py

# from django.db.models import Sum
# from economic.b2b.models.bulk_order import BulkOrder


# def recalculate_bulk_order_total(bulk_order: BulkOrder):
#     total = bulk_order.items.aggregate(
#         total=Sum("total_price")
#     )["total"] or 0

#     bulk_order.total_amount = total
#     bulk_order.save(update_fields=["total_amount"])
