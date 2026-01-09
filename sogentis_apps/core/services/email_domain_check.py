# core/services/email_domain_check.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

from django.conf import settings


@dataclass(frozen=True)
class EmailDomainPolicy:
    allowlist: set[str]
    blocklist: set[str]
    require_dot: bool


def _policy() -> EmailDomainPolicy:
    allowlist = set(map(str.lower, getattr(settings, "EMAIL_DOMAIN_ALLOWLIST", []) or []))
    blocklist = set(map(str.lower, getattr(settings, "EMAIL_DOMAIN_BLOCKLIST", []) or []))
    require_dot = bool(getattr(settings, "EMAIL_DOMAIN_REQUIRE_DOT", True))
    return EmailDomainPolicy(allowlist=allowlist, blocklist=blocklist, require_dot=require_dot)


def is_email_domain_allowed(email: str) -> Tuple[bool, str]:
    """
    Retourne (ok, reason_code)
    reason_code: 'missing-at' | 'missing-domain' | 'blocked-domain' | 'not-allowed-domain'
    """
    email = (email or "").strip()
    if "@" not in email:
        return False, "missing-at"

    domain = email.split("@", 1)[1].strip().lower()
    if not domain:
        return False, "missing-domain"

    p = _policy()

    if p.require_dot and "." not in domain:
        return False, "missing-domain"

    if domain in p.blocklist:
        return False, "blocked-domain"

    if p.allowlist and domain not in p.allowlist:
        return False, "not-allowed-domain"

    return True, ""
