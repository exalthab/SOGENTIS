# dashboard/views/b2b/home.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from dashboard.views.utils import StatCard, breadcrumb


@login_required
def b2b_dashboard_home_view(request):
    cards = []
    recent_orders = []

    try:
        from economic.b2b.models.bulk_order import BulkOrder
        recent_orders = BulkOrder.objects.filter(user=request.user).order_by("-created_at")[:8]
        cards.append(StatCard(label=_("Commandes B2B"), value=BulkOrder.objects.filter(user=request.user).count(), icon="🏢"))
    except Exception:
        recent_orders = []

    return render(request, "dashboard/b2b/index.html", {
        "breadcrumbs": breadcrumb((_('Dashboard'), "/dashboard/"), (_("B2B"), None)),
        "cards": [c.__dict__ for c in cards],
        "recent_orders": recent_orders,
    })



# # dashboard/views/b2b/home.py

# from django.contrib.auth.decorators import login_required, user_passes_test
# from django.shortcuts import render
# from django.utils.translation import gettext_lazy as _

# from dashboard.permissions import is_b2b_user
# from dashboard.services.b2b_dashboard_service import get_b2b_dashboard_data


# @login_required
# @user_passes_test(is_b2b_user)
# def b2b_dashboard_home_view(request):
#     company_user = request.user.company_user
#     company = company_user.company

#     context = {
#         "page_title": _("Espace B2B"),
#         # "section_menu": "core/partials/_menu_dashboard.html",
#         "dashboard_menu": "dashboard/b2b/_menu.html",

#         "company": company,
#         **get_b2b_dashboard_data(company),
#     }

#     return render(request, "dashboard/b2b/home.html", context)





# # dashboard/views/b2b/home.py
# from django.shortcuts import render
# from django.contrib.auth.decorators import login_required

# from dashboard.permissions import is_b2b_user
# from dashboard.services.b2b_dashboard_service import get_b2b_dashboard_data


# @login_required
# def b2b_dashboard_home_view(request):
#     """
#     Dashboard principal B2B
#     Affiche les indicateurs clés de l'entreprise
#     """
#     if not is_b2b_user(request.user):
#         return render(request, "dashboard/errors/not_authorized.html", status=403)

#     company_user = request.user.company_user
#     company = company_user.company

#     context = get_b2b_dashboard_data(company)
#     context.update({
#         "company": company,
#     })

#     return render(request, "dashboard/b2b/home.html", context)





# # dashboard/views/b2b/home.py
# from django.shortcuts import render
# from django.contrib.auth.decorators import login_required
# from dashboard.permissions import is_b2b_user
# from dashboard.services.b2b_dashboard_service import get_b2b_dashboard_data

# @login_required
# def b2b_dashboard_view(request):
#     if not is_b2b_user(request.user):
#         return render(request, "dashboard/errors/403.html", status=403)

#     company_user = request.user.company_user
#     context = get_b2b_dashboard_data(company_user.company)

#     return render(request, "dashboard/b2b/home.html", context)
