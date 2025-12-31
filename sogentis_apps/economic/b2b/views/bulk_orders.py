# economic/b2b/views/bulk_orders.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def bulk_orders_view(request):
    """
    Page de gestion des commandes en gros
    """
    # Example context, replace with your real query logic
    context = {
        "orders": []  # Replace with your actual bulk orders queryset
    }
    return render(request, "b2b/bulk_orders.html", context)
