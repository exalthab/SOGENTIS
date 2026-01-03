# economic/b2b/views/home.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from economic.b2b.models import Company


@login_required
def b2b_home_view(request):
    """
    Hub B2B : liste des entreprises accessibles (owner ou membership).
    Template: economic/b2b/b2b_home.html
    """
    companies = (
        Company.objects.filter(owner=request.user)
        | Company.objects.filter(users__user=request.user, users__is_active=True)
    ).distinct().order_by("name")

    return render(request, "economic/b2b/b2b_home.html", {"companies": companies})





# # economic/b2b/views/index.py
# from django.shortcuts import render
# from django.db.models import Sum
# from economic.decorators import b2b_admin_required
# from economic.b2b.models import CompanyUser, BulkOrder


# @b2b_admin_required
# def b2b_index_view(request):
#     company_user = request.user.company_user
#     company = company_user.company

#     users = CompanyUser.objects.filter(company=company)
#     orders = BulkOrder.objects.filter(company=company)

#     stats = {
#         "users_count": users.count(),
#         "orders_count": orders.count(),
#         "total_spent": orders.aggregate(
#             total=Sum("total_amount")
#         )["total"] or 0,
#     }

#     context = {
#         "company": company,
#         "users": users,
#         "orders": orders[:10],
#         "stats": stats,
#     }

#     return render(
#         request,
#         "b2b/index.html",
#         context,
#     )
