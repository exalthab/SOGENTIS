# economic/b2b/views/rfqs.py
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from economic.b2b.forms import RFQForm
from economic.b2b.models import RFQ
from economic.b2b.services import company_user_required


@login_required
@company_user_required(role="viewer")
def rfq_list_view(request, company_id: int):
    company = request.company
    rfqs = company.rfqs.select_related("company", "created_by").order_by("-created_at")
    return render(request, "economic/b2b/rfqs/rfq_list.html", {"company": company, "rfqs": rfqs})


@login_required
@company_user_required(role="staff")
def rfq_create_view(request, company_id: int):
    company = request.company

    if request.method == "POST":
        form = RFQForm(request.POST)
        if form.is_valid():
            rfq = form.save(commit=False)
            rfq.company = company
            rfq.created_by = request.user
            rfq.save()
            messages.success(request, "RFQ créée.")
            return redirect("economic:b2b:rfq_list", company_id=company.id)
    else:
        form = RFQForm()

    return render(request, "economic/b2b/rfqs/rfq_form.html", {"company": company, "form": form})
