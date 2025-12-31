# economic/ecommerce/views/product_detail.py
from django.shortcuts import get_object_or_404, render
from django.utils.translation import get_language
from economic.ecommerce.models import Product


def product_detail_view(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)

    # Images (si tu as ProductImage)
    images_qs = getattr(product, "images", None)
    images = images_qs.all().order_by("-is_primary", "id") if images_qs else []

    # Produits similaires (même catégorie)
    related_products = (
        Product.objects.filter(is_active=True, category=product.category)
        .exclude(pk=product.pk)
        .order_by("-is_featured", "-created_at")[:12]
    )

    # SEO (tu peux enrichir via context_processor)
    seo_title = product.safe_translation_getter("name", any_language=True) or "Produit"
    seo_description = product.safe_translation_getter("short_description", any_language=True) or ""

    context = {
        "product": product,
        "images": images,
        "related_products": related_products,
        "seo_title": seo_title,
        "seo_description": seo_description,
        "lang": get_language(),
    }
    return render(request, "economic/product_detail.html", context)
