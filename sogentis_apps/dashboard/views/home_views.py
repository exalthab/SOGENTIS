# dashboard/views/home_views.py
from __future__ import annotations

import json
import logging
from datetime import timedelta
from typing import Any, Dict, List, Tuple

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import Sum, Count
from django.db.models.functions import TruncDate
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from dashboard.views.utils import get_user_profile, detect_profile_status

logger = logging.getLogger(__name__)


try:
    from dashboard.models import UserActivityLog  # type: ignore
except Exception:  # pragma: no cover
    UserActivityLog = None  # type: ignore

try:
    from social.models import Don, Engagement  # type: ignore
except Exception:  # pragma: no cover
    Don = None  # type: ignore
    Engagement = None  # type: ignore


def home(request):
    """
    Home dashboard :
    - si connecté -> router (décide admin/social/economic/hub)
    - sinon -> login + next
    """
    if request.user.is_authenticated:
        return redirect("dashboard:router")
    login_url = reverse("accounts_users:web:auth:login")
    return redirect(f"{login_url}?next={request.path}")


def _get_range_days(request) -> Tuple[str, int]:
    raw = (request.GET.get("range") or "30").strip()
    if raw not in ("7", "30", "90"):
        raw = "30"
    return raw, int(raw)


def _cache_seconds() -> int:
    return int(getattr(settings, "DASHBOARD_CACHE_SECONDS", 60) or 60)


def _get_date_field(model, preferred: List[str]) -> str:
    for name in preferred:
        try:
            model._meta.get_field(name)
            return name
        except Exception:
            continue
    raise ValueError("No date field found")


def _since_for_field(model, field_name: str, since_dt) -> Any:
    try:
        f = model._meta.get_field(field_name)
        internal = getattr(f, "get_internal_type", lambda: "")()
        if internal == "DateField":
            return since_dt.date()
    except Exception:
        pass
    return since_dt


def _pick_user_fk(model, candidates: List[str]) -> str:
    for name in candidates:
        try:
            model._meta.get_field(name)
            return name
        except Exception:
            continue
    return "user"


def _pick_amount_field(model, candidates: List[str]) -> str:
    for name in candidates:
        try:
            model._meta.get_field(name)
            return name
        except Exception:
            continue
    return "montant"


def _build_activity_series(user, days: int) -> Tuple[List[str], List[int]]:
    labels = [(timezone.now().date() - timedelta(days=days - 1 - i)).strftime("%d/%m") for i in range(days)]
    if Don is None or Engagement is None:
        return labels, [0] * days

    since_dt = timezone.now() - timedelta(days=days - 1)
    since_date = since_dt.date()

    try:
        don_user_field = _pick_user_fk(Don, ["user", "donor", "created_by", "owner"])
        eng_user_field = _pick_user_fk(Engagement, ["user", "member", "volunteer", "created_by"])

        don_date_field = _get_date_field(Don, ["date", "created_at", "created"])
        eng_date_field = _get_date_field(Engagement, ["created_at", "date", "created"])

        don_since = _since_for_field(Don, don_date_field, since_dt)
        eng_since = _since_for_field(Engagement, eng_date_field, since_dt)

        dons_qs = (
            Don.objects
            .filter(**{don_user_field: user, f"{don_date_field}__gte": don_since})
            .annotate(day=TruncDate(don_date_field))
            .values("day")
            .annotate(c=Count("id"))
            .order_by("day")
        )

        eng_qs = (
            Engagement.objects
            .filter(**{eng_user_field: user, f"{eng_date_field}__gte": eng_since})
            .annotate(day=TruncDate(eng_date_field))
            .values("day")
            .annotate(c=Count("id"))
            .order_by("day")
        )

        don_map = {row["day"]: int(row["c"] or 0) for row in dons_qs}
        eng_map = {row["day"]: int(row["c"] or 0) for row in eng_qs}

        values: List[int] = []
        for i in range(days):
            d = since_date + timedelta(days=i)
            values.append(don_map.get(d, 0) + eng_map.get(d, 0))

        return labels, values
    except Exception:
        return labels, [0] * days


def _get_orders_count(user) -> int:
    try:
        from economic.ecommerce.models.order import Order  # type: ignore
        # user field standard
        return Order.objects.filter(user=user).count()
    except Exception:
        return 0


def _get_notes_count(user) -> int:
    for path in ("dashboard.models.dashboard_note.DashboardNote", "dashboard.models.DashboardNote"):
        try:
            module_path, cls_name = path.rsplit(".", 1)
            mod = __import__(module_path, fromlist=[cls_name])
            Model = getattr(mod, cls_name)
            return Model.objects.filter(user=user).count()
        except Exception:
            continue
    return 0


def _get_donation_total(user) -> Any:
    if Don is None:
        return 0
    try:
        user_field = _pick_user_fk(Don, ["user", "donor", "created_by", "owner"])
        amount_field = _pick_amount_field(Don, ["montant", "amount", "value", "total"])
        return Don.objects.filter(**{user_field: user}).aggregate(total=Sum(amount_field))["total"] or 0
    except Exception:
        return 0


def _profile_status(user) -> str:
    p = get_user_profile(user)
    return detect_profile_status(p) if p else ""


@login_required
def dashboard_home_view(request):
    user = request.user
    range_key, days = _get_range_days(request)

    ttl = _cache_seconds()
    cache_key = f"dash:home:{user.id}:r{range_key}"

    if ttl > 0:
        cached = cache.get(cache_key)
        if isinstance(cached, dict):
            return render(request, "dashboard/home.html", cached)

    # KPI safe
    kpi_donations_count = 0
    kpi_engagements_count = 0
    try:
        if Don is not None:
            user_field = _pick_user_fk(Don, ["user", "donor", "created_by", "owner"])
            kpi_donations_count = Don.objects.filter(**{user_field: user}).count()
        if Engagement is not None:
            user_field = _pick_user_fk(Engagement, ["user", "member", "volunteer", "created_by"])
            kpi_engagements_count = Engagement.objects.filter(**{user_field: user}).count()
    except Exception:
        pass

    kpi_orders_count = _get_orders_count(user)
    kpi_notes_count = _get_notes_count(user)
    kpi_donations_total = _get_donation_total(user)

    labels, values = _build_activity_series(user, days)

    recent_activity: List[Dict[str, Any]] = []
    if UserActivityLog is not None:
        logs = UserActivityLog.objects.filter(user=user).order_by("-id")[:10]
        for l in logs:
            recent_activity.append({
                "date": getattr(l, "created_at", None) or getattr(l, "date", None) or timezone.now(),
                "kind": getattr(l, "kind", _("Action")),
                "label": getattr(l, "label", "") or str(l),
                "status": getattr(l, "status", "info"),
            })

    context: Dict[str, Any] = {
        "page_title": _("Dashboard"),
        "range_key": range_key,
        "profile_status": _profile_status(user),

        "kpi_donations_count": kpi_donations_count,
        "kpi_donations_total": kpi_donations_total,
        "kpi_engagements_count": kpi_engagements_count,
        "kpi_orders_count": kpi_orders_count,
        "kpi_notes_count": kpi_notes_count,

        "chart_labels_json": json.dumps(labels, ensure_ascii=False),
        "chart_values_json": json.dumps(values),

        "recent_activity": recent_activity,
    }

    if ttl > 0:
        cache.set(cache_key, context, ttl)

    return render(request, "dashboard/home.html", context)


@login_required
def dashboard_stats_view(request):
    user = request.user
    donation_total = _get_donation_total(user)
    engagement_count = 0
    try:
        if Engagement is not None:
            user_field = _pick_user_fk(Engagement, ["user", "member", "volunteer", "created_by"])
            engagement_count = Engagement.objects.filter(**{user_field: user}).count()
    except Exception:
        pass

    summary_cards = [
        {"label": _("Total des dons"), "value": f"{donation_total or 0} FCFA", "color": "primary"},
        {"label": _("Engagements"), "value": engagement_count, "color": "success"},
    ]

    return render(request, "dashboard/stats.html", {
        "donation_total": donation_total,
        "engagement_count": engagement_count,
        "summary_cards": summary_cards,
    })


@login_required
def engagements_list_view(request):
    if Engagement is None:
        return render(request, "dashboard/engagements_list.html", {"engagements": [], "page_title": _("Mes engagements")})

    try:
        user_field = _pick_user_fk(Engagement, ["user", "member", "volunteer", "created_by"])
        engagements = Engagement.objects.filter(**{user_field: request.user}).order_by("-created_at", "-date")
    except Exception:
        engagements = Engagement.objects.none()

    paginator = Paginator(engagements, 10)
    engagements_page = paginator.get_page(request.GET.get("page"))

    return render(request, "dashboard/engagements_list.html", {
        "engagements": engagements_page,
        "page_title": _("Mes engagements"),
    })


@login_required
def dons_list_view(request):
    if Don is None:
        return render(request, "dashboard/dons_list.html", {"dons": [], "page_title": _("Mes dons")})

    try:
        user_field = _pick_user_fk(Don, ["user", "donor", "created_by", "owner"])
        dons = Don.objects.filter(**{user_field: request.user}).order_by("-date", "-created_at")
    except Exception:
        dons = Don.objects.none()

    paginator = Paginator(dons, 10)
    dons_page = paginator.get_page(request.GET.get("page"))

    return render(request, "dashboard/dons_list.html", {"dons": dons_page, "page_title": _("Mes dons")})


@login_required
def recent_activity_logs_view(request):
    if UserActivityLog is None:
        return render(request, "dashboard/recent_logs.html", {"logs": [], "page_title": _("Activités récentes")})

    logs = UserActivityLog.objects.filter(user=request.user).order_by("-id")[:10]
    return render(request, "dashboard/recent_logs.html", {"logs": logs, "page_title": _("Activités récentes")})





# # dashboard/views/home_views.py
# from __future__ import annotations

# import json
# import logging
# from datetime import timedelta
# from typing import Any, Dict, List, Tuple

# from django.conf import settings
# from django.contrib.auth.decorators import login_required
# from django.core.cache import cache
# from django.core.paginator import Paginator
# from django.db.models import Sum, Count
# from django.db.models.functions import TruncDate
# from django.shortcuts import redirect, render
# from django.urls import reverse
# from django.utils import timezone
# from django.utils.translation import gettext_lazy as _

# logger = logging.getLogger(__name__)


# # ======================================================
# # SAFE IMPORTS (prod)
# # ======================================================
# try:
#     from dashboard.models import UserActivityLog  # type: ignore
# except Exception:  # pragma: no cover
#     UserActivityLog = None  # type: ignore

# try:
#     from social.models import Don, Engagement  # type: ignore
# except Exception:  # pragma: no cover
#     Don = None  # type: ignore
#     Engagement = None  # type: ignore


# # ======================================================
# # 0) PUBLIC HOME (optionnel)
# # ======================================================
# def home(request):
#     """
#     Home dashboard : si connecté -> dashboard_home_view, sinon -> page publique (ou login).
#     Ici on redirige vers la page login si non authentifié pour éviter un dashboard vide.
#     """
#     if request.user.is_authenticated:
#         return redirect("dashboard:home")  # ou le name réel de ta home connectée
#     return redirect(f"{reverse('accounts_users:web:auth:login')}?next={request.path}")


# # ======================================================
# # 1) HELPERS PROD (safe)
# # ======================================================
# def _get_range_days(request) -> Tuple[str, int]:
#     raw = (request.GET.get("range") or "30").strip()
#     if raw not in ("7", "30", "90"):
#         raw = "30"
#     return raw, int(raw)


# def _cache_seconds() -> int:
#     return int(getattr(settings, "DASHBOARD_CACHE_SECONDS", 60) or 60)


# def _get_date_field(model, preferred: List[str]) -> str:
#     """
#     Renvoie le 1er champ existant parmi `preferred`, sinon lève ValueError.
#     """
#     for name in preferred:
#         try:
#             model._meta.get_field(name)
#             return name
#         except Exception:
#             continue
#     raise ValueError("No date field found")


# def _since_for_field(model, field_name: str, since_dt) -> Any:
#     """
#     Si field est DateField -> utiliser since_dt.date()
#     Sinon (DateTimeField) -> since_dt
#     """
#     try:
#         f = model._meta.get_field(field_name)
#         internal = getattr(f, "get_internal_type", lambda: "")()
#         if internal == "DateField":
#             return since_dt.date()
#     except Exception:
#         pass
#     return since_dt


# def _build_activity_series(user, days: int) -> Tuple[List[str], List[int]]:
#     """
#     Série d'activité (dons + engagements) groupée par jour.
#     """
#     if Don is None or Engagement is None:
#         labels = [(timezone.now().date() - timedelta(days=days - 1 - i)).strftime("%d/%m") for i in range(days)]
#         return labels, [0] * days

#     since_dt = timezone.now() - timedelta(days=days - 1)
#     since_date = since_dt.date()

#     # champs date robustes
#     don_date_field = _get_date_field(Don, ["date", "created_at", "created"])
#     eng_date_field = _get_date_field(Engagement, ["created_at", "date", "created"])

#     don_since = _since_for_field(Don, don_date_field, since_dt)
#     eng_since = _since_for_field(Engagement, eng_date_field, since_dt)

#     dons_qs = (
#         Don.objects
#         .filter(user=user, **{f"{don_date_field}__gte": don_since})
#         .annotate(day=TruncDate(don_date_field))
#         .values("day")
#         .annotate(c=Count("id"))
#         .order_by("day")
#     )

#     eng_qs = (
#         Engagement.objects
#         .filter(user=user, **{f"{eng_date_field}__gte": eng_since})
#         .annotate(day=TruncDate(eng_date_field))
#         .values("day")
#         .annotate(c=Count("id"))
#         .order_by("day")
#     )

#     don_map = {row["day"]: int(row["c"] or 0) for row in dons_qs}
#     eng_map = {row["day"]: int(row["c"] or 0) for row in eng_qs}

#     labels: List[str] = []
#     values: List[int] = []

#     for i in range(days):
#         d = since_date + timedelta(days=i)
#         labels.append(d.strftime("%d/%m"))
#         values.append(don_map.get(d, 0) + eng_map.get(d, 0))

#     return labels, values


# def _get_orders_count(user) -> int:
#     try:
#         from economic.ecommerce.models.order import Order  # type: ignore
#         return Order.objects.filter(user=user).count()
#     except Exception:
#         return 0


# def _get_notes_count(user) -> int:
#     try:
#         from dashboard.models.dashboard_note import DashboardNote  # type: ignore
#         return DashboardNote.objects.filter(user=user).count()
#     except Exception:
#         try:
#             from dashboard.models import DashboardNote  # type: ignore
#             return DashboardNote.objects.filter(user=user).count()
#         except Exception:
#             return 0


# def _get_donation_total(user) -> Any:
#     if Don is None:
#         return 0
#     try:
#         if hasattr(Don.objects, "aggregate_total_amount"):
#             return Don.objects.filter(user=user).aggregate_total_amount()
#     except Exception:
#         pass
#     try:
#         return Don.objects.filter(user=user).aggregate(total=Sum("montant"))["total"] or 0
#     except Exception:
#         return 0


# def _profile_status(user) -> str:
#     profile = getattr(user, "userprofile", None)
#     return (getattr(profile, "status", "") or "").lower().strip()


# # ======================================================
# # 2) DASHBOARD HOME (PROD)
# # ======================================================
# @login_required
# def dashboard_home_view(request):
#     user = request.user
#     range_key, days = _get_range_days(request)

#     ttl = _cache_seconds()
#     cache_key = f"dash:home:{user.id}:r{range_key}"

#     if ttl > 0:
#         cached = cache.get(cache_key)
#         if isinstance(cached, dict):
#             return render(request, "dashboard/home.html", cached)

#     # KPI safe
#     kpi_donations_count = Don.objects.filter(user=user).count() if Don is not None else 0
#     kpi_engagements_count = Engagement.objects.filter(user=user).count() if Engagement is not None else 0
#     kpi_orders_count = _get_orders_count(user)
#     kpi_notes_count = _get_notes_count(user)
#     kpi_donations_total = _get_donation_total(user)

#     # Chart
#     labels, values = _build_activity_series(user, days)

#     # Logs -> recent_activity
#     recent_activity: List[Dict[str, Any]] = []
#     if UserActivityLog is not None:
#         logs = UserActivityLog.objects.filter(user=user).order_by("-id")[:10]
#         for l in logs:
#             recent_activity.append({
#                 "date": getattr(l, "created_at", None) or getattr(l, "date", None) or timezone.now(),
#                 "kind": getattr(l, "kind", _("Action")),
#                 "label": getattr(l, "label", "") or str(l),
#                 "status": getattr(l, "status", "info"),
#             })

#     context: Dict[str, Any] = {
#         "page_title": _("Dashboard"),

#         # IMPORTANT: on passe TOUJOURS ces valeurs au template (pas de request.GET.*)
#         "range_key": range_key,
#         "profile_status": _profile_status(user),

#         # KPI
#         "kpi_donations_count": kpi_donations_count,
#         "kpi_donations_total": kpi_donations_total,
#         "kpi_engagements_count": kpi_engagements_count,
#         "kpi_orders_count": kpi_orders_count,
#         "kpi_notes_count": kpi_notes_count,

#         # Chart: on fournit des JSON sûrs (prod)
#         "chart_labels_json": json.dumps(labels, ensure_ascii=False),
#         "chart_values_json": json.dumps(values),

#         # Activity
#         "recent_activity": recent_activity,
#     }

#     if ttl > 0:
#         cache.set(cache_key, context, ttl)

#     return render(request, "dashboard/home.html", context)


# # ======================================================
# # 3) VUES EXISTANTES (complètes)
# # ======================================================
# @login_required
# def dashboard_stats_view(request):
#     user = request.user

#     donation_total = _get_donation_total(user)
#     engagement_count = Engagement.objects.filter(user=user).count() if Engagement is not None else 0

#     summary_cards = [
#         {"label": _("Total des dons"), "value": f"{donation_total or 0} FCFA", "color": "primary"},
#         {"label": _("Engagements"), "value": engagement_count, "color": "success"},
#     ]

#     return render(request, "dashboard/stats.html", {
#         "donation_total": donation_total,
#         "engagement_count": engagement_count,
#         "summary_cards": summary_cards,
#     })


# @login_required
# def engagements_list_view(request):
#     if Engagement is None:
#         return render(request, "dashboard/engagements_list.html", {
#             "engagements": [],
#             "page_title": _("Mes engagements"),
#         })

#     engagements = Engagement.objects.filter(user=request.user).order_by("-created_at", "-date")
#     paginator = Paginator(engagements, 10)
#     page_number = request.GET.get("page")
#     engagements_page = paginator.get_page(page_number)

#     return render(request, "dashboard/engagements_list.html", {
#         "engagements": engagements_page,
#         "page_title": _("Mes engagements"),
#     })


# @login_required
# def dons_list_view(request):
#     if Don is None:
#         return render(request, "dashboard/dons_list.html", {
#             "dons": [],
#             "page_title": _("Mes dons"),
#         })

#     dons = Don.objects.filter(user=request.user).order_by("-date", "-created_at")
#     paginator = Paginator(dons, 10)
#     page_number = request.GET.get("page")
#     dons_page = paginator.get_page(page_number)

#     return render(request, "dashboard/dons_list.html", {
#         "dons": dons_page,
#         "page_title": _("Mes dons"),
#     })


# @login_required
# def recent_activity_logs_view(request):
#     if UserActivityLog is None:
#         return render(request, "dashboard/recent_logs.html", {
#             "logs": [],
#             "page_title": _("Activités récentes"),
#         })

#     logs = UserActivityLog.objects.filter(user=request.user).order_by("-id")[:10]
#     return render(request, "dashboard/recent_logs.html", {
#         "logs": logs,
#         "page_title": _("Activités récentes"),
#     })








# # dashboard/views/home_views.py
# from __future__ import annotations

# import logging
# from datetime import timedelta
# from typing import Any, Dict, List, Tuple

# from django.contrib.auth.decorators import login_required
# from django.core.cache import cache
# from django.core.paginator import Paginator
# from django.db.models import Sum, Count
# from django.db.models.functions import TruncDate
# from django.shortcuts import render
# from django.utils import timezone
# from django.utils.translation import gettext_lazy as _

# from dashboard.models import UserActivityLog

# # Social
# from social.models import Don, Engagement

# logger = logging.getLogger(__name__)


# # ======================================================
# # 0) PUBLIC HOME (si tu gardes une page dashboard publique)
# # ======================================================
# def home(request):
#     """
#     Page d'accueil du tableau de bord (publique ou protégée selon le design).
#     """
#     return render(request, "dashboard/home.html")


# # ======================================================
# # 1) HELPERS PROD (safe)
# # ======================================================
# def _get_range_days(request) -> Tuple[str, int]:
#     """
#     Range choisi via ?range=7|30|90 (default 30)
#     Retourne (range_key_str, days_int)
#     """
#     raw = (request.GET.get("range") or "30").strip()
#     if raw not in ("7", "30", "90"):
#         raw = "30"
#     return raw, int(raw)


# def _get_cache_seconds() -> int:
#     """
#     TTL cache dashboard (prod). Mettre DASHBOARD_CACHE_SECONDS dans settings.
#     """
#     try:
#         from django.conf import settings
#         return int(getattr(settings, "DASHBOARD_CACHE_SECONDS", 60) or 0)
#     except Exception:
#         return 60


# def _get_don_date_field() -> str:
#     """
#     Détecte le champ date le plus plausible pour Don : date ou created_at.
#     """
#     try:
#         Don._meta.get_field("date")
#         return "date"
#     except Exception:
#         return "created_at"


# def _get_engagement_date_field() -> str:
#     """
#     Détecte le champ date le plus plausible pour Engagement : created_at ou date.
#     """
#     try:
#         Engagement._meta.get_field("created_at")
#         return "created_at"
#     except Exception:
#         return "date"


# def _build_activity_series(user, days: int) -> Tuple[List[str], List[int]]:
#     """
#     Série d'activité (dons + engagements) groupée par jour.
#     Retourne (labels, values) sur 'days' jours.
#     """
#     since_dt = timezone.now() - timedelta(days=days - 1)
#     since_date = since_dt.date()

#     don_date_field = _get_don_date_field()
#     eng_date_field = _get_engagement_date_field()

#     dons_qs = (
#         Don.objects
#         .filter(user=user, **{f"{don_date_field}__gte": since_dt})
#         .annotate(day=TruncDate(don_date_field))
#         .values("day")
#         .annotate(c=Count("id"))
#         .order_by("day")
#     )

#     eng_qs = (
#         Engagement.objects
#         .filter(user=user, **{f"{eng_date_field}__gte": since_dt})
#         .annotate(day=TruncDate(eng_date_field))
#         .values("day")
#         .annotate(c=Count("id"))
#         .order_by("day")
#     )

#     don_map = {row["day"]: int(row["c"] or 0) for row in dons_qs}
#     eng_map = {row["day"]: int(row["c"] or 0) for row in eng_qs}

#     labels: List[str] = []
#     values: List[int] = []

#     for i in range(days):
#         d = since_date + timedelta(days=i)
#         labels.append(d.strftime("%d/%m"))
#         values.append(don_map.get(d, 0) + eng_map.get(d, 0))

#     return labels, values


# def _get_orders_count(user) -> int:
#     """
#     KPI commandes (si ecommerce dispo).
#     """
#     try:
#         from economic.ecommerce.models.order import Order  # type: ignore
#         return Order.objects.filter(user=user).count()
#     except Exception:
#         return 0


# def _get_notes_count(user) -> int:
#     """
#     KPI notes (si dashboard note dispo).
#     """
#     # Essai 1: module dashboard_note
#     try:
#         from dashboard.models.dashboard_note import DashboardNote  # type: ignore
#         return DashboardNote.objects.filter(user=user).count()
#     except Exception:
#         pass

#     # Essai 2: DashboardNote direct
#     try:
#         from dashboard.models import DashboardNote  # type: ignore
#         return DashboardNote.objects.filter(user=user).count()
#     except Exception:
#         return 0


# def _get_donation_total(user) -> Any:
#     """
#     Total dons (compatible manager custom ou fallback).
#     """
#     try:
#         if hasattr(Don.objects, "aggregate_total_amount"):
#             return Don.objects.filter(user=user).aggregate_total_amount()
#     except Exception:
#         pass

#     # fallback
#     try:
#         return Don.objects.filter(user=user).aggregate(total=Sum("montant"))["total"]
#     except Exception:
#         return 0


# # ======================================================
# # 2) DASHBOARD HOME (PROD)
# # ======================================================
# @login_required
# def dashboard_home_view(request):
#     """
#     Dashboard HOME (PROD)
#     - Range 7/30/90 jours
#     - KPI (dons, engagements, commandes, notes)
#     - Graph (activité)
#     - Recent activity (logs)
#     - Cache léger par user + range (settings.DASHBOARD_CACHE_SECONDS)
#     """
#     user = request.user
#     range_key, days = _get_range_days(request)

#     cache_seconds = _get_cache_seconds()
#     cache_key = f"dash:home:{user.id}:r{range_key}"

#     if cache_seconds > 0:
#         cached = cache.get(cache_key)
#         if isinstance(cached, dict):
#             return render(request, "dashboard/home.html", cached)

#     # ===== KPI =====
#     kpi_donations_count = Don.objects.filter(user=user).count()
#     kpi_engagements_count = Engagement.objects.filter(user=user).count()
#     kpi_orders_count = _get_orders_count(user)
#     kpi_notes_count = _get_notes_count(user)

#     donation_total = _get_donation_total(user) or 0

#     # ===== CHART =====
#     chart_labels, chart_values = _build_activity_series(user, days)

#     # ===== LOGS =====
#     logs = (
#         UserActivityLog.objects
#         .filter(user=user)
#         .order_by("-id")[:10]
#     )

#     recent_activity: List[Dict[str, Any]] = []
#     for l in logs:
#         recent_activity.append({
#             "date": getattr(l, "created_at", None) or getattr(l, "date", None) or timezone.now(),
#             "kind": getattr(l, "kind", _("Action")),
#             "label": getattr(l, "label", "") or str(l),
#             "status": getattr(l, "status", "info"),
#         })

#     # ===== Profil (optionnel) =====
#     profile = getattr(user, "userprofile", None)
#     profile_status = getattr(profile, "status", "")

#     context = {
#         "page_title": _("Dashboard"),
#         "range_key": range_key,

#         # KPI
#         "kpi_donations_count": kpi_donations_count,
#         "kpi_donations_total": donation_total,
#         "kpi_engagements_count": kpi_engagements_count,
#         "kpi_orders_count": kpi_orders_count,
#         "kpi_notes_count": kpi_notes_count,

#         # Chart
#         "chart_labels": chart_labels,   # LIST -> ton template fait |safe
#         "chart_values": chart_values,   # LIST -> ton template fait |safe

#         # Activity
#         "recent_activity": recent_activity,

#         # Optional
#         "profile_status": profile_status,
#     }

#     if cache_seconds > 0:
#         cache.set(cache_key, context, cache_seconds)

#     return render(request, "dashboard/home.html", context)


# # ======================================================
# # 3) VUES EXISTANTES (inchangées, complètes)
# # ======================================================
# @login_required
# def dashboard_stats_view(request):
#     """
#     Statistiques globales de l'utilisateur (total dons, engagements…)
#     """
#     user = request.user

#     donation_total = _get_donation_total(user)
#     engagement_count = Engagement.objects.filter(user=user).count()

#     summary_cards = [
#         {"label": _("Total des dons"), "value": f"{donation_total or 0} FCFA", "color": "primary"},
#         {"label": _("Engagements"), "value": engagement_count, "color": "success"},
#     ]

#     context = {
#         "donation_total": donation_total,
#         "engagement_count": engagement_count,
#         "summary_cards": summary_cards,
#     }
#     return render(request, "dashboard/stats.html", context)


# @login_required
# def engagements_list_view(request):
#     """
#     Liste paginée des engagements de l'utilisateur connecté.
#     """
#     engagements = Engagement.objects.filter(user=request.user).order_by("-created_at", "-date")
#     paginator = Paginator(engagements, 10)
#     page_number = request.GET.get("page")
#     engagements_page = paginator.get_page(page_number)

#     return render(
#         request,
#         "dashboard/engagements_list.html",
#         {
#             "engagements": engagements_page,
#             "page_title": _("Mes engagements"),
#         },
#     )


# @login_required
# def dons_list_view(request):
#     """
#     Liste paginée des dons de l'utilisateur connecté.
#     """
#     dons = Don.objects.filter(user=request.user).order_by("-date", "-created_at")
#     paginator = Paginator(dons, 10)
#     page_number = request.GET.get("page")
#     dons_page = paginator.get_page(page_number)

#     return render(
#         request,
#         "dashboard/dons_list.html",
#         {
#             "dons": dons_page,
#             "page_title": _("Mes dons"),
#         },
#     )


# @login_required
# def recent_activity_logs_view(request):
#     """
#     Affiche les dernières activités de l'utilisateur connecté.
#     """
#     logs = UserActivityLog.objects.filter(user=request.user).order_by("-id")[:10]
#     return render(
#         request,
#         "dashboard/recent_logs.html",
#         {
#             "logs": logs,
#             "page_title": _("Activités récentes"),
#         },
#     )






# # #dashboard/views/home_views.py
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render
# from django.core.paginator import Paginator
# from django.utils.translation import gettext_lazy as _
# from django.db.models import Sum

# from dashboard.models import UserActivityLog

# from social.models import Don, Engagement

# def home(request):
#     """
#     Page d'accueil du tableau de bord (publique ou protégée selon le design).
#     """
#     return render(request, "dashboard/home.html")

# # Vue principale du dashboard déplacée vers index.py (voir dashboard/views/index.py)

# @login_required
# def dashboard_stats_view(request):
#     """
#     Statistiques globales de l'utilisateur (total dons, engagements…)
#     """
#     user = request.user

#     # Agrégation du total des dons (compatible manager custom ou fallback)
#     if hasattr(Don.objects, "aggregate_total_amount"):
#         donation_total = Don.objects.filter(user=user).aggregate_total_amount()
#     else:
#         donation_total = Don.objects.filter(user=user).aggregate(total=Sum("montant"))["total"]

#     engagement_count = Engagement.objects.filter(user=user).count()

#     summary_cards = [
#         {"label": _("Total des dons"), "value": f"{donation_total or 0} FCFA", "color": "primary"},
#         {"label": _("Engagements"),    "value": engagement_count,              "color": "success"},
#     ]

#     context = {
#         "donation_total": donation_total,
#         "engagement_count": engagement_count,
#         "summary_cards": summary_cards,
#     }
#     return render(request, "dashboard/stats.html", context)

# @login_required
# def engagements_list_view(request):
#     """
#     Liste paginée des engagements de l'utilisateur connecté.
#     """
#     engagements = Engagement.objects.filter(user=request.user).order_by("-created_at", "-date")
#     paginator = Paginator(engagements, 10)
#     page_number = request.GET.get("page")
#     engagements_page = paginator.get_page(page_number)

#     return render(request, "dashboard/engagements_list.html", {
#         "engagements": engagements_page,
#         "page_title": _("Mes engagements"),
#     })

# @login_required
# def dons_list_view(request):
#     """
#     Liste paginée des dons de l'utilisateur connecté.
#     """
#     dons = Don.objects.filter(user=request.user).order_by("-date")
#     paginator = Paginator(dons, 10)
#     page_number = request.GET.get("page")
#     dons_page = paginator.get_page(page_number)

#     return render(request, "dashboard/dons_list.html", {
#         "dons": dons_page,
#         "page_title": _("Mes dons"),
#     })

# @login_required
# def recent_activity_logs_view(request):
#     """
#     Affiche les dernières activités de l'utilisateur connecté.
#     """
#     logs = UserActivityLog.objects.filter(user=request.user)[:10]
#     return render(request, "dashboard/recent_logs.html", {
#         "logs": logs,
#         "page_title": _("Activités récentes"),
#     })




# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render
# from django.core.paginator import Paginator
# from django.utils.translation import gettext_lazy as _
# from django.db.models import Sum

# from social.models import Don, Engagement  # Utilisation cohérente des modèles Don et Engagement

# def home(request):
#     """
#     Page d'accueil du tableau de bord (publique ou protégée selon le design).
#     """
#     return render(request, "dashboard/home.html")

# # Vue principale du tableau de bord déplacée vers index.py pour éviter les conflits de nom.
# # (voir dashboard/views/index.py pour la fonction dashboard_index_view)

# @login_required
# def dashboard_stats_view(request):
#     """
#     Vue affichant les statistiques globales de l'utilisateur (total des dons, engagements, etc.).
#     """
#     user = request.user

#     # Vérifie si la méthode d’agrégation personnalisée existe sur le manager Don.objects
#     if hasattr(Don.objects, "aggregate_total_amount"):
#         donation_total = Don.objects.filter(user=user).aggregate_total_amount()
#     else:
#         # Solution de repli : somme des montants des dons de l'utilisateur
#         donation_total = Don.objects.filter(user=user).aggregate(total=Sum("amount"))["total"]

#     engagement_count = Engagement.objects.filter(user=user).count()

#     # Prépare les données pour les cartes de synthèse affichées dans le template
#     summary_cards = [
#         {"label": "Total des dons", "value": f"{donation_total or 0} €", "color": "primary"},
#         {"label": "Engagements",    "value": engagement_count,          "color": "success"},
#     ]

#     context = {
#         "donation_total": donation_total,
#         "engagement_count": engagement_count,
#         "summary_cards": summary_cards,
#     }
#     return render(request, "dashboard/stats.html", context)

# @login_required
# def engagements_list_view(request):
#     """
#     Liste paginée des engagements de l'utilisateur connecté.
#     """
#     engagements = Engagement.objects.filter(user=request.user).order_by("-created_at")
#     paginator = Paginator(engagements, 10)
#     page_number = request.GET.get("page")
#     engagements_page = paginator.get_page(page_number)

#     return render(request, "dashboard/engagements_list.html", {
#         "engagements": engagements_page,
#         "page_title": _("Mes engagements"),
#     })

# @login_required
# def dons_list_view(request):
#     """
#     Liste paginée des dons de l'utilisateur connecté.
#     """
#     dons = Don.objects.filter(user=request.user).order_by("-date")
#     paginator = Paginator(dons, 10)
#     page_number = request.GET.get("page")
#     dons_page = paginator.get_page(page_number)

#     return render(request, "dashboard/dons_list.html", {
#         "dons": dons_page,
#         "page_title": _("Mes dons"),
#     })
