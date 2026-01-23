# dashboard/views/pending_profiles.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from django.apps import apps
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import FieldDoesNotExist, PermissionDenied
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import QuerySet, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from dashboard.permissions import is_admin, is_staff_user

User = get_user_model()


PROFILE_MODEL_CANDIDATES: Tuple[Tuple[str, str, str], ...] = (
    ("accounts_users", "UserProfile", "Général"),
    ("accounts_users", "SocialProfile", "Social"),
    ("accounts_users", "UserEconomicProfile", "Économique"),
    ("accounts_users", "EconomicProfile", "Économique"),
)


def _is_staff_or_admin(user) -> bool:
    return bool(is_admin(user) or is_staff_user(user))


def _safe_model(app_label: str, model_name: str):
    try:
        return apps.get_model(app_label, model_name)
    except Exception:
        return None


def _model_has_field(model, field: str) -> bool:
    try:
        model._meta.get_field(field)
        return True
    except FieldDoesNotExist:
        return False
    except Exception:
        return False


def _field_names(model) -> set[str]:
    try:
        return {f.name for f in model._meta.get_fields()}
    except Exception:
        return set()


def _status_field(model) -> Optional[str]:
    if _model_has_field(model, "status"):
        return "status"
    if _model_has_field(model, "validation_status"):
        return "validation_status"
    if _model_has_field(model, "account_status"):
        return "account_status"
    return None


def _bool_validation_field(model) -> Optional[str]:
    for f in ("is_validated", "is_approved"):
        if _model_has_field(model, f):
            return f
    return None


def _pending_queryset(ProfileModel) -> QuerySet:
    st_field = _status_field(ProfileModel)
    if st_field:
        # pending élargi
        return ProfileModel.objects.filter(
            Q(**{f"{st_field}__iexact": "pending"})
            | Q(**{f"{st_field}__iexact": "waiting"})
            | Q(**{f"{st_field}__iexact": "to_validate"})
            | Q(**{f"{st_field}__iexact": "awaiting"})
        )

    bool_field = _bool_validation_field(ProfileModel)
    if bool_field:
        return ProfileModel.objects.filter(**{bool_field: False})

    return ProfileModel.objects.none()


def _pick_created_at(profile_obj) -> timezone.datetime:
    for name in ("created_at", "updated_at"):
        v = getattr(profile_obj, name, None)
        if v:
            return v
    return timezone.now()


def _pick_phone(profile_obj) -> str:
    for name in ("phone_number", "phone"):
        v = getattr(profile_obj, name, None)
        if v:
            return str(v)
    return "—"


def _pick_role_label(profile_obj) -> str:
    mr = getattr(profile_obj, "membership_role", None)
    if mr:
        return str(getattr(mr, "label", "") or getattr(mr, "code", "") or mr)

    r = getattr(profile_obj, "role", None)
    if r:
        return str(getattr(r, "label", "") or getattr(r, "code", "") or getattr(r, "slug", "") or r)

    return "—"


def _normalize_choice_value(model, field_name: str, logical_value: str) -> str:
    try:
        f = model._meta.get_field(field_name)
        choices = list(getattr(f, "choices", []) or [])
        if choices:
            keys = [str(k) for k, _ in choices]
            target_lower = logical_value.lower()
            target_upper = logical_value.upper()

            if target_lower in keys:
                return target_lower
            if target_upper in keys:
                return target_upper

            for k in keys:
                if str(k).lower() == target_lower:
                    return k

            if sum(1 for k in keys if str(k).isupper()) >= max(1, len(keys) // 2):
                return target_upper
    except Exception:
        pass
    return logical_value


def _set_profile_approved(profile_obj) -> None:
    Model = profile_obj.__class__
    st_field = _status_field(Model)
    if st_field:
        setattr(profile_obj, st_field, _normalize_choice_value(Model, st_field, "approved"))
        if hasattr(profile_obj, "validated_at") and getattr(profile_obj, "validated_at", None) is None:
            profile_obj.validated_at = timezone.now()
        update = [st_field] + (["validated_at"] if hasattr(profile_obj, "validated_at") else [])
        profile_obj.save(update_fields=update)
        return

    bool_field = _bool_validation_field(Model)
    if bool_field:
        setattr(profile_obj, bool_field, True)
        profile_obj.save(update_fields=[bool_field])
        return


def _set_profile_refused(profile_obj) -> None:
    Model = profile_obj.__class__
    st_field = _status_field(Model)
    if st_field:
        setattr(profile_obj, st_field, _normalize_choice_value(Model, st_field, "rejected"))
        if hasattr(profile_obj, "rejected_at") and getattr(profile_obj, "rejected_at", None) is None:
            profile_obj.rejected_at = timezone.now()
        update = [st_field] + (["rejected_at"] if hasattr(profile_obj, "rejected_at") else [])
        profile_obj.save(update_fields=update)
        return

    bool_field = _bool_validation_field(Model)
    if bool_field:
        setattr(profile_obj, bool_field, False)
        profile_obj.save(update_fields=[bool_field])
        return


def _get_profile_models() -> List[Tuple[Any, str]]:
    out: List[Tuple[Any, str]] = []
    for app_label, model_name, kind_label in PROFILE_MODEL_CANDIDATES:
        m = _safe_model(app_label, model_name)
        if m:
            out.append((m, kind_label))
    return out


@dataclass
class PendingUserRow:
    user_id: int
    full_name: str
    username: str
    email: str
    phone: str
    kinds: List[str]
    role_label: str
    created_at: timezone.datetime

    @property
    def kinds_label(self) -> str:
        return " + ".join(sorted(set(self.kinds))) if self.kinds else "—"


def _build_pending_users() -> List[PendingUserRow]:
    models = _get_profile_models()
    by_user: Dict[int, PendingUserRow] = {}

    for ProfileModel, kind_label in models:
        qs = _pending_queryset(ProfileModel)

        fields = _field_names(ProfileModel)
        sr = []
        if "user" in fields:
            sr.append("user")
        if "membership_role" in fields:
            sr.append("membership_role")
        if "role" in fields:
            sr.append("role")
        if sr:
            try:
                qs = qs.select_related(*sr)
            except Exception:
                pass

        if "created_at" in fields:
            qs = qs.order_by("created_at")
        else:
            qs = qs.order_by("id")

        for p in qs[:1000]:
            u = getattr(p, "user", None)
            if not u:
                continue

            uid = int(u.pk)
            created_at = _pick_created_at(p)
            role_label = _pick_role_label(p)
            phone = _pick_phone(p)

            try:
                full_name = u.get_full_name() or ""
            except Exception:
                full_name = ""

            row = by_user.get(uid)
            if row is None:
                by_user[uid] = PendingUserRow(
                    user_id=uid,
                    full_name=full_name or getattr(u, "username", "") or str(u),
                    username=getattr(u, "username", "") or "",
                    email=getattr(u, "email", "") or "—",
                    phone=phone or "—",
                    kinds=[kind_label],
                    role_label=role_label or "—",
                    created_at=created_at,
                )
            else:
                row.kinds.append(kind_label)
                if created_at and created_at < row.created_at:
                    row.created_at = created_at
                if row.phone == "—" and phone and phone != "—":
                    row.phone = phone
                if row.role_label == "—" and role_label and role_label != "—":
                    row.role_label = role_label

    return sorted(by_user.values(), key=lambda r: r.created_at or timezone.now())


@login_required
def pending_profiles_list(request):
    if not _is_staff_or_admin(request.user):
        raise PermissionDenied

    page_number = (request.GET.get("page") or "1").strip()
    pending_users = _build_pending_users()

    paginator = Paginator(pending_users, 25)
    page_obj = paginator.get_page(page_number)

    rows = []
    for r in page_obj.object_list:
        rows.append({
            "user_id": r.user_id,
            "full_name": r.full_name,
            "username": r.username,
            "email": r.email,
            "phone": r.phone,
            "kinds_label": r.kinds_label,
            "role_label": r.role_label,
            "created_at": r.created_at,
            "approve_url": reverse("dashboard:profile_approve", args=[r.user_id]),
            "refuse_url": reverse("dashboard:profile_refuse", args=[r.user_id]),
        })

    return render(request, "dashboard/profile/pending_list.html", {
        "page_title": _("Profils en attente"),
        "profiles": rows,
        "page_obj": page_obj,
        "paginator": paginator,
        "is_paginated": page_obj.has_other_pages(),
        "pending_count": len(pending_users),
    })


@login_required
@transaction.atomic
def validate_profile_view(request, user_id: int):
    if not _is_staff_or_admin(request.user):
        raise PermissionDenied

    # ✅ action uniquement en POST (sécurité)
    if request.method != "POST":
        messages.error(request, _("Action non autorisée. Utilisez un formulaire POST."))
        return redirect("dashboard:pending_profiles")

    user = get_object_or_404(User, pk=user_id)

    changed = 0
    for ProfileModel, _kind_label in _get_profile_models():
        st_field = _status_field(ProfileModel)
        bool_field = _bool_validation_field(ProfileModel)

        qs = ProfileModel.objects.filter(user=user)
        if st_field:
            qs = qs.filter(
                Q(**{f"{st_field}__iexact": "pending"})
                | Q(**{f"{st_field}__iexact": "waiting"})
                | Q(**{f"{st_field}__iexact": "to_validate"})
                | Q(**{f"{st_field}__iexact": "awaiting"})
            )
        elif bool_field:
            qs = qs.filter(**{bool_field: False})
        else:
            qs = ProfileModel.objects.none()

        for p in qs:
            _set_profile_approved(p)
            changed += 1

    if changed:
        messages.success(request, _("Utilisateur validé (profils mis à jour: %(n)s).") % {"n": changed})
    else:
        messages.info(request, _("Aucun profil en attente pour cet utilisateur."))

    return redirect("dashboard:pending_profiles")


@login_required
@transaction.atomic
def refuse_profile_view(request, user_id: int):
    if not _is_staff_or_admin(request.user):
        raise PermissionDenied

    # ✅ action uniquement en POST (sécurité)
    if request.method != "POST":
        messages.error(request, _("Action non autorisée. Utilisez un formulaire POST."))
        return redirect("dashboard:pending_profiles")

    user = get_object_or_404(User, pk=user_id)

    changed = 0
    for ProfileModel, _kind_label in _get_profile_models():
        st_field = _status_field(ProfileModel)
        bool_field = _bool_validation_field(ProfileModel)

        qs = ProfileModel.objects.filter(user=user)
        if st_field:
            qs = qs.filter(
                Q(**{f"{st_field}__iexact": "pending"})
                | Q(**{f"{st_field}__iexact": "waiting"})
                | Q(**{f"{st_field}__iexact": "to_validate"})
                | Q(**{f"{st_field}__iexact": "awaiting"})
            )
        elif bool_field:
            qs = qs.filter(**{bool_field: False})
        else:
            qs = ProfileModel.objects.none()

        for p in qs:
            _set_profile_refused(p)
            changed += 1

    if changed:
        messages.warning(request, _("Utilisateur refusé (profils mis à jour: %(n)s).") % {"n": changed})
    else:
        messages.info(request, _("Aucun profil en attente pour cet utilisateur."))

    return redirect("dashboard:pending_profiles")





# # dashboard/views/pending_profiles.py
# from __future__ import annotations

# from dataclasses import dataclass
# from typing import Any, Dict, Iterable, List, Optional, Tuple

# from django.apps import apps
# from django.contrib import messages
# from django.contrib.auth import get_user_model
# from django.contrib.auth.decorators import login_required
# from django.core.exceptions import FieldDoesNotExist, PermissionDenied
# from django.core.paginator import Paginator
# from django.db import transaction
# from django.db.models import QuerySet
# from django.shortcuts import get_object_or_404, redirect, render
# from django.urls import reverse
# from django.utils import timezone
# from django.utils.translation import gettext_lazy as _

# from dashboard.permissions import is_admin, is_staff_user

# User = get_user_model()


# # ============================================================
# # Registry: liste des modèles "profil" à valider
# # (ajuste/complète selon ton projet)
# # ============================================================
# PROFILE_MODEL_CANDIDATES: Tuple[Tuple[str, str, str], ...] = (
#     # (app_label, model_name, kind_label)
#     ("accounts_users", "UserProfile", "Général"),
#     ("accounts_users", "SocialProfile", "Social"),
#     ("accounts_users", "UserEconomicProfile", "Économique"),
#     ("accounts_users", "EconomicProfile", "Économique"),
# )


# def _is_staff_or_admin(user) -> bool:
#     return bool(is_admin(user) or is_staff_user(user))


# def _safe_model(app_label: str, model_name: str):
#     try:
#         return apps.get_model(app_label, model_name)
#     except Exception:
#         return None


# def _model_has_field(model, field: str) -> bool:
#     try:
#         model._meta.get_field(field)
#         return True
#     except FieldDoesNotExist:
#         return False
#     except Exception:
#         return False


# def _field_names(model) -> set[str]:
#     try:
#         return {f.name for f in model._meta.get_fields()}
#     except Exception:
#         return set()


# def _status_field(model) -> Optional[str]:
#     # on supporte status / validation_status
#     if _model_has_field(model, "status"):
#         return "status"
#     if _model_has_field(model, "validation_status"):
#         return "validation_status"
#     return None


# def _bool_validation_field(model) -> Optional[str]:
#     # fallback bool
#     for f in ("is_validated", "is_approved"):
#         if _model_has_field(model, f):
#             return f
#     return None


# def _pending_queryset(ProfileModel) -> QuerySet:
#     fields = _field_names(ProfileModel)

#     st_field = _status_field(ProfileModel)
#     if st_field:
#         # supporte pending / PENDING etc.
#         return ProfileModel.objects.filter(**{f"{st_field}__in": ["pending", "PENDING", "Pending"]})

#     bool_field = _bool_validation_field(ProfileModel)
#     if bool_field:
#         return ProfileModel.objects.filter(**{bool_field: False})

#     return ProfileModel.objects.none()


# def _pick_created_at(profile_obj) -> timezone.datetime:
#     for name in ("created_at", "updated_at", "id"):
#         v = getattr(profile_obj, name, None)
#         if v:
#             if name == "id":
#                 # fallback: pas une date, on met now()
#                 return timezone.now()
#             return v
#     return timezone.now()


# def _pick_phone(profile_obj) -> str:
#     for name in ("phone_number", "phone"):
#         v = getattr(profile_obj, name, None)
#         if v:
#             return str(v)
#     return "—"


# def _pick_role_label(profile_obj) -> str:
#     # membership_role.label ou role.label/code
#     mr = getattr(profile_obj, "membership_role", None)
#     if mr:
#         return str(getattr(mr, "label", "") or getattr(mr, "code", "") or mr)

#     r = getattr(profile_obj, "role", None)
#     if r:
#         return str(getattr(r, "label", "") or getattr(r, "code", "") or getattr(r, "slug", "") or r)

#     return "—"


# def _normalize_choice_value(model, field_name: str, logical_value: str) -> str:
#     """
#     Essaie d'aligner la valeur sur tes choices si elles existent.
#     - Si choices contiennent APPROVED/REJECTED/PENDING -> renvoie la clé correspondante.
#     - Sinon fallback sur lower/upper selon ce qu'on détecte.
#     """
#     try:
#         f = model._meta.get_field(field_name)
#         choices = list(getattr(f, "choices", []) or [])
#         if choices:
#             # choices = [(key, label), ...]
#             keys = [str(k) for k, _ in choices]
#             target_lower = logical_value.lower()
#             target_upper = logical_value.upper()

#             # match direct
#             if target_lower in keys:
#                 return target_lower
#             if target_upper in keys:
#                 return target_upper

#             # match "Approved"/"APPROVED"/etc.
#             for k in keys:
#                 if str(k).lower() == target_lower:
#                     return k

#             # si la majorité des clés est uppercase
#             if sum(1 for k in keys if str(k).isupper()) >= max(1, len(keys) // 2):
#                 return target_upper
#     except Exception:
#         pass

#     # fallback heuristique
#     return logical_value


# def _set_profile_approved(profile_obj) -> None:
#     Model = profile_obj.__class__
#     st_field = _status_field(Model)
#     if st_field:
#         setattr(profile_obj, st_field, _normalize_choice_value(Model, st_field, "approved"))
#         if hasattr(profile_obj, "validated_at") and getattr(profile_obj, "validated_at", None) is None:
#             profile_obj.validated_at = timezone.now()
#         profile_obj.save(update_fields=[st_field] + (["validated_at"] if hasattr(profile_obj, "validated_at") else []))
#         return

#     bool_field = _bool_validation_field(Model)
#     if bool_field:
#         setattr(profile_obj, bool_field, True)
#         profile_obj.save(update_fields=[bool_field])
#         return


# def _set_profile_refused(profile_obj) -> None:
#     Model = profile_obj.__class__
#     st_field = _status_field(Model)
#     if st_field:
#         setattr(profile_obj, st_field, _normalize_choice_value(Model, st_field, "rejected"))
#         if hasattr(profile_obj, "rejected_at") and getattr(profile_obj, "rejected_at", None) is None:
#             profile_obj.rejected_at = timezone.now()
#         profile_obj.save(update_fields=[st_field] + (["rejected_at"] if hasattr(profile_obj, "rejected_at") else []))
#         return

#     # bool fallback: on ne peut pas distinguer "refusé" si seulement is_validated,
#     # donc on laisse False (et on peut logguer ailleurs)
#     bool_field = _bool_validation_field(Model)
#     if bool_field:
#         setattr(profile_obj, bool_field, False)
#         profile_obj.save(update_fields=[bool_field])
#         return


# def _get_profile_models() -> List[Tuple[Any, str]]:
#     """
#     Retourne [(ProfileModel, kind_label), ...] pour ceux qui existent.
#     """
#     out: List[Tuple[Any, str]] = []
#     for app_label, model_name, kind_label in PROFILE_MODEL_CANDIDATES:
#         m = _safe_model(app_label, model_name)
#         if m:
#             out.append((m, kind_label))
#     return out


# @dataclass
# class PendingUserRow:
#     user_id: int
#     full_name: str
#     username: str
#     email: str
#     phone: str
#     kinds: List[str]
#     role_label: str
#     created_at: timezone.datetime

#     @property
#     def kinds_label(self) -> str:
#         return " + ".join(sorted(set(self.kinds))) if self.kinds else "—"


# def _build_pending_users() -> List[PendingUserRow]:
#     """
#     Agrège tous les profils en attente, DÉDOUBLONNE par user.
#     """
#     models = _get_profile_models()
#     by_user: Dict[int, PendingUserRow] = {}

#     for ProfileModel, kind_label in models:
#         qs = _pending_queryset(ProfileModel)

#         # select_related safe
#         fields = _field_names(ProfileModel)
#         sr = []
#         if "user" in fields:
#             sr.append("user")
#         if "membership_role" in fields:
#             sr.append("membership_role")
#         if "role" in fields:
#             sr.append("role")
#         if sr:
#             try:
#                 qs = qs.select_related(*sr)
#             except Exception:
#                 pass

#         # ordering safe
#         if "created_at" in fields:
#             qs = qs.order_by("created_at")
#         else:
#             qs = qs.order_by("id")

#         # limite par modèle (évite explosion)
#         for p in qs[:1000]:
#             u = getattr(p, "user", None)
#             if not u:
#                 continue

#             uid = int(u.pk)
#             created_at = _pick_created_at(p)
#             role_label = _pick_role_label(p)
#             phone = _pick_phone(p)

#             full_name = ""
#             try:
#                 full_name = u.get_full_name() or ""
#             except Exception:
#                 full_name = ""

#             row = by_user.get(uid)
#             if row is None:
#                 by_user[uid] = PendingUserRow(
#                     user_id=uid,
#                     full_name=full_name or getattr(u, "username", "") or str(u),
#                     username=getattr(u, "username", "") or "",
#                     email=getattr(u, "email", "") or "—",
#                     phone=phone or "—",
#                     kinds=[kind_label],
#                     role_label=role_label or "—",
#                     created_at=created_at,
#                 )
#             else:
#                 row.kinds.append(kind_label)
#                 # conserver la date la plus ancienne (priorité)
#                 if created_at and created_at < row.created_at:
#                     row.created_at = created_at
#                 # garder une info utile si manquante
#                 if row.phone == "—" and phone and phone != "—":
#                     row.phone = phone
#                 if row.role_label == "—" and role_label and role_label != "—":
#                     row.role_label = role_label

#     # tri: plus anciens en premier
#     return sorted(by_user.values(), key=lambda r: r.created_at or timezone.now())


# @login_required
# def pending_profiles_list(request):
#     if not _is_staff_or_admin(request.user):
#         raise PermissionDenied

#     page_number = (request.GET.get("page") or "1").strip()
#     pending_users = _build_pending_users()

#     paginator = Paginator(pending_users, 25)
#     page_obj = paginator.get_page(page_number)

#     # on prépare les urls dans le contexte (templates simples, zéro NoReverseMatch)
#     rows = []
#     for r in page_obj.object_list:
#         rows.append({
#             "user_id": r.user_id,
#             "full_name": r.full_name,
#             "username": r.username,
#             "email": r.email,
#             "phone": r.phone,
#             "kinds_label": r.kinds_label,
#             "role_label": r.role_label,
#             "created_at": r.created_at,
#             "approve_url": reverse("dashboard:profile_approve", args=[r.user_id]),
#             "refuse_url": reverse("dashboard:profile_refuse", args=[r.user_id]),
#         })

#     return render(request, "dashboard/profile/pending_list.html", {
#         "page_title": _("Profils en attente"),
#         "profiles": rows,  # on garde le nom "profiles" pour compatibilité template
#         "page_obj": page_obj,
#         "paginator": paginator,
#         "is_paginated": page_obj.has_other_pages(),
#         "pending_count": len(pending_users),
#     })


# @login_required
# @transaction.atomic
# def validate_profile_view(request, user_id: int):
#     if not _is_staff_or_admin(request.user):
#         raise PermissionDenied

#     user = get_object_or_404(User, pk=user_id)

#     changed = 0
#     for ProfileModel, _kind_label in _get_profile_models():
#         st_field = _status_field(ProfileModel)
#         bool_field = _bool_validation_field(ProfileModel)

#         qs = ProfileModel.objects.filter(user=user)
#         if st_field:
#             qs = qs.filter(**{f"{st_field}__in": ["pending", "PENDING", "Pending"]})
#         elif bool_field:
#             qs = qs.filter(**{bool_field: False})
#         else:
#             qs = ProfileModel.objects.none()

#         for p in qs:
#             _set_profile_approved(p)
#             changed += 1

#     if changed:
#         messages.success(request, _("Utilisateur validé (profils mis à jour: %(n)s).") % {"n": changed})
#     else:
#         messages.info(request, _("Aucun profil en attente pour cet utilisateur."))

#     return redirect("dashboard:pending_profiles")


# @login_required
# @transaction.atomic
# def refuse_profile_view(request, user_id: int):
#     if not _is_staff_or_admin(request.user):
#         raise PermissionDenied

#     user = get_object_or_404(User, pk=user_id)

#     changed = 0
#     for ProfileModel, _kind_label in _get_profile_models():
#         st_field = _status_field(ProfileModel)
#         bool_field = _bool_validation_field(ProfileModel)

#         qs = ProfileModel.objects.filter(user=user)
#         if st_field:
#             qs = qs.filter(**{f"{st_field}__in": ["pending", "PENDING", "Pending"]})
#         elif bool_field:
#             qs = qs.filter(**{bool_field: False})
#         else:
#             qs = ProfileModel.objects.none()

#         for p in qs:
#             _set_profile_refused(p)
#             changed += 1

#     if changed:
#         messages.warning(request, _("Utilisateur refusé (profils mis à jour: %(n)s).") % {"n": changed})
#     else:
#         messages.info(request, _("Aucun profil en attente pour cet utilisateur."))

#     return redirect("dashboard:pending_profiles")





# # dashboard/views/pending_profiles.py
# from django.contrib.admin.views.decorators import staff_member_required
# from django.contrib import messages
# from django.shortcuts import render, redirect, get_object_or_404
# from django.utils.translation import gettext_lazy as _

# from dashboard.views.utils import has_field


# def _get_profile_model():
#     """
#     Essaie d'importer ton modèle de profil "social" ou générique.
#     Ajuste si ton modèle réel est ailleurs.
#     """
#     try:
#         from accounts_users.models.social.social_profile import SocialProfile
#         return SocialProfile
#     except Exception:
#         try:
#             from accounts_users.models.users_profile import UserProfile
#             return UserProfile
#         except Exception:
#             return None


# @staff_member_required
# def pending_profiles_list(request):
#     Profile = _get_profile_model()
#     if Profile is None:
#         messages.error(request, _("Aucun modèle de profil trouvé (SocialProfile/UserProfile)."))
#         return render(request, "dashboard/admin/pending_profiles_list.html", {"pending_profiles": []})

#     qs = Profile.objects.all()

#     # logique "pending" robuste selon champs existants
#     if has_field(Profile, "status"):
#         qs = qs.filter(status__in=["PENDING", "PENDING_VALIDATION", "WAITING", "EN_ATTENTE"])
#     elif has_field(Profile, "is_active_member"):
#         qs = qs.filter(is_active_member=False)
#     elif has_field(Profile, "is_approved"):
#         qs = qs.filter(is_approved=False)
#     else:
#         # pas de champ -> on ne devine pas, on affiche vide (pas fake)
#         qs = Profile.objects.none()

#     qs = qs.select_related("user").order_by("-created_at") if has_field(Profile, "created_at") else qs.select_related("user")

#     return render(request, "dashboard/admin/pending_profiles_list.html", {
#         "pending_profiles": qs,
#         "breadcrumbs": [
#             {"label": _("Dashboard"), "url": "/dashboard/"},
#             {"label": _("Admin"), "url": "/dashboard/admin/"},
#             {"label": _("Profils en attente"), "url": None},
#         ],
#     })


# @staff_member_required
# def validate_profile_view(request, profile_id):
#     Profile = _get_profile_model()
#     if Profile is None:
#         messages.error(request, _("Aucun modèle de profil trouvé."))
#         return redirect("dashboard:pending_profiles")

#     profile = get_object_or_404(Profile, pk=profile_id)

#     # champs possibles
#     if has_field(Profile, "status"):
#         profile.status = "APPROVED"
#         profile.save(update_fields=["status"])
#     elif has_field(Profile, "is_active_member"):
#         profile.is_active_member = True
#         profile.save(update_fields=["is_active_member"])
#     elif has_field(Profile, "is_approved"):
#         profile.is_approved = True
#         profile.save(update_fields=["is_approved"])

#     messages.success(request, _("Profil approuvé."))
#     return redirect("dashboard:pending_profiles")


# @staff_member_required
# def refuse_profile_view(request, profile_id):
#     Profile = _get_profile_model()
#     if Profile is None:
#         messages.error(request, _("Aucun modèle de profil trouvé."))
#         return redirect("dashboard:pending_profiles")

#     profile = get_object_or_404(Profile, pk=profile_id)

#     if has_field(Profile, "status"):
#         profile.status = "REFUSED"
#         profile.save(update_fields=["status"])
#     elif has_field(Profile, "is_active_member"):
#         profile.is_active_member = False
#         profile.save(update_fields=["is_active_member"])
#     elif has_field(Profile, "is_approved"):
#         profile.is_approved = False
#         profile.save(update_fields=["is_approved"])

#     messages.warning(request, _("Profil refusé."))
#     return redirect("dashboard:pending_profiles")





# from django.contrib.admin.views.decorators import staff_member_required
# from django.shortcuts import render, get_object_or_404, redirect
# from django.contrib import messages
# from django.utils.translation import gettext_lazy as _
# from django.core.mail import send_mail
# from django.template.loader import render_to_string
# from django.conf import settings

# from accounts_users.models.users_economic_profile import UserEconomicProfile


# # ======================================================
# # LISTE DES PROFILS EN ATTENTE
# # ======================================================
# @staff_member_required
# def pending_profiles_list(request):
#     profiles = UserEconomicProfile.objects.filter(status=UserEconomicProfile.Status.PENDING)
#     return render(request, "dashboard/profile/pending_list.html", {"profiles": profiles})


# # ======================================================
# # APPROBATION PROFIL
# # ======================================================
# @staff_member_required
# def validate_profile_view(request, profile_id):
#     profile = get_object_or_404(UserEconomicProfile, id=profile_id)
#     user = profile.user

#     profile.status = UserEconomicProfile.Status.APPROVED
#     profile.save(update_fields=["status", "updated_at"])

#     subject = _("Validation de votre profil SOGENTIS")
#     html_message = render_to_string("accounts_users/emails/profile_approved.html", {"user": user, "profile": profile})

#     send_mail(
#         subject=subject,
#         message=_("Votre profil a été validé."),
#         from_email=settings.DEFAULT_FROM_EMAIL,
#         recipient_list=[user.email],
#         html_message=html_message,
#         fail_silently=True,  # évite de casser l'admin si SMTP down
#     )

#     messages.success(request, _("Le profil a été validé et un e-mail a été envoyé."))
#     return redirect("dashboard:pending_profiles")


# # ======================================================
# # REFUS PROFIL
# # ======================================================
# @staff_member_required
# def refuse_profile_view(request, profile_id):
#     profile = get_object_or_404(UserEconomicProfile, id=profile_id)
#     user = profile.user

#     profile.status = UserEconomicProfile.Status.REFUSED
#     profile.save(update_fields=["status", "updated_at"])

#     subject = _("Votre profil SOGENTIS a été refusé")
#     html_message = render_to_string("accounts_users/emails/profile_refused.html", {"user": user, "profile": profile})

#     send_mail(
#         subject=subject,
#         message=_("Votre profil n’a pas été validé."),
#         from_email=settings.DEFAULT_FROM_EMAIL,
#         recipient_list=[user.email],
#         html_message=html_message,
#         fail_silently=True,
#     )

#     messages.error(request, _("Le profil a été refusé et un e-mail a été envoyé."))
#     return redirect("dashboard:pending_profiles")








# # dashboard/views/pending_profiles.py
# from django.contrib.admin.views.decorators import staff_member_required
# from django.shortcuts import render, get_object_or_404, redirect
# from django.contrib import messages
# from django.utils.translation import gettext_lazy as _
# from django.core.mail import send_mail
# from django.template.loader import render_to_string
# from django.conf import settings

# from accounts_users.models.users_economic_profile import UserProfile


# # ======================================================
# # LISTE DES PROFILS EN ATTENTE
# # ======================================================
# # @staff_member_required
# def pending_profiles_list(request):
#     profiles = UserProfile.objects.filter(status="pending")
#     return render(request, "dashboard/profile/pending_list.html", {
#         "profiles": profiles
#     })


# # ======================================================
# # APPROBATION PROFIL
# # ======================================================
# # @staff_member_required
# def validate_profile_view(request, profile_id):
#     profile = get_object_or_404(UserProfile, id=profile_id)
#     user = profile.user

#     # 1. mise à jour statut
#     profile.status = "approved"
#     profile.save()

#     # 2. envoi email
#     subject = _("Validation de votre profil SOGENTIS")
#     html_message = render_to_string(
#         "accounts_users/emails/profile_approved.html",
#         {"user": user}
#     )

#     send_mail(
#         subject=subject,
#         message=_("Votre profil a été validé."),
#         from_email=settings.DEFAULT_FROM_EMAIL,
#         recipient_list=[user.email],
#         html_message=html_message,
#     )

#     # 3. message interface
#     messages.success(request, _("Le profil a été validé et un e-mail a été envoyé."))

#     return redirect("dashboard:pending_profiles")


# # ======================================================
# # REFUS PROFIL
# # ======================================================
# # @staff_member_required
# def refuse_profile_view(request, profile_id):
#     profile = get_object_or_404(UserProfile, id=profile_id)
#     user = profile.user

#     # 1. mise à jour statut
#     profile.status = "refused"
#     profile.save()

#     # 2. envoi email
#     subject = _("Votre profil SOGENTIS a été refusé")
#     html_message = render_to_string(
#         "accounts_users/emails/profile_refused.html",
#         {"user": user}
#     )

#     send_mail(
#         subject=subject,
#         message=_("Votre profil n’a pas été validé."),
#         from_email=settings.DEFAULT_FROM_EMAIL,
#         recipient_list=[user.email],
#         html_message=html_message,
#     )

#     # 3. message interface
#     messages.error(request, _("Le profil a été refusé et un e-mail a été envoyé."))

#     return redirect("dashboard:pending_profiles")
