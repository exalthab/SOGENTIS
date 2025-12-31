# dashboard/views/b2b/invoices.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from economic.b2b.models import Invoice

@login_required
def b2b_invoices(request):
    invoices = Invoice.objects.filter(company=request.user.company_user.company)
    return render(request, "dashboard/b2b/invoices.html", {"invoices": invoices})
