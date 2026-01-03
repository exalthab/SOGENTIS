# economic/b2b/views/bulk_orders.py
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from economic.b2b.forms import BulkOrderForm, BulkOrderItemForm
from economic.b2b.models import BulkOrder, BulkOrderItem
from economic.b2b.services import company_user_required


@login_required
@company_user_required(role="viewer")
def bulk_order_list_view(request, company_id: int):
    company = request.company
    orders = company.bulk_orders.select_related("company").prefetch_related("items").order_by("-created_at")
    return render(request, "economic/b2b/bulk_orders/bulk_order_list.html", {"company": company, "orders": orders})


@login_required
@company_user_required(role="staff")
def bulk_order_create_view(request, company_id: int):
    company = request.company
    if request.method == "POST":
        form = BulkOrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.company = company
            order.status = BulkOrder.Status.DRAFT
            order.save()
            messages.success(request, "Commande en gros créée (brouillon).")
            return redirect("economic:b2b:bulk_order_detail", company_id=company.id, order_id=order.id)
    else:
        form = BulkOrderForm()
    return render(request, "economic/b2b/bulk_orders/bulk_order_form.html", {"company": company, "form": form})


@login_required
@company_user_required(role="viewer")
def bulk_order_detail_view(request, company_id: int, order_id: int):
    company = request.company
    order = get_object_or_404(BulkOrder, pk=order_id, company=company)
    items = order.items.select_related("product").order_by("id")
    can_edit = order.status == BulkOrder.Status.DRAFT and request.company_user.role in (
        "admin", "staff"
    )

    return render(
        request,
        "economic/b2b/bulk_orders/bulk_order_detail.html",
        {"company": company, "order": order, "items": items, "can_edit": can_edit},
    )


@login_required
@company_user_required(role="staff")
def bulk_order_add_item_view(request, company_id: int, order_id: int):
    company = request.company
    order = get_object_or_404(BulkOrder, pk=order_id, company=company)

    if order.status != BulkOrder.Status.DRAFT:
        raise Http404("Commande non modifiable.")

    if request.method == "POST":
        form = BulkOrderItemForm(request.POST)
        if form.is_valid():
            item: BulkOrderItem = form.save(commit=False)
            item.bulk_order = order
            item.save()
            messages.success(request, "Produit ajouté.")
            return redirect("economic:b2b:bulk_order_detail", company_id=company.id, order_id=order.id)
    else:
        form = BulkOrderItemForm()

    return render(
        request,
        "economic/b2b/bulk_orders/bulk_order_item_form.html",
        {"company": company, "order": order, "form": form},
    )


@login_required
@company_user_required(role="staff")
def bulk_order_submit_view(request, company_id: int, order_id: int):
    company = request.company
    order = get_object_or_404(BulkOrder, pk=order_id, company=company)

    if order.status != BulkOrder.Status.DRAFT:
        messages.info(request, "Commande déjà soumise.")
        return redirect("economic:b2b:bulk_order_detail", company_id=company.id, order_id=order.id)

    if not order.items.exists():
        messages.error(request, "Ajoute au moins un produit avant de soumettre.")
        return redirect("economic:b2b:bulk_order_detail", company_id=company.id, order_id=order.id)

    order.recalc_total(save=True)
    order.status = BulkOrder.Status.SUBMITTED
    order.save(update_fields=["status", "updated_at"])

    messages.success(request, "Commande soumise.")
    return redirect("economic:b2b:bulk_order_detail", company_id=company.id, order_id=order.id)




# # economic/b2b/views/bulk_orders.py
# from django.shortcuts import render
# from django.core.paginator import Paginator
# from django.utils.translation import gettext_lazy as _

# from economic.decorators import b2b_required
# from economic.b2b.models import BulkOrder


# @b2b_required
# def bulk_orders_view(request):
#     """
#     Liste des commandes en gros pour l'entreprise du user connecté
#     """
#     company = request.user.company_user.company

#     qs = BulkOrder.objects.filter(company=company).order_by("-created_at")
#     paginator = Paginator(qs, 20)
#     page_obj = paginator.get_page(request.GET.get("page"))

#     context = {
#         "page_title": _("Commandes en gros"),
#         "page_obj": page_obj,
#     }
#     return render(request, "economic/b2b/bulk_orders/list.html", context)




# # economic/b2b/views/bulk_orders.py
# from django.shortcuts import render
# from django.contrib.auth.decorators import login_required

# @login_required
# def bulk_orders_view(request):
#     """
#     Page de gestion des commandes en gros
#     """
#     # Example context, replace with your real query logic
#     context = {
#         "orders": []  # Replace with your actual bulk orders queryset
#     }
#     return render(request, "b2b/bulk_orders.html", context)
