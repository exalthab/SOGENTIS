# dashboard/context_processors/dashboard_context.py
from __future__ import annotations

from typing import Any, Dict


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


def dashboard_info(request) -> Dict[str, Any]:
    """
    Infos globales injectées dans les templates dashboard.
    """
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return {}

    return {
        "dashboard_user": user,
        "dashboard_notifications": 0,  # placeholder (à brancher plus tard)
    }


def dashboard_roles(request) -> Dict[str, Any]:
    """
    Rôles utiles pour afficher dynamiquement sidebar / menus.
    """
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return {
            "is_vendor": False,
            "is_b2b_user": False,
        }

    is_vendor, is_b2b_user = _safe_permissions()

    try:
        return {
            "is_vendor": bool(is_vendor(user)),
            "is_b2b_user": bool(is_b2b_user(user)),
        }
    except Exception:
        return {
            "is_vendor": False,
            "is_b2b_user": False,
        }






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
