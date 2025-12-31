# economic/ecommerce/services/stock_service.py
def is_in_stock(product, quantity=1):
    return product.stock >= quantity
