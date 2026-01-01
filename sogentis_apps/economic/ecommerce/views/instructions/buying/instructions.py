# economic/ecommerce/views/instructions/buying/instructions.py

from django.shortcuts import render


def buying_instructions_view(request):
    """
    Mode d’emploi pour acheter.
    Template : economic/ecommerce/instructions/buying/instructions.html
    """
    return render(
        request,
        "economic/ecommerce/instructions/buying/instructions.html",
    )





# # views/instructions.py
# from django.shortcuts import render


# def buying_instructions_view(request):
#     context = {}

#     return render(
#         request,
#         "economic/ecommerce/instructions/buying.html",
#         context,
#     )
