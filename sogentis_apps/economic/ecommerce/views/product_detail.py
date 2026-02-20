# economic/ecommerce/views/product_detail.py
from __future__ import annotations

from decimal import Decimal, InvalidOperation

from django.shortcuts import get_object_or_404, render
from django.utils.translation import get_language

from ..models.favorite import Favorite
from ..models.product import Product


def _safe_discount_percent(base_price, current_price) -> int:
    try:
        bp = Decimal(str(base_price))
        cp = Decimal(str(current_price))
        if bp <= 0 or cp >= bp:
            return 0
        pct = (bp - cp) / bp * Decimal("100")
        return max(0, min(int(pct.quantize(Decimal("1"))), 95))
    except (InvalidOperation, TypeError, ValueError):
        return 0


def product_detail_view(request, slug: str):
    """
    Détail produit – PROD SAFE (Parler)

    - slug = Product.translations.slug
    - Pricing prioritaire si présent/actif
    - fallback sur Product.price / old_price
    """

    language = getattr(request, "LANGUAGE_CODE", None) or get_language() or "fr"

    qs = (
        Product.objects.filter(is_active=True)
        .select_related("vendor", "category")
        .prefetch_related("images")
    )

    # pricing est optionnel (selon ton projet)
    try:
        qs = qs.select_related("pricing")
    except Exception:
        pass

    # ✅ filtre parler safe
    product = get_object_or_404(qs.translated(language, slug=slug))

    images_qs = product.images.all()
    main_image = images_qs.filter(is_main=True).first() or images_qs.order_by("sort_order", "id").first()

    # ✅ related produits (même langue) + images
    related_products = Product.objects.none()
    if product.category_id:
        related_qs = (
            Product.objects.filter(is_active=True, category_id=product.category_id)
            .exclude(pk=product.pk)
            .select_related("vendor", "category")
            .prefetch_related("images")
        )
        try:
            related_qs = related_qs.select_related("pricing")
        except Exception:
            pass

        related_products = (
            related_qs.translated(language)
            .order_by("-is_featured", "-created_at")[:8]
        )

    # Favoris
    is_favorited = False
    if request.user.is_authenticated:
        is_favorited = Favorite.objects.filter(user=request.user, product=product).exists()

    # =====================================================
    # PRIX NORMALISÉS (UNE SEULE SOURCE)
    # =====================================================
    pricing = getattr(product, "pricing", None)

    if pricing and getattr(pricing, "is_active", False):
        current_price = getattr(pricing, "effective_unit_price", None) or product.price
        base_price = getattr(pricing, "base_price", None) or product.old_price or product.price
        has_promo = False
        try:
            has_promo = bool(pricing.has_promo())
        except Exception:
            has_promo = bool(base_price and current_price and base_price > current_price)

        discount_percent = _safe_discount_percent(base_price, current_price) if has_promo else 0
    else:
        current_price = product.price
        base_price = product.old_price or product.price
        has_promo = bool(product.old_price and product.old_price > product.price)
        discount_percent = int(getattr(product, "discount_percent", 0) or 0) if has_promo else 0

    context = {
        "product": product,
        "product_images": images_qs,
        "main_image": main_image,
        "related_products": related_products,
        "is_favorited": is_favorited,
        # ✅ prix normalisés pour template
        "current_price": current_price,
        "base_price": base_price,
        "has_promo": has_promo,
        "discount_percent": discount_percent,
        # ✅ mode (si tu l’utilises dans le template)
        "commerce_mode": request.session.get("ECOMMERCE_MODE", "B2C"),
        # shipping_cost optional (si template l’affiche)
        "shipping_cost": None,
    }

    return render(request, "economic/ecommerce/articles/product_detail.html", context)









# # economic/ecommerce/views/product_detail.py
# from django.shortcuts import get_object_or_404, render
# from django.utils.translation import get_language

# from ..models.product import Product
# from ..models.favorite import Favorite


# def product_detail_view(request, slug):
#     """
#     Détail produit – PROD SAFE

#     - slug = Product.translations.slug (Parler)
#     - ProductPricing est prioritaire
#     - fallback sur Product.price / old_price si pricing absent
#     """

#     language = request.LANGUAGE_CODE or get_language() or "fr"

#     product = get_object_or_404(
#         Product.objects.filter(is_active=True)
#         .select_related("pricing", "vendor", "category")
#         .translated(language),
#         translations__slug=slug,
#     )

#     images_qs = product.images.all()
#     main_image = images_qs.filter(is_main=True).first() or images_qs.first()

#     related_products = Product.objects.none()
#     if product.category_id:
#         related_products = (
#             Product.objects.filter(
#                 is_active=True,
#                 category_id=product.category_id,
#             )
#             .exclude(pk=product.pk)
#             .select_related("pricing")
#             .translated(language)
#             .order_by("-is_featured", "-created_at")[:8]
#         )

#     # Favoris
#     is_favorited = False
#     if request.user.is_authenticated:
#         is_favorited = Favorite.objects.filter(
#             user=request.user,
#             product=product,
#         ).exists()

#     # =====================================================
#     # 🔑 RÉSOLUTION PRIX (UNE SEULE FOIS – SOURCE UNIQUE)
#     # =====================================================
#     pricing = getattr(product, "pricing", None)

#     if pricing and pricing.is_active:
#         current_price = pricing.effective_unit_price
#         base_price = pricing.base_price
#         has_promo = pricing.has_promo()
#         if has_promo and base_price:
#             discount_percent = int(
#                 ((base_price - current_price) / base_price) * 100
#             )
#         else:
#             discount_percent = 0
#     else:
#         # Fallback legacy Product
#         current_price = product.price
#         base_price = product.old_price or product.price
#         has_promo = bool(
#             product.old_price and product.old_price > product.price
#         )
#         discount_percent = product.discount_percent if has_promo else 0

#     context = {
#         "product": product,
#         "product_images": images_qs,
#         "main_image": main_image,
#         "related_products": related_products,
#         "is_favorited": is_favorited,
#         # ✅ PRIX NORMALISÉS POUR LE TEMPLATE
#         "current_price": current_price,
#         "base_price": base_price,
#         "has_promo": has_promo,
#         "discount_percent": discount_percent,
#     }

#     return render(
#         request,
#         "economic/ecommerce/articles/product_detail.html",
#         context,
#     )






# # economic/ecommerce/views/product_detail.py
# from django.contrib.auth import get_user_model
# from django.shortcuts import get_object_or_404, render
# from django.utils.translation import get_language

# from ..models.product import Product
# from ..models.favorite import Favorite


# def product_detail_view(request, slug):
#     """
#     URL:
#       path("products/<slug:slug>/", product_detail_view, name="product_detail")

#     - slug est dans Product.translations.slug (Parler)
#     - on filtre explicitement translations__slug pour être 100% fiable en prod
#     """
#     language = request.LANGUAGE_CODE or get_language() or "fr"

#     product = get_object_or_404(
#         Product.objects.filter(is_active=True).translated(language),
#         translations__slug=slug,
#     )

#     images_qs = product.images.all()
#     main_image = images_qs.filter(is_main=True).first() or images_qs.first()

#     related_products = Product.objects.none()
#     if product.category_id:
#         related_products = (
#             Product.objects.filter(is_active=True, category_id=product.category_id)
#             .exclude(pk=product.pk)
#             .translated(language)
#             .order_by("-is_featured", "-created_at")[:8]
#         )

#     # ✅ Favoris (état)
#     is_favorited = False
#     if request.user.is_authenticated:
#         is_favorited = Favorite.objects.filter(user=request.user, product=product).exists()

#     context = {
#         "product": product,
#         "product_images": images_qs,
#         "main_image": main_image,
#         "related_products": related_products,
#         "is_favorited": is_favorited,
#     }
#     return render(request, "economic/ecommerce/articles/product_detail.html", context)





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
