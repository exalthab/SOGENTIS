# economic/ecommerce/views/index.py
from django.shortcuts import render
from django.db.models import Max
from parler.utils.context import switch_language

from ..models.product import Product
from ..models.category import Category


def ecommerce_index_view(request, category_slug=None):
    """
    Catalogue principal des produits
    Compatible Django-Parler (langue courante)
    """
    language = request.LANGUAGE_CODE

    products = Product.objects.filter(is_active=True).translated(language)
    categories = Category.objects.filter(is_active=True).translated(language)

    current_category = None
    if category_slug:
        current_category = Category.objects.translated(language).get(slug=category_slug)
        products = products.filter(category=current_category)

    # ✅ CORRECTION : prix maximum réel
    max_price = products.aggregate(max_price=Max("price"))["max_price"] or 0

    context = {
        "products": products,
        "categories": categories,
        "current_category": current_category,
        "max_price": max_price,  # 🔑 FIX
    }

    return render(request, "economic/ecommerce/index.html", context)








# # economic/ecommerce/views/index.py
# from django.shortcuts import render
# from parler.utils.context import switch_language

# from ..models.product import Product
# from ..models.category import Category


# def ecommerce_index_view(request, category_slug=None):
#     """
#     Catalogue principal des produits
#     Compatible Parler (langue courante)
#     """
#     language = request.LANGUAGE_CODE

#     products = Product.objects.filter(is_active=True).translated(language)
#     categories = Category.objects.filter(is_active=True).translated(language)

#     current_category = None
#     if category_slug:
#         current_category = Category.objects.translated(language).get(slug=category_slug)
#         products = products.filter(category=current_category)

#     context = {
#         "products": products,
#         "categories": categories,
#         "current_category": current_category,
#     }
#     return render(request, "economic/ecommerce/index.html", context)
