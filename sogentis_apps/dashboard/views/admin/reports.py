# dashboard/views/admin/reports.py
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.db.models import Sum, Count
from django.shortcuts import render
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from dashboard.permissions import is_admin, is_staff_user

User = get_user_model()

try:
    from social.models import Donation, Engagement
except Exception:
    Donation = None
    Engagement = None


def _is_staff_or_admin(user):
    return is_admin(user) or is_staff_user(user)


@login_required
def admin_reports_view(request):
    """
    Rapports & statistiques globales de la plateforme.
    Version simple, extensible.
    """
    user = request.user
    if not _is_staff_or_admin(user):
        raise PermissionDenied

    today = now()
    since = today - timedelta(days=30)

    # Nouveaux utilisateurs sur 30 jours
    new_users_30d = User.objects.filter(date_joined__gte=since).count()

    donations_30d = 0
    engagements_30d = 0

    if Donation is not None:
        donations_30d = (
            Donation.objects.filter(created_at__gte=since)
            .aggregate(total=Sum("amount"))
            .get("total")
            or 0
        )

    if Engagement is not None:
        engagements_30d = (
            Engagement.objects.filter(created_at__gte=since)
            .aggregate(total=Count("id"))
            .get("total")
            or 0
        )

    stats = {
        "new_users_30d": int(new_users_30d or 0),
        "donations_30d": int(donations_30d or 0),
        "engagements_30d": int(engagements_30d or 0),
    }

    context = {
        "page_title": _("Rapports & statistiques"),
        "stats": stats,
    }
    return render(request, "dashboard/admin/reports.html", context)




# from django.contrib.auth.decorators import login_required, user_passes_test
# from django.shortcuts import render
# from dashboard.permissions import is_admin


# @login_required
# @user_passes_test(is_admin)
# def reports_dashboard(request):
#     return render(request, "dashboard/admin/reports.html")
