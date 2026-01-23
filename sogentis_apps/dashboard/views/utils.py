# dashboard/views/utils.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, Tuple, Type, Iterable, List, Dict

from django.apps import apps
from django.contrib import messages
from django.core.exceptions import FieldDoesNotExist
from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import NoReverseMatch, reverse
from django.utils.translation import gettext_lazy as _


# =====================================================
# Fields helpers (safe)
# =====================================================
def has_field(model: Type[Any], field_name: str) -> bool:
    try:
        model._meta.get_field(field_name)
        return True
    except FieldDoesNotExist:
        return False
    except Exception:
        return False


def _safe_getattr(obj: Any, attr: str) -> Any:
    """
    Accès safe aux OneToOne / related_name.
    Django peut lever RelatedObjectDoesNotExist si non existant.
    """
    try:
        return getattr(obj, attr, None)
    except Exception:
        return None


def _upper(val: Any) -> str:
    return (str(val or "")).strip().upper()


def _lower(val: Any) -> str:
    return (str(val or "")).strip().lower()


def _first_attr(obj: Any, attrs: Iterable[str], default=None):
    for a in attrs:
        try:
            if hasattr(obj, a):
                return getattr(obj, a)
        except Exception:
            continue
    return default


def _safe_model(app_label: str, model_name: str):
    """
    apps.get_model safe.
    """
    try:
        return apps.get_model(app_label, model_name)
    except Exception:
        return None


# =====================================================
# Profile resolver (SOCIAL + ECONOMIC + legacy)
# =====================================================
PROFILE_ATTR_CANDIDATES: Tuple[str, ...] = (
    "profile",
    "social_profile",
    "economic_profile",
    "userprofile",
    "socialprofile",
    "economicprofile",
    "usersocialprofile",
    "usereconomicprofile",
    "user_economic_profile",
    "social",
    "economic",
)

# (app_label, model_name, kind_hint)
PROFILE_MODEL_CANDIDATES: Tuple[Tuple[str, str, str], ...] = (
    ("accounts_users", "UserProfile", "generic"),
    ("accounts_users", "SocialProfile", "social"),
    ("accounts_users", "UserEconomicProfile", "economic"),
    ("accounts_users", "EconomicProfile", "economic"),
)


def iter_user_profiles(user) -> List[Any]:
    """
    Retourne une LISTE de profils (social/economic/generic) liés à l'utilisateur, de manière SAFE.
    Ne crashe jamais si les modèles ne sont pas installés.
    """
    if not user or not getattr(user, "is_authenticated", False):
        return []

    out: List[Any] = []
    seen: set[tuple[str, Any]] = set()

    def _add(p: Any):
        if not p:
            return
        key = (p.__class__.__name__, getattr(p, "pk", None) or id(p))
        if key in seen:
            return
        seen.add(key)
        out.append(p)

    # 1) accès par attributs
    for attr in PROFILE_ATTR_CANDIDATES:
        p = _safe_getattr(user, attr)
        if p:
            _add(p)

    # 2) fallback ORM
    for app_label, model_name, _kind in PROFILE_MODEL_CANDIDATES:
        Model = _safe_model(app_label, model_name)
        if not Model:
            continue
        try:
            p = Model.objects.filter(user=user).first()
        except Exception:
            p = None
        if p:
            _add(p)

    return out


def detect_profile_kind(profile: Any) -> str:
    """
    Déduit le type de profil: social / economic / generic
    """
    if not profile:
        return "generic"

    name = profile.__class__.__name__.lower()
    app_label = str(getattr(getattr(profile, "_meta", None), "app_label", "") or "").lower()

    if any(x in name for x in ("economic", "ecom", "b2b")) or any(x in app_label for x in ("economic", "ecommerce", "b2b")):
        return "economic"
    if "social" in name or "social" in app_label:
        return "social"

    Model = profile.__class__
    if any(has_field(Model, f) for f in ("company", "company_name", "ninea", "vendor_status", "b2b_status", "business_name")):
        return "economic"
    if any(has_field(Model, f) for f in ("membership_role", "judicial_record", "is_active_member")):
        return "social"

    return "generic"


def detect_profile_status(profile: Any) -> str:
    """
    Normalise un statut de profil vers:
    approved / pending / rejected / "" / autres valeurs.
    """
    if not profile:
        return ""

    raw = (
        _safe_getattr(profile, "status")
        or _safe_getattr(profile, "validation_status")
        or _safe_getattr(profile, "account_status")
        or ""
    )
    raw = _lower(raw)

    if raw in ("approved", "valid", "validated", "active", "enabled", "ok"):
        return "approved"
    if raw in ("pending", "wait", "waiting", "to_validate", "awaiting", "in_review", "review"):
        return "pending"
    if raw in ("rejected", "refused", "denied", "disabled", "banned", "blocked"):
        return "rejected"
    return raw


def get_user_profile(user, preferred: str = "") -> Any:
    """
    Retourne un profil pertinent.
    preferred: "social"|"economic"|"generic" (optionnel)
    """
    if not user:
        return None

    preferred = (preferred or "").strip().lower()
    profiles = iter_user_profiles(user)

    if not profiles:
        return None

    if preferred in {"social", "economic", "generic"}:
        for p in profiles:
            if detect_profile_kind(p) == preferred:
                return p
        return profiles[0]

    # défaut: social d’abord, puis economic, puis generic
    for kind in ("social", "economic", "generic"):
        for p in profiles:
            if detect_profile_kind(p) == kind:
                return p

    return profiles[0]


def extract_membership_role_code_from_profiles(profiles: List[Any]) -> str:
    """
    Cherche un code de rôle d'adhésion (social) dans une liste de profils.
    """
    if not profiles:
        return ""

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

    for p in profiles:
        role_obj = _first_attr(p, ("membership_role", "role", "membershiprole"), None)
        if role_obj:
            code = _first_attr(role_obj, ("code", "slug", "name"), "")
            if code:
                return _upper(code)

    return ""


def economic_access_flags(user, profiles: Optional[List[Any]] = None) -> Dict[str, bool]:
    """
    Flags économiques:
    - can_vendor / can_b2b
    - vendor_approved / b2b_approved
    """
    flags: Dict[str, bool] = {
        "can_vendor": False,
        "can_b2b": False,
        "vendor_approved": False,
        "b2b_approved": False,
    }

    profiles = profiles or []

    try:
        flags["can_vendor"] |= bool(getattr(user, "is_vendor", False) or getattr(user, "vendor_enabled", False))
        flags["can_b2b"] |= bool(getattr(user, "is_b2b", False) or getattr(user, "b2b_enabled", False) or getattr(user, "is_company_user", False))
    except Exception:
        pass

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

        if detect_profile_status(eco) == "approved":
            if flags["can_vendor"] and not vendor_status:
                flags["vendor_approved"] = True
            if flags["can_b2b"] and not b2b_status:
                flags["b2b_approved"] = True

    return flags


def pick_profile_display_values(profile: Any) -> Dict[str, Any]:
    """
    Pré-calcule des valeurs sûres pour templates.
    """
    if not profile:
        return {
            "profile_phone": "—",
            "profile_country": "—",
            "profile_city": "—",
            "profile_status": "",
        }

    def pick(*names: str) -> Optional[Any]:
        for n in names:
            if hasattr(profile, n):
                try:
                    v = getattr(profile, n, None)
                except Exception:
                    v = None
                if v not in (None, ""):
                    return v
        return None

    phone = pick("phone_number", "phone", "mobile", "tel")
    country = pick("country", "country_of_residence", "residence_country")
    city = pick("city", "city_of_residence", "residence_city")
    status = pick("status", "validation_status", "account_status")

    return {
        "profile_phone": str(phone) if phone else "—",
        "profile_country": str(country) if country else "—",
        "profile_city": str(city) if city else "—",
        "profile_status": _lower(status) if status else "",
    }


# =====================================================
# UI helpers
# =====================================================
def breadcrumb(*items: Tuple[str, Optional[str]]) -> list[dict]:
    return [{"label": label, "url": url} for label, url in items]


def safe_reverse(name: str, fallback: str = "#") -> str:
    try:
        return reverse(name)
    except NoReverseMatch:
        return fallback
    except Exception:
        return fallback


def safe_redirect_names(names: Iterable[str], fallback: str = "/"):
    for n in names:
        try:
            return redirect(n)
        except Exception:
            continue
    return redirect(fallback)


# =====================================================
# Messages wrappers
# =====================================================
def info(request: HttpRequest, msg: str) -> None:
    messages.info(request, msg)


def success(request: HttpRequest, msg: str) -> None:
    messages.success(request, msg)


def warning(request: HttpRequest, msg: str) -> None:
    messages.warning(request, msg)


def error(request: HttpRequest, msg: str) -> None:
    messages.error(request, msg)


# =====================================================
# DTOs
# =====================================================
@dataclass
class StatCard:
    label: str
    value: Any
    icon: str = "📊"
    help: str = ""

    def as_dict(self) -> dict:
        return {"label": self.label, "value": self.value, "icon": self.icon, "help": self.help}






# # dashboard/views/utils.py
# from __future__ import annotations

# from dataclasses import dataclass
# from typing import Any, Optional, Tuple, Type, Iterable, List, Dict

# from django.apps import apps
# from django.contrib import messages
# from django.core.exceptions import FieldDoesNotExist
# from django.http import HttpRequest
# from django.shortcuts import redirect
# from django.urls import NoReverseMatch, reverse
# from django.utils.translation import gettext_lazy as _


# # =====================================================
# # Fields helpers (safe)
# # =====================================================
# def has_field(model: Type[Any], field_name: str) -> bool:
#     try:
#         model._meta.get_field(field_name)
#         return True
#     except FieldDoesNotExist:
#         return False
#     except Exception:
#         return False


# def _safe_getattr(obj: Any, attr: str) -> Any:
#     """
#     Accès safe aux OneToOne / related_name.
#     Django peut lever RelatedObjectDoesNotExist si non existant.
#     """
#     try:
#         return getattr(obj, attr, None)
#     except Exception:
#         return None


# def _upper(val: Any) -> str:
#     return (str(val or "")).strip().upper()


# def _lower(val: Any) -> str:
#     return (str(val or "")).strip().lower()


# def _first_attr(obj: Any, attrs: Iterable[str], default=None):
#     for a in attrs:
#         try:
#             if hasattr(obj, a):
#                 return getattr(obj, a)
#         except Exception:
#             continue
#     return default


# def _safe_model(app_label: str, model_name: str):
#     """
#     apps.get_model safe.
#     """
#     try:
#         return apps.get_model(app_label, model_name)
#     except Exception:
#         return None


# # =====================================================
# # Profile resolver (SOCIAL + ECONOMIC + legacy)
# # =====================================================
# PROFILE_ATTR_CANDIDATES: Tuple[str, ...] = (
#     # related_name probables
#     "profile",
#     "social_profile",
#     "economic_profile",

#     # legacy / variations fréquentes
#     "userprofile",
#     "socialprofile",
#     "economicprofile",
#     "usersocialprofile",
#     "usereconomicprofile",
#     "user_economic_profile",

#     # variations possibles (noms que tu peux rencontrer)
#     "social",
#     "economic",
# )


# # (app_label, model_name, kind_hint)
# PROFILE_MODEL_CANDIDATES: Tuple[Tuple[str, str, str], ...] = (
#     ("accounts_users", "UserProfile", "generic"),
#     ("accounts_users", "SocialProfile", "social"),
#     ("accounts_users", "UserEconomicProfile", "economic"),
#     ("accounts_users", "EconomicProfile", "economic"),
# )


# # dashboard/views/utils.py (remplace get_user_profile)
# def get_user_profile(user, preferred: str = "") -> Any:
#     """
#     Retourne un profil pertinent.
#     preferred: "social"|"economic"|"generic" (optionnel)
#     """
#     if not user:
#         return None

#     preferred = (preferred or "").strip().lower()
#     profiles = iter_user_profiles(user)

#     if not profiles:
#         return None

#     if preferred in {"social", "economic", "generic"}:
#         for p in profiles:
#             if detect_profile_kind(p) == preferred:
#                 return p
#         # si demandé mais introuvable → fallback
#         return profiles[0]

#     # défaut : social d’abord (cohérent avec ton dashboard_profile.py),
#     # puis economic, puis generic
#     for kind in ("social", "economic", "generic"):
#         for p in profiles:
#             if detect_profile_kind(p) == kind:
#                 return p

#     return profiles[0]



# def iter_user_profiles(user) -> List[Any]:
#     """
#     Retourne une LISTE de profils (social/economic/generic) liés à l'utilisateur, de manière SAFE.

#     Objectif:
#     - router/dashboard : détecter rôle social, accès vendor/b2b, etc.
#     - ne doit jamais crasher même si certains modèles n'existent pas.

#     Stratégie:
#     1) on récupère par attributs usuels (OneToOne/related_name)
#     2) fallback ORM sur modèles connus (si installés)
#     3) on dédoublonne (par classe + pk / id)
#     """
#     if not user or not getattr(user, "is_authenticated", False):
#         return []

#     out: List[Any] = []
#     seen: set[tuple[str, Any]] = set()

#     def _add(p: Any):
#         if not p:
#             return
#         key = (p.__class__.__name__, getattr(p, "pk", None) or id(p))
#         if key in seen:
#             return
#         seen.add(key)
#         out.append(p)

#     # 1) accès par attributs (rapide)
#     for attr in PROFILE_ATTR_CANDIDATES:
#         p = _safe_getattr(user, attr)
#         if p:
#             _add(p)

#     # 2) fallback ORM (safe) : utile si related_name non standard
#     for app_label, model_name, _kind in PROFILE_MODEL_CANDIDATES:
#         Model = _safe_model(app_label, model_name)
#         if not Model:
#             continue
#         try:
#             p = Model.objects.filter(user=user).first()
#         except Exception:
#             p = None
#         if p:
#             _add(p)

#     return out


# # =====================================================
# # Profile classification & status
# # =====================================================
# def detect_profile_kind(profile: Any) -> str:
#     """
#     Déduit le type de profil: social / economic / generic
#     sans imports risqués.

#     Retour: "social" | "economic" | "generic"
#     """
#     if not profile:
#         return "generic"

#     name = profile.__class__.__name__.lower()
#     app_label = str(getattr(getattr(profile, "_meta", None), "app_label", "") or "").lower()

#     # heuristique par nom de classe / app label
#     if any(x in name for x in ("economic", "ecom", "b2b")) or any(x in app_label for x in ("economic", "ecommerce", "b2b")):
#         return "economic"
#     if "social" in name or "social" in app_label:
#         return "social"

#     # heuristique par champs fréquents
#     Model = profile.__class__
#     if any(has_field(Model, f) for f in ("company", "company_name", "ninea", "vendor_status", "b2b_status", "business_name")):
#         return "economic"
#     if any(has_field(Model, f) for f in ("membership_role", "judicial_record", "is_active_member")):
#         return "social"

#     return "generic"


# def detect_profile_status(profile: Any) -> str:
#     """
#     Normalise un statut de profil vers:
#     approved / pending / rejected / "" / autres valeurs.
#     """
#     if not profile:
#         return ""

#     raw = (
#         _safe_getattr(profile, "status")
#         or _safe_getattr(profile, "validation_status")
#         or _safe_getattr(profile, "account_status")
#         or ""
#     )
#     raw = _lower(raw)

#     if raw in ("approved", "valid", "validated", "active", "enabled", "ok"):
#         return "approved"
#     if raw in ("pending", "wait", "waiting", "to_validate", "awaiting", "in_review", "review"):
#         return "pending"
#     if raw in ("rejected", "refused", "denied", "disabled", "banned", "blocked"):
#         return "rejected"
#     return raw


# def extract_membership_role_code_from_profiles(profiles: List[Any]) -> str:
#     """
#     Cherche un code de rôle d'adhésion (social) dans une liste de profils.
#     Compatible:
#     - profile.membership_role.code
#     - profile.role.code
#     - profile.role_code / membership_role_code
#     """
#     if not profiles:
#         return ""

#     # priorité social/generic d'abord
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

#     # fallback: scan tout
#     for p in profiles:
#         role_obj = _first_attr(p, ("membership_role", "role", "membershiprole"), None)
#         if role_obj:
#             code = _first_attr(role_obj, ("code", "slug", "name"), "")
#             if code:
#                 return _upper(code)

#     return ""


# def economic_access_flags(user, profiles: Optional[List[Any]] = None) -> Dict[str, bool]:
#     """
#     Flags économiques robustes:
#     - can_vendor / can_b2b : intention/feature existe
#     - vendor_approved / b2b_approved : accès autorisé
#     """
#     flags: Dict[str, bool] = {
#         "can_vendor": False,
#         "can_b2b": False,
#         "vendor_approved": False,
#         "b2b_approved": False,
#     }

#     profiles = profiles or []

#     # User flags si existants
#     try:
#         flags["can_vendor"] |= bool(getattr(user, "is_vendor", False) or getattr(user, "vendor_enabled", False))
#         flags["can_b2b"] |= bool(getattr(user, "is_b2b", False) or getattr(user, "b2b_enabled", False) or getattr(user, "is_company_user", False))
#     except Exception:
#         pass

#     # Related objects
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

#     # Economic profile (si dispo)
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

#         # fallback: profil eco approuvé + feature activée
#         if detect_profile_status(eco) == "approved":
#             if flags["can_vendor"] and not vendor_status:
#                 flags["vendor_approved"] = True
#             if flags["can_b2b"] and not b2b_status:
#                 flags["b2b_approved"] = True

#     return flags


# def pick_profile_display_values(profile: Any) -> Dict[str, Any]:
#     """
#     Pré-calcule des valeurs sûres pour templates (évite failed lookup).
#     """
#     if not profile:
#         return {
#             "profile_phone": "—",
#             "profile_country": "—",
#             "profile_city": "—",
#             "profile_status": "",
#         }

#     def pick(*names: str) -> Optional[Any]:
#         for n in names:
#             if hasattr(profile, n):
#                 try:
#                     v = getattr(profile, n, None)
#                 except Exception:
#                     v = None
#                 if v not in (None, ""):
#                     return v
#         return None

#     phone = pick("phone_number", "phone", "mobile", "tel")
#     country = pick("country", "country_of_residence", "residence_country")
#     city = pick("city", "city_of_residence", "residence_city")
#     status = pick("status", "validation_status", "account_status")

#     return {
#         "profile_phone": str(phone) if phone else "—",
#         "profile_country": str(country) if country else "—",
#         "profile_city": str(city) if city else "—",
#         "profile_status": _lower(status) if status else "",
#     }


# # =====================================================
# # UI helpers
# # =====================================================
# def breadcrumb(*items: Tuple[str, Optional[str]]) -> list[dict]:
#     return [{"label": label, "url": url} for label, url in items]


# def safe_reverse(name: str, fallback: str = "#") -> str:
#     try:
#         return reverse(name)
#     except NoReverseMatch:
#         return fallback
#     except Exception:
#         return fallback


# def safe_redirect_names(names: Iterable[str], fallback: str = "/"):
#     """
#     redirect safe à partir d'une liste de url names.
#     """
#     for n in names:
#         try:
#             return redirect(n)
#         except Exception:
#             continue
#     return redirect(fallback)


# # =====================================================
# # Messages wrappers
# # =====================================================
# def info(request: HttpRequest, msg: str) -> None:
#     messages.info(request, msg)


# def success(request: HttpRequest, msg: str) -> None:
#     messages.success(request, msg)


# def warning(request: HttpRequest, msg: str) -> None:
#     messages.warning(request, msg)


# def error(request: HttpRequest, msg: str) -> None:
#     messages.error(request, msg)


# # =====================================================
# # DTOs
# # =====================================================
# @dataclass
# class StatCard:
#     label: str
#     value: Any
#     icon: str = "📊"
#     help: str = ""

#     def as_dict(self) -> dict:
#         return {"label": self.label, "value": self.value, "icon": self.icon, "help": self.help}






# # dashboard/views/utils.py
# from __future__ import annotations

# from dataclasses import dataclass
# from typing import Any, Iterator, Optional, Tuple, Type

# from django.contrib import messages
# from django.core.exceptions import FieldDoesNotExist
# from django.http import HttpRequest
# from django.urls import reverse


# # =====================================================
# # Fields helpers (safe)
# # =====================================================
# def has_field(model: Type[Any], field_name: str) -> bool:
#     try:
#         model._meta.get_field(field_name)
#         return True
#     except FieldDoesNotExist:
#         return False
#     except Exception:
#         return False


# def _safe_getattr(obj: Any, attr: str) -> Any:
#     """
#     Accès safe aux OneToOne / related_name.
#     Django peut lever RelatedObjectDoesNotExist si non existant.
#     """
#     try:
#         return getattr(obj, attr, None)
#     except Exception:
#         return None


# # =====================================================
# # Profile resolver (SOCIAL + ECONOMIC + legacy)
# # =====================================================
# PROFILE_ATTR_CANDIDATES: Tuple[str, ...] = (
#     # standards / probables
#     "profile",
#     "social_profile",
#     "economic_profile",

#     # legacy / variations fréquentes
#     "userprofile",
#     "socialprofile",
#     "economicprofile",
#     "usersocialprofile",
#     "usereconomicprofile",
#     "user_economic_profile",
# )


# def iter_user_profiles(user) -> Iterator[Any]:
#     """
#     Itère sur TOUS les profils existants de l'utilisateur, sans doublons.
#     Utile pour détecter pending/refused “globalement”.
#     """
#     if not user:
#         return
#     seen: set[tuple[str, Any]] = set()

#     for attr in PROFILE_ATTR_CANDIDATES:
#         p = _safe_getattr(user, attr)
#         if not p:
#             continue
#         key = (p.__class__.__name__, getattr(p, "pk", id(p)))
#         if key in seen:
#             continue
#         seen.add(key)
#         yield p


# def get_user_profile(user, preferred: str = "") -> Any:
#     """
#     Retourne un profil “principal” lié à l'utilisateur.

#     - preferred peut être: "social" | "economic" | "generic" | ""
#     - Par défaut, on retourne un profil pertinent SANS casser social:
#       priorité: social -> economic -> generic -> legacy.
#       (car le dashboard router & social roles reposent souvent sur SocialProfile / membership_role)
#     """
#     if not user:
#         return None

#     preferred = (preferred or "").strip().lower()

#     # accès direct
#     social = _safe_getattr(user, "social_profile")
#     eco = _safe_getattr(user, "economic_profile")
#     generic = _safe_getattr(user, "profile")

#     if preferred == "social" and social:
#         return social
#     if preferred == "economic" and eco:
#         return eco
#     if preferred == "generic" and generic:
#         return generic

#     # ✅ Par défaut: social d'abord (rôles membership), puis eco, puis generic
#     if social:
#         return social
#     if eco:
#         return eco
#     if generic:
#         return generic

#     # fallback legacy
#     for attr in PROFILE_ATTR_CANDIDATES:
#         p = _safe_getattr(user, attr)
#         if p:
#             return p

#     return None


# def detect_profile_kind(profile: Any) -> str:
#     """
#     Déduit le type de profil: social / economic / generic
#     sans imports risqués.

#     Retour: "social" | "economic" | "generic"
#     """
#     if not profile:
#         return "generic"

#     name = profile.__class__.__name__.lower()

#     if "economic" in name:
#         return "economic"
#     if "social" in name:
#         return "social"

#     Model = profile.__class__
#     if any(has_field(Model, f) for f in ("country_of_residence", "profession", "function", "profile_picture")):
#         return "economic"
#     if any(has_field(Model, f) for f in ("membership_role", "judicial_record", "is_active_member")):
#         return "social"

#     return "generic"


# def detect_profile_status(profile: Any) -> str:
#     """
#     Normalise un statut de profil vers:
#     - "approved" | "pending" | "rejected" | "" | autres valeurs (raw)

#     Supporte:
#     - status / validation_status / account_status
#     - flags: is_pending, pending_validation, is_refused, is_rejected
#     - bool: is_validated / is_approved
#     """
#     if not profile:
#         return ""

#     # Flags explicites
#     if bool(_safe_getattr(profile, "is_rejected") or _safe_getattr(profile, "is_refused")):
#         return "rejected"
#     if bool(_safe_getattr(profile, "is_pending") or _safe_getattr(profile, "pending_validation")):
#         return "pending"

#     # Bool validation
#     for f in ("is_validated", "is_approved"):
#         v = _safe_getattr(profile, f)
#         if v is True:
#             return "approved"
#         if v is False:
#             # parfois c'est juste “pas encore validé” => pending
#             return "pending"

#     raw = (
#         _safe_getattr(profile, "status")
#         or _safe_getattr(profile, "validation_status")
#         or _safe_getattr(profile, "account_status")
#         or ""
#     )
#     raw_str = str(raw).strip()
#     low = raw_str.lower()

#     if low in ("approved", "valid", "validated", "active"):
#         return "approved"
#     if low in ("pending", "wait", "waiting", "to_validate", "awaiting"):
#         return "pending"
#     if low in ("rejected", "refused", "denied", "disabled", "banned"):
#         return "rejected"

#     return low or raw_str


# def user_has_pending_or_refused_profile(user) -> bool:
#     """
#     Vrai si AU MOINS un profil (social/economic/generic/legacy) est pending ou rejected.
#     """
#     for p in iter_user_profiles(user):
#         st = detect_profile_status(p)
#         if st in {"pending", "rejected"}:
#             return True
#     return False


# # =====================================================
# # UI helpers
# # =====================================================
# def breadcrumb(*items: Tuple[str, Optional[str]]) -> list[dict]:
#     """
#     items: (label, url) où url peut être None.
#     """
#     return [{"label": label, "url": url} for label, url in items]


# def safe_reverse(name: str, fallback: str = "#") -> str:
#     try:
#         return reverse(name)
#     except Exception:
#         return fallback


# # =====================================================
# # Messages wrappers
# # =====================================================
# def info(request: HttpRequest, msg: str) -> None:
#     messages.info(request, msg)


# def success(request: HttpRequest, msg: str) -> None:
#     messages.success(request, msg)


# def warning(request: HttpRequest, msg: str) -> None:
#     messages.warning(request, msg)


# def error(request: HttpRequest, msg: str) -> None:
#     messages.error(request, msg)


# # =====================================================
# # DTOs
# # =====================================================
# @dataclass
# class StatCard:
#     label: str
#     value: Any
#     icon: str = "📊"
#     help: str = ""





# # dashboard/views/utils.py
# from __future__ import annotations

# from dataclasses import dataclass
# from typing import Any, Optional, Tuple, Type

# from django.contrib import messages
# from django.core.exceptions import FieldDoesNotExist
# from django.http import HttpRequest
# from django.urls import reverse
# from django.utils.translation import gettext_lazy as _


# # =====================================================
# # Fields helpers (safe)
# # =====================================================
# def has_field(model: Type[Any], field_name: str) -> bool:
#     try:
#         model._meta.get_field(field_name)
#         return True
#     except FieldDoesNotExist:
#         return False
#     except Exception:
#         return False


# def _safe_getattr(obj: Any, attr: str) -> Any:
#     """
#     Accès safe aux OneToOne / related_name.
#     Django peut lever RelatedObjectDoesNotExist si non existant.
#     """
#     try:
#         return getattr(obj, attr, None)
#     except Exception:
#         return None


# # =====================================================
# # Profile resolver (SOCIAL + ECONOMIC + legacy)
# # =====================================================
# PROFILE_ATTR_CANDIDATES = (
#     # related_name probables
#     "profile",
#     "social_profile",
#     "economic_profile",

#     # legacy / variations fréquentes
#     "userprofile",
#     "socialprofile",
#     "economicprofile",
#     "usersocialprofile",
#     "usereconomicprofile",
#     "user_economic_profile",
# )


# def get_user_profile(user) -> Any:
#     """
#     Retourne le profil le plus pertinent lié à l'utilisateur,
#     compatible avec plusieurs structures possibles.

#     Priorité:
#     1) economic_profile (si présent)
#     2) social_profile (si présent)
#     3) profile (générique)
#     4) legacy variants
#     """
#     if not user:
#         return None

#     # 1) economic first (si tu as un profil eco central)
#     p = _safe_getattr(user, "economic_profile")
#     if p:
#         return p

#     # 2) social
#     p = _safe_getattr(user, "social_profile")
#     if p:
#         return p

#     # 3) generic
#     p = _safe_getattr(user, "profile")
#     if p:
#         return p

#     # 4) autres candidats
#     for attr in PROFILE_ATTR_CANDIDATES:
#         p = _safe_getattr(user, attr)
#         if p:
#             return p

#     return None


# def detect_profile_kind(profile: Any) -> str:
#     """
#     Déduit le type de profil: social / economic / generic
#     sans imports risqués.

#     Retour: "social" | "economic" | "generic"
#     """
#     if not profile:
#         return "generic"

#     name = profile.__class__.__name__.lower()

#     # heuristique par nom de classe
#     if "economic" in name:
#         return "economic"
#     if "social" in name:
#         return "social"

#     # heuristique par champs fréquents
#     Model = profile.__class__
#     if any(has_field(Model, f) for f in ("country_of_residence", "profession", "function", "profile_picture")):
#         return "economic"
#     if any(has_field(Model, f) for f in ("membership_role", "judicial_record", "is_active_member")):
#         return "social"

#     return "generic"


# def detect_profile_status(profile: Any) -> str:
#     """
#     Normalise un statut de profil (selon tes structures) vers:
#     approved / pending / rejected / "" / autres valeurs.
#     """
#     if not profile:
#         return ""

#     raw = (
#         _safe_getattr(profile, "status")
#         or _safe_getattr(profile, "validation_status")
#         or ""
#     )
#     raw = str(raw).strip().lower()

#     if raw in ("approved", "valid", "validated"):
#         return "approved"
#     if raw in ("pending", "wait", "waiting"):
#         return "pending"
#     if raw in ("rejected", "refused", "denied"):
#         return "rejected"
#     return raw


# # =====================================================
# # UI helpers
# # =====================================================
# def breadcrumb(*items: Tuple[str, Optional[str]]) -> list[dict]:
#     """
#     items: (label, url) où url peut être None.
#     """
#     return [{"label": label, "url": url} for label, url in items]


# def safe_reverse(name: str, fallback: str = "#") -> str:
#     try:
#         return reverse(name)
#     except Exception:
#         return fallback


# # =====================================================
# # Messages wrappers
# # =====================================================
# def info(request: HttpRequest, msg: str) -> None:
#     messages.info(request, msg)


# def success(request: HttpRequest, msg: str) -> None:
#     messages.success(request, msg)


# def warning(request: HttpRequest, msg: str) -> None:
#     messages.warning(request, msg)


# def error(request: HttpRequest, msg: str) -> None:
#     messages.error(request, msg)


# # =====================================================
# # DTOs
# # =====================================================
# @dataclass
# class StatCard:
#     label: str
#     value: Any
#     icon: str = "📊"
#     help: str = ""







# # dashboard/views/utils.py
# from __future__ import annotations

# from dataclasses import dataclass
# from typing import Any, Dict, Optional, Tuple, Type

# from django.contrib import messages
# from django.core.exceptions import FieldDoesNotExist
# from django.http import HttpRequest
# from django.urls import reverse
# from django.utils.translation import gettext_lazy as _


# def has_field(model: Type[Any], field_name: str) -> bool:
#     try:
#         model._meta.get_field(field_name)
#         return True
#     except FieldDoesNotExist:
#         return False


# def get_user_profile(user) -> Any:
#     """
#     Retourne un profil lié à l'utilisateur, en restant compatible avec:
#     - user.profile (related_name="profile")
#     - user.social_profile (si existant)
#     - None si absent
#     """
#     if hasattr(user, "profile") and user.profile:
#         return user.profile
#     if hasattr(user, "social_profile") and user.social_profile:
#         return user.social_profile
#     return None


# def breadcrumb(*items: Tuple[str, Optional[str]]) -> list[dict]:
#     """
#     items: (label, url) where url can be None for current.
#     """
#     out = []
#     for label, url in items:
#         out.append({"label": label, "url": url})
#     return out


# def safe_reverse(name: str, fallback: str = "#") -> str:
#     try:
#         return reverse(name)
#     except Exception:
#         return fallback


# def info(request: HttpRequest, msg: str) -> None:
#     messages.info(request, msg)


# def success(request: HttpRequest, msg: str) -> None:
#     messages.success(request, msg)


# def warning(request: HttpRequest, msg: str) -> None:
#     messages.warning(request, msg)


# def error(request: HttpRequest, msg: str) -> None:
#     messages.error(request, msg)


# @dataclass
# class StatCard:
#     label: str
#     value: Any
#     icon: str = "📊"
#     help: str = ""



# # # dashboard/utils.py
# from django.db.models import Sum, Count, F
# from social.models import Donation, Engagement, Project
# from accounts_users.models.users_economic_profile import UserProfile
# from accounts_users.models import CustomUser

# def get_dashboard_stats():
#     total_members = CustomUser.objects.count()

#     # Attention à la casse et au pluriel
#     total_volunteers = UserProfile.objects.filter(membership_role__name__icontains="volontaire").count()

#     total_donations = Donation.objects.aggregate(total=Sum('amount'))['total'] or 0
#     donors_count = Donation.objects.exclude(email="").values('email').distinct().count()

#     total_projects = Project.objects.filter(is_active=True).count()
#     engagements_count = Engagement.objects.count()

#     # Statistiques par projet (en évitant None pour project)
#     donations_by_project = (
#         Donation.objects
#         .filter(project__isnull=False)
#         .values(project_title=F('project__title'))
#         .annotate(total=Sum('amount'))
#         .order_by('-total')
#     )

#     # Statistiques par année d'engagement (utilisation de TruncYear pour Django >= 1.10)
#     from django.db.models.functions import ExtractYear
#     engagements_by_year = (
#         Engagement.objects
#         .annotate(year=ExtractYear('date'))
#         .values('year')
#         .annotate(count=Count('id'))
#         .order_by('year')
#     )

#     # Cartes de synthèse pour le dashboard (icônes Bootstrap)
#     cards = [
#         ("Utilisateurs", total_members, "bi-people", "primary"),
#         ("Volontaires", total_volunteers, "bi-person-check", "success"),
#         ("Dons (FCFA)", total_donations, "bi-cash-coin", "warning"),
#         ("Projets actifs", total_projects, "bi-diagram-3", "info"),
#         ("Engagements", engagements_count, "bi-calendar-check", "secondary"),
#         ("Donateurs", donors_count, "bi-person-heart", "dark"),
#     ]

#     return {
#         "cards": cards,
#         "stats": {
#             "total_members": total_members,
#             "total_volunteers": total_volunteers,
#             "total_donations": total_donations,
#             "total_projects": total_projects,
#             "engagements_count": engagements_count,
#             "donors_count": donors_count,
#         },
#         "detailed_stats": {
#             "donations_by_project": list(donations_by_project),
#             "engagements_by_year": list(engagements_by_year),
#         }
#     }





# from django.db.models import Sum, Count
# from social.models import Donation, Engagement, Project
# from accounts_users.models.users_profile import UserProfile
# from accounts_users.models import CustomUser


# def get_dashboard_stats():
#     total_members = CustomUser.objects.count()

#     # ✅ Assure-toi que MembershipRole a un champ 'name'
#     total_volunteers = UserProfile.objects.filter(membership_role__name__icontains="volontaire").count()

#     total_donations = Donation.objects.aggregate(total=Sum('amount'))['total'] or 0
#     donors_count = Donation.objects.values('email').distinct().count()

#     total_projects = Project.objects.filter(is_active=True).count()
#     engagements_count = Engagement.objects.count()

#     # ✅ Correction ici : project__title
#     donations_by_project = Donation.objects.values('project__title').annotate(total=Sum('amount')).order_by('-total')

#     # ✅ Correction ici : EXTRACT(year FROM date)
#     engagements_by_year = Engagement.objects.extra(select={
#         'year': "EXTRACT(year FROM date)"
#     }).values('year').annotate(count=Count('id')).order_by('year')

#     # ✅ Cartes pour affichage
#     cards = [
#         ("Utilisateurs", total_members, "bi-people", "primary"),
#         ("Volontaires", total_volunteers, "bi-person-check", "success"),
#         ("Dons (FCFA)", total_donations, "bi-cash-coin", "warning"),
#         ("Projets actifs", total_projects, "bi-diagram-3", "info"),
#         ("Engagements", engagements_count, "bi-calendar-check", "secondary"),
#         ("Donateurs", donors_count, "bi-person-heart", "dark"),
#     ]

#     return {
#         "cards": cards,
#         "stats": {
#             "total_members": total_members,
#             "total_volunteers": total_volunteers,
#             "total_donations": total_donations,
#             "total_projects": total_projects,
#             "engagements_count": engagements_count,
#             "donors_count": donors_count,
#         },
#         "detailed_stats": {
#             "donations_by_project": list(donations_by_project),
#             "engagements_by_year": list(engagements_by_year),
#         }
#     }
