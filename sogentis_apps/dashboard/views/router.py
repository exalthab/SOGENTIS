# dashboard/views/router.py
from __future__ import annotations

import logging
from typing import Any, Iterable, List

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import NoReverseMatch
from django.utils.http import url_has_allowed_host_and_scheme

from dashboard.views.utils import iter_user_profiles, detect_profile_kind, detect_profile_status

logger = logging.getLogger(__name__)


# ============================================================
# Helpers
# ============================================================

def _safe_next_url(request: HttpRequest) -> str:
    nxt = (request.POST.get("next") or request.GET.get("next") or "").strip()
    if not nxt or nxt == request.path:
        return ""
    if url_has_allowed_host_and_scheme(
        url=nxt,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return nxt
    return ""


def _try_redirect(names: Iterable[str], *, fallback: str):
    for name in names:
        try:
            return redirect(name)
        except NoReverseMatch:
            continue
        except Exception:
            continue
    return redirect(fallback)


def _upper(val) -> str:
    return (str(val or "")).strip().upper()


def _first_attr(obj, attrs: Iterable[str], default=None):
    for a in attrs:
        try:
            return getattr(obj, a)
        except Exception:
            continue
    return default


def _requested_context(request: HttpRequest) -> str:
    pole = (request.GET.get("context") or request.GET.get("pole") or "").strip().lower()
    if not pole:
        pole = (request.session.get("login_context") or request.session.get("auth_pole") or "").strip().lower()
    if pole not in {"social", "economic", "generic"}:
        return ""
    return pole


def _extract_membership_role_code_from_profiles(profiles: List[Any]) -> str:
    """
    Cherche un membership role code dans tous les profils.
    Priorité aux profils social/generic.
    """
    def _scan(items: List[Any], restrict_kinds: set[str] | None) -> str:
        for p in items:
            if restrict_kinds is not None:
                k = detect_profile_kind(p)
                if k not in restrict_kinds:
                    continue

            role_obj = _first_attr(p, ("membership_role", "role", "membershiprole"), None)
            if role_obj:
                code = _first_attr(role_obj, ("code", "slug", "name"), "")
                if code:
                    return _upper(code)

            code2 = _first_attr(p, ("role_code", "membership_role_code"), "")
            if code2:
                return _upper(code2)

        return ""

    code = _scan(profiles, {"social", "generic"})
    if code:
        return code
    return _scan(profiles, None)


def _route_social_by_role(role_code: str):
    rc = _upper(role_code)

    if rc in {"SPONSOR", "DONOR"}:
        return _try_redirect(names=("dashboard:social:donor_home",), fallback="dashboard:social:index")

    if rc == "VOLUNTEER":
        return _try_redirect(names=("dashboard:social:volunteer_home",), fallback="dashboard:social:index")

    if rc == "MEMBER":
        return _try_redirect(names=("dashboard:social:member_home",), fallback="dashboard:social:index")

    if rc == "INSTITUTION":
        return _try_redirect(names=("dashboard:social:institution_home",), fallback="dashboard:social:index")

    if rc == "BENEFICIARY":
        return _try_redirect(names=("dashboard:social:beneficiary_home",), fallback="dashboard:social:index")

    return redirect("dashboard:social:index")


def _economic_access_flags(user, profiles: List[Any]) -> dict:
    """
    Distingue:
    - can_vendor / can_b2b: fonctionnalité “possible”
    - vendor_approved / b2b_approved: accès “autorisé”
    """
    flags = {
        "can_vendor": False,
        "can_b2b": False,
        "vendor_approved": False,
        "b2b_approved": False,
    }

    # flags user
    try:
        flags["can_vendor"] |= bool(getattr(user, "is_vendor", False) or getattr(user, "vendor_enabled", False))
        flags["can_b2b"] |= bool(
            getattr(user, "is_b2b", False)
            or getattr(user, "b2b_enabled", False)
            or getattr(user, "is_company_user", False)
        )
    except Exception:
        pass

    # related objects (safe)
    vendor = None
    company_user = None
    try:
        vendor = getattr(user, "vendor", None)
    except Exception:
        vendor = None
    try:
        company_user = getattr(user, "company_user", None)
    except Exception:
        company_user = None

    if vendor is not None:
        flags["can_vendor"] = True
        try:
            flags["vendor_approved"] = bool(getattr(vendor, "is_verified", False) or getattr(vendor, "is_active", False))
        except Exception:
            pass

    if company_user is not None:
        flags["can_b2b"] = True
        try:
            role = str(getattr(company_user, "role", "") or "").strip().upper()
            status = str(getattr(company_user, "status", "") or "").strip().upper()
            # On considère b2b_approved si rôle OK ou status OK (selon ton modèle)
            flags["b2b_approved"] = role in {"ADMIN", "OWNER", "MANAGER"} or status in {"APPROVED", "ACTIVE", "VALIDATED"}
        except Exception:
            pass

    # profil economic
    eco = None
    for p in profiles:
        if detect_profile_kind(p) == "economic":
            eco = p
            break

    if eco:
        # capacités
        flags["can_vendor"] |= bool(_first_attr(eco, ("is_vendor", "can_vendor", "vendor_active"), False))
        flags["can_b2b"] |= bool(_first_attr(eco, ("is_b2b", "can_b2b", "company_active"), False))

        # statuts dédiés
        vendor_status = _upper(_first_attr(eco, ("vendor_status", "seller_status", "status_vendor"), ""))
        if vendor_status in {"APPROVED", "ACTIVE", "VALIDATED"}:
            flags["vendor_approved"] = True

        b2b_status = _upper(_first_attr(eco, ("b2b_status", "company_status", "enterprise_status"), ""))
        if b2b_status in {"APPROVED", "ACTIVE", "VALIDATED"}:
            flags["b2b_approved"] = True

        # fallback simple: si le profil eco global est approved, et pas de statuts spécifiques -> accès basique
        if detect_profile_status(eco) == "approved":
            if flags["can_vendor"] and not vendor_status:
                flags["vendor_approved"] = True
            if flags["can_b2b"] and not b2b_status:
                flags["b2b_approved"] = True

    return flags


# ============================================================
# Router
# ============================================================

@login_required
def dashboard_router(request: HttpRequest):
    """
    Router global dashboard.

    IMPORTANT:
    - Le statut du profil ne doit PAS impacter la navigation normale du site.
    - Ici, on ne fait QUE choisir une landing page dashboard.
    - Les restrictions réelles (ex: vendor/b2b) doivent être dans les views/modules (guards).
    """
    user = request.user

    # 0) next=
    nxt = _safe_next_url(request)
    if nxt:
        return redirect(nxt)

    # 1) admin
    if getattr(user, "is_superuser", False) or getattr(user, "is_staff", False):
        return redirect("dashboard:admin:index")

    # 2) collect profils (safe)
    try:
        profiles = iter_user_profiles(user)
    except Exception:
        logger.exception("iter_user_profiles failed user_id=%s", getattr(user, "id", None))
        profiles = []

    role_code = _extract_membership_role_code_from_profiles(profiles)
    econ = _economic_access_flags(user, profiles)
    pole = _requested_context(request)

    # 3) context explicite
    if pole == "social":
        if role_code:
            return _route_social_by_role(role_code)
        return redirect("dashboard:social:index")

    if pole == "economic":
        # On n’envoie vers vendor/b2b que si approuvé
        if econ.get("can_vendor") and econ.get("vendor_approved"):
            return redirect("dashboard:vendor:home")
        if econ.get("can_b2b") and econ.get("b2b_approved"):
            return redirect("dashboard:b2b:home")

        # sinon hub (non bloquant)
        return redirect("dashboard:hub")

    # 4) sans context : rôle social prioritaire
    if role_code:
        return _route_social_by_role(role_code)

    # 5) sinon, si vendor/b2b approuvé -> accès direct
    if econ.get("can_vendor") and econ.get("vendor_approved"):
        return redirect("dashboard:vendor:home")
    if econ.get("can_b2b") and econ.get("b2b_approved"):
        return redirect("dashboard:b2b:home")

    # 6) default
    return redirect("dashboard:hub")





# # dashboard/views/router.py
# from __future__ import annotations

# import logging
# from typing import Iterable

# from django.contrib.auth.decorators import login_required
# from django.http import HttpRequest
# from django.shortcuts import redirect
# from django.urls import NoReverseMatch
# from django.utils.http import url_has_allowed_host_and_scheme

# from dashboard.views.utils import (
#     get_user_profile,
#     iter_user_profiles,
#     user_has_pending_or_refused_profile,
# )

# logger = logging.getLogger(__name__)


# # ============================================================
# # Helpers
# # ============================================================

# def _safe_next_url(request: HttpRequest) -> str:
#     nxt = (request.POST.get("next") or request.GET.get("next") or "").strip()
#     if not nxt or nxt == request.path:
#         return ""

#     allowed_hosts = {request.get_host()}
#     if url_has_allowed_host_and_scheme(
#         url=nxt,
#         allowed_hosts=allowed_hosts,
#         require_https=request.is_secure(),
#     ):
#         return nxt
#     return ""


# def _try_redirect(names: Iterable[str], *, fallback: str):
#     for name in names:
#         try:
#             return redirect(name)
#         except NoReverseMatch:
#             continue
#     return redirect(fallback)


# def _upper(val) -> str:
#     return (str(val or "")).strip().upper()


# def _first_attr(obj, attrs: Iterable[str], default=None):
#     for a in attrs:
#         try:
#             if hasattr(obj, a):
#                 return getattr(obj, a, default)
#         except Exception:
#             continue
#     return default


# def _bool_attr(obj, attrs: Iterable[str]) -> bool:
#     for a in attrs:
#         try:
#             if hasattr(obj, a):
#                 return bool(getattr(obj, a))
#         except Exception:
#             continue
#     return False


# def _extract_membership_role_code_from_profiles(user) -> str:
#     """
#     Cherche un rôle membership en priorité sur social/generic, puis autres profils.
#     (Important: ne pas dépendre du profil “principal” si economic_profile existe.)
#     """
#     profiles = list(iter_user_profiles(user))

#     # priorité : social puis generic puis economic (heuristique par nom)
#     def score(p) -> int:
#         n = p.__class__.__name__.lower()
#         if "social" in n:
#             return 0
#         if "userprofile" in n or n == "userprofile" or "profile" == n:
#             return 1
#         if "economic" in n:
#             return 2
#         return 3

#     profiles.sort(key=score)

#     for profile in profiles:
#         role_obj = _first_attr(profile, ("membership_role", "role", "membershiprole"), None)
#         if role_obj:
#             code = _first_attr(role_obj, ("code", "slug", "name"), "")
#             code = _upper(code)
#             if code:
#                 return code

#         # fallback: parfois stocké direct
#         direct = _upper(_first_attr(profile, ("role_code", "membership_role_code"), ""))
#         if direct:
#             return direct

#     return ""


# def _economic_access_flags(user, profile) -> dict:
#     """
#     Détecte l’accès vendor / b2b via attributs courants.
#     On regarde user + economic_profile si présent.
#     """
#     flags = {"can_vendor": False, "can_b2b": False}

#     flags["can_vendor"] |= _bool_attr(user, ("is_vendor", "vendor_enabled"))
#     flags["can_b2b"] |= _bool_attr(user, ("is_b2b", "b2b_enabled", "is_company_user"))

#     eco = _first_attr(user, ("economic_profile", "economicprofile", "eco_profile", "ecoprofile"), None)
#     if eco is None and profile is not None:
#         eco = _first_attr(profile, ("economic_profile", "eco_profile"), None)

#     if eco:
#         flags["can_vendor"] |= _bool_attr(eco, ("is_vendor", "can_vendor", "vendor_active"))
#         flags["can_b2b"] |= _bool_attr(eco, ("is_b2b", "can_b2b", "company_active"))

#         vendor_status = _upper(_first_attr(eco, ("vendor_status",), ""))
#         if vendor_status in {"APPROVED", "ACTIVE", "VALIDATED"}:
#             flags["can_vendor"] = True

#         b2b_status = _upper(_first_attr(eco, ("b2b_status", "company_status"), ""))
#         if b2b_status in {"APPROVED", "ACTIVE", "VALIDATED"}:
#             flags["can_b2b"] = True

#     return flags


# def _requested_context(request: HttpRequest) -> str:
#     pole = (request.GET.get("context") or request.GET.get("pole") or "").strip().lower()
#     if not pole:
#         pole = (request.session.get("login_context") or request.session.get("auth_pole") or "").strip().lower()
#     if pole not in {"social", "economic", "generic"}:
#         pole = ""
#     return pole


# def _route_social_by_role(role_code: str):
#     rc = _upper(role_code)

#     if rc in {"SPONSOR", "DONOR"}:
#         return redirect("dashboard:social:donor_home")

#     if rc == "VOLUNTEER":
#         return redirect("dashboard:social:volunteer_home")

#     if rc == "MEMBER":
#         return redirect("dashboard:social:member_home")

#     if rc == "INSTITUTION":
#         return redirect("dashboard:social:institution_home")

#     if rc == "BENEFICIARY":
#         return redirect("dashboard:social:beneficiary_home")

#     # rôle inconnu → router social
#     return redirect("dashboard:social:index")


# # ============================================================
# # Router
# # ============================================================

# @login_required
# def dashboard_router(request: HttpRequest):
#     """
#     Router global dashboard.

#     Règles:
#     0) next= safe -> on respecte
#     1) Staff/Superuser -> dashboard admin
#     2) Si un des profils est pending/rejected -> page utilisateur account_pending
#     3) context=social/economic -> redirection ciblée si possible
#     4) role social (MembershipRole) -> pages social dédiées
#     5) sinon -> hub
#     """
#     user = request.user

#     # 0) next=
#     nxt = _safe_next_url(request)
#     if nxt:
#         return redirect(nxt)

#     # 1) Admin
#     if user.is_superuser or user.is_staff:
#         return redirect("dashboard:admin:index")

#     # Profil “principal” (utile pour eco flags), mais on ne l’utilise pas pour détecter pending global
#     profile = None
#     try:
#         # preferred vide => social d’abord (cf utils.py)
#         profile = get_user_profile(user)
#     except Exception:
#         logger.exception("get_user_profile failed user_id=%s", getattr(user, "id", None))

#     # 2) Pending/refused global (social/economic/generic)
#     try:
#         if user_has_pending_or_refused_profile(user):
#             return redirect("dashboard:account_pending")
#     except Exception:
#         logger.exception("pending/refused detection failed user_id=%s", getattr(user, "id", None))

#     # Données rôle + accès eco
#     role_code = _extract_membership_role_code_from_profiles(user)
#     econ = _economic_access_flags(user, profile)
#     pole = _requested_context(request)

#     # 3) Context explicite
#     if pole == "social":
#         if role_code:
#             return _route_social_by_role(role_code)
#         return redirect("dashboard:social:index")

#     if pole == "economic":
#         # priorité: vendor -> b2b -> formations
#         if econ.get("can_vendor"):
#             return redirect("dashboard:vendor:home")
#         if econ.get("can_b2b"):
#             return redirect("dashboard:b2b:home")
#         return redirect("dashboard:formations:home")

#     # 4) Social role-based (si pas de context)
#     if role_code:
#         return _route_social_by_role(role_code)

#     # 5) Default
#     return redirect("dashboard:hub")





# # dashboard/views/router.py
# from __future__ import annotations

# import logging
# from typing import Iterable

# from django.contrib.auth.decorators import login_required
# from django.http import HttpRequest
# from django.shortcuts import redirect
# from django.urls import NoReverseMatch, reverse
# from django.utils.http import url_has_allowed_host_and_scheme

# from dashboard.views.utils import get_user_profile

# logger = logging.getLogger(__name__)


# # ============================================================
# # Helpers
# # ============================================================

# def _safe_next_url(request: HttpRequest) -> str:
#     """
#     Récupère ?next= (GET/POST) et vérifie qu'il est sûr (même host / https si besoin).
#     """
#     nxt = (request.POST.get("next") or request.GET.get("next") or "").strip()
#     if not nxt or nxt == request.path:
#         return ""

#     allowed_hosts = {request.get_host()}
#     if url_has_allowed_host_and_scheme(
#         url=nxt,
#         allowed_hosts=allowed_hosts,
#         require_https=request.is_secure(),
#     ):
#         return nxt
#     return ""


# def _try_redirect(names: Iterable[str], *, fallback: str):
#     """
#     Essaie le premier url_name existant, sinon fallback.
#     """
#     for name in names:
#         try:
#             return redirect(name)
#         except NoReverseMatch:
#             continue
#     return redirect(fallback)


# def _upper(val) -> str:
#     return (str(val or "")).strip().upper()


# def _first_attr(obj, attrs: Iterable[str], default=None):
#     for a in attrs:
#         if hasattr(obj, a):
#             return getattr(obj, a, default)
#     return default


# def _bool_attr(obj, attrs: Iterable[str]) -> bool:
#     for a in attrs:
#         if hasattr(obj, a):
#             try:
#                 return bool(getattr(obj, a))
#             except Exception:
#                 continue
#     return False


# def _extract_membership_role_code(profile) -> str:
#     """
#     Supporte plusieurs structures:
#     - profile.role.code
#     - profile.membership_role.code
#     - role.slug / role.name
#     - profile.role_code (fallback)
#     """
#     if not profile:
#         return ""

#     role_obj = _first_attr(profile, ("role", "membership_role", "membershiprole"), None)
#     if role_obj:
#         return _upper(_first_attr(role_obj, ("code", "slug", "name"), ""))

#     return _upper(_first_attr(profile, ("role_code", "membership_role_code"), ""))


# def _profile_is_pending_or_refused(profile) -> bool:
#     """
#     Détecte "pending/refused" sans imposer un seul champ.
#     Si tu as un modèle SocialProfile/EconomicProfile, ça reste safe.
#     """
#     if not profile:
#         return False

#     # flags explicites
#     if _bool_attr(profile, ("is_pending", "pending_validation")):
#         return True
#     if _bool_attr(profile, ("is_refused", "is_rejected")):
#         return True

#     # status textuel
#     status = _upper(_first_attr(profile, ("status", "validation_status", "account_status"), ""))
#     if status in {"PENDING", "WAITING", "TO_VALIDATE", "AWAITING", "REFUSED", "REJECTED", "BANNED", "DISABLED"}:
#         return True

#     # approved flag inverse
#     if hasattr(profile, "is_approved") and not bool(getattr(profile, "is_approved")):
#         return True
#     if hasattr(profile, "is_validated") and not bool(getattr(profile, "is_validated")):
#         return True

#     return False


# def _economic_access_flags(user, profile) -> dict:
#     """
#     Détecte l’accès vendor / b2b via attributs courants (sans casser si absent).
#     """
#     flags = {"can_vendor": False, "can_b2b": False}

#     # sur user
#     flags["can_vendor"] |= _bool_attr(user, ("is_vendor", "vendor_enabled"))
#     flags["can_b2b"] |= _bool_attr(user, ("is_b2b", "b2b_enabled", "is_company_user"))

#     # sur economic_profile si présent
#     eco = _first_attr(user, ("economic_profile", "economicprofile", "eco_profile", "ecoprofile"), None)
#     if eco is None and profile is not None:
#         eco = _first_attr(profile, ("economic_profile", "eco_profile"), None)

#     if eco:
#         flags["can_vendor"] |= _bool_attr(eco, ("is_vendor", "can_vendor", "vendor_active"))
#         flags["can_b2b"] |= _bool_attr(eco, ("is_b2b", "can_b2b", "company_active"))

#         vendor_status = _upper(_first_attr(eco, ("vendor_status",), ""))
#         if vendor_status in {"APPROVED", "ACTIVE", "VALIDATED"}:
#             flags["can_vendor"] = True

#         b2b_status = _upper(_first_attr(eco, ("b2b_status", "company_status"), ""))
#         if b2b_status in {"APPROVED", "ACTIVE", "VALIDATED"}:
#             flags["can_b2b"] = True

#     return flags


# def _requested_context(request: HttpRequest) -> str:
#     """
#     ?context=social|economic|generic ou ?pole= ...
#     + fallback session si posé au login.
#     """
#     pole = (request.GET.get("context") or request.GET.get("pole") or "").strip().lower()
#     if not pole:
#         pole = (request.session.get("login_context") or request.session.get("auth_pole") or "").strip().lower()
#     if pole not in {"social", "economic", "generic"}:
#         pole = ""
#     return pole


# def _route_social_by_role(role_code: str):
#     """
#     Codes officiels (MembershipRole):
#     MEMBER / VOLUNTEER / SPONSOR / INSTITUTION
#     + tolérance DONOR/BENEFICIARY
#     """
#     rc = _upper(role_code)

#     if rc in {"SPONSOR", "DONOR"}:
#         return _try_redirect(
#             names=("dashboard:social:donor_home",),
#             fallback="dashboard:social:index",
#         )

#     if rc == "VOLUNTEER":
#         return _try_redirect(
#             names=("dashboard:social:volunteer_home",),
#             fallback="dashboard:social:index",
#         )

#     if rc == "MEMBER":
#         return _try_redirect(
#             names=("dashboard:social:member_home",),
#             fallback="dashboard:social:index",
#         )

#     if rc == "INSTITUTION":
#         return _try_redirect(
#             names=("dashboard:social:institution_home",),
#             fallback="dashboard:social:index",
#         )

#     if rc == "BENEFICIARY":
#         return _try_redirect(
#             names=("dashboard:social:beneficiary_home",),
#             fallback="dashboard:social:index",
#         )

#     return redirect("dashboard:social:index")


# # ============================================================
# # Router
# # ============================================================

# @login_required
# def dashboard_router(request: HttpRequest):
#     """
#     Router global dashboard.

#     Règles:
#     0) next= safe -> on respecte
#     1) Staff/Superuser -> dashboard admin
#     2) Profil pending/refused -> page "pending" si tu l’ajoutes, sinon hub
#     3) context=social/economic -> redirection ciblée si possible
#     4) role social (MembershipRole) -> pages social dédiées
#     5) sinon -> hub
#     """
#     user = request.user

#     # 0) next=
#     nxt = _safe_next_url(request)
#     if nxt:
#         return redirect(nxt)

#     # 1) Admin
#     if user.is_superuser or user.is_staff:
#         return redirect("dashboard:admin:index")

#     # 2) Profile + status
#     profile = None
#     try:
#         profile = get_user_profile(user)
#     except Exception:
#         logger.exception("get_user_profile failed user_id=%s", getattr(user, "id", None))

#     if profile and _profile_is_pending_or_refused(profile):
#         # ⚠️ Tu n’as pas encore d’URL publique "account_pending" dans tes urls.
#         # On tente si elle existe, sinon fallback hub.
#         return _try_redirect(
#             names=("dashboard:account_pending", "dashboard:pending"),
#             fallback="dashboard:hub",
#         )

#     role_code = _extract_membership_role_code(profile)
#     econ = _economic_access_flags(user, profile)
#     pole = _requested_context(request)

#     # 3) Context explicite
#     if pole == "social":
#         if role_code:
#             return _route_social_by_role(role_code)
#         return redirect("dashboard:social:index")

#     if pole == "economic":
#         # priorité vendor puis b2b (modifie si tu veux)
#         if econ.get("can_vendor"):
#             return redirect("dashboard:vendor:home")
#         if econ.get("can_b2b"):
#             return redirect("dashboard:b2b:home")
#         # à défaut, hub (ou formations si tu préfères)
#         return redirect("dashboard:hub")

#     # 4) Social role-based (si pas de context)
#     if role_code:
#         return _route_social_by_role(role_code)

#     # 5) Default
#     return redirect("dashboard:hub")







# # dashboard/views/router.py
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import redirect

# from dashboard.views.utils import get_user_profile


# @login_required
# def dashboard_router(request):
#     """
#     Router global dashboard (production).

#     Règles:
#     1) Staff/Admin -> dashboard admin
#     2) Selon rôle membership (Social) -> pages social dédiées
#     3) Sinon -> hub (home dashboard)
#     """
#     user = request.user

#     # 1) STAFF / ADMIN
#     if user.is_staff or user.is_superuser:
#         # ✅ adapte selon tes urls admin:
#         # - dans _sidebar_premium.html tu as: {% url 'dashboard:admin:index' %}
#         # Donc on utilise "dashboard:admin:index".
#         return redirect("dashboard:admin:index")

#     # 2) ROLE (membership) — via profile.role.code / slug
#     profile = get_user_profile(user)
#     role_code = ""

#     if profile is not None:
#         role = getattr(profile, "role", None)
#         if role:
#             role_code = (getattr(role, "code", "") or getattr(role, "slug", "") or "").upper()

#     # Social routes (si tu as ces noms exacts)
#     if role_code in {"SPONSOR", "DONOR"}:
#         # si tu as un nom plus simple, tu peux changer ici
#         try:
#             return redirect("dashboard:social:donor_home")
#         except Exception:
#             return redirect("dashboard:social:index")

#     if role_code in {"VOLUNTEER"}:
#         try:
#             return redirect("dashboard:social:volunteer_home")
#         except Exception:
#             return redirect("dashboard:social:index")

#     if role_code in {"MEMBER"}:
#         try:
#             return redirect("dashboard:social:member_home")
#         except Exception:
#             return redirect("dashboard:social:index")

#     if role_code in {"INSTITUTION"}:
#         try:
#             return redirect("dashboard:social:institution_home")
#         except Exception:
#             return redirect("dashboard:social:index")

#     # 3) DEFAULT
#     return redirect("dashboard:hub")








# # dashboard/views/router.py
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import redirect
# from django.urls import reverse

# from dashboard.views.utils import get_user_profile


# @login_required
# def dashboard_router(request):
#     """
#     Router global dashboard:
#     - staff -> hub
#     - sinon redirige vers hub (qui propose les espaces)
#     """
#     if request.user.is_staff:
#         return redirect("dashboard:hub")

#     # Si tu veux router automatiquement selon rôle membership:
#     profile = get_user_profile(request.user)
#     if profile and hasattr(profile, "role") and profile.role:
#         code = getattr(profile.role, "code", "") or getattr(profile.role, "slug", "")
#         code = (code or "").upper()
#         if code in {"SPONSOR", "DONOR"}:
#             return redirect("dashboard:social:donor_home")
#         if code in {"VOLUNTEER"}:
#             return redirect("dashboard:social:volunteer_home")
#         if code in {"MEMBER"}:
#             return redirect("dashboard:social:member_home")
#         if code in {"INSTITUTION"}:
#             return redirect("dashboard:social:institution_home")

#     return redirect("dashboard:hub")





# # /dashboard/views/router.py

# from django.shortcuts import redirect
# from django.contrib.auth.decorators import login_required

# from .hub import dashboard_hub_view


# @login_required
# def dashboard_router(request):
#     """
#     Router central du dashboard.
#     Utilise la même logique que dashboard_hub_view.
#     Branché sur la racine de /dashboard/ (voir dashboard/urls.py).
#     """
#     return dashboard_hub_view(request)






# # dashboard/views/router.py

# from django.shortcuts import redirect
# from django.contrib.auth.decorators import login_required

# from dashboard.permissions import (
#     is_admin,
#     is_vendor,
#     is_b2b_user,
# )


# @login_required
# def dashboard_router(request):
#     """
#     Router central du dashboard.
#     Redirige l'utilisateur selon son rôle principal.
#     Ordre de priorité :
#     1. Admin / Staff
#     2. Vendeur
#     3. B2B
#     4. Utilisateur standard
#     """

#     user = request.user

#     # =====================================================
#     # ADMIN / STAFF
#     # =====================================================
#     if is_admin(user) or user.is_staff:
#         return redirect("dashboard:admin_home")

#     # =====================================================
#     # VENDEUR
#     # =====================================================
#     if is_vendor(user):
#         return redirect("dashboard:vendor_index")

#     # =====================================================
#     # B2B
#     # =====================================================
#     if is_b2b_user(user):
#         return redirect("dashboard:b2b_home")

#     # =====================================================
#     # UTILISATEUR STANDARD
#     # =====================================================
#     return redirect("dashboard:user_home")




# # dashboard/views/router.py
# from django.shortcuts import redirect
# from django.contrib.auth.decorators import login_required

# from dashboard.permissions import (
#     is_admin,
#     is_vendor,
#     is_b2b_user,
# )


# @login_required
# def dashboard_router(request):
#     user = request.user

#     # if is_admin(user):
#     #     return redirect("dashboard:admin_home")

#     if is_vendor(user):
#         return redirect("dashboard:vendor_home")

#     if is_b2b_user(user):
#         return redirect("dashboard:b2b_home")

#     return redirect("dashboard:user_home")
