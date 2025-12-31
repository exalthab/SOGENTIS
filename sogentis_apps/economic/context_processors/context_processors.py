# economic/context_processors/context_processors.py
"""
Context processors globaux pour le pôle économique
"""

from django.conf import settings
from django.db.utils import OperationalError, ProgrammingError


ALLOWED_COMMERCE_MODES = {"B2C", "B2B"}
DEFAULT_COMMERCE_MODE = "B2C"


def economic_context(request):
    """
    Variables globales pour tout le pôle économique
    """

    # ==========================
    # Mode commerce (B2C par défaut)
    # ==========================
    commerce_mode = request.session.get("commerce_mode", DEFAULT_COMMERCE_MODE)
    if commerce_mode not in ALLOWED_COMMERCE_MODES:
        commerce_mode = DEFAULT_COMMERCE_MODE

    # ==========================
    # Devise e-commerce (fallback sécurisé)
    # ==========================
    ecommerce_currency = getattr(settings, "ECOMMERCE_CURRENCY", "EUR")

    # ==========================
    # Panier (compteur)
    # ==========================
    cart_items_count = 0

    if request.user.is_authenticated:
        try:
            # Import local pour éviter circular import / migrations issues
            from economic.ecommerce.models.cart import Cart
        except ImportError:
            Cart = None

        if Cart is not None:
            try:
                cart = Cart.objects.get(user=request.user)
                cart_items_count = cart.items.count()
            except (Cart.DoesNotExist, OperationalError, ProgrammingError):
                cart_items_count = 0

    return {
        "ECONOMIC_ENABLED": True,
        "commerce_mode": commerce_mode,
        "cart_items_count": cart_items_count,
        "ECOMMERCE_CURRENCY": ecommerce_currency,
    }











# # economic/context_processors/context_processors.py
# """
# Context processors globaux pour le pôle économique
# """

# from django.conf import settings
# from economic.ecommerce.models.cart import Cart


# def economic_context(request):
#     """
#     Variables globales pour tout le pôle économique
#     """
#     cart_items_count = 0

#     # Mode commerce (B2C par défaut)
#     commerce_mode = request.session.get("commerce_mode", "B2C")

#     # Devise e-commerce (fallback sécurisé)
#     ecommerce_currency = getattr(settings, "ECOMMERCE_CURRENCY", "EUR")

#     if request.user.is_authenticated:
#         try:
#             cart = Cart.objects.prefetch_related("items").get(user=request.user)
#             cart_items_count = cart.items.count()
#         except Cart.DoesNotExist:
#             cart_items_count = 0

#     return {
#         # ==========================
#         # GLOBAL
#         # ==========================
#         "ECONOMIC_ENABLED": True,

#         # ==========================
#         # E-COMMERCE
#         # ==========================
#         "commerce_mode": commerce_mode,
#         "cart_items_count": cart_items_count,
#         "ECOMMERCE_CURRENCY": ecommerce_currency,
#     }











# # economic/context_processors/context_processors.py
# """
# Context processors globaux pour le pôle économique
# """

# from economic.ecommerce.models.cart import Cart


# def economic_context(request):
#     """
#     Variables globales pour tout le pôle économique
#     """
#     cart_items_count = 0
#     commerce_mode = request.session.get("commerce_mode", "B2C")

#     if request.user.is_authenticated:
#         try:
#             cart = Cart.objects.get(user=request.user)
#             cart_items_count = cart.items.count()
#         except Cart.DoesNotExist:
#             pass

#     return {
#         # Global
#         "ECONOMIC_ENABLED": True,

#         # E-commerce
#         "commerce_mode": commerce_mode,
#         "cart_items_count": cart_items_count,
#     }





# # economic/context_processors/context_processors.py
# """
# Context processors globaux pour le pôle économique
# """

# def economic_context(request):
#     return {
#         "ECONOMIC_ENABLED": True,
#     }
