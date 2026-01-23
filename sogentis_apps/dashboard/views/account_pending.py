# dashboard/views/account_pending.py
from __future__ import annotations

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from dashboard.views.utils import iter_user_profiles, detect_profile_kind, detect_profile_status


@login_required
def account_pending_view(request):
    """
    Page utilisateur read-only:
    - explique l'état pending/refused
    - N'AFFECTE PAS la navigation du site
    - N'affecte que certaines sections dashboard (vendor/b2b/admin)
    """
    profiles = []
    try:
        profiles = iter_user_profiles(request.user)
    except Exception:
        profiles = []

    def label_kind(k: str) -> str:
        if k == "social":
            return str(_("Social"))
        if k == "economic":
            return str(_("Économique"))
        return str(_("Général"))

    rows = []
    for p in profiles:
        rows.append({
            "kind": detect_profile_kind(p),
            "kind_label": label_kind(detect_profile_kind(p)),
            "status": detect_profile_status(p) or "",
            "model": p.__class__.__name__,
        })

    pending = [r for r in rows if r["status"] == "pending"]
    rejected = [r for r in rows if r["status"] == "rejected"]

    support_email = getattr(settings, "SUPPORT_EMAIL", "") or getattr(settings, "DEFAULT_FROM_EMAIL", "")

    context = {
        "page_title": _("Compte / Profils"),
        "profiles_rows": rows,
        "pending_rows": pending,
        "rejected_rows": rejected,
        "support_email": support_email,
    }
    return render(request, "dashboard/account_pending.html", context)



# # dashboard/views/account_pending.py
# from __future__ import annotations

# from django.conf import settings
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render
# from django.utils.translation import gettext_lazy as _

# from dashboard.views.utils import (
#     detect_profile_kind,
#     detect_profile_status,
#     get_user_profile,
#     iter_user_profiles,
# )


# @login_required
# def account_pending_view(request):
#     """
#     Page utilisateur (read-only) :
#     - compte activé mais profil(s) en attente / refusé / non validé.
#     - aucun write en base.
#     """
#     user = request.user

#     # Profil "principal" (pour afficher un status lisible),
#     # mais le statut global se calcule sur tous les profils.
#     profile = get_user_profile(user)

#     # Status lisible (raw)
#     status_raw = ""
#     if profile is not None:
#         status_raw = (
#             getattr(profile, "status", None)
#             or getattr(profile, "validation_status", None)
#             or getattr(profile, "account_status", None)
#             or ""
#         )
#     profile_status = str(status_raw or "").strip()

#     # Synthèse multi-profils (social/economic/generic)
#     summary = []
#     any_rejected = False
#     any_pending = False

#     for p in iter_user_profiles(user):
#         st = detect_profile_status(p)
#         kd = detect_profile_kind(p)

#         if st == "rejected":
#             any_rejected = True
#         elif st == "pending":
#             any_pending = True

#         summary.append({"kind": kd, "status": st})

#     # Pending state global (si un profil refusé => refusé)
#     pending_state = "rejected" if any_rejected else ("pending" if any_pending else "pending")

#     support_email = getattr(settings, "SUPPORT_EMAIL", "") or getattr(settings, "DEFAULT_FROM_EMAIL", "")

#     context = {
#         "page_title": _("Compte en attente"),
#         "profile": profile,
#         "profile_status": profile_status,
#         "profiles_summary": summary,
#         "pending_state": pending_state,
#         "support_email": support_email,
#     }
#     return render(request, "dashboard/account_pending.html", context)




# # dashboard/views/account_pending.py
# from __future__ import annotations

# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render
# from django.utils.translation import gettext_lazy as _

# from dashboard.views.utils import get_user_profile


# @login_required
# def account_pending_view(request):
#     """
#     Page utilisateur (read-only) :
#     - compte activé mais profil(s) en attente / refusé / non validé.
#     - aucun write en base.
#     """
#     profile = get_user_profile(request.user)

#     # On essaye de déduire un statut lisible (sans imposer un modèle)
#     status = ""
#     if profile is not None:
#         status = (
#             getattr(profile, "status", None)
#             or getattr(profile, "validation_status", None)
#             or getattr(profile, "account_status", None)
#             or ""
#         )
#     status_str = str(status or "").strip()

#     context = {
#         "page_title": _("Compte en attente"),
#         "profile": profile,
#         "profile_status": status_str,
#     }
#     return render(request, "dashboard/account_pending.html", context)




# # dashboard/views/account_pending.py
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render

# from dashboard.views.utils import get_user_profile


# @login_required
# def account_pending_view(request):
#     profile = get_user_profile(request.user)
#     return render(request, "dashboard/account_pending.html", {"profile": profile})
