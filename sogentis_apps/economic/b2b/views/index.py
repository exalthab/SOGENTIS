# economic/b2b/views/dashboard.py
from django.shortcuts import render
from django.db.models import Sum
from economic.decorators import b2b_admin_required
from economic.b2b.models import CompanyUser, BulkOrder


@b2b_admin_required
def b2b_index_view(request):
    company_user = request.user.company_user
    company = company_user.company

    users = CompanyUser.objects.filter(company=company)
    orders = BulkOrder.objects.filter(company=company)

    stats = {
        "users_count": users.count(),
        "orders_count": orders.count(),
        "total_spent": orders.aggregate(
            total=Sum("total_amount")
        )["total"] or 0,
    }

    context = {
        "company": company,
        "users": users,
        "orders": orders[:10],
        "stats": stats,
    }

    return render(
        request,
        "b2b/index.html",
        context,
    )
