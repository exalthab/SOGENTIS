# dashboard/views/hub.py
from __future__ import annotations

from datetime import timedelta
from typing import Any, Dict, List, Optional, Tuple

from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


def _safe_model(app_label: str, model_name: str):
    """
    Retourne le modèle si présent, sinon None (no fail).
    """
    try:
        return apps.get_model(app_label, model_name)
    except Exception:
        return None


def _last_30_days_labels() -> List[str]:
    """
    Retourne 30 labels (JJ/MM) du plus ancien au plus récent.
    """
    today = timezone.localdate()
    labels = []
    for i in range(29, -1, -1):
        d = today - timedelta(days=i)
        labels.append(d.strftime("%d/%m"))
    return labels


def _counts_by_day(qs, date_field: str) -> Dict[str, int]:
    """
    Groupe un queryset par jour sur 30 jours.
    qs: queryset du modèle
    date_field: champ datetime (ex: "created_at")
    Retourne un dict { "YYYY-MM-DD": count }
    """
    # On évite TruncDay (DB differences), on fait simple: range + annotate si possible
    # Si annotate échoue, on fallback en Python.
    start_dt = timezone.now() - timedelta(days=30)
    try:
        # annotate by date part
        from django.db.models.functions import TruncDate

        agg = (
            qs.filter(**{f"{date_field}__gte": start_dt})
            .annotate(day=TruncDate(date_field))
            .values("day")
            .annotate(c=Count("id"))
            .order_by("day")
        )
        out = {}
        for row in agg:
            day = row.get("day")
            if day:
                out[str(day)] = int(row.get("c") or 0)
        return out
    except Exception:
        # Fallback Python
        out = {}
        for obj in qs.filter(**{f"{date_field}__gte": start_dt}):
            dt = getattr(obj, date_field, None)
            if not dt:
                continue
            key = str(timezone.localdate(dt))
            out[key] = out.get(key, 0) + 1
        return out


def _build_recent_activity(request: HttpRequest) -> List[Dict[str, Any]]:
    """
    Construit un journal d'activités récent en piochant dans des modèles existants.
    Chaque entrée: {date, kind, label, status}
    """
    user = request.user
    items: List[Dict[str, Any]] = []

    # Notes (dashboard.DashboardNote)
    Note = _safe_model("dashboard", "DashboardNote")
    if Note:
        try:
            qs = Note.objects.filter(user=user).order_by("-updated_at")[:5]
            for n in qs:
                title = getattr(n, "title", None) or _("Note")
                items.append(
                    {
                        "date": getattr(n, "updated_at", None) or getattr(n, "created_at", None) or timezone.now(),
                        "kind": _("Note"),
                        "label": str(title),
                        "status": "info",
                    }
                )
        except Exception:
            pass

    # Donations (donations.Donation) ou (social.Donation) selon ton projet
    Donation = _safe_model("donations", "Donation") or _safe_model("social", "Donation")
    if Donation:
        try:
            # On tente d'identifier le champ user (author/donor/user)
            user_field = None
            for f in ("user", "author", "donor"):
                if hasattr(Donation, f):
                    user_field = f
                    break

            qs = Donation.objects.all()
            if user_field:
                qs = qs.filter(**{user_field: user})

            qs = qs.order_by("-created_at")[:5] if hasattr(Donation, "created_at") else qs.order_by("-id")[:5]

            for d in qs:
                amount = getattr(d, "amount", None) or getattr(d, "total_amount", None)
                label = _("Donation")
                if amount is not None:
                    label = _("Donation: %(amount)s") % {"amount": amount}

                # statut simple si champ exists
                status_val = getattr(d, "status", None) or getattr(d, "payment_status", None)
                status = "success" if str(status_val).lower() in ("paid", "success", "completed", "succeeded") else "info"

                items.append(
                    {
                        "date": getattr(d, "created_at", None) or getattr(d, "updated_at", None) or timezone.now(),
                        "kind": _("Donation"),
                        "label": str(label),
                        "status": status,
                    }
                )
        except Exception:
            pass

    # Orders (economic.ecommerce.Order) / (ecommerce.Order)
    Order = _safe_model("ecommerce", "Order") or _safe_model("economic_ecommerce", "Order") or _safe_model("economic", "Order")
    if Order:
        try:
            # champ utilisateur probable
            user_field = None
            for f in ("user", "customer", "buyer", "author"):
                if hasattr(Order, f):
                    user_field = f
                    break

            qs = Order.objects.all()
            if user_field:
                qs = qs.filter(**{user_field: user})

            qs = qs.order_by("-created_at")[:5] if hasattr(Order, "created_at") else qs.order_by("-id")[:5]

            for o in qs:
                code = getattr(o, "uuid", None) or getattr(o, "reference", None) or getattr(o, "id", None)
                label = _("Commande #%(code)s") % {"code": code}
                status_val = getattr(o, "status", None) or getattr(o, "payment_status", None)
                status = "success" if str(status_val).lower() in ("paid", "success", "completed", "succeeded") else "info"

                items.append(
                    {
                        "date": getattr(o, "created_at", None) or getattr(o, "updated_at", None) or timezone.now(),
                        "kind": _("Commande"),
                        "label": str(label),
                        "status": status,
                    }
                )
        except Exception:
            pass

    # Trier et limiter
    items.sort(key=lambda x: x.get("date") or timezone.now(), reverse=True)
    return items[:10]


@login_required
def hub_view(request: HttpRequest) -> HttpResponse:
    """
    Page Dashboard Home (Hub) — production safe.
    Template: dashboard/home.html
    """
    user = request.user

    # -------- KPIs --------
    kpi_notes_count = 0
    Note = _safe_model("dashboard", "DashboardNote")
    if Note:
        try:
            kpi_notes_count = Note.objects.filter(user=user).count()
        except Exception:
            kpi_notes_count = 0

    kpi_donations_count = 0
    Donation = _safe_model("donations", "Donation") or _safe_model("social", "Donation")
    if Donation:
        try:
            user_field = None
            for f in ("user", "author", "donor"):
                if hasattr(Donation, f):
                    user_field = f
                    break
            qs = Donation.objects.all()
            if user_field:
                qs = qs.filter(**{user_field: user})
            kpi_donations_count = qs.count()
        except Exception:
            kpi_donations_count = 0

    kpi_orders_count = 0
    Order = _safe_model("ecommerce", "Order") or _safe_model("economic_ecommerce", "Order") or _safe_model("economic", "Order")
    if Order:
        try:
            user_field = None
            for f in ("user", "customer", "buyer", "author"):
                if hasattr(Order, f):
                    user_field = f
                    break
            qs = Order.objects.all()
            if user_field:
                qs = qs.filter(**{user_field: user})
            kpi_orders_count = qs.count()
        except Exception:
            kpi_orders_count = 0

    # -------- Chart (30 jours) --------
    labels = _last_30_days_labels()
    values = [0] * len(labels)

    # On prend une "activité" simple: notes + donations + orders, si dispo
    day_counts: Dict[str, int] = {}

    # Notes counts
    if Note and hasattr(Note, "created_at"):
        try:
            c = _counts_by_day(Note.objects.filter(user=user), "created_at")
            for k, v in c.items():
                day_counts[k] = day_counts.get(k, 0) + v
        except Exception:
            pass

    # Donations counts
    if Donation and hasattr(Donation, "created_at"):
        try:
            user_field = None
            for f in ("user", "author", "donor"):
                if hasattr(Donation, f):
                    user_field = f
                    break
            qs = Donation.objects.all()
            if user_field:
                qs = qs.filter(**{user_field: user})
            c = _counts_by_day(qs, "created_at")
            for k, v in c.items():
                day_counts[k] = day_counts.get(k, 0) + v
        except Exception:
            pass

    # Orders counts
    if Order and hasattr(Order, "created_at"):
        try:
            user_field = None
            for f in ("user", "customer", "buyer", "author"):
                if hasattr(Order, f):
                    user_field = f
                    break
            qs = Order.objects.all()
            if user_field:
                qs = qs.filter(**{user_field: user})
            c = _counts_by_day(qs, "created_at")
            for k, v in c.items():
                day_counts[k] = day_counts.get(k, 0) + v
        except Exception:
            pass

    # Map day_counts into chart arrays
    # labels are dd/mm for last 30 days; we match via localdate string
    today = timezone.localdate()
    for i in range(29, -1, -1):
        d = today - timedelta(days=i)
        key = str(d)  # YYYY-MM-DD
        idx = 29 - i
        if 0 <= idx < len(values):
            values[idx] = int(day_counts.get(key, 0))

    # -------- Recent activity --------
    recent_activity = _build_recent_activity(request)

    ctx = {
        "kpi_donations_count": kpi_donations_count,
        "kpi_orders_count": kpi_orders_count,
        "kpi_notes_count": kpi_notes_count,
        "recent_activity": recent_activity,

        # Chart.js expects JSON arrays (safe in template with |safe)
        "chart_labels": labels,
        "chart_values": values,
    }
    return render(request, "dashboard/home.html", ctx)







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
