# economic/ecommerce/services/pricing_service.py
from decimal import Decimal


def calculate_price(product, quantity=1):
    """
    Version minimale :
    prix unitaire * quantité
    """
    return Decimal(product.price) * Decimal(quantity)

def get_effective_price(pricing, quantity=1, commerce_mode="B2C"):
    """
    Retourne le prix unitaire effectif selon :
    - B2C / B2B
    - Promotions
    - Quantité (B2B)
    """

    # ----- B2C -----
    if commerce_mode == "B2C":
        return pricing.get_unit_price()

    # ----- B2B -----
    bulk_prices = pricing.bulk_prices.all()

    applicable_price = pricing.get_unit_price()

    for bulk in bulk_prices:
        if quantity >= bulk.min_quantity:
            applicable_price = bulk.unit_price

    return applicable_price


def get_total_price(pricing, quantity=1, commerce_mode="B2C"):
    unit_price = get_effective_price(pricing, quantity, commerce_mode)
    return unit_price * Decimal(quantity)
