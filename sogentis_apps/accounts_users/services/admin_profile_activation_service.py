# accounts_users/services/admin_profile_activation_service.py
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models.fields import NOT_PROVIDED
from django.utils.timezone import now

logger = logging.getLogger(__name__)


APPROVED_CANDIDATES = ("approved", "validated", "active", "accepted", "ok")
PENDING_CANDIDATES = ("pending", "in_review", "waiting")


def _pick_choice_value_for_field(obj, field_name: str, preferred: Tuple[str, ...]) -> Optional[str]:
    """
    Retourne une valeur de choix valide si le champ a des choices.
    """
    try:
        f = obj._meta.get_field(field_name)
    except Exception:
        return None

    choices = getattr(f, "choices", None) or []
    if not choices:
        # champ sans choices -> on peut tenter directement la valeur "approved"
        return preferred[0] if preferred else None

    valid_values = {str(v) for (v, _label) in choices}
    for cand in preferred:
        if cand in valid_values:
            return cand
    return None


def _safe_set(obj, field: str, value: Any, changed: List[str]) -> None:
    if hasattr(obj, field):
        try:
            if getattr(obj, field) != value:
                setattr(obj, field, value)
                changed.append(field)
        except Exception:
            # si getter/setter échoue, on ignore
            return


def _can_create_profile_model(model) -> bool:
    """
    On ne crée un profil manquant QUE si tous les champs (hors user/auto/timestamps)
    sont optionnels (blank/null) ou ont un default.
    """
    required_blockers = []
    for f in model._meta.fields:
        name = getattr(f, "name", "")
        if name in ("id", "pk", "user", "created_at", "updated_at"):
            continue
        if getattr(f, "auto_created", False):
            continue
        if getattr(f, "primary_key", False):
            continue
        if getattr(f, "editable", True) is False:
            continue

        has_default = getattr(f, "default", NOT_PROVIDED) is not NOT_PROVIDED
        is_optional = bool(getattr(f, "blank", False)) or bool(getattr(f, "null", False))
        if not has_default and not is_optional:
            required_blockers.append(name)

    return len(required_blockers) == 0


def _get_related_one_to_one_profiles(user) -> List[Any]:
    """
    Récupère tous les profils OneToOne reliés au user (sans dépendre des noms).
    """
    rel_profiles = []
    for rel in user._meta.related_objects:
        # OneToOneRel
        if getattr(rel, "one_to_one", False) and hasattr(rel, "get_accessor_name"):
            accessor = rel.get_accessor_name()
            try:
                prof = getattr(user, accessor)
                rel_profiles.append(prof)
            except ObjectDoesNotExist:
                # profil manquant: on tente une création safe si possible
                model = getattr(rel, "related_model", None)
                if model and _can_create_profile_model(model):
                    try:
                        prof = model.objects.create(user=user)
                        rel_profiles.append(prof)
                    except Exception as e:
                        logger.warning("Impossible de créer le profil %s pour %s: %s", model, user, e)
            except Exception:
                continue
    return rel_profiles


def _approve_profile_obj(profile) -> List[str]:
    """
    Marque un objet profil comme 'approuvé/actif' si possible.
    Retourne les champs modifiés.
    """
    changed: List[str] = []

    # status (choices-safe)
    if hasattr(profile, "status"):
        v = _pick_choice_value_for_field(profile, "status", APPROVED_CANDIDATES)
        if v:
            _safe_set(profile, "status", v, changed)

    # flags communs
    _safe_set(profile, "is_approved", True, changed)
    _safe_set(profile, "approved", True, changed)
    _safe_set(profile, "is_validated", True, changed)
    _safe_set(profile, "validated", True, changed)
    _safe_set(profile, "is_active_member", True, changed)
    _safe_set(profile, "is_active", True, changed)
    _safe_set(profile, "active", True, changed)

    # timestamps
    ts = now()
    _safe_set(profile, "approved_at", ts, changed)
    _safe_set(profile, "validated_at", ts, changed)
    _safe_set(profile, "activated_at", ts, changed)

    # vérifications (si tu veux bypass pour l’admin)
    _safe_set(profile, "email_verified", True, changed)
    _safe_set(profile, "is_email_verified", True, changed)
    _safe_set(profile, "phone_verified", True, changed)
    _safe_set(profile, "is_phone_verified", True, changed)

    if changed:
        try:
            profile.save(update_fields=list(set(changed)))
        except Exception:
            # fallback save normal si update_fields bloque
            profile.save()

    return changed


@transaction.atomic
def activate_admin_user(user, ensure_is_active: bool = True) -> Dict[str, Any]:
    """
    Active le compte admin/superuser + approuve ses profils liés.
    """
    res: Dict[str, Any] = {
        "user_id": user.pk,
        "username": getattr(user, "username", ""),
        "email": getattr(user, "email", ""),
        "user_updated": False,
        "profiles": [],
    }

    if ensure_is_active and hasattr(user, "is_active") and not user.is_active:
        user.is_active = True
        try:
            user.save(update_fields=["is_active"])
        except Exception:
            user.save()
        res["user_updated"] = True

    profiles = _get_related_one_to_one_profiles(user)
    for p in profiles:
        changed = _approve_profile_obj(p)
        res["profiles"].append(
            {
                "model": f"{p._meta.app_label}.{p.__class__.__name__}",
                "id": getattr(p, "pk", None),
                "changed_fields": changed,
            }
        )

    return res


@transaction.atomic
def activate_all_admins(also_staff: bool = True) -> Dict[str, Any]:
    """
    Active tous les superusers (et staff si demandé) + leurs profils.
    """
    User = get_user_model()
    qs = User.objects.filter(is_superuser=True)
    if also_staff:
        qs = qs.union(User.objects.filter(is_staff=True))

    out = {"count": 0, "results": []}
    for u in qs.distinct():
        out["results"].append(activate_admin_user(u, ensure_is_active=True))
        out["count"] += 1
    return out
