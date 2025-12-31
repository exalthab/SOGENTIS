# dashboard/views/admin/settings.py
from types import SimpleNamespace

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _

from dashboard.permissions import is_admin


def _get_fake_settings():
    """
    Placeholder pour des paramètres globaux.
    À remplacer plus tard par un vrai modèle (ex: SiteSettings).
    """
    return SimpleNamespace(
        site_name="SOGENTIS",
        support_email="support@example.com",
        maintenance_mode=False,
    )


@login_required
def admin_settings_view(request):
    """
    Paramètres globaux de la plateforme.
    Version simple : pas encore de persistance en base.
    """
    user = request.user
    if not is_admin(user):
        # On réserve cette page aux vrais admins
        raise PermissionDenied

    settings_obj = _get_fake_settings()

    if request.method == "POST":
        site_name = request.POST.get("site_name") or settings_obj.site_name
        support_email = request.POST.get("support_email") or settings_obj.support_email
        maintenance_mode = bool(request.POST.get("maintenance_mode"))

        # TODO: persister dans un vrai modèle plus tard
        settings_obj.site_name = site_name
        settings_obj.support_email = support_email
        settings_obj.maintenance_mode = maintenance_mode

        messages.success(
            request,
            _("Les paramètres ont été enregistrés (exemple, sans persistance réelle pour l’instant)."),
        )
        return redirect("dashboard:admin:settings")

    context = {
        "page_title": _("Paramètres"),
        "settings": settings_obj,
    }
    return render(request, "dashboard/admin/settings.html", context)





# from django.contrib.auth.decorators import login_required, user_passes_test
# from django.shortcuts import render
# from dashboard.permissions import is_admin


# @login_required
# @user_passes_test(is_admin)
# def admin_settings(request):
#     return render(request, "dashboard/admin/settings.html")
