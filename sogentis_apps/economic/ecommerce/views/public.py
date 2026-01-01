# economic/ecommerce/views/public.py

from django.shortcuts import render


def ecommerce_public_view(request):
    """
    Landing / vitrine du pôle e-commerce.
    Template : economic/ecommerce/public.html (si tu l'utilises)
    """
    return render(request, "economic/ecommerce/public.html")





# # views/public.py
# from django.shortcuts import render
# from django.core.paginator import Paginator
# from ..models.product import Product


# def product_list_view(request):
#     products_qs = Product.objects.filter(is_active=True)

#     # Pagination
#     paginator = Paginator(products_qs, 12)  # 12 products per page
#     page_number = request.GET.get("page")
#     products = paginator.get_page(page_number)

#     context = {
#         "products": products,
#     }

#     return render(
#         request,
#         "economic/ecommerce/product_list.html",
#         context
#     )
