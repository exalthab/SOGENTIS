# views/instructions.py
from django.shortcuts import render


def buying_instructions_view(request):
    context = {}

    return render(
        request,
        "economic/ecommerce/instructions/buying.html",
        context,
    )
