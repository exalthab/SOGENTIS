# dashboard/context_processors/dashboard_context.py
from __future__ import annotations

from typing import Any, Dict, Tuple


def _safe_utils():
    """
    Import sécurisé (évite de casser le site si un import est instable).
    """
    try:
        from dashboard.views.utils import (  # type: ignore
            get_user_profile,
            iter_user_profiles,
            detect_profile_status,
            economic_access_flags,
        )
        return get_user_profile, iter_user_profiles, detect_profile_status, economic_access_flags
    except Exception:
        return (
            (lambda _u, preferred="": None),
            (lambda _u: []),
            (lambda _p: ""),
            (lambda _u, _p=None: {
                "can_vendor": False,
                "can_b2b": False,
                "vendor_approved": False,
                "b2b_approved": False,
            }),
        )


def _safe_permissions():
    """
    Import sécurisé pour éviter de casser tout le site si dashboard.permissions
    a un problème (ImportError, circular import, etc.).
    """
    try:
        from dashboard.permissions import is_vendor, is_b2b_user  # type: ignore
        return is_vendor, is_b2b_user
    except Exception:
        return (lambda _u: False), (lambda _u: False)


def _safe_apps() -> Tuple[Any, Any]:
    """
    Apps registry safe.
    """
    try:
        from django.apps import apps  # type: ignore
        return apps, None
    except Exception:
        return None, None


def _is_installed(dotted: str) -> bool:
    apps, _ = _safe_apps()
    if not apps:
        return False
    try:
        return bool(apps.is_installed(dotted))
    except Exception:
        return False


def _safe_finance_access():
    """
    Flags d'accès finance (accounting/payments) basés sur permissions Django.
    On reste permissif pour staff/superuser.
    """
    def _can(u, perm: str) -> bool:
        try:
            return bool(getattr(u, "is_superuser", False) or getattr(u, "is_staff", False) or u.has_perm(perm))
        except Exception:
            return False

    def finance_flags(u) -> Dict[str, bool]:
        return {
            "can_payments": _can(u, "payments.view_paymentintent") or _can(u, "payments.change_paymentintent"),
            "can_accounting": _can(u, "accounting.view_journalentry") or _can(u, "accounting.change_journalentry"),
            "can_accounting_admin": _can(u, "accounting.add_account") or _can(u, "accounting.change_account"),
        }

    return finance_flags


def _detect_space(request) -> str:
    """
    Détermine l'espace courant façon apps modernes:
    - basé sur namespaces (vendor/b2b/social/formations/user/admin/accounting/payments)
    - fallback sur view_name
    """
    rm = getattr(request, "resolver_match", None)
    if not rm:
        return "dashboard"

    nss = getattr(rm, "namespaces", None) or ()
    view_name = str(getattr(rm, "view_name", "") or "")

    # namespaces d'abord
    for ns in ("admin", "vendor", "b2b", "social", "formations", "user", "accounting", "payments"):
        if ns in nss:
            return ns

    # fallback
    if view_name.startswith("dashboard:admin:"):
        return "admin"
    if view_name.startswith("dashboard:vendor:"):
        return "vendor"
    if view_name.startswith("dashboard:b2b:"):
        return "b2b"
    if view_name.startswith("dashboard:social:"):
        return "social"
    if view_name.startswith("dashboard:formations:"):
        return "formations"
    if view_name.startswith("dashboard:user:"):
        return "user"
    if view_name.startswith("dashboard:accounting:"):
        return "accounting"
    if view_name.startswith("dashboard:payments:"):
        return "payments"

    return "dashboard"


def _detect_pole(request) -> str:
    """
    Déduit le pôle courant (utile pour scope comptable).
    - priorité: session si définie
    - sinon: namespace dashboard:social/formations/vendor/b2b etc.
    - fallback: ECONOMIC
    """
    try:
        pole = (request.session.get("DASHBOARD_POLE") or "").strip().upper()
        if pole in {"ECONOMIC", "SOCIAL", "INSTITUTION", "CORE"}:
            return pole
    except Exception:
        pass

    space = _detect_space(request)
    if space == "social":
        return "SOCIAL"
    if space in {"formations", "vendor", "b2b"}:
        return "ECONOMIC"
    return "ECONOMIC"


def _safe_finance_metrics(user, pole: str) -> Dict[str, Any]:
    """
    Metrics légers (safe) pour topbar/menus.
    IMPORTANT: pas de requêtes lourdes / pas d'exception qui casse le rendu.
    """
    out: Dict[str, Any] = {
        "payments_pending": 0,
        "payments_paid_today": 0,
        "accounting_drafts": 0,
        "accounting_posted_today": 0,
    }

    # ---- payments ----
    if _is_installed("payments"):
        try:
            from payments.models import PaymentIntent  # type: ignore

            # évite de lire trop: count only
            out["payments_pending"] = int(
                PaymentIntent.objects.filter(
                    user=user,
                    status__in=["CREATED", "PENDING", "REQUIRES_ACTION"],
                ).count()
            )
            # payé aujourd'hui
            try:
                from django.utils import timezone  # type: ignore
                today = timezone.localdate()
                out["payments_paid_today"] = int(
                    PaymentIntent.objects.filter(user=user, status="PAID", paid_at__date=today).count()
                )
            except Exception:
                out["payments_paid_today"] = 0
        except Exception:
            pass

    # ---- accounting ----
    if _is_installed("accounting"):
        try:
            from accounting.models import JournalEntry  # type: ignore
            from django.utils import timezone  # type: ignore

            today = timezone.localdate()
            # drafts (scope pole)
            qs = JournalEntry.objects.all()
            if pole:
                qs = qs.filter(pole=pole)
            out["accounting_drafts"] = int(qs.filter(status="DRAFT").count())
            out["accounting_posted_today"] = int(qs.filter(status="POSTED", posted_at__date=today).count())
        except Exception:
            pass

    return out


def dashboard_info(request) -> Dict[str, Any]:
    """
    Infos globales injectées dans les templates dashboard.
    """
    user = getattr(request, "user", None)
    if not user or not getattr(user, "is_authenticated", False):
        return {}

    # cache par request pour éviter double calcul (dashboard_info + dashboard_roles)
    if hasattr(request, "_dashboard_ctx_cache") and isinstance(request._dashboard_ctx_cache, dict):
        cached = request._dashboard_ctx_cache.get("dashboard_info")
        if isinstance(cached, dict):
            return cached

    # Space courant (pour topbar / sidebar)
    space = _detect_space(request)
    pole = _detect_pole(request)

    # Profil status (safe)
    get_user_profile, iter_user_profiles, detect_profile_status, econ_flags_func = _safe_utils()

    try:
        profile = get_user_profile(user)
    except Exception:
        profile = None

    try:
        prof_status = detect_profile_status(profile) or ""
    except Exception:
        prof_status = ""

    # mini-UX flags
    is_vendor, is_b2b_user = _safe_permissions()

    # flags économiques robustes (safe)
    try:
        profiles = iter_user_profiles(user)
    except Exception:
        profiles = []

    try:
        econ = econ_flags_func(user, profiles)
    except Exception:
        econ = {
            "can_vendor": False,
            "can_b2b": False,
            "vendor_approved": False,
            "b2b_approved": False,
        }

    # Finance access + metrics (safe)
    finance_flags = _safe_finance_access()(user)
    metrics = _safe_finance_metrics(user, pole=pole)

    # Notifications (placeholder branchable plus tard)
    notifications = int(metrics.get("payments_pending") or 0)

    data = {
        "dashboard_user": user,
        "dashboard_space": space,
        "dashboard_pole": pole,
        "dashboard_notifications": notifications,

        # status profil (pour badges)
        "dashboard_profile_status": str(prof_status).strip().lower(),

        # compat rôles (existant dans ton code/sidebar)
        "is_vendor": bool(is_vendor(user)),
        "is_b2b_user": bool(is_b2b_user(user)),

        # gating économique (topbar/sidebar switcher)
        "can_vendor": bool(econ.get("can_vendor")),
        "can_b2b": bool(econ.get("can_b2b")),
        "vendor_approved": bool(econ.get("vendor_approved")),
        "b2b_approved": bool(econ.get("b2b_approved")),

        # finance apps presence
        "has_payments_app": _is_installed("payments"),
        "has_accounting_app": _is_installed("accounting"),

        # finance access flags
        "can_payments": bool(finance_flags.get("can_payments")),
        "can_accounting": bool(finance_flags.get("can_accounting")),
        "can_accounting_admin": bool(finance_flags.get("can_accounting_admin")),

        # finance metrics (topbar widgets)
        "payments_pending": int(metrics.get("payments_pending") or 0),
        "payments_paid_today": int(metrics.get("payments_paid_today") or 0),
        "accounting_drafts": int(metrics.get("accounting_drafts") or 0),
        "accounting_posted_today": int(metrics.get("accounting_posted_today") or 0),
    }

    try:
        request._dashboard_ctx_cache = getattr(request, "_dashboard_ctx_cache", {}) or {}
        request._dashboard_ctx_cache["dashboard_info"] = data
    except Exception:
        pass

    return data


def dashboard_roles(request) -> Dict[str, Any]:
    """
    ✅ COMPAT: ton settings pointe probablement encore sur
    dashboard.context_processors.dashboard_context.dashboard_roles

    Rôles utiles pour afficher dynamiquement sidebar / menus.
    (On renvoie aussi les mêmes flags que dashboard_info pour éviter les surprises.)
    """
    user = getattr(request, "user", None)
    if not user or not getattr(user, "is_authenticated", False):
        return {
            "is_vendor": False,
            "is_b2b_user": False,
            "can_vendor": False,
            "can_b2b": False,
            "vendor_approved": False,
            "b2b_approved": False,
            "has_payments_app": False,
            "has_accounting_app": False,
            "can_payments": False,
            "can_accounting": False,
            "can_accounting_admin": False,
        }

    # cache
    if hasattr(request, "_dashboard_ctx_cache") and isinstance(request._dashboard_ctx_cache, dict):
        cached = request._dashboard_ctx_cache.get("dashboard_roles")
        if isinstance(cached, dict):
            return cached

    is_vendor, is_b2b_user = _safe_permissions()
    _get_user_profile, iter_user_profiles, _detect_profile_status, econ_flags_func = _safe_utils()

    try:
        profiles = iter_user_profiles(user)
    except Exception:
        profiles = []

    try:
        econ = econ_flags_func(user, profiles)
    except Exception:
        econ = {
            "can_vendor": False,
            "can_b2b": False,
            "vendor_approved": False,
            "b2b_approved": False,
        }

    finance = _safe_finance_access()(user)

    data = {
        "is_vendor": bool(is_vendor(user)),
        "is_b2b_user": bool(is_b2b_user(user)),
        "can_vendor": bool(econ.get("can_vendor")),
        "can_b2b": bool(econ.get("can_b2b")),
        "vendor_approved": bool(econ.get("vendor_approved")),
        "b2b_approved": bool(econ.get("b2b_approved")),
        "has_payments_app": _is_installed("payments"),
        "has_accounting_app": _is_installed("accounting"),
        "can_payments": bool(finance.get("can_payments")),
        "can_accounting": bool(finance.get("can_accounting")),
        "can_accounting_admin": bool(finance.get("can_accounting_admin")),
    }

    try:
        request._dashboard_ctx_cache = getattr(request, "_dashboard_ctx_cache", {}) or {}
        request._dashboard_ctx_cache["dashboard_roles"] = data
    except Exception:
        pass

    return data









# # dashboard/context_processors/dashboard_context.py 16-02-2026
# from __future__ import annotations

# from typing import Any, Dict


# def _safe_utils():
#     """
#     Import sécurisé (évite de casser le site si un import est instable).
#     """
#     try:
#         from dashboard.views.utils import (  # type: ignore
#             get_user_profile,
#             iter_user_profiles,
#             detect_profile_status,
#             economic_access_flags,
#         )
#         return get_user_profile, iter_user_profiles, detect_profile_status, economic_access_flags
#     except Exception:
#         return (
#             (lambda _u, preferred="": None),
#             (lambda _u: []),
#             (lambda _p: ""),
#             (lambda _u, _p=None: {
#                 "can_vendor": False,
#                 "can_b2b": False,
#                 "vendor_approved": False,
#                 "b2b_approved": False,
#             }),
#         )


# def _safe_permissions():
#     """
#     Import sécurisé pour éviter de casser tout le site si dashboard.permissions
#     a un problème (ImportError, circular import, etc.).
#     """
#     try:
#         from dashboard.permissions import is_vendor, is_b2b_user  # type: ignore
#         return is_vendor, is_b2b_user
#     except Exception:
#         return (lambda _u: False), (lambda _u: False)


# def _detect_space(request) -> str:
#     """
#     Détermine l'espace courant façon apps modernes:
#     - basé sur namespaces (vendor/b2b/social/formations/user/admin)
#     - fallback sur view_name
#     """
#     rm = getattr(request, "resolver_match", None)
#     if not rm:
#         return "dashboard"

#     nss = getattr(rm, "namespaces", None) or ()
#     view_name = str(getattr(rm, "view_name", "") or "")

#     # namespaces d'abord
#     for ns in ("admin", "vendor", "b2b", "social", "formations", "user"):
#         if ns in nss:
#             return ns

#     # fallback
#     if view_name.startswith("dashboard:admin:"):
#         return "admin"
#     if view_name.startswith("dashboard:vendor:"):
#         return "vendor"
#     if view_name.startswith("dashboard:b2b:"):
#         return "b2b"
#     if view_name.startswith("dashboard:social:"):
#         return "social"
#     if view_name.startswith("dashboard:formations:"):
#         return "formations"
#     if view_name.startswith("dashboard:user:"):
#         return "user"

#     return "dashboard"


# def dashboard_info(request) -> Dict[str, Any]:
#     """
#     Infos globales injectées dans les templates dashboard.
#     """
#     user = getattr(request, "user", None)
#     if not user or not getattr(user, "is_authenticated", False):
#         return {}

#     # Space courant (pour topbar / sidebar)
#     space = _detect_space(request)

#     # Profil status (safe)
#     get_user_profile, iter_user_profiles, detect_profile_status, econ_flags_func = _safe_utils()

#     try:
#         profile = get_user_profile(user)
#     except Exception:
#         profile = None

#     try:
#         prof_status = detect_profile_status(profile) or ""
#     except Exception:
#         prof_status = ""

#     # mini-UX flags
#     is_vendor, is_b2b_user = _safe_permissions()

#     # flags économiques robustes (safe)
#     try:
#         profiles = iter_user_profiles(user)
#     except Exception:
#         profiles = []

#     try:
#         econ = econ_flags_func(user, profiles)
#     except Exception:
#         econ = {
#             "can_vendor": False,
#             "can_b2b": False,
#             "vendor_approved": False,
#             "b2b_approved": False,
#         }

#     # Notifications (placeholder branchable plus tard)
#     notifications = 0

#     return {
#         "dashboard_user": user,
#         "dashboard_space": space,
#         "dashboard_notifications": notifications,

#         # status profil (pour badges)
#         "dashboard_profile_status": str(prof_status).strip().lower(),

#         # compat rôles (existant dans ton code/sidebar)
#         "is_vendor": bool(is_vendor(user)),
#         "is_b2b_user": bool(is_b2b_user(user)),

#         # gating économique (topbar/sidebar switcher)
#         "can_vendor": bool(econ.get("can_vendor")),
#         "can_b2b": bool(econ.get("can_b2b")),
#         "vendor_approved": bool(econ.get("vendor_approved")),
#         "b2b_approved": bool(econ.get("b2b_approved")),
#     }


# def dashboard_roles(request) -> Dict[str, Any]:
#     """
#     ✅ COMPAT: ton settings pointe probablement encore sur
#     dashboard.context_processors.dashboard_context.dashboard_roles

#     Rôles utiles pour afficher dynamiquement sidebar / menus.
#     (On renvoie aussi les mêmes flags que dashboard_info pour éviter les surprises.)
#     """
#     user = getattr(request, "user", None)
#     if not user or not getattr(user, "is_authenticated", False):
#         return {
#             "is_vendor": False,
#             "is_b2b_user": False,
#             "can_vendor": False,
#             "can_b2b": False,
#             "vendor_approved": False,
#             "b2b_approved": False,
#         }

#     is_vendor, is_b2b_user = _safe_permissions()
#     _get_user_profile, iter_user_profiles, _detect_profile_status, econ_flags_func = _safe_utils()

#     try:
#         profiles = iter_user_profiles(user)
#     except Exception:
#         profiles = []

#     try:
#         econ = econ_flags_func(user, profiles)
#     except Exception:
#         econ = {
#             "can_vendor": False,
#             "can_b2b": False,
#             "vendor_approved": False,
#             "b2b_approved": False,
#         }

#     try:
#         return {
#             "is_vendor": bool(is_vendor(user)),
#             "is_b2b_user": bool(is_b2b_user(user)),
#             "can_vendor": bool(econ.get("can_vendor")),
#             "can_b2b": bool(econ.get("can_b2b")),
#             "vendor_approved": bool(econ.get("vendor_approved")),
#             "b2b_approved": bool(econ.get("b2b_approved")),
#         }
#     except Exception:
#         return {
#             "is_vendor": False,
#             "is_b2b_user": False,
#             "can_vendor": False,
#             "can_b2b": False,
#             "vendor_approved": False,
#             "b2b_approved": False,
#         }







# # dashboard/context_processors/dashboard_context.py
# from __future__ import annotations

# from typing import Any, Dict


# def _safe_utils():
#     """
#     Import sécurisé (évite de casser le site si un import est instable).
#     """
#     try:
#         from dashboard.views.utils import (  # type: ignore
#             get_user_profile,
#             iter_user_profiles,
#             detect_profile_status,
#             economic_access_flags,
#         )
#         return get_user_profile, iter_user_profiles, detect_profile_status, economic_access_flags
#     except Exception:
#         return (lambda _u, preferred="": None), (lambda _u: []), (lambda _p: ""), (lambda _u, _p=None: {
#             "can_vendor": False,
#             "can_b2b": False,
#             "vendor_approved": False,
#             "b2b_approved": False,
#         })


# def _safe_permissions():
#     """
#     Import sécurisé pour éviter de casser tout le site si dashboard.permissions
#     a un problème (ImportError, circular import, etc.).
#     """
#     try:
#         from dashboard.permissions import is_vendor, is_b2b_user  # type: ignore
#         return is_vendor, is_b2b_user
#     except Exception:
#         return (lambda _u: False), (lambda _u: False)


# def _detect_space(request) -> str:
#     """
#     Détermine l'espace courant façon apps modernes:
#     - basé sur namespaces (vendor/b2b/social/formations/user/admin)
#     - fallback sur view_name
#     """
#     rm = getattr(request, "resolver_match", None)
#     if not rm:
#         return "dashboard"

#     nss = getattr(rm, "namespaces", None) or ()
#     view_name = str(getattr(rm, "view_name", "") or "")

#     # namespaces d'abord
#     for ns in ("admin", "vendor", "b2b", "social", "formations", "user"):
#         if ns in nss:
#             return ns

#     # fallback
#     if view_name.startswith("dashboard:admin:"):
#         return "admin"
#     if view_name.startswith("dashboard:vendor:"):
#         return "vendor"
#     if view_name.startswith("dashboard:b2b:"):
#         return "b2b"
#     if view_name.startswith("dashboard:social:"):
#         return "social"
#     if view_name.startswith("dashboard:formations:"):
#         return "formations"
#     if view_name.startswith("dashboard:user:"):
#         return "user"

#     return "dashboard"


# def dashboard_info(request) -> Dict[str, Any]:
#     """
#     Infos globales injectées dans les templates dashboard.
#     """
#     user = getattr(request, "user", None)
#     if not user or not getattr(user, "is_authenticated", False):
#         return {}

#     # Space courant (pour topbar / sidebar)
#     space = _detect_space(request)

#     # Profil status (safe)
#     get_user_profile, iter_user_profiles, detect_profile_status, _econ_flags = _safe_utils()
#     profile = None
#     try:
#         profile = get_user_profile(user)
#     except Exception:
#         profile = None

#     prof_status = ""
#     try:
#         prof_status = detect_profile_status(profile)
#     except Exception:
#         prof_status = ""

#     # mini-UX flags
#     is_vendor, is_b2b_user = _safe_permissions()

#     # flags économiques robustes (safe)
#     try:
#         profiles = iter_user_profiles(user)
#     except Exception:
#         profiles = []

#     try:
#         econ = _econ_flags(user, profiles)
#     except Exception:
#         econ = {"can_vendor": False, "can_b2b": False, "vendor_approved": False, "b2b_approved": False}

#     # Notifications (placeholder branchable plus tard)
#     notifications = 0

#     return {
#         "dashboard_user": user,
#         "dashboard_space": space,
#         "dashboard_notifications": notifications,

#         # status profil (pour badges)
#         "dashboard_profile_status": prof_status,

#         # compat rôles
#         "is_vendor": bool(is_vendor(user)),
#         "is_b2b_user": bool(is_b2b_user(user)),

#         # gating économique (pour sidebar/topbar switcher)
#         "can_vendor": bool(econ.get("can_vendor")),
#         "can_b2b": bool(econ.get("can_b2b")),
#         "vendor_approved": bool(econ.get("vendor_approved")),
#         "b2b_approved": bool(econ.get("b2b_approved")),
#     }





# # dashboard/context_processors/dashboard_context.py
# from __future__ import annotations

# from typing import Any, Dict


# def _safe_permissions():
#     """
#     Import sécurisé : évite de casser les templates si permissions import plante.
#     """
#     try:
#         from dashboard.permissions import is_vendor, is_b2b_user  # type: ignore
#         return is_vendor, is_b2b_user
#     except Exception:
#         return (lambda _u: False), (lambda _u: False)


# def dashboard_info(request) -> Dict[str, Any]:
#     """
#     Infos globales injectées dans les templates dashboard.
#     """
#     user = getattr(request, "user", None)
#     if not user or not getattr(user, "is_authenticated", False):
#         return {}

#     return {
#         "dashboard_user": user,
#         "dashboard_notifications": 0,  # placeholder
#         # ✅ Défauts sûrs pour éviter VariableDoesNotExist dans les partials
#         "page_title": "",
#         "topbar_title": "",
#         "topbar_subtitle": "",
#         "topbar_actions": "",
#     }


# def dashboard_roles(request) -> Dict[str, Any]:
#     """
#     Rôles utiles pour afficher dynamiquement sidebar / menus.
#     """
#     user = getattr(request, "user", None)
#     if not user or not getattr(user, "is_authenticated", False):
#         return {
#             "is_vendor": False,
#             "is_b2b_user": False,
#         }

#     is_vendor, is_b2b_user = _safe_permissions()

#     try:
#         return {
#             "is_vendor": bool(is_vendor(user)),
#             "is_b2b_user": bool(is_b2b_user(user)),
#         }
#     except Exception:
#         return {
#             "is_vendor": False,
#             "is_b2b_user": False,
#         }






# # dashboard/context_processors/dashboard_context.py
# from __future__ import annotations

# from typing import Any, Dict


# def _safe_permissions():
#     """
#     Import sécurisé pour éviter de casser tout le site si dashboard.permissions
#     a un problème (ImportError, circular import, etc.).
#     """
#     try:
#         from dashboard.permissions import is_vendor, is_b2b_user  # type: ignore
#         return is_vendor, is_b2b_user
#     except Exception:
#         return (lambda _u: False), (lambda _u: False)


# def dashboard_info(request) -> Dict[str, Any]:
#     """
#     Infos globales injectées dans les templates dashboard.
#     """
#     user = getattr(request, "user", None)
#     if not user or not user.is_authenticated:
#         return {}

#     return {
#         "dashboard_user": user,
#         "dashboard_notifications": 0,  # placeholder (à brancher plus tard)
#     }


# def dashboard_roles(request) -> Dict[str, Any]:
#     """
#     Rôles utiles pour afficher dynamiquement sidebar / menus.
#     """
#     user = getattr(request, "user", None)
#     if not user or not user.is_authenticated:
#         return {
#             "is_vendor": False,
#             "is_b2b_user": False,
#         }

#     is_vendor, is_b2b_user = _safe_permissions()

#     try:
#         return {
#             "is_vendor": bool(is_vendor(user)),
#             "is_b2b_user": bool(is_b2b_user(user)),
#         }
#     except Exception:
#         return {
#             "is_vendor": False,
#             "is_b2b_user": False,
#         }






# # dashboard/context_processors/dashboard_context.py

# from dashboard.permissions import is_vendor, is_b2b_user

# def dashboard_info(request):
#     """
#     Informations globales injectées dans tous les templates dashboard
#     """
#     if not request.user.is_authenticated:
#         return {}

#     return {
#         "dashboard_user": request.user,
#         "dashboard_notifications": 0,  # placeholder (à brancher plus tard)
#     }


# def dashboard_roles(request):
#     """
#     Rôles utiles pour afficher dynamiquement le sidebar / menus
#     """
#     if not request.user.is_authenticated:
#         return {
#             "is_vendor": bool,
#             "is_b2b_user": bool,
#         }

#     user = request.user

#     return {
#         "is_vendor": is_vendor(user),
#         "is_b2b_user": is_b2b_user(user),
#     }


# # dashboard/context_processors/dashboard_context.py
# def dashboard_info(request):
#     if request.user.is_authenticated:
#         return {
#             "dashboard_user": request.user,
#             "dashboard_notifications": 3,  # Exemples à adapter
#         }
#     return {}
