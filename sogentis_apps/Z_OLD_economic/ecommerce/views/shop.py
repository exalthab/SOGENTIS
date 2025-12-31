# economic/ecommerce/views/shop.py

from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q, F
from django.utils.translation import gettext_lazy as _
from economic.ecommerce.models.product import Product, Category


# ============================================================
#  SHOP INDEX — PAGE BOUTIQUE PRINCIPALE (type JUMIA)
# ============================================================

def shop_view(request):

    # ===========================================
    # 1️⃣ RÉCUPÉRATION DES FILTRES
    # ===========================================
    category_slug = request.GET.get("category")
    search = request.GET.get("search")
    sort = request.GET.get("sort")
    promo_only = request.GET.get("promo")
    new_only = request.GET.get("new")
    min_price = request.GET.get("min")
    max_price = request.GET.get("max")

    products = Product.objects.filter(is_active=True)

    # ===========================================
    # 2️⃣ FILTRE PAR CATÉGORIE
    # ===========================================
    category = None
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    # ===========================================
    # 3️⃣ RECHERCHE PRODUITS
    # ===========================================
    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search) |
            Q(fiche_technique__icontains=search)
        )

    # ===========================================
    # 4️⃣ FILTRE PAR PROMOTION
    # ===========================================
    if promo_only:
        products = products.filter(promo_percent__gt=0)

    # ===========================================
    # 5️⃣ FILTRE PRODUITS NOUVEAUX
    # ===========================================
    if new_only:
        products = products.filter(is_new=True)

    # ===========================================
    # 6️⃣ FILTRE PAR PRIX MIN/MAX
    # ===========================================
    if min_price:
        products = products.filter(price__gte=min_price)

    if max_price:
        products = products.filter(price__lte=max_price)

    # ===========================================
    # 7️⃣ TRI AVANCÉ
    # ===========================================
    if sort == "price_asc":
        products = products.order_by("price")
    elif sort == "price_desc":
        products = products.order_by("-price")
    elif sort == "newest":
        products = products.order_by("-created_at")
    elif sort == "rating":
        products = products.order_by("-rating")
    elif sort == "sold":
        products = products.order_by("-sold_count")
    else:
        products = products.order_by("-created_at")  # tri par défaut

    # ===========================================
    # 8️⃣ PRODUITS VEDETTES (carrousel)
    # ===========================================
    featured_products = Product.objects.filter(
        is_featured=True, is_active=True
    ).order_by("-created_at")[:8]

    # ===========================================
    # 9️⃣ PAGINATION
    # ===========================================
    paginator = Paginator(products, 12)  # 12 produits par page
    page_number = request.GET.get("page")
    products_page = paginator.get_page(page_number)

    # ===========================================
    # 🔟 CONTEXTE FINAL
    # ===========================================
    context = {
        "products": products_page,
        "featured_products": featured_products,
        "categories": Category.objects.all(),

        # valeurs utiles pour front
        "active_category": category,
        "search": search or "",
        "sort": sort or "",
        "promo_only": promo_only,
        "new_only": new_only,
        "min_price": min_price or "",
        "max_price": max_price or "",
    }

    return render(request, "economic/shop/shop.html", context)
