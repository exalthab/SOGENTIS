# economic/ecommerce/instructions/selling/selling.py
from django.shortcuts import render


def selling_instructions_view(request):
    context = {}

    return render(
        request,
        "economic/ecommerce/instructions/selling.html",
        context,
    )
