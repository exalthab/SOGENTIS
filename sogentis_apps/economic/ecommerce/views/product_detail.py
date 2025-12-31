# economic/ecommerce/views/product_detail.py
from django.shortcuts import render, get_object_or_404
from django.utils.translation import get_language

from ..models.product import Product


def product_detail_view(request, slug):
    """
    Page détail produit
    Slug multilingue (Parler)
    """
    language = get_language()

    product = get_object_or_404(
        Product.objects.filter(
            translations__language_code=language,
            translations__slug=slug,
            is_active=True,
        )
    )

    images = product.images.all()  # related_name="images" d'après ton erreur

    context = {
        "product": product,
        "images": images,
    }
    return render(request, "economic/ecommerce/product_detail.html", context)






# # economic/ecommerce/views/product_detail.py
# from django.shortcuts import render, get_object_or_404
# from parler.utils.context import switch_language

# from ..models.product import Product


# def product_detail_view(request, slug):
#     """
#     Page détail produit
#     Slug multilingue (Parler)
#     """
#     language = request.LANGUAGE_CODE

#     product = get_object_or_404(
#         Product.objects.translated(language),
#         slug=slug,
#         is_active=True,
#     )

#     images = product.images.all()

#     context = {
#         "product": product,
#         "images": images,
#     }
#     return render(request, "economic/ecommerce/product_detail.html", context)
