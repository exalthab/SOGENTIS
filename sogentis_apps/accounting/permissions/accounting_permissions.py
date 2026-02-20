# accounting/permissions/accounting_permissions.py
from __future__ import annotations

from functools import wraps
from typing import Callable

from django.core.exceptions import PermissionDenied


PERMS_VIEW_ANY = (
    "accounting.view_account",
    "accounting.view_journal",
    "accounting.view_journalentry",
    "accounting.view_journalline",
)

DASHBOARD_ACCESS_FLAG = "dashboard.access_accounting_space"


def can_access_accounting(user) -> bool:
    if not user or not getattr(user, "is_authenticated", False):
        return False
    if getattr(user, "is_superuser", False) or getattr(user, "is_staff", False):
        return True
    try:
        if user.has_perm(DASHBOARD_ACCESS_FLAG):
            return True
        return any(user.has_perm(p) for p in PERMS_VIEW_ANY)
    except Exception:
        return False


def accounting_required(view_func: Callable):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not can_access_accounting(getattr(request, "user", None)):
            raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return _wrapped
