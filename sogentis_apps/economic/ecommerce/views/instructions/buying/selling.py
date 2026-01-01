# economic/ecommerce/views/instructions/buying/selling.py

from django.shortcuts import render


def selling_instructions_view(request):
    """
    Mode d’emploi pour vendre.
    Template : economic/ecommerce/instructions/buying/selling.html
    """
    return render(
        request,
        "economic/ecommerce/instructions/buying/selling.html",
    )






# # economic/ecommerce/instructions/selling/selling.py
# from django.shortcuts import render


# def selling_instructions_view(request):
#     context = {}

#     return render(
#         request,
#         "economic/ecommerce/instructions/selling.html",
#         context,
#     )
