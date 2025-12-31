# economic/ecommerce/permissions.py
def can_review_product(user, product):
    """
    Règles :
    - utilisateur connecté
    - produit actif
    - un seul avis par produit
    """
    if not user.is_authenticated:
        return False

    if not product.is_active:
        return False

    return not product.reviews.filter(user=user).exists()
