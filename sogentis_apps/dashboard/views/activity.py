from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from dashboard.models import UserActivityLog

@login_required
def recent_activity_logs_view(request):
    """
    Vue modulaire dédiée aux activités utilisateur.
    """
    logs = UserActivityLog.objects.filter(user=request.user)[:10]
    return render(request, "dashboard/recent_logs.html", {
        "logs": logs,
        "page_title": _("Mes activités récentes"),
    })
