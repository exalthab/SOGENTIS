# dashboard/context_processors/dashboard_context.py
from __future__ import annotations

from typing import Any, Dict


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


def _detect_space(request) -> str:
    """
    Détermine l'espace courant façon apps modernes:
    - basé sur namespaces (vendor/b2b/social/formations/user/admin)
    - fallback sur view_name
    """
    rm = getattr(request, "resolver_match", None)
    if not rm:
        return "dashboard"

    nss = getattr(rm, "namespaces", None) or ()
    view_name = str(getattr(rm, "view_name", "") or "")

    # namespaces d'abord
    for ns in ("admin", "vendor", "b2b", "social", "formations", "user"):
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

    return "dashboard"


def dashboard_info(request) -> Dict[str, Any]:
    """
    Infos globales injectées dans les templates dashboard.
    """
    user = getattr(request, "user", None)
    if not user or not getattr(user, "is_authenticated", False):
        return {}

    # Space courant (pour topbar / sidebar)
    space = _detect_space(request)

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

    # Notifications (placeholder branchable plus tard)
    notifications = 0

    return {
        "dashboard_user": user,
        "dashboard_space": space,
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
    }


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
        }

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

    try:
        return {
            "is_vendor": bool(is_vendor(user)),
            "is_b2b_user": bool(is_b2b_user(user)),
            "can_vendor": bool(econ.get("can_vendor")),
            "can_b2b": bool(econ.get("can_b2b")),
            "vendor_approved": bool(econ.get("vendor_approved")),
            "b2b_approved": bool(econ.get("b2b_approved")),
        }
    except Exception:
        return {
            "is_vendor": False,
            "is_b2b_user": False,
            "can_vendor": False,
            "can_b2b": False,
            "vendor_approved": False,
            "b2b_approved": False,
        }







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
