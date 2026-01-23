# dashboard/access.py
from __future__ import annotations

from functools import wraps
from typing import Any, Iterable, List, Set, Tuple

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import NoReverseMatch
from django.utils.translation import gettext_lazy as _

from dashboard.views.utils import iter_user_profiles, detect_profile_kind, detect_profile_status


# ------------------------------------------------------------
# Redirect targets (compat dashboard + accounts_users)
# ------------------------------------------------------------
PENDING_REDIRECTS: Tuple[str, ...] = (
    "dashboard:account_pending",                 # si tu as la page pending côté dashboard
    "accounts_users:web:profile:pending",        # ton URL visible sur le screenshot
    "dashboard:hub",
)

SOCIAL_FALLBACK: Tuple[str, ...] = (
    "dashboard:social:index",
    "dashboard:hub",
)


# ============================================================
# Helpers
# ============================================================

def _upper(val: Any) -> str:
    return (str(val or "")).strip().upper()


def _first_attr(obj: Any, attrs: Iterable[str], default=None):
    for a in attrs:
        try:
            return getattr(obj, a)
        except Exception:
            continue
    return default


def _try_redirect(names: Tuple[str, ...], fallback: str = "dashboard:hub"):
    for name in names:
        try:
            return redirect(name)
        except NoReverseMatch:
            continue
        except Exception:
            continue
    return redirect(fallback)


def _is_staff(user) -> bool:
    return bool(
        user
        and user.is_authenticated
        and (getattr(user, "is_staff", False) or getattr(user, "is_superuser", False))
    )


# ============================================================
# Social role detection
# ============================================================

def _membership_role_code(user) -> str:
    """
    Extract membership role code from profiles:
    - profile.membership_role.code / profile.role.code
    - profile.role_code / profile.membership_role_code
    """
    try:
        profiles = list(iter_user_profiles(user))
    except Exception:
        profiles = []

    # priorité social/generic
    for p in profiles:
        k = detect_profile_kind(p)
        if k not in {"social", "generic"}:
            continue

        role_obj = _first_attr(p, ("membership_role", "role", "membershiprole"), None)
        if role_obj:
            code = _first_attr(role_obj, ("code", "slug", "name"), "")
            if code:
                return _upper(code)

        code2 = _first_attr(p, ("role_code", "membership_role_code"), "")
        if code2:
            return _upper(code2)

    # fallback: scan tout
    for p in profiles:
        role_obj = _first_attr(p, ("membership_role", "role", "membershiprole"), None)
        if role_obj:
            code = _first_attr(role_obj, ("code", "slug", "name"), "")
            if code:
                return _upper(code)

    return ""


def require_social_role(*allowed_codes: str, fallback: Tuple[str, ...] = SOCIAL_FALLBACK):
    """
    Soft-guard social:
    - si rôle mismatch -> redirect social index (ou hub) + message
    - staff bypass
    """
    allowed: Set[str] = {_upper(c) for c in allowed_codes if c}

    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if _is_staff(request.user):
                return view_func(request, *args, **kwargs)

            code = _membership_role_code(request.user)

            if not allowed:
                return view_func(request, *args, **kwargs)

            if code in allowed:
                return view_func(request, *args, **kwargs)

            if not code:
                messages.info(request, _("Votre rôle social n’est pas encore défini."))
            else:
                messages.warning(
                    request,
                    _("Accès réservé au rôle : %(role)s.") % {"role": ", ".join(sorted(allowed))}
                )

            return _try_redirect(fallback, fallback="dashboard:hub")

        return _wrapped

    return decorator


# ============================================================
# Economic (Vendor / B2B) approvals
# ============================================================

def _economic_access_flags(user, profiles: List[Any]) -> dict:
    """
    can_* : intention/feature existe
    *_approved : accès autorisé
    """
    flags = {
        "can_vendor": False,
        "can_b2b": False,
        "vendor_approved": False,
        "b2b_approved": False,
    }

    # user flags (si existants)
    try:
        flags["can_vendor"] |= bool(getattr(user, "is_vendor", False) or getattr(user, "vendor_enabled", False))
        flags["can_b2b"] |= bool(getattr(user, "is_b2b", False) or getattr(user, "b2b_enabled", False) or getattr(user, "is_company_user", False))
    except Exception:
        pass

    # related objects (best effort)
    try:
        vendor_obj = getattr(user, "vendor", None)
    except Exception:
        vendor_obj = None

    if vendor_obj is not None:
        flags["can_vendor"] = True
        try:
            flags["vendor_approved"] |= bool(
                getattr(vendor_obj, "is_verified", False)
                or getattr(vendor_obj, "is_active", False)
                or _upper(getattr(vendor_obj, "status", "")) in {"APPROVED", "ACTIVE", "VALIDATED"}
            )
        except Exception:
            pass

    try:
        company_user = getattr(user, "company_user", None)
    except Exception:
        company_user = None

    if company_user is not None:
        flags["can_b2b"] = True
        try:
            role = _upper(getattr(company_user, "role", ""))
            status = _upper(getattr(company_user, "status", ""))
            flags["b2b_approved"] |= role in {"ADMIN", "OWNER", "MANAGER"} or status in {"APPROVED", "ACTIVE", "VALIDATED"}
        except Exception:
            pass

    # economic profile (si un profil est présent)
    eco = None
    for p in profiles:
        if detect_profile_kind(p) == "economic":
            eco = p
            break

    if eco:
        flags["can_vendor"] |= bool(_first_attr(eco, ("is_vendor", "can_vendor", "vendor_active"), False))
        flags["can_b2b"] |= bool(_first_attr(eco, ("is_b2b", "can_b2b", "company_active"), False))

        vendor_status = _upper(_first_attr(eco, ("vendor_status", "seller_status", "status_vendor"), ""))
        if vendor_status in {"APPROVED", "ACTIVE", "VALIDATED"}:
            flags["vendor_approved"] = True

        b2b_status = _upper(_first_attr(eco, ("b2b_status", "company_status", "enterprise_status"), ""))
        if b2b_status in {"APPROVED", "ACTIVE", "VALIDATED"}:
            flags["b2b_approved"] = True

        # fallback: profil eco approuvé + feature activée
        if detect_profile_status(eco) == "approved":
            if flags["can_vendor"] and not vendor_status:
                flags["vendor_approved"] = True
            if flags["can_b2b"] and not b2b_status:
                flags["b2b_approved"] = True

    return flags


def require_vendor_approved(view_func=None, *, pending_redirect: Tuple[str, ...] = PENDING_REDIRECTS):
    """
    Soft-guard vendor:
    - can_vendor True mais pas approved -> pending page (accounts_users OU dashboard) + message
    - pas vendor -> hub
    - staff bypass
    """
    def decorator(func):
        @login_required
        @wraps(func)
        def _wrapped(request, *args, **kwargs):
            if _is_staff(request.user):
                return func(request, *args, **kwargs)

            try:
                profiles = list(iter_user_profiles(request.user))
            except Exception:
                profiles = []

            flags = _economic_access_flags(request.user, profiles)

            if flags["can_vendor"] and flags["vendor_approved"]:
                return func(request, *args, **kwargs)

            if flags["can_vendor"] and not flags["vendor_approved"]:
                messages.info(request, _("Votre accès vendeur est en attente de validation."))
                return _try_redirect(pending_redirect, fallback="dashboard:hub")

            messages.warning(request, _("Accès vendeur non autorisé pour ce compte."))
            return _try_redirect(("dashboard:hub",), fallback="dashboard:hub")

        return _wrapped

    return decorator(view_func) if view_func else decorator


def require_b2b_approved(view_func=None, *, pending_redirect: Tuple[str, ...] = PENDING_REDIRECTS):
    """
    Soft-guard B2B:
    - can_b2b True mais pas approved -> pending page (accounts_users OU dashboard) + message
    - pas b2b -> hub
    - staff bypass
    """
    def decorator(func):
        @login_required
        @wraps(func)
        def _wrapped(request, *args, **kwargs):
            if _is_staff(request.user):
                return func(request, *args, **kwargs)

            try:
                profiles = list(iter_user_profiles(request.user))
            except Exception:
                profiles = []

            flags = _economic_access_flags(request.user, profiles)

            if flags["can_b2b"] and flags["b2b_approved"]:
                return func(request, *args, **kwargs)

            if flags["can_b2b"] and not flags["b2b_approved"]:
                messages.info(request, _("Votre accès entreprise (B2B) est en attente de validation."))
                return _try_redirect(pending_redirect, fallback="dashboard:hub")

            messages.warning(request, _("Accès entreprise (B2B) non autorisé pour ce compte."))
            return _try_redirect(("dashboard:hub",), fallback="dashboard:hub")

        return _wrapped

    return decorator(view_func) if view_func else decorator





# # dashboard/access.py
# from __future__ import annotations

# from functools import wraps
# from typing import Any, Iterable, List, Optional, Set, Tuple

# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import redirect
# from django.urls import NoReverseMatch
# from django.utils.translation import gettext_lazy as _

# from dashboard.views.utils import iter_user_profiles, detect_profile_kind, detect_profile_status


# # ============================================================
# # Small helpers
# # ============================================================

# def _upper(val: Any) -> str:
#     return (str(val or "")).strip().upper()


# def _first_attr(obj: Any, attrs: Iterable[str], default=None):
#     for a in attrs:
#         try:
#             return getattr(obj, a)
#         except Exception:
#             continue
#     return default


# def _try_redirect(names: Tuple[str, ...], fallback: str = "dashboard:hub"):
#     """
#     Safe redirect by url name, fallback if missing.
#     """
#     for name in names:
#         try:
#             return redirect(name)
#         except NoReverseMatch:
#             continue
#         except Exception:
#             continue
#     return redirect(fallback)


# def _is_staff(user) -> bool:
#     return bool(user and user.is_authenticated and (getattr(user, "is_staff", False) or getattr(user, "is_superuser", False)))


# # ============================================================
# # Social role detection
# # ============================================================

# def _membership_role_code(user) -> str:
#     """
#     Extract membership role code from any profile:
#     - profile.membership_role.code / profile.role.code
#     - profile.role_code / profile.membership_role_code
#     """
#     profiles = []
#     try:
#         profiles = iter_user_profiles(user)
#     except Exception:
#         profiles = []

#     # priority: social/generic
#     for p in profiles:
#         k = detect_profile_kind(p)
#         if k not in {"social", "generic"}:
#             continue

#         role_obj = _first_attr(p, ("membership_role", "role", "membershiprole"), None)
#         if role_obj:
#             code = _first_attr(role_obj, ("code", "slug", "name"), "")
#             if code:
#                 return _upper(code)

#         code2 = _first_attr(p, ("role_code", "membership_role_code"), "")
#         if code2:
#             return _upper(code2)

#     # fallback: any profile
#     for p in profiles:
#         role_obj = _first_attr(p, ("membership_role", "role", "membershiprole"), None)
#         if role_obj:
#             code = _first_attr(role_obj, ("code", "slug", "name"), "")
#             if code:
#                 return _upper(code)

#     return ""


# def require_social_role(*allowed_codes: str, fallback: str = "dashboard:social:index"):
#     """
#     Guard soft (non-bloquant): si role mismatch -> redirect social index + message.
#     Staff bypass.
#     """
#     allowed: Set[str] = {_upper(c) for c in allowed_codes if c}

#     def decorator(view_func):
#         @login_required
#         @wraps(view_func)
#         def _wrapped(request, *args, **kwargs):
#             if _is_staff(request.user):
#                 return view_func(request, *args, **kwargs)

#             code = _membership_role_code(request.user)

#             if allowed and code in allowed:
#                 return view_func(request, *args, **kwargs)

#             # si aucun code -> on laisse tomber sur social index (non bloquant)
#             if not code:
#                 messages.info(request, _("Votre rôle social n’est pas encore défini."))
#             else:
#                 messages.warning(request, _("Accès réservé au rôle : %(role)s.") % {"role": ", ".join(sorted(allowed))})

#             return _try_redirect((fallback,), fallback="dashboard:hub")

#         return _wrapped

#     return decorator


# # ============================================================
# # Economic (Vendor / B2B) approvals
# # ============================================================

# def _economic_access_flags(user, profiles: List[Any]) -> dict:
#     """
#     can_* : feature/intent exists
#     *_approved : access allowed
#     """
#     flags = {
#         "can_vendor": False,
#         "can_b2b": False,
#         "vendor_approved": False,
#         "b2b_approved": False,
#     }

#     # User flags (if present)
#     try:
#         flags["can_vendor"] |= bool(getattr(user, "is_vendor", False) or getattr(user, "vendor_enabled", False))
#         flags["can_b2b"] |= bool(getattr(user, "is_b2b", False) or getattr(user, "b2b_enabled", False) or getattr(user, "is_company_user", False))
#     except Exception:
#         pass

#     # Related objects (best effort)
#     try:
#         vendor_obj = getattr(user, "vendor", None)
#     except Exception:
#         vendor_obj = None

#     if vendor_obj is not None:
#         flags["can_vendor"] = True
#         try:
#             flags["vendor_approved"] |= bool(
#                 getattr(vendor_obj, "is_verified", False)
#                 or getattr(vendor_obj, "is_active", False)
#                 or _upper(getattr(vendor_obj, "status", "")) in {"APPROVED", "ACTIVE", "VALIDATED"}
#             )
#         except Exception:
#             pass

#     try:
#         company_user = getattr(user, "company_user", None)
#     except Exception:
#         company_user = None

#     if company_user is not None:
#         flags["can_b2b"] = True
#         try:
#             role = _upper(getattr(company_user, "role", ""))
#             status = _upper(getattr(company_user, "status", ""))
#             flags["b2b_approved"] |= role in {"ADMIN", "OWNER", "MANAGER"} or status in {"APPROVED", "ACTIVE", "VALIDATED"}
#         except Exception:
#             pass

#     # Economic profile (if any)
#     eco = None
#     for p in profiles:
#         if detect_profile_kind(p) == "economic":
#             eco = p
#             break

#     if eco:
#         flags["can_vendor"] |= bool(_first_attr(eco, ("is_vendor", "can_vendor", "vendor_active"), False))
#         flags["can_b2b"] |= bool(_first_attr(eco, ("is_b2b", "can_b2b", "company_active"), False))

#         vendor_status = _upper(_first_attr(eco, ("vendor_status", "seller_status", "status_vendor"), ""))
#         if vendor_status in {"APPROVED", "ACTIVE", "VALIDATED"}:
#             flags["vendor_approved"] = True

#         b2b_status = _upper(_first_attr(eco, ("b2b_status", "company_status", "enterprise_status"), ""))
#         if b2b_status in {"APPROVED", "ACTIVE", "VALIDATED"}:
#             flags["b2b_approved"] = True

#         # fallback simple: profile eco approved + feature enabled
#         if detect_profile_status(eco) == "approved":
#             if flags["can_vendor"] and not vendor_status:
#                 flags["vendor_approved"] = True
#             if flags["can_b2b"] and not b2b_status:
#                 flags["b2b_approved"] = True

#     return flags


# def require_vendor_approved(view_func=None, *, pending_redirect: Tuple[str, ...] = ("dashboard:account_pending", "dashboard:hub")):
#     """
#     Guard vendor (soft):
#     - si vendor exists mais pas approuvé -> account_pending (ou hub)
#     - si pas vendor du tout -> hub
#     Staff bypass.
#     """
#     def decorator(func):
#         @login_required
#         @wraps(func)
#         def _wrapped(request, *args, **kwargs):
#             if _is_staff(request.user):
#                 return func(request, *args, **kwargs)

#             try:
#                 profiles = iter_user_profiles(request.user)
#             except Exception:
#                 profiles = []

#             flags = _economic_access_flags(request.user, profiles)

#             if flags["can_vendor"] and flags["vendor_approved"]:
#                 return func(request, *args, **kwargs)

#             if flags["can_vendor"] and not flags["vendor_approved"]:
#                 messages.info(request, _("Votre accès vendeur est en attente de validation."))
#                 return _try_redirect(pending_redirect, fallback="dashboard:hub")

#             messages.warning(request, _("Accès vendeur non autorisé pour ce compte."))
#             return _try_redirect(("dashboard:hub",), fallback="dashboard:hub")

#         return _wrapped

#     return decorator(view_func) if view_func else decorator


# def require_b2b_approved(view_func=None, *, pending_redirect: Tuple[str, ...] = ("dashboard:account_pending", "dashboard:hub")):
#     """
#     Guard B2B (soft):
#     - si b2b exists mais pas approuvé -> account_pending (ou hub)
#     - si pas b2b du tout -> hub
#     Staff bypass.
#     """
#     def decorator(func):
#         @login_required
#         @wraps(func)
#         def _wrapped(request, *args, **kwargs):
#             if _is_staff(request.user):
#                 return func(request, *args, **kwargs)

#             try:
#                 profiles = iter_user_profiles(request.user)
#             except Exception:
#                 profiles = []

#             flags = _economic_access_flags(request.user, profiles)

#             if flags["can_b2b"] and flags["b2b_approved"]:
#                 return func(request, *args, **kwargs)

#             if flags["can_b2b"] and not flags["b2b_approved"]:
#                 messages.info(request, _("Votre accès entreprise (B2B) est en attente de validation."))
#                 return _try_redirect(pending_redirect, fallback="dashboard:hub")

#             messages.warning(request, _("Accès entreprise (B2B) non autorisé pour ce compte."))
#             return _try_redirect(("dashboard:hub",), fallback="dashboard:hub")

#         return _wrapped

#     return decorator(view_func) if view_func else decorator







# # dashboard/access.py
# from __future__ import annotations

# from functools import wraps
# from typing import Callable, Any

# from django.contrib import messages
# from django.shortcuts import redirect
# from django.utils.translation import gettext_lazy as _

# from dashboard.views.utils import iter_user_profiles, detect_profile_kind, detect_profile_status


# def _economic_profile(user):
#     for p in iter_user_profiles(user):
#         if detect_profile_kind(p) == "economic":
#             return p
#     return None


# def require_vendor_approved(view_func: Callable[..., Any]):
#     """
#     Autorise l'accès aux vues Vendor seulement si vendor_approved.
#     Sinon: redirect hub + message (sans bloquer le reste).
#     """
#     @wraps(view_func)
#     def _wrapped(request, *args, **kwargs):
#         eco = _economic_profile(request.user)

#         # aucune structure eco => pas vendor
#         if not eco:
#             messages.info(request, _("Cette section nécessite un profil économique."))
#             return redirect("dashboard:hub")

#         status = (getattr(eco, "vendor_status", "") or "").upper().strip()
#         if status in {"APPROVED", "ACTIVE", "VALIDATED"}:
#             return view_func(request, *args, **kwargs)

#         # fallback: si profil eco approved + tu n'as pas vendor_status
#         if not status and detect_profile_status(eco) == "approved":
#             return view_func(request, *args, **kwargs)

#         messages.warning(request, _("Votre accès vendeur est en attente de validation."))
#         return redirect("dashboard:hub")
#     return _wrapped


# def require_b2b_approved(view_func: Callable[..., Any]):
#     """
#     Autorise l'accès aux vues B2B seulement si b2b_approved.
#     """
#     @wraps(view_func)
#     def _wrapped(request, *args, **kwargs):
#         eco = _economic_profile(request.user)
#         if not eco:
#             messages.info(request, _("Cette section nécessite un profil économique."))
#             return redirect("dashboard:hub")

#         status = (getattr(eco, "b2b_status", "") or getattr(eco, "company_status", "") or "").upper().strip()
#         if status in {"APPROVED", "ACTIVE", "VALIDATED"}:
#             return view_func(request, *args, **kwargs)

#         if not status and detect_profile_status(eco) == "approved":
#             return view_func(request, *args, **kwargs)

#         messages.warning(request, _("Votre accès entreprise (B2B) est en attente de validation."))
#         return redirect("dashboard:hub")
#     return _wrapped
