# # economic/b2b/views/dashboard.py
# from django.db.models import Sum
# from django.shortcuts import render

# from economic.decorators import b2b_admin_required
# from economic.b2b.models import BulkOrder, CompanyUser


# @b2b_admin_required
# def b2b_index_view(request):
#     company_user = request.user.company_user
#     company = company_user.company

#     users = CompanyUser.objects.select_related("user").filter(company=company)
#     orders = BulkOrder.objects.filter(company=company)

#     stats = {
#         "users_count": users.count(),
#         "orders_count": orders.count(),
#         "total_spent": orders.aggregate(total=Sum("total_amount"))["total"] or 0,
#     }

#     context = {
#         "company": company,
#         "users": users,
#         "orders": orders.order_by("-created_at")[:10],
#         "stats": stats,
#     }

#     return render(request, "economic/b2b/index.html", context)
