# dashboard/views/dashboard_hub.py
from __future__ import annotations

from datetime import timedelta
from typing import Any, Dict, List, Optional, Tuple

from django.apps import apps
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext_lazy as _

from dashboard.views.utils import (
    iter_user_profiles,
    detect_profile_kind,
    detect_profile_status,
)


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


def _get_range_days(request: HttpRequest) -> Tuple[str, int]:
    raw = (request.GET.get("range") or "30").strip()
    if raw not in ("7", "30", "90"):
        raw = "30"
    return raw, int(raw)


def _cache_seconds() -> int:
    try:
        return int(getattr(settings, "DASHBOARD_HUB_CACHE_SECONDS", 60) or 0)
    except Exception:
        return 60


def _safe_next(request: HttpRequest, fallback_url_name: str = "dashboard:hub") -> str:
    nxt = (request.POST.get("next") or request.GET.get("next") or "").strip()
    if nxt and url_has_allowed_host_and_scheme(
        url=nxt,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return nxt
    try:
        return reverse(fallback_url_name)
    except Exception:
        return "/"


def _try_reverse(name: str) -> str:
    try:
        return reverse(name)
    except Exception:
        return ""


def _pick_user_field(model, candidates: Tuple[str, ...]) -> Optional[str]:
    for f in candidates:
        if _model_has_field(model, f):
            return f
    return None


def _pick_amount_field(model) -> Optional[str]:
    return _pick_user_field(model, ("montant", "amount", "total_amount", "total", "value"))


def _sum_amount(qs, amount_field: Optional[str]) -> int:
    if not amount_field:
        return 0
    try:
        val = qs.aggregate(s=Sum(amount_field)).get("s")
        return int(val or 0)
    except Exception:
        return 0


def _date_labels(days: int) -> Tuple[List[str], List[str]]:
    today = timezone.localdate()
    labels: List[str] = []
    keys: List[str] = []
    for i in range(days - 1, -1, -1):
        d = today - timedelta(days=i)
        labels.append(d.strftime("%d/%m"))
        keys.append(str(d))
    return labels, keys


def _counts_by_day(qs, date_field: str, days: int) -> Dict[str, int]:
    start_dt = timezone.now() - timedelta(days=days - 1)
    try:
        agg = (
            qs.filter(**{f"{date_field}__gte": start_dt})
            .annotate(day=TruncDate(date_field))
            .values("day")
            .annotate(c=Count("id"))
            .order_by("day")
        )
        out: Dict[str, int] = {}
        for row in agg:
            day = row.get("day")
            if day:
                out[str(day)] = int(row.get("c") or 0)
        return out
    except Exception:
        out: Dict[str, int] = {}
        for obj in qs.filter(**{f"{date_field}__gte": start_dt}):
            dt = getattr(obj, date_field, None)
            if not dt:
                continue
            key = str(timezone.localdate(dt))
            out[key] = out.get(key, 0) + 1
        return out


def _profile_state(user) -> Dict[str, Any]:
    profiles = []
    try:
        profiles = iter_user_profiles(user)
    except Exception:
        profiles = []

    pending = []
    rejected = []
    approved = []

    for p in profiles:
        st = detect_profile_status(p)
        kind = detect_profile_kind(p)
        row = {"kind": kind, "status": st, "model": p.__class__.__name__}
        if st == "pending":
            pending.append(row)
        elif st == "rejected":
            rejected.append(row)
        elif st == "approved":
            approved.append(row)

    def label_kind(k: str) -> str:
        if k == "social":
            return str(_("Social"))
        if k == "economic":
            return str(_("Économique"))
        return str(_("Général"))

    pending_kinds = sorted({label_kind(r["kind"]) for r in pending})
    rejected_kinds = sorted({label_kind(r["kind"]) for r in rejected})

    show_banner = bool(pending or rejected)
    level = "warning" if pending else ("danger" if rejected else "info")

    banner_title = ""
    banner_text = ""

    if rejected:
        banner_title = _("Accès partiellement limité sur le dashboard")
        banner_text = _(
            "Un ou plusieurs profils ont été refusés. Vous pouvez continuer à utiliser le site, "
            "mais certaines sections du dashboard peuvent rester indisponibles."
        )
    elif pending:
        banner_title = _("Validation en cours")
        banner_text = _(
            "Votre compte fonctionne normalement. Certaines sections du dashboard peuvent être limitées "
            "tant que la validation n’est pas terminée."
        )

    if rejected:
        dashboard_profile_status = "rejected"
    elif pending:
        dashboard_profile_status = "pending"
    else:
        dashboard_profile_status = "approved"

    return {
        "profiles_count": len(profiles),
        "pending": pending,
        "rejected": rejected,
        "approved": approved,
        "show_banner": show_banner,
        "banner_level": level,
        "banner_title": banner_title,
        "banner_text": banner_text,
        "pending_kinds": pending_kinds,
        "rejected_kinds": rejected_kinds,
        "dashboard_profile_status": dashboard_profile_status,
    }


def _economic_gate_flags(user) -> Dict[str, Any]:
    profiles = []
    try:
        profiles = iter_user_profiles(user)
    except Exception:
        profiles = []

    eco = None
    for p in profiles:
        if detect_profile_kind(p) == "economic":
            eco = p
            break

    can_vendor = bool(getattr(user, "is_vendor", False) or getattr(user, "vendor_enabled", False))
    can_b2b = bool(
        getattr(user, "is_b2b", False)
        or getattr(user, "b2b_enabled", False)
        or getattr(user, "is_company_user", False)
    )

    vendor_approved = False
    b2b_approved = False

    if eco:
        can_vendor |= bool(
            getattr(eco, "is_vendor", False)
            or getattr(eco, "can_vendor", False)
            or getattr(eco, "vendor_active", False)
        )
        can_b2b |= bool(
            getattr(eco, "is_b2b", False)
            or getattr(eco, "can_b2b", False)
            or getattr(eco, "company_active", False)
        )

        vs = str(getattr(eco, "vendor_status", "") or "").upper().strip()
        cs = str(getattr(eco, "b2b_status", "") or getattr(eco, "company_status", "") or "").upper().strip()

        if vs in {"APPROVED", "ACTIVE", "VALIDATED"}:
            vendor_approved = True
        if cs in {"APPROVED", "ACTIVE", "VALIDATED"}:
            b2b_approved = True

        if not vs and detect_profile_status(eco) == "approved":
            vendor_approved |= bool(can_vendor)
        if not cs and detect_profile_status(eco) == "approved":
            b2b_approved |= bool(can_b2b)

    return {
        "can_vendor": bool(can_vendor),
        "can_b2b": bool(can_b2b),
        "vendor_approved": bool(vendor_approved),
        "b2b_approved": bool(b2b_approved),
    }


@login_required
def hub_view(request: HttpRequest) -> HttpResponse:
    user = request.user
    range_key, days = _get_range_days(request)
    next_url = _safe_next(request, fallback_url_name="dashboard:hub")

    auth_pole = (request.GET.get("context") or request.GET.get("pole") or "generic").strip().lower()
    if auth_pole not in ("social", "economic", "generic"):
        auth_pole = "generic"

    ttl = _cache_seconds()
    cache_key = f"dash:hub:{user.id}:r{range_key}"

    is_admin_user = bool(getattr(user, "is_superuser", False))
    is_staff_user = bool(getattr(user, "is_staff", False))

    if ttl > 0:
        cached = cache.get(cache_key)
        if isinstance(cached, dict):
            ctx = dict(cached)
            ctx["next_url"] = next_url
            ctx["auth_pole"] = auth_pole
            ctx["is_admin_user"] = is_admin_user
            ctx["is_staff_user"] = is_staff_user
            return render(request, "dashboard/dashboard_hub.html", ctx)

    Note = _safe_model("dashboard", "DashboardNote")
    Donation = _safe_model("donations", "Donation") or _safe_model("social", "Donation")
    Order = _safe_model("ecommerce", "Order")

    kpi_notes_count = 0
    if Note:
        try:
            kpi_notes_count = Note.objects.filter(user=user).count()
        except Exception:
            kpi_notes_count = 0

    kpi_donations_count = 0
    kpi_donations_total = 0
    if Donation:
        try:
            user_field = _pick_user_field(Donation, ("user", "author", "donor"))
            qs = Donation.objects.all()
            if user_field:
                qs = qs.filter(**{user_field: user})
            kpi_donations_count = qs.count()
            amount_field = _pick_amount_field(Donation)
            kpi_donations_total = _sum_amount(qs, amount_field)
        except Exception:
            kpi_donations_count = 0
            kpi_donations_total = 0

    kpi_orders_count = 0
    if Order:
        try:
            user_field = _pick_user_field(Order, ("user", "customer", "buyer", "author"))
            qs = Order.objects.all()
            if user_field:
                qs = qs.filter(**{user_field: user})
            kpi_orders_count = qs.count()
        except Exception:
            kpi_orders_count = 0

    labels, keys = _date_labels(days)
    values = [0] * len(labels)
    day_counts: Dict[str, int] = {}

    if Note and _model_has_field(Note, "created_at"):
        try:
            c = _counts_by_day(Note.objects.filter(user=user), "created_at", days)
            for k, v in c.items():
                day_counts[k] = day_counts.get(k, 0) + v
        except Exception:
            pass

    if Donation and _model_has_field(Donation, "created_at"):
        try:
            user_field = _pick_user_field(Donation, ("user", "author", "donor"))
            qs = Donation.objects.all()
            if user_field:
                qs = qs.filter(**{user_field: user})
            c = _counts_by_day(qs, "created_at", days)
            for k, v in c.items():
                day_counts[k] = day_counts.get(k, 0) + v
        except Exception:
            pass

    if Order and _model_has_field(Order, "created_at"):
        try:
            user_field = _pick_user_field(Order, ("user", "customer", "buyer", "author"))
            qs = Order.objects.all()
            if user_field:
                qs = qs.filter(**{user_field: user})
            c = _counts_by_day(qs, "created_at", days)
            for k, v in c.items():
                day_counts[k] = day_counts.get(k, 0) + v
        except Exception:
            pass

    for idx, key in enumerate(keys):
        values[idx] = int(day_counts.get(key, 0))

    pstate = _profile_state(user)
    econ_flags = _economic_gate_flags(user)

    can_vendor = bool(econ_flags["can_vendor"])
    can_b2b = bool(econ_flags["can_b2b"])
    vendor_approved = bool(econ_flags["vendor_approved"])
    b2b_approved = bool(econ_flags["b2b_approved"])

    vendor_ok = bool(can_vendor and vendor_approved)
    b2b_ok = bool(can_b2b and b2b_approved)

    can_social = True
    can_formations = True

    can_vendor_space = bool(is_admin_user or user.has_perm("dashboard.access_vendor_space") or vendor_ok)
    can_b2b_space = bool(is_admin_user or user.has_perm("dashboard.access_b2b_space") or b2b_ok)
    can_social_space = bool(is_admin_user or user.has_perm("dashboard.access_social_space") or can_social)
    can_formations_space = bool(is_admin_user or user.has_perm("dashboard.access_formations_space") or can_formations)
    can_admin_area = bool(
        is_admin_user
        or user.has_perm("dashboard.access_admin_area")
        or user.has_perm("dashboard.validate_profiles")
    )

    cards = [
        {"label": _("Dons"), "value": kpi_donations_count, "icon": "❤️", "help": _("Nombre total de dons")},
        {"label": _("Montant donné"), "value": kpi_donations_total, "icon": "💰", "help": _("Somme cumulée")},
        {"label": _("Commandes"), "value": kpi_orders_count, "icon": "🧾", "help": _("E-commerce / achats")},
        {"label": _("Notes"), "value": kpi_notes_count, "icon": "📝", "help": _("Notes personnelles")},
    ]

    ctx = {
        "page_title": _("Hub"),
        "next_url": next_url,
        "range_key": range_key,
        "auth_pole": auth_pole,

        "is_admin_user": is_admin_user,
        "is_staff_user": is_staff_user,

        "cards": cards,

        "can_vendor": can_vendor,
        "can_b2b": can_b2b,
        "vendor_approved": vendor_approved,
        "b2b_approved": b2b_approved,

        "can_social": can_social,
        "can_formations": can_formations,

        "can_vendor_space": can_vendor_space,
        "can_b2b_space": can_b2b_space,
        "can_social_space": can_social_space,
        "can_formations_space": can_formations_space,
        "can_admin_area": can_admin_area,

        "dashboard_profile_status": pstate["dashboard_profile_status"],
        "show_pending_banner": pstate["show_banner"],
        "pending_banner_level": pstate["banner_level"],
        "pending_banner_title": pstate["banner_title"],
        "pending_banner_text": pstate["banner_text"],
        "pending_kinds": pstate["pending_kinds"],
        "rejected_kinds": pstate["rejected_kinds"],
        "account_pending_url": _try_reverse("dashboard:account_pending"),

        "chart_labels": labels,
        "chart_values": values,
    }

    if ttl > 0:
        cache.set(cache_key, ctx, ttl)

    return render(request, "dashboard/dashboard_hub.html", ctx)





# # dashboard/views/dashboard_hub.py
# from __future__ import annotations

# from datetime import timedelta
# from typing import Any, Dict, List, Optional, Tuple

# from django.apps import apps
# from django.conf import settings
# from django.contrib.auth.decorators import login_required
# from django.core.cache import cache
# from django.db.models import Count, Sum
# from django.db.models.functions import TruncDate
# from django.http import HttpRequest, HttpResponse
# from django.shortcuts import render
# from django.urls import NoReverseMatch, reverse
# from django.utils import timezone
# from django.utils.http import url_has_allowed_host_and_scheme
# from django.utils.translation import gettext_lazy as _

# from dashboard.views.utils import (
#     iter_user_profiles,
#     detect_profile_kind,
#     detect_profile_status,
# )


# # ======================================================
# # Helpers (safe)
# # ======================================================
# def _safe_model(app_label: str, model_name: str):
#     try:
#         return apps.get_model(app_label, model_name)
#     except Exception:
#         return None


# def _model_has_field(model, field_name: str) -> bool:
#     try:
#         model._meta.get_field(field_name)
#         return True
#     except Exception:
#         return False


# def _get_range_days(request: HttpRequest) -> Tuple[str, int]:
#     raw = (request.GET.get("range") or "30").strip()
#     if raw not in ("7", "30", "90"):
#         raw = "30"
#     return raw, int(raw)


# def _cache_seconds() -> int:
#     try:
#         return int(getattr(settings, "DASHBOARD_HUB_CACHE_SECONDS", 60) or 0)
#     except Exception:
#         return 60


# def _safe_next(request: HttpRequest, fallback_url_name: str = "dashboard:hub") -> str:
#     nxt = (request.POST.get("next") or request.GET.get("next") or "").strip()
#     if nxt and url_has_allowed_host_and_scheme(
#         url=nxt,
#         allowed_hosts={request.get_host()},
#         require_https=request.is_secure(),
#     ):
#         return nxt
#     try:
#         return reverse(fallback_url_name)
#     except Exception:
#         return "/"


# def _try_reverse(name: str) -> str:
#     try:
#         return reverse(name)
#     except Exception:
#         return ""


# def _pick_user_field(model, candidates: Tuple[str, ...]) -> Optional[str]:
#     for f in candidates:
#         if _model_has_field(model, f):
#             return f
#     return None


# def _pick_amount_field(model) -> Optional[str]:
#     return _pick_user_field(model, ("montant", "amount", "total_amount", "total", "value"))


# def _sum_amount(qs, amount_field: Optional[str]) -> int:
#     if not amount_field:
#         return 0
#     try:
#         val = qs.aggregate(s=Sum(amount_field)).get("s")
#         return int(val or 0)
#     except Exception:
#         return 0


# def _date_labels(days: int) -> Tuple[List[str], List[str]]:
#     today = timezone.localdate()
#     labels: List[str] = []
#     keys: List[str] = []
#     for i in range(days - 1, -1, -1):
#         d = today - timedelta(days=i)
#         labels.append(d.strftime("%d/%m"))
#         keys.append(str(d))
#     return labels, keys


# def _counts_by_day(qs, date_field: str, days: int) -> Dict[str, int]:
#     start_dt = timezone.now() - timedelta(days=days - 1)
#     try:
#         agg = (
#             qs.filter(**{f"{date_field}__gte": start_dt})
#             .annotate(day=TruncDate(date_field))
#             .values("day")
#             .annotate(c=Count("id"))
#             .order_by("day")
#         )
#         out: Dict[str, int] = {}
#         for row in agg:
#             day = row.get("day")
#             if day:
#                 out[str(day)] = int(row.get("c") or 0)
#         return out
#     except Exception:
#         out: Dict[str, int] = {}
#         for obj in qs.filter(**{f"{date_field}__gte": start_dt}):
#             dt = getattr(obj, date_field, None)
#             if not dt:
#                 continue
#             key = str(timezone.localdate(dt))
#             out[key] = out.get(key, 0) + 1
#         return out


# def _profile_state(user) -> Dict[str, Any]:
#     """
#     IMPORTANT:
#     - pending/rejected n'empêche pas la navigation.
#     - on renvoie juste des infos pour banner / UX.
#     """
#     profiles = []
#     try:
#         profiles = iter_user_profiles(user)
#     except Exception:
#         profiles = []

#     pending = []
#     rejected = []
#     approved = []

#     for p in profiles:
#         st = detect_profile_status(p)
#         kind = detect_profile_kind(p)
#         row = {"kind": kind, "status": st, "model": p.__class__.__name__}
#         if st == "pending":
#             pending.append(row)
#         elif st == "rejected":
#             rejected.append(row)
#         elif st == "approved":
#             approved.append(row)

#     def label_kind(k: str) -> str:
#         if k == "social":
#             return str(_("Social"))
#         if k == "economic":
#             return str(_("Économique"))
#         return str(_("Général"))

#     pending_kinds = sorted({label_kind(r["kind"]) for r in pending})
#     rejected_kinds = sorted({label_kind(r["kind"]) for r in rejected})

#     show_banner = bool(pending or rejected)
#     level = "warning" if pending else ("danger" if rejected else "info")

#     banner_title = ""
#     banner_text = ""

#     if rejected:
#         banner_title = _("Accès partiellement limité sur le dashboard")
#         banner_text = _("Un ou plusieurs profils ont été refusés. Vous pouvez continuer à utiliser le site, mais certaines sections du dashboard peuvent rester indisponibles.")
#     elif pending:
#         banner_title = _("Validation en cours")
#         banner_text = _("Votre compte fonctionne normalement. Certaines sections du dashboard peuvent être limitées tant que la validation n’est pas terminée.")

#     return {
#         "profiles_count": len(profiles),
#         "pending": pending,
#         "rejected": rejected,
#         "approved": approved,
#         "show_banner": show_banner,
#         "banner_level": level,
#         "banner_title": banner_title,
#         "banner_text": banner_text,
#         "pending_kinds": pending_kinds,
#         "rejected_kinds": rejected_kinds,
#     }


# def _economic_gate_flags(user) -> Dict[str, Any]:
#     """
#     Flags UI seulement (le vrai blocage se fait dans les vues vendor/b2b via guards).
#     """
#     profiles = []
#     try:
#         profiles = iter_user_profiles(user)
#     except Exception:
#         profiles = []

#     eco = None
#     for p in profiles:
#         if detect_profile_kind(p) == "economic":
#             eco = p
#             break

#     can_vendor = bool(getattr(user, "is_vendor", False) or getattr(user, "vendor_enabled", False))
#     can_b2b = bool(getattr(user, "is_b2b", False) or getattr(user, "b2b_enabled", False) or getattr(user, "is_company_user", False))

#     vendor_approved = False
#     b2b_approved = False

#     if eco:
#         can_vendor |= bool(getattr(eco, "is_vendor", False) or getattr(eco, "can_vendor", False) or getattr(eco, "vendor_active", False))
#         can_b2b |= bool(getattr(eco, "is_b2b", False) or getattr(eco, "can_b2b", False) or getattr(eco, "company_active", False))

#         vs = str(getattr(eco, "vendor_status", "") or "").upper().strip()
#         cs = str(getattr(eco, "b2b_status", "") or getattr(eco, "company_status", "") or "").upper().strip()

#         if vs in {"APPROVED", "ACTIVE", "VALIDATED"}:
#             vendor_approved = True
#         if cs in {"APPROVED", "ACTIVE", "VALIDATED"}:
#             b2b_approved = True

#         # fallback si ton modèle n'a pas vendor_status/b2b_status
#         if not vs and detect_profile_status(eco) == "approved":
#             vendor_approved |= bool(can_vendor)
#         if not cs and detect_profile_status(eco) == "approved":
#             b2b_approved |= bool(can_b2b)

#     return {
#         "can_vendor": bool(can_vendor),
#         "can_b2b": bool(can_b2b),
#         "vendor_approved": bool(vendor_approved),
#         "b2b_approved": bool(b2b_approved),
#     }

# # ======================================================
# # View (PROD)
# # ======================================================
# @login_required 
# def hub_view(request: HttpRequest) -> HttpResponse:
#     """
#     Hub Dashboard (router-friendly).
#     Template: templates/dashboard/dashboard_hub.html (et non home.html).
#     """
#     user = request.user
#     range_key, days = _get_range_days(request)
#     next_url = _safe_next(request, fallback_url_name="dashboard:hub")

#     ttl = _cache_seconds()
#     cache_key = f"dash:hub:{user.id}:r{range_key}"

#     if ttl > 0:
#         cached = cache.get(cache_key)
#         if isinstance(cached, dict):
#             ctx = dict(cached)
#             ctx["next_url"] = next_url  # évite un next_url “stale”
#             return render(request, "dashboard/dashboard_hub.html", ctx)

#     # -------- Models safe --------
#     Note = _safe_model("dashboard", "DashboardNote")
#     Donation = _safe_model("donations", "Donation") or _safe_model("social", "Donation")
#     Order = _safe_model("ecommerce", "Order")

#     # -------- KPIs --------
#     kpi_notes_count = 0
#     if Note:
#         try:
#             kpi_notes_count = Note.objects.filter(user=user).count()
#         except Exception:
#             kpi_notes_count = 0

#     kpi_donations_count = 0
#     kpi_donations_total = 0
#     if Donation:
#         try:
#             user_field = _pick_user_field(Donation, ("user", "author", "donor"))
#             qs = Donation.objects.all()
#             if user_field:
#                 qs = qs.filter(**{user_field: user})
#             kpi_donations_count = qs.count()

#             amount_field = _pick_amount_field(Donation)
#             kpi_donations_total = _sum_amount(qs, amount_field)
#         except Exception:
#             kpi_donations_count = 0
#             kpi_donations_total = 0

#     kpi_orders_count = 0
#     if Order:
#         try:
#             user_field = _pick_user_field(Order, ("user", "customer", "buyer", "author"))
#             qs = Order.objects.all()
#             if user_field:
#                 qs = qs.filter(**{user_field: user})
#             kpi_orders_count = qs.count()
#         except Exception:
#             kpi_orders_count = 0

#     # -------- Chart (optionnel, si tu l'affiches plus tard) --------
#     labels, keys = _date_labels(days)
#     values = [0] * len(labels)
#     day_counts: Dict[str, int] = {}

#     if Note and _model_has_field(Note, "created_at"):
#         try:
#             c = _counts_by_day(Note.objects.filter(user=user), "created_at", days)
#             for k, v in c.items():
#                 day_counts[k] = day_counts.get(k, 0) + v
#         except Exception:
#             pass

#     if Donation and _model_has_field(Donation, "created_at"):
#         try:
#             user_field = _pick_user_field(Donation, ("user", "author", "donor"))
#             qs = Donation.objects.all()
#             if user_field:
#                 qs = qs.filter(**{user_field: user})
#             c = _counts_by_day(qs, "created_at", days)
#             for k, v in c.items():
#                 day_counts[k] = day_counts.get(k, 0) + v
#         except Exception:
#             pass

#     if Order and _model_has_field(Order, "created_at"):
#         try:
#             user_field = _pick_user_field(Order, ("user", "customer", "buyer", "author"))
#             qs = Order.objects.all()
#             if user_field:
#                 qs = qs.filter(**{user_field: user})
#             c = _counts_by_day(qs, "created_at", days)
#             for k, v in c.items():
#                 day_counts[k] = day_counts.get(k, 0) + v
#         except Exception:
#             pass

#     for idx, key in enumerate(keys):
#         values[idx] = int(day_counts.get(key, 0))

#     # -------- UX : profil/pending banner (sans blocage) --------
#     pstate = _profile_state(user)
#     econ_flags = _economic_gate_flags(user)

#     # -------- Cards hub --------
#     # (ton partial _stats_cards.html doit supporter label/value/icon/help)
#     cards = [
#         {"label": _("Dons"), "value": kpi_donations_count, "icon": "❤️", "help": _("Nombre total de dons")},
#         {"label": _("Montant donné"), "value": kpi_donations_total, "icon": "💰", "help": _("Somme cumulée")},
#         {"label": _("Commandes"), "value": kpi_orders_count, "icon": "🧾", "help": _("E-commerce / achats")},
#         {"label": _("Notes"), "value": kpi_notes_count, "icon": "📝", "help": _("Notes personnelles")},
#     ]

#     ctx = {
#         "page_title": _("Hub"),
#         "next_url": next_url,
#         "range_key": range_key,

#         # cards + permissions UI
#         "cards": cards,
#         "can_vendor": econ_flags["can_vendor"] and econ_flags["vendor_approved"],
#         "can_b2b": econ_flags["can_b2b"] and econ_flags["b2b_approved"],
#         "can_social": True,  # social accessible (pas bloqué par pending)

#         # pending banner
#         "show_pending_banner": pstate["show_banner"],
#         "pending_banner_level": pstate["banner_level"],   # warning / danger
#         "pending_banner_title": pstate["banner_title"],
#         "pending_banner_text": pstate["banner_text"],
#         "pending_kinds": pstate["pending_kinds"],
#         "rejected_kinds": pstate["rejected_kinds"],
#         "account_pending_url": _try_reverse("dashboard:account_pending"),

#         # chart (si tu l'utilises)
#         "chart_labels": labels,
#         "chart_values": values,
#     }

#     if ttl > 0:
#         cache.set(cache_key, ctx, ttl)

#     return render(request, "dashboard/dashboard_hub.html", ctx)








# # dashboard/views/dashboard_hub.py
# from __future__ import annotations

# import json
# from datetime import timedelta
# from typing import Any, Dict, List, Optional, Tuple

# from django.apps import apps
# from django.conf import settings
# from django.contrib.auth.decorators import login_required
# from django.core.cache import cache
# from django.db.models import Count, Sum
# from django.db.models.functions import TruncDate
# from django.http import HttpRequest, HttpResponse
# from django.shortcuts import render
# from django.urls import reverse
# from django.utils import timezone
# from django.utils.http import url_has_allowed_host_and_scheme
# from django.utils.translation import gettext_lazy as _


# # ======================================================
# # Helpers (safe)
# # ======================================================
# def _safe_model(app_label: str, model_name: str):
#     """
#     Retourne le modèle si présent, sinon None (no fail).
#     """
#     try:
#         return apps.get_model(app_label, model_name)
#     except Exception:
#         return None


# def _model_has_field(model, field_name: str) -> bool:
#     try:
#         model._meta.get_field(field_name)
#         return True
#     except Exception:
#         return False


# def _get_range_days(request: HttpRequest) -> Tuple[str, int]:
#     """
#     Range choisi via ?range=7|30|90 (default 30)
#     Retourne (range_key, days)
#     """
#     raw = (request.GET.get("range") or "30").strip()
#     if raw not in ("7", "30", "90"):
#         raw = "30"
#     return raw, int(raw)


# def _cache_seconds() -> int:
#     """
#     TTL cache hub. Config: DASHBOARD_HUB_CACHE_SECONDS
#     """
#     try:
#         return int(getattr(settings, "DASHBOARD_HUB_CACHE_SECONDS", 60) or 0)
#     except Exception:
#         return 60


# def _safe_next(request: HttpRequest, fallback_url_name: str = "dashboard:hub") -> str:
#     """
#     next sécurisé (évite open redirect).
#     """
#     nxt = (request.POST.get("next") or request.GET.get("next") or "").strip()
#     if nxt and url_has_allowed_host_and_scheme(
#         url=nxt,
#         allowed_hosts={request.get_host()},
#         require_https=request.is_secure(),
#     ):
#         return nxt
#     try:
#         return reverse(fallback_url_name)
#     except Exception:
#         return "/"


# def _date_labels(days: int) -> Tuple[List[str], List[str]]:
#     """
#     Retourne:
#       - labels: ["JJ/MM", ...] (days éléments)
#       - keys:   ["YYYY-MM-DD", ...] correspondants (même index)
#     """
#     today = timezone.localdate()
#     labels: List[str] = []
#     keys: List[str] = []

#     for i in range(days - 1, -1, -1):
#         d = today - timedelta(days=i)
#         labels.append(d.strftime("%d/%m"))
#         keys.append(str(d))  # YYYY-MM-DD

#     return labels, keys


# def _counts_by_day(qs, date_field: str, days: int) -> Dict[str, int]:
#     """
#     Groupe un queryset par jour sur 'days' derniers jours.
#     Retour: {"YYYY-MM-DD": count}
#     """
#     start_dt = timezone.now() - timedelta(days=days - 1)

#     # annotate DB (rapide)
#     try:
#         agg = (
#             qs.filter(**{f"{date_field}__gte": start_dt})
#             .annotate(day=TruncDate(date_field))
#             .values("day")
#             .annotate(c=Count("id"))
#             .order_by("day")
#         )
#         out: Dict[str, int] = {}
#         for row in agg:
#             day = row.get("day")
#             if day:
#                 out[str(day)] = int(row.get("c") or 0)
#         return out
#     except Exception:
#         # fallback python
#         out: Dict[str, int] = {}
#         for obj in qs.filter(**{f"{date_field}__gte": start_dt}):
#             dt = getattr(obj, date_field, None)
#             if not dt:
#                 continue
#             key = str(timezone.localdate(dt))
#             out[key] = out.get(key, 0) + 1
#         return out


# def _pick_user_field(model, candidates: Tuple[str, ...]) -> Optional[str]:
#     for f in candidates:
#         if _model_has_field(model, f):
#             return f
#     return None


# def _pick_amount_field(model) -> Optional[str]:
#     return _pick_user_field(model, ("montant", "amount", "total_amount", "total", "value"))


# def _sum_amount(qs, amount_field: Optional[str]) -> int:
#     if not amount_field:
#         return 0
#     try:
#         val = qs.aggregate(s=Sum(amount_field)).get("s")
#         return int(val or 0)
#     except Exception:
#         return 0


# def _get_profile_status(user) -> str:
#     """
#     Essaye de récupérer un status de profil (si ton projet le porte).
#     """
#     candidates = ("userprofile", "profile", "social_profile", "economic_profile", "usereconomicprofile")
#     for attr in candidates:
#         try:
#             p = getattr(user, attr, None)
#             if not p:
#                 continue
#             for st_field in ("status", "validation_status"):
#                 if hasattr(p, st_field):
#                     st = getattr(p, st_field, "") or ""
#                     if st:
#                         return str(st)
#         except Exception:
#             continue
#     return ""


# def _build_recent_activity(user) -> List[Dict[str, Any]]:
#     """
#     1) Si UserActivityLog existe → on prend ça.
#     2) Sinon fallback notes/donations/orders.
#     """
#     items: List[Dict[str, Any]] = []

#     Log = _safe_model("dashboard", "UserActivityLog")
#     if Log:
#         try:
#             qs = Log.objects.filter(user=user).order_by("-id")[:10]
#             for l in qs:
#                 items.append({
#                     "date": getattr(l, "created_at", None) or getattr(l, "date", None) or timezone.now(),
#                     "kind": getattr(l, "kind", _("Action")),
#                     "label": getattr(l, "label", "") or str(l),
#                     "status": getattr(l, "status", "info") or "info",
#                 })
#             return items
#         except Exception:
#             items = []

#     Note = _safe_model("dashboard", "DashboardNote")
#     if Note:
#         try:
#             qs = Note.objects.filter(user=user).order_by("-updated_at", "-id")[:5]
#             for n in qs:
#                 title = getattr(n, "title", None) or _("Note")
#                 items.append({
#                     "date": getattr(n, "updated_at", None) or getattr(n, "created_at", None) or timezone.now(),
#                     "kind": _("Note"),
#                     "label": str(title),
#                     "status": "info",
#                 })
#         except Exception:
#             pass

#     Donation = _safe_model("donations", "Donation") or _safe_model("social", "Donation")
#     if Donation:
#         try:
#             user_field = _pick_user_field(Donation, ("user", "author", "donor"))
#             qs = Donation.objects.all()
#             if user_field:
#                 qs = qs.filter(**{user_field: user})

#             order_field = "created_at" if _model_has_field(Donation, "created_at") else "id"
#             qs = qs.order_by(f"-{order_field}")[:5]

#             amount_field = _pick_amount_field(Donation)

#             for d in qs:
#                 amount = getattr(d, amount_field, None) if amount_field else None
#                 label = _("Donation")
#                 if amount is not None:
#                     label = _("Donation: %(amount)s") % {"amount": amount}

#                 status_val = getattr(d, "status", None) or getattr(d, "payment_status", None)
#                 status = "success" if str(status_val).lower() in ("paid", "success", "completed", "succeeded") else "info"

#                 items.append({
#                     "date": getattr(d, "created_at", None) or getattr(d, "updated_at", None) or timezone.now(),
#                     "kind": _("Donation"),
#                     "label": str(label),
#                     "status": status,
#                 })
#         except Exception:
#             pass

#     Order = _safe_model("ecommerce", "Order")
#     if Order:
#         try:
#             user_field = _pick_user_field(Order, ("user", "customer", "buyer", "author"))
#             qs = Order.objects.all()
#             if user_field:
#                 qs = qs.filter(**{user_field: user})

#             order_field = "created_at" if _model_has_field(Order, "created_at") else "id"
#             qs = qs.order_by(f"-{order_field}")[:5]

#             for o in qs:
#                 code = getattr(o, "uuid", None) or getattr(o, "reference", None) or getattr(o, "id", None)
#                 label = _("Commande #%(code)s") % {"code": code}

#                 status_val = getattr(o, "status", None) or getattr(o, "payment_status", None)
#                 status = "success" if str(status_val).lower() in ("paid", "success", "completed", "succeeded") else "info"

#                 items.append({
#                     "date": getattr(o, "created_at", None) or getattr(o, "updated_at", None) or timezone.now(),
#                     "kind": _("Commande"),
#                     "label": str(label),
#                     "status": status,
#                 })
#         except Exception:
#             pass

#     items.sort(key=lambda x: x.get("date") or timezone.now(), reverse=True)
#     return items[:10]


# # ======================================================
# # View (PROD)
# # ======================================================
# @login_required
# def hub_view(request: HttpRequest) -> HttpResponse:
#     """
#     Hub (activité + KPIs + chart + recent).
#     Template: dashboard/home.html
#     """
#     user = request.user
#     range_key, days = _get_range_days(request)
#     next_url = _safe_next(request, fallback_url_name="dashboard:hub")

#     ttl = _cache_seconds()
#     cache_key = f"dash:hub:{user.id}:r{range_key}"

#     if ttl > 0:
#         cached = cache.get(cache_key)
#         if isinstance(cached, dict):
#             return render(request, "dashboard/home.html", cached)

#     # -------- Models safe --------
#     Note = _safe_model("dashboard", "DashboardNote")
#     Donation = _safe_model("donations", "Donation") or _safe_model("social", "Donation")
#     Order = _safe_model("ecommerce", "Order")

#     # -------- KPIs --------
#     kpi_notes_count = 0
#     if Note:
#         try:
#             kpi_notes_count = Note.objects.filter(user=user).count()
#         except Exception:
#             kpi_notes_count = 0

#     kpi_donations_count = 0
#     kpi_donations_total = 0
#     if Donation:
#         try:
#             user_field = _pick_user_field(Donation, ("user", "author", "donor"))
#             qs = Donation.objects.all()
#             if user_field:
#                 qs = qs.filter(**{user_field: user})
#             kpi_donations_count = qs.count()

#             amount_field = _pick_amount_field(Donation)
#             kpi_donations_total = _sum_amount(qs, amount_field)
#         except Exception:
#             kpi_donations_count = 0
#             kpi_donations_total = 0

#     kpi_orders_count = 0
#     if Order:
#         try:
#             user_field = _pick_user_field(Order, ("user", "customer", "buyer", "author"))
#             qs = Order.objects.all()
#             if user_field:
#                 qs = qs.filter(**{user_field: user})
#             kpi_orders_count = qs.count()
#         except Exception:
#             kpi_orders_count = 0

#     # -------- Chart (days) --------
#     labels, keys = _date_labels(days)
#     values = [0] * len(labels)

#     day_counts: Dict[str, int] = {}

#     if Note and _model_has_field(Note, "created_at"):
#         try:
#             c = _counts_by_day(Note.objects.filter(user=user), "created_at", days)
#             for k, v in c.items():
#                 day_counts[k] = day_counts.get(k, 0) + v
#         except Exception:
#             pass

#     if Donation and _model_has_field(Donation, "created_at"):
#         try:
#             user_field = _pick_user_field(Donation, ("user", "author", "donor"))
#             qs = Donation.objects.all()
#             if user_field:
#                 qs = qs.filter(**{user_field: user})
#             c = _counts_by_day(qs, "created_at", days)
#             for k, v in c.items():
#                 day_counts[k] = day_counts.get(k, 0) + v
#         except Exception:
#             pass

#     if Order and _model_has_field(Order, "created_at"):
#         try:
#             user_field = _pick_user_field(Order, ("user", "customer", "buyer", "author"))
#             qs = Order.objects.all()
#             if user_field:
#                 qs = qs.filter(**{user_field: user})
#             c = _counts_by_day(qs, "created_at", days)
#             for k, v in c.items():
#                 day_counts[k] = day_counts.get(k, 0) + v
#         except Exception:
#             pass

#     for idx, key in enumerate(keys):
#         values[idx] = int(day_counts.get(key, 0))

#     # -------- Recent activity --------
#     recent_activity = _build_recent_activity(user)

#     # -------- Profil status (optionnel) --------
#     profile_status = _get_profile_status(user)

#     ctx = {
#         "page_title": _("Dashboard"),
#         "next_url": next_url,
#         "range_key": range_key,
#         "profile_status": profile_status,

#         "kpi_donations_count": kpi_donations_count,
#         "kpi_donations_total": kpi_donations_total,
#         "kpi_orders_count": kpi_orders_count,
#         "kpi_notes_count": kpi_notes_count,

#         # JSON pour le JS (template fait |safe)
#         # "chart_labels": json.dumps(labels),
#         # "chart_values": json.dumps(values),
#         "chart_labels": labels,
#         "chart_values": values,


#         "recent_activity": recent_activity,
#     }

#     if ttl > 0:
#         cache.set(cache_key, ctx, ttl)

#     return render(request, "dashboard/home.html", ctx)








# # dashboard/views/dashboard_hub.py
# from __future__ import annotations

# from datetime import timedelta
# from typing import Any, Dict, List, Optional, Tuple

# from django.apps import apps
# from django.contrib.auth.decorators import login_required
# from django.db.models import Count
# from django.http import HttpRequest, HttpResponse
# from django.shortcuts import render
# from django.utils import timezone
# from django.utils.translation import gettext_lazy as _


# def _safe_model(app_label: str, model_name: str):
#     """
#     Retourne le modèle si présent, sinon None (no fail).
#     """
#     try:
#         return apps.get_model(app_label, model_name)
#     except Exception:
#         return None


# def _last_30_days_labels() -> List[str]:
#     """
#     Retourne 30 labels (JJ/MM) du plus ancien au plus récent.
#     """
#     today = timezone.localdate()
#     labels = []
#     for i in range(29, -1, -1):
#         d = today - timedelta(days=i)
#         labels.append(d.strftime("%d/%m"))
#     return labels


# def _counts_by_day(qs, date_field: str) -> Dict[str, int]:
#     """
#     Groupe un queryset par jour sur 30 jours.
#     qs: queryset du modèle
#     date_field: champ datetime (ex: "created_at")
#     Retourne un dict { "YYYY-MM-DD": count }
#     """
#     # On évite TruncDay (DB differences), on fait simple: range + annotate si possible
#     # Si annotate échoue, on fallback en Python.
#     start_dt = timezone.now() - timedelta(days=30)
#     try:
#         # annotate by date part
#         from django.db.models.functions import TruncDate

#         agg = (
#             qs.filter(**{f"{date_field}__gte": start_dt})
#             .annotate(day=TruncDate(date_field))
#             .values("day")
#             .annotate(c=Count("id"))
#             .order_by("day")
#         )
#         out = {}
#         for row in agg:
#             day = row.get("day")
#             if day:
#                 out[str(day)] = int(row.get("c") or 0)
#         return out
#     except Exception:
#         # Fallback Python
#         out = {}
#         for obj in qs.filter(**{f"{date_field}__gte": start_dt}):
#             dt = getattr(obj, date_field, None)
#             if not dt:
#                 continue
#             key = str(timezone.localdate(dt))
#             out[key] = out.get(key, 0) + 1
#         return out


# def _build_recent_activity(request: HttpRequest) -> List[Dict[str, Any]]:
#     """
#     Construit un journal d'activités récent en piochant dans des modèles existants.
#     Chaque entrée: {date, kind, label, status}
#     """
#     user = request.user
#     items: List[Dict[str, Any]] = []

#     # Notes (dashboard.DashboardNote)
#     Note = _safe_model("dashboard", "DashboardNote")
#     if Note:
#         try:
#             qs = Note.objects.filter(user=user).order_by("-updated_at")[:5]
#             for n in qs:
#                 title = getattr(n, "title", None) or _("Note")
#                 items.append(
#                     {
#                         "date": getattr(n, "updated_at", None) or getattr(n, "created_at", None) or timezone.now(),
#                         "kind": _("Note"),
#                         "label": str(title),
#                         "status": "info",
#                     }
#                 )
#         except Exception:
#             pass

#     # Donations (donations.Donation) ou (social.Donation) selon ton projet
#     Donation = _safe_model("donations", "Donation") or _safe_model("social", "Donation")
#     if Donation:
#         try:
#             # On tente d'identifier le champ user (author/donor/user)
#             user_field = None
#             for f in ("user", "author", "donor"):
#                 if hasattr(Donation, f):
#                     user_field = f
#                     break

#             qs = Donation.objects.all()
#             if user_field:
#                 qs = qs.filter(**{user_field: user})

#             qs = qs.order_by("-created_at")[:5] if hasattr(Donation, "created_at") else qs.order_by("-id")[:5]

#             for d in qs:
#                 amount = getattr(d, "amount", None) or getattr(d, "total_amount", None)
#                 label = _("Donation")
#                 if amount is not None:
#                     label = _("Donation: %(amount)s") % {"amount": amount}

#                 # statut simple si champ exists
#                 status_val = getattr(d, "status", None) or getattr(d, "payment_status", None)
#                 status = "success" if str(status_val).lower() in ("paid", "success", "completed", "succeeded") else "info"

#                 items.append(
#                     {
#                         "date": getattr(d, "created_at", None) or getattr(d, "updated_at", None) or timezone.now(),
#                         "kind": _("Donation"),
#                         "label": str(label),
#                         "status": status,
#                     }
#                 )
#         except Exception:
#             pass

#     # Orders (economic.ecommerce.Order) / (ecommerce.Order)
#     Order = _safe_model("ecommerce", "Order") or _safe_model("economic_ecommerce", "Order") or _safe_model("economic", "Order")
#     if Order:
#         try:
#             # champ utilisateur probable
#             user_field = None
#             for f in ("user", "customer", "buyer", "author"):
#                 if hasattr(Order, f):
#                     user_field = f
#                     break

#             qs = Order.objects.all()
#             if user_field:
#                 qs = qs.filter(**{user_field: user})

#             qs = qs.order_by("-created_at")[:5] if hasattr(Order, "created_at") else qs.order_by("-id")[:5]

#             for o in qs:
#                 code = getattr(o, "uuid", None) or getattr(o, "reference", None) or getattr(o, "id", None)
#                 label = _("Commande #%(code)s") % {"code": code}
#                 status_val = getattr(o, "status", None) or getattr(o, "payment_status", None)
#                 status = "success" if str(status_val).lower() in ("paid", "success", "completed", "succeeded") else "info"

#                 items.append(
#                     {
#                         "date": getattr(o, "created_at", None) or getattr(o, "updated_at", None) or timezone.now(),
#                         "kind": _("Commande"),
#                         "label": str(label),
#                         "status": status,
#                     }
#                 )
#         except Exception:
#             pass

#     # Trier et limiter
#     items.sort(key=lambda x: x.get("date") or timezone.now(), reverse=True)
#     return items[:10]


# @login_required
# def hub_view(request: HttpRequest) -> HttpResponse:
#     """
#     Page Dashboard Home (Hub) — production safe.
#     Template: dashboard/home.html
#     """
#     user = request.user

#     # -------- KPIs --------
#     kpi_notes_count = 0
#     Note = _safe_model("dashboard", "DashboardNote")
#     if Note:
#         try:
#             kpi_notes_count = Note.objects.filter(user=user).count()
#         except Exception:
#             kpi_notes_count = 0

#     kpi_donations_count = 0
#     Donation = _safe_model("donations", "Donation") or _safe_model("social", "Donation")
#     if Donation:
#         try:
#             user_field = None
#             for f in ("user", "author", "donor"):
#                 if hasattr(Donation, f):
#                     user_field = f
#                     break
#             qs = Donation.objects.all()
#             if user_field:
#                 qs = qs.filter(**{user_field: user})
#             kpi_donations_count = qs.count()
#         except Exception:
#             kpi_donations_count = 0

#     kpi_orders_count = 0
#     Order = _safe_model("ecommerce", "Order") or _safe_model("economic_ecommerce", "Order") or _safe_model("economic", "Order")
#     if Order:
#         try:
#             user_field = None
#             for f in ("user", "customer", "buyer", "author"):
#                 if hasattr(Order, f):
#                     user_field = f
#                     break
#             qs = Order.objects.all()
#             if user_field:
#                 qs = qs.filter(**{user_field: user})
#             kpi_orders_count = qs.count()
#         except Exception:
#             kpi_orders_count = 0

#     # -------- Chart (30 jours) --------
#     labels = _last_30_days_labels()
#     values = [0] * len(labels)

#     # On prend une "activité" simple: notes + donations + orders, si dispo
#     day_counts: Dict[str, int] = {}

#     # Notes counts
#     if Note and hasattr(Note, "created_at"):
#         try:
#             c = _counts_by_day(Note.objects.filter(user=user), "created_at")
#             for k, v in c.items():
#                 day_counts[k] = day_counts.get(k, 0) + v
#         except Exception:
#             pass

#     # Donations counts
#     if Donation and hasattr(Donation, "created_at"):
#         try:
#             user_field = None
#             for f in ("user", "author", "donor"):
#                 if hasattr(Donation, f):
#                     user_field = f
#                     break
#             qs = Donation.objects.all()
#             if user_field:
#                 qs = qs.filter(**{user_field: user})
#             c = _counts_by_day(qs, "created_at")
#             for k, v in c.items():
#                 day_counts[k] = day_counts.get(k, 0) + v
#         except Exception:
#             pass

#     # Orders counts
#     if Order and hasattr(Order, "created_at"):
#         try:
#             user_field = None
#             for f in ("user", "customer", "buyer", "author"):
#                 if hasattr(Order, f):
#                     user_field = f
#                     break
#             qs = Order.objects.all()
#             if user_field:
#                 qs = qs.filter(**{user_field: user})
#             c = _counts_by_day(qs, "created_at")
#             for k, v in c.items():
#                 day_counts[k] = day_counts.get(k, 0) + v
#         except Exception:
#             pass

#     # Map day_counts into chart arrays
#     # labels are dd/mm for last 30 days; we match via localdate string
#     today = timezone.localdate()
#     for i in range(29, -1, -1):
#         d = today - timedelta(days=i)
#         key = str(d)  # YYYY-MM-DD
#         idx = 29 - i
#         if 0 <= idx < len(values):
#             values[idx] = int(day_counts.get(key, 0))

#     # -------- Recent activity --------
#     recent_activity = _build_recent_activity(request)

#     ctx = {
#         "kpi_donations_count": kpi_donations_count,
#         "kpi_orders_count": kpi_orders_count,
#         "kpi_notes_count": kpi_notes_count,
#         "recent_activity": recent_activity,

#         # Chart.js expects JSON arrays (safe in template with |safe)
#         "chart_labels": labels,
#         "chart_values": values,
#     }
#     return render(request, "dashboard/home.html", ctx)







# # dashboard/views/hub.py
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render
# from django.utils.translation import gettext_lazy as _

# from dashboard.views.utils import breadcrumb, StatCard, get_user_profile


# @login_required
# def dashboard_hub_view(request):
#     profile = get_user_profile(request.user)

#     cards = [
#         StatCard(label=_("Compte"), value=_("Actif") if request.user.is_active else _("Inactif"), icon="👤"),
#         StatCard(label=_("Staff"), value=_("Oui") if request.user.is_staff else _("Non"), icon="🛡️"),
#     ]

#     ctx = {
#         "breadcrumbs": breadcrumb((_('Dashboard'), None)),
#         "profile": profile,
#         "cards": [c.__dict__ for c in cards],
#     }
#     return render(request, "dashboard/hub.html", ctx)





# # /dashboard/views/hub.py
# from django.shortcuts import redirect
# from django.contrib.auth.decorators import login_required

# from dashboard.permissions import (
#     is_staff_user,
#     is_admin,
#     is_vendor,
#     is_b2b_user,
# )
# from accounts_users.services.users_service import has_social_role


# @login_required
# def dashboard_hub_view(request):
#     """
#     Point d’entrée UNIQUE après login.
#     Redirection par priorité métier.
#     Ordre de priorité :
#       1. Admin / Staff
#       2. Vendeur B2C
#       3. B2B
#       4. Social
#       5. Utilisateur standard
#     """
#     user = request.user

#     # 1) ADMIN / STAFF
#     if is_admin(user) or user.is_staff or is_staff_user(user):
#         # Namespace "admin" défini dans dashboard/urls.py :
#         # path("admin/", include(("dashboard.urls.admin", "admin"), namespace="admin"))
#         return redirect("dashboard:admin:home")

#     # 2) VENDEUR B2C
#     if is_vendor(user):
#         # Nom défini dans dashboard/urls.py : name="vendor_home"
#         return redirect("dashboard:vendor_home")

#     # 3) B2B
#     if is_b2b_user(user):
#         # Nom défini dans dashboard/urls.py : name="b2b_home"
#         return redirect("dashboard:b2b_home")

#     # 4) SOCIAL (donateur, membre, volontaire, etc.)
#     if has_social_role(user):
#         # Router social défini dans dashboard/urls.py : name="social_router"
#         return redirect("dashboard:social_router")

#     # 5) UTILISATEUR STANDARD (dashboard utilisateur)
#     # Nom défini dans dashboard/urls.py :
#     #   path("user/", user_dashboard_home_view, name="home")
#     return redirect("dashboard:home")






# # /dashboard/views/hub.py
# from django.shortcuts import redirect
# from django.contrib.auth.decorators import login_required

# from dashboard.permissions import is_staff_user, is_admin, is_vendor, is_b2b_user
# from accounts_users.services.users_service import has_social_role


# @login_required
# def dashboard_hub_view(request):
#     """
#     Point d’entrée UNIQUE après login.
#     Redirection par priorité métier.
#     """
#     user = request.user

#     # ADMIN / STAFF
#     if is_admin(user) or user.is_staff:
#         return redirect("dashboard:admin:home")
    
#     if is_admin(user):
#         return redirect("dashboard:admin:home")

#     if is_staff_user(user):
#         return redirect("dashboard:admin:staff")


#     # VENDEUR B2C
#     if is_vendor(user):
#         return redirect("dashboard:vendor:vendor_index")

#     # B2B
#     if is_b2b_user(user):
#         return redirect("dashboard:b2b:home")

#     # SOCIAL
#     if has_social_role(user):
#         return redirect("dashboard:social:home")

#     # UTILISATEUR STANDARD
#     return redirect("dashboard:user:home")





# # dashboard/views/hub.py
# from django.shortcuts import redirect
# from django.contrib.auth.decorators import login_required

# from dashboard.permissions import is_admin, is_vendor, is_b2b_user
# from accounts_users.services import has_social_role  # à adapter si besoin

# @login_required
# def dashboard_hub_view(request):
#     """
#     Point d’entrée UNIQUE après login.
#     Redirige selon le rôle principal.
#     """
#     user = request.user

#     # ADMIN / STAFF
#     if is_admin(user) or user.is_staff:
#         return redirect("dashboard:admin_home")

#     # VENDEUR (B2C)
#     if is_vendor(user):
#         return redirect("dashboard:vendor:vendor_index")

#     # B2B
#     if is_b2b_user(user):
#         return redirect("dashboard:b2b:home")

#     # SOCIAL (donateur, membre, volontaire, institution)
#     if has_social_role(user):
#         return redirect("dashboard:social:home")

#     # CLIENT ÉCO STANDARD
#     return redirect("dashboard:user:home")











# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render, redirect
# from dashboard.permissions import is_vendor, is_b2b_user


# @login_required
# def dashboard_hub_view(request):
#     """
#     Hub central : choix du pôle
#     """

#     context = {
#         "has_social_access": hasattr(request.user, "profile") and request.user.profile.membership_role,
#         "has_eco_access": is_vendor(request.user) or is_b2b_user(request.user),
#     }

#     return render(request, "dashboard/hub.html", context)
