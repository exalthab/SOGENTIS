# economic/ecommerce/views/favorites_list.py
from __future__ import annotations

from dataclasses import dataclass

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import get_language

from ..models.favorite import Favorite
from ..models.product import Product


@dataclass(frozen=True)
class FavoriteRow:
    """
    View-model: évite la logique Parler fragile dans le template.
    """
    favorite: Favorite
    product: Product
    product_url: str


def _normalize_lang(code: str) -> str:
    """
    Normalise une locale type "fr-sn" -> "fr" pour Parler.
    """
    c = (code or "").strip().lower()
    if not c:
        return ""
    return c.split("-")[0].split("_")[0]


@login_required
def favorites_list_view(request):
    """
    Liste des favoris de l'utilisateur connecté.

    Fix principal:
    - Avec Parler, p.slug peut être vide si la traduction courante n'est pas "chargée".
    - On calcule donc l'URL produit côté Python via safe_translation_getter(any_language=True),
      puis on la passe au template => "Voir" ne sera plus désactivé.
    """
    favorites_qs = (
        Favorite.objects
        .filter(user=request.user)
        .select_related("product", "product__category", "product__vendor")
        .prefetch_related("product__images")
        .order_by("-created_at")
    )

    favorites = list(favorites_qs)  # ✅ évaluation stable
    rows: list[FavoriteRow] = []

    cur_lang = _normalize_lang(get_language() or "")

    for fav in favorites:
        p = getattr(fav, "product", None)
        if not p:
            continue

        slug = ""

        # 1) slug langue courante (si dispo)
        if cur_lang:
            try:
                slug = p.safe_translation_getter("slug", language_code=cur_lang) or ""
            except Exception:
                slug = ""

        # 2) fallback: n'importe quelle langue
        if not slug:
            try:
                slug = p.safe_translation_getter("slug", any_language=True) or ""
            except Exception:
                slug = ""

        if slug:
            product_url = reverse("economic:ecommerce:product_detail", args=[slug])
        else:
            product_url = reverse("economic:ecommerce:index")

        rows.append(FavoriteRow(favorite=fav, product=p, product_url=product_url))

    return render(
        request,
        "economic/ecommerce/favorites/favorites_list.html",
        {
            "favorites": favorites,
            "favorite_rows": rows,
        },
    )







# # economic/ecommerce/views/favorites_list.py
# from __future__ import annotations

# from dataclasses import dataclass

# from django.contrib.auth.decorators import login_required
# from django.urls import reverse
# from django.shortcuts import render
# from django.utils.translation import get_language

# from ..models.favorite import Favorite


# @dataclass(frozen=True)
# class FavoriteRow:
#     """
#     View-model: évite la logique Parler fragile dans le template.
#     """
#     favorite: Favorite
#     product: object
#     product_url: str


# @login_required
# def favorites_list_view(request):
#     """
#     Liste des favoris de l'utilisateur connecté.

#     Fix principal:
#     - Avec Parler, p.slug peut être vide si la traduction courante n'est pas "chargée".
#     - On calcule donc l'URL produit côté Python via safe_translation_getter(any_language=True),
#       puis on la passe au template => "Voir" ne sera plus désactivé.
#     """
#     qs = (
#         Favorite.objects
#         .filter(user=request.user)
#         .select_related("product", "product__category", "product__vendor")
#         .prefetch_related("product__images")
#         .order_by("-created_at")
#     )

#     rows: list[FavoriteRow] = []
#     cur_lang = (get_language() or "").lower()

#     for fav in qs:
#         p = getattr(fav, "product", None)
#         if not p:
#             continue

#         # 1) slug langue courante (si dispo)
#         slug = ""
#         try:
#             slug = p.safe_translation_getter("slug", language_code=cur_lang) or ""
#         except Exception:
#             slug = ""

#         # 2) fallback: n'importe quelle langue
#         if not slug:
#             try:
#                 slug = p.safe_translation_getter("slug", any_language=True) or ""
#             except Exception:
#                 slug = ""

#         if slug:
#             product_url = reverse("economic:ecommerce:product_detail", args=[slug])
#         else:
#             # fallback boutique (ou "#")
#             product_url = reverse("economic:ecommerce:index")

#         rows.append(FavoriteRow(favorite=fav, product=p, product_url=product_url))

#     return render(
#         request,
#         "economic/ecommerce/favorites/favorites_list.html",
#         {"favorites": qs, "favorite_rows": rows},
#     )





# # economic/ecommerce/views/favorites_list.py
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render

# from ..models.favorite import Favorite


# @login_required
# def favorites_list_view(request):
#     favorites = (
#         Favorite.objects
#         .filter(user=request.user)
#         .select_related("product", "product__category", "product__vendor")
#         .prefetch_related("product__images")
#         .order_by("-created_at")
#     )

#     return render(
#         request,
#         "economic/ecommerce/favorites/favorites_list.html",
#         {"favorites": favorites},
#     )
