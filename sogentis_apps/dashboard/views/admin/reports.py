# dashboard/views/admin/reports.py
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import timedelta
from typing import Any, Dict, List, Optional, Tuple

from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from dashboard.permissions import is_admin, is_staff_user

User = get_user_model()


# ======================================================
# Helpers (safe + prod)
# ======================================================
def _safe_model(app_label: str, model_name: str):
    try:
        return apps.get_model(app_label, model_name)
    except Exception:
        return None


def _model_has_field(model, field_name: str) -> bool:
    try:
        model._meta.get_field(field_name)
        return True
    except Exception:
        return False


def _pick_field(model, candidates: Tuple[str, ...]) -> Optional[str]:
    for f in candidates:
        if _model_has_field(model, f):
            return f
    return None


def _pick_user_field(model) -> Optional[str]:
    return _pick_field(model, ("user", "author", "donor", "created_by", "owner"))


def _pick_date_field(model) -> Optional[str]:
    return _pick_field(model, ("created_at", "created_on", "date", "timestamp", "created"))


def _pick_amount_field(model) -> Optional[str]:
    return _pick_field(model, ("amount", "montant", "total_amount", "total", "value"))


def _sum_amount(qs, amount_field: Optional[str]) -> int:
    if not amount_field:
        return 0
    try:
        val = qs.aggregate(s=Sum(amount_field)).get("s")
        return int(val or 0)
    except Exception:
        return 0


def _counts_by_day(qs, date_field: str, days: int) -> Dict[str, int]:
    """
    Retour {"YYYY-MM-DD": count} sur les N derniers jours.
    """
    start_dt = timezone.now() - timedelta(days=days - 1)
    out: Dict[str, int] = {}
    try:
        agg = (
            qs.filter(**{f"{date_field}__gte": start_dt})
            .annotate(day=TruncDate(date_field))
            .values("day")
            .annotate(c=Count("id"))
            .order_by("day")
        )
        for row in agg:
            d = row.get("day")
            if d:
                out[str(d)] = int(row.get("c") or 0)
        return out
    except Exception:
        # fallback python
        for obj in qs.filter(**{f"{date_field}__gte": start_dt}):
            dt = getattr(obj, date_field, None)
            if not dt:
                continue
            key = str(timezone.localdate(dt))
            out[key] = out.get(key, 0) + 1
        return out


def _date_labels(days: int) -> Tuple[List[str], List[str]]:
    """
    labels: ["JJ/MM", ...]
    keys:   ["YYYY-MM-DD", ...]
    """
    today = timezone.localdate()
    labels: List[str] = []
    keys: List[str] = []
    for i in range(days - 1, -1, -1):
        d = today - timedelta(days=i)
        labels.append(d.strftime("%d/%m"))
        keys.append(str(d))
    return labels, keys


def _get_range_days(request) -> Tuple[str, int]:
    raw = (request.GET.get("range") or "30").strip()
    if raw not in {"7", "30", "90", "180"}:
        raw = "30"
    return raw, int(raw)


def _cache_seconds() -> int:
    """
    TTL cache. Optionnel via settings: DASHBOARD_ADMIN_REPORTS_CACHE_SECONDS
    """
    try:
        from django.conf import settings
        return int(getattr(settings, "DASHBOARD_ADMIN_REPORTS_CACHE_SECONDS", 120) or 0)
    except Exception:
        return 120


def _is_staff_or_admin(user) -> bool:
    return is_admin(user) or is_staff_user(user)


@dataclass
class Series:
    label: str
    values: List[int]


# ======================================================
# View
# ======================================================
@login_required
def admin_reports_view(request):
    """
    Rapports & statistiques globales (staff/admin).
    - stats: new users, donations total/count, engagements count
    - chart_labels + chart_values (activité agrégée)
    - chart_datasets (bonus multi-series)
    """
    if not _is_staff_or_admin(request.user):
        raise PermissionDenied

    range_key, days = _get_range_days(request)
    ttl = _cache_seconds()
    cache_key = f"dash:admin:reports:r{range_key}"

    if ttl > 0:
        cached = cache.get(cache_key)
        if isinstance(cached, dict):
            return render(request, "dashboard/admin/reports.html", cached)

    now_dt = timezone.now()
    since_dt = now_dt - timedelta(days=days)

    # ----------------------------
    # Users stats
    # ----------------------------
    user_date_field = "date_joined" if _model_has_field(User, "date_joined") else _pick_field(User, ("created_at", "created_on"))
    new_users = 0
    users_by_day: Dict[str, int] = {}
    if user_date_field:
        try:
            new_users = User.objects.filter(**{f"{user_date_field}__gte": since_dt}).count()
            users_by_day = _counts_by_day(User.objects.all(), user_date_field, days)
        except Exception:
            new_users = 0
            users_by_day = {}

    # ----------------------------
    # Donations stats (safe)
    # (donations.Donation ou social.Donation)
    # ----------------------------
    Donation = _safe_model("donations", "Donation") or _safe_model("social", "Donation")
    donations_total = 0
    donations_count = 0
    donations_by_day: Dict[str, int] = {}
    if Donation:
        try:
            d_date = _pick_date_field(Donation)
            d_amount = _pick_amount_field(Donation)

            qs = Donation.objects.all()
            # global platform stats -> pas filtré par user

            if d_date:
                donations_count = qs.filter(**{f"{d_date}__gte": since_dt}).count()
                donations_by_day = _counts_by_day(qs, d_date, days)

            if d_amount and d_date:
                donations_total = _sum_amount(qs.filter(**{f"{d_date}__gte": since_dt}), d_amount)
            elif d_amount:
                # fallback sans date
                donations_total = _sum_amount(qs, d_amount)

        except Exception:
            donations_total = 0
            donations_count = 0
            donations_by_day = {}

    # ----------------------------
    # Engagements stats (safe)
    # (social.Engagement ou engagements.Engagement)
    # ----------------------------
    Engagement = _safe_model("social", "Engagement") or _safe_model("engagements", "Engagement")
    engagements_count = 0
    engagements_by_day: Dict[str, int] = {}
    if Engagement:
        try:
            e_date = _pick_date_field(Engagement)
            qs = Engagement.objects.all()
            if e_date:
                engagements_count = qs.filter(**{f"{e_date}__gte": since_dt}).count()
                engagements_by_day = _counts_by_day(qs, e_date, days)
        except Exception:
            engagements_count = 0
            engagements_by_day = {}

    # ----------------------------
    # Build chart (labels + aggregated activity)
    # aggregated = users + donations + engagements per day
    # ----------------------------
    labels, keys = _date_labels(days)

    def _values_from_map(day_map: Dict[str, int]) -> List[int]:
        return [int(day_map.get(k, 0)) for k in keys]

    users_vals = _values_from_map(users_by_day) if users_by_day else [0] * len(keys)
    dons_vals = _values_from_map(donations_by_day) if donations_by_day else [0] * len(keys)
    eng_vals = _values_from_map(engagements_by_day) if engagements_by_day else [0] * len(keys)

    aggregated_vals = [int(u + d + e) for u, d, e in zip(users_vals, dons_vals, eng_vals)]

    # Compat template actuel (chart_labels/chart_values)
    chart_labels = labels
    chart_values = aggregated_vals

    # Bonus datasets (si tu veux afficher plusieurs lignes plus tard)
    chart_datasets = [
        {"label": str(_("Nouveaux utilisateurs")), "data": users_vals},
        {"label": str(_("Dons (nombre)")), "data": dons_vals},
        {"label": str(_("Engagements (nombre)")), "data": eng_vals},
        {"label": str(_("Activité totale")), "data": aggregated_vals},
    ]

    stats = {
        "new_users_30d": int(new_users or 0),
        "donations_30d": int(donations_total or 0),
        "donations_count_30d": int(donations_count or 0),
        "engagements_30d": int(engagements_count or 0),
    }

    ctx = {
        "page_title": _("Rapports & statistiques"),
        "stats": stats,
        "range_key": range_key,

        # pour ton template reports.html (json_script)
        "chart_labels": chart_labels,
        "chart_values": chart_values,

        # bonus (facultatif, si tu veux l’exploiter plus tard)
        "chart_datasets": chart_datasets,
    }

    if ttl > 0:
        cache.set(cache_key, ctx, ttl)

    return render(request, "dashboard/admin/reports.html", ctx)








# # dashboard/views/admin/reports.py
# from datetime import timedelta

# from django.contrib.auth.decorators import login_required
# from django.contrib.auth import get_user_model
# from django.core.exceptions import PermissionDenied
# from django.db.models import Sum, Count
# from django.shortcuts import render
# from django.utils.timezone import now
# from django.utils.translation import gettext_lazy as _

# from dashboard.permissions import is_admin, is_staff_user

# User = get_user_model()

# try:
#     from social.models import Donation, Engagement
# except Exception:
#     Donation = None
#     Engagement = None


# def _is_staff_or_admin(user):
#     return is_admin(user) or is_staff_user(user)


# @login_required
# def admin_reports_view(request):
#     """
#     Rapports & statistiques globales de la plateforme.
#     Version simple, extensible.
#     """
#     user = request.user
#     if not _is_staff_or_admin(user):
#         raise PermissionDenied

#     today = now()
#     since = today - timedelta(days=30)

#     # Nouveaux utilisateurs sur 30 jours
#     new_users_30d = User.objects.filter(date_joined__gte=since).count()

#     donations_30d = 0
#     engagements_30d = 0

#     if Donation is not None:
#         donations_30d = (
#             Donation.objects.filter(created_at__gte=since)
#             .aggregate(total=Sum("amount"))
#             .get("total")
#             or 0
#         )

#     if Engagement is not None:
#         engagements_30d = (
#             Engagement.objects.filter(created_at__gte=since)
#             .aggregate(total=Count("id"))
#             .get("total")
#             or 0
#         )

#     stats = {
#         "new_users_30d": int(new_users_30d or 0),
#         "donations_30d": int(donations_30d or 0),
#         "engagements_30d": int(engagements_30d or 0),
#     }

#     context = {
#         "page_title": _("Rapports & statistiques"),
#         "stats": stats,
#     }
#     return render(request, "dashboard/admin/reports.html", context)




# from django.contrib.auth.decorators import login_required, user_passes_test
# from django.shortcuts import render
# from dashboard.permissions import is_admin


# @login_required
# @user_passes_test(is_admin)
# def reports_dashboard(request):
#     return render(request, "dashboard/admin/reports.html")
