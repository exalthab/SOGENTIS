# economic/ecommerce/views/review.py
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from ..models.product import Product
# from ..models.review import ProductReview
# from ..forms import ProductReviewForm


@login_required
@require_POST
def add_review_view(request, product_id):
    """
    URL:
      path("reviews/add/<int:product_id>/", add_review_view, name="add_review")
    """
    product = get_object_or_404(Product, pk=product_id, is_active=True)

    # TODO: brancher ProductReviewForm + ProductReview ici
    messages.success(request, _("Avis reçu (à implémenter côté modèle/formulaire)."))

    return redirect(reverse("economic:ecommerce:product_detail", kwargs={"slug": product.slug}))





# # economic/ecommerce/views/review.py
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import get_object_or_404, redirect
# from django.contrib import messages

# from ..models.product import Product
# from ..services.review_service import create_review
# from ..permissions import can_review_product


# @login_required
# def add_review_view(request, product_id):
#     product = get_object_or_404(Product, id=product_id)

#     if not can_review_product(request.user, product):
#         messages.error(request, "Vous ne pouvez pas évaluer ce produit.")
#         return redirect("ecommerce:product_detail", slug=product.slug)

#     if request.method == "POST":
#         rating = request.POST.get("rating")
#         title = request.POST.get("title")
#         content = request.POST.get("content")

#         create_review(request.user, product, rating, title, content)
#         messages.success(request, "Merci pour votre avis. Il sera publié après validation.")

#     return redirect("ecommerce:product_detail", slug=product.slug)
