# economic/ecommerce/views/product_detail.py
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, render
from django.utils.translation import get_language

from ..models.product import Product
from ..models.favorite import Favorite


def product_detail_view(request, slug):
    """
    URL:
      path("products/<slug:slug>/", product_detail_view, name="product_detail")

    - slug est dans Product.translations.slug (Parler)
    - on filtre explicitement translations__slug pour être 100% fiable en prod
    """
    language = request.LANGUAGE_CODE or get_language() or "fr"

    product = get_object_or_404(
        Product.objects.filter(is_active=True).translated(language),
        translations__slug=slug,
    )

    images_qs = product.images.all()
    main_image = images_qs.filter(is_main=True).first() or images_qs.first()

    related_products = Product.objects.none()
    if product.category_id:
        related_products = (
            Product.objects.filter(is_active=True, category_id=product.category_id)
            .exclude(pk=product.pk)
            .translated(language)
            .order_by("-is_featured", "-created_at")[:8]
        )

    # ✅ Favoris (état)
    is_favorited = False
    if request.user.is_authenticated:
        is_favorited = Favorite.objects.filter(user=request.user, product=product).exists()

    context = {
        "product": product,
        "product_images": images_qs,
        "main_image": main_image,
        "related_products": related_products,
        "is_favorited": is_favorited,
    }
    return render(request, "economic/ecommerce/articles/product_detail.html", context)





# # economic/ecommerce/views/product_detail.py

# from django.shortcuts import get_object_or_404, render
# from django.utils.translation import get_language

# from ..models.product import Product


# def product_detail_view(request, slug):
#     """
#     URL:
#       path("products/<slug:slug>/", product_detail_view, name="product_detail")

#     - slug est dans Product.translations.slug (Parler)
#     - On filtre explicitement translations__slug pour être 100% fiable en prod
#     """
#     language = request.LANGUAGE_CODE or get_language() or "fr"

#     # ✅ Produit (slug traduit)
#     product = get_object_or_404(
#         Product.objects.filter(is_active=True).translated(language),
#         translations__slug=slug,
#     )

#     # ✅ Images (ProductImage related_name="images", ordering: -is_main, id)
#     images_qs = product.images.all()
#     main_image = images_qs.filter(is_main=True).first() or images_qs.first()

#     # ✅ Produits similaires (même catégorie)
#     related_products = Product.objects.none()
#     if product.category_id:
#         related_products = (
#             Product.objects.filter(is_active=True, category_id=product.category_id)
#             .exclude(pk=product.pk)
#             .translated(language)
#             .order_by("-is_featured", "-created_at")[:8]
#         )

#     context = {
#         "product": product,
#         "product_images": images_qs,
#         "main_image": main_image,
#         "related_products": related_products,
#     }

#     # ✅ IMPORTANT : ton template final est ici (pas /articles/)
#     return render(request, "economic/ecommerce/articles/product_detail.html", context)







# # economic/ecommerce/views/product_detail.py

# from django.shortcuts import get_object_or_404, render
# from django.utils.translation import get_language

# from ..models.product import Product


# def product_detail_view(request, slug):
#     """
#     URL:
#       path("products/<slug:slug>/", product_detail_view, name="product_detail")

#     - slug est dans Product.translations.slug (Django-Parler)
#     - on filtre explicitement translations__slug pour éviter les cas où Parler ne mappe pas le champ directement
#     """
#     language = request.LANGUAGE_CODE or get_language() or "fr"

#     # ⚠️ slug = champ de traduction -> translations__slug
#     product = get_object_or_404(
#         Product.objects.filter(is_active=True).translated(language),
#         translations__slug=slug,
#     )

#     # Images (ProductImage related_name="images")
#     images_qs = product.images.all()  # ordering déjà défini dans le model
#     main_image = images_qs.filter(is_main=True).first() or images_qs.first()

#     # Produits similaires (même catégorie)
#     related_products = []
#     if product.category_id:
#         related_products = (
#             Product.objects.filter(is_active=True, category_id=product.category_id)
#             .exclude(pk=product.pk)
#             .translated(language)
#             .order_by("-is_featured", "-created_at")[:8]
#         )

#     context = {
#         "product": product,
#         "product_images": images_qs,
#         "main_image": main_image,
#         "related_products": related_products,
#     }
#     return render(request, "economic/ecommerce/articles/product_detail.html", context)




# # economic/ecommerce/views/product_detail.py
# from django.shortcuts import render, get_object_or_404
# from django.utils.translation import get_language

# from ..models.product import Product


# def product_detail_view(request, slug):
#     """
#     Page détail produit
#     Slug multilingue (Parler)
#     """
#     language = get_language()

#     product = get_object_or_404(
#         Product.objects.filter(
#             translations__language_code=language,
#             translations__slug=slug,
#             is_active=True,
#         )
#     )

#     images = product.images.all()  # related_name="images" d'après ton erreur

#     context = {
#         "product": product,
#         "images": images,
#     }
#     return render(request, "economic/ecommerce/product_detail.html", context)






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
