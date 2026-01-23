# core/services/email_domain_check.py
"""
Email Domain Check Service
--------------------------
Module pour vérifier si un email est autorisé en fonction des paramètres
de configuration Django : allowlist, blocklist, sous-domaines, TLD, et emails locaux.

Settings pris en charge :
- EMAIL_DOMAIN_ALLOWLIST: list[str]
- EMAIL_DOMAIN_BLOCKLIST: list[str]
- EMAIL_DOMAIN_REQUIRE_DOT: bool (default True)
- EMAIL_DOMAIN_ALLOW_SUBDOMAINS: bool (default True)
- EMAIL_DOMAIN_BLOCK_SUBDOMAINS: bool (default True)
- EMAIL_DOMAIN_BLOCK_LOCAL: bool (default True)
- EMAIL_DOMAIN_NORMALIZE_IDNA: bool (default True)  # unicode domains -> punycode
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Tuple

from django.conf import settings


# ============================================================
# Policy
# ============================================================
@dataclass(frozen=True)
class EmailDomainPolicy:
    """Configuration des règles de validation de domaines email."""
    allowlist: set[str]
    blocklist: set[str]
    require_dot: bool
    allow_subdomains: bool
    block_subdomains: bool
    block_local_domains: bool
    normalize_idna: bool


def _normalize_rule_domain(d: str) -> str:
    """
    Normalise un domaine venant des settings (allowlist / blocklist).
    - trim
    - lower
    - supprime '.' final
    - supprime '.' en tête (ex: .example.com)
    """
    x = (d or "").strip().lower().rstrip(".")
    while x.startswith("."):
        x = x[1:]
    return x


@lru_cache(maxsize=1)
def _policy() -> EmailDomainPolicy:
    """
    Retourne la configuration de validation des emails depuis settings Django.
    Memoization pour éviter la reconstruction à chaque appel.
    """
    allowlist_raw = getattr(settings, "EMAIL_DOMAIN_ALLOWLIST", []) or []
    blocklist_raw = getattr(settings, "EMAIL_DOMAIN_BLOCKLIST", []) or []

    allowlist = { _normalize_rule_domain(x) for x in allowlist_raw if _normalize_rule_domain(x) }
    blocklist = { _normalize_rule_domain(x) for x in blocklist_raw if _normalize_rule_domain(x) }

    return EmailDomainPolicy(
        allowlist=allowlist,
        blocklist=blocklist,
        require_dot=bool(getattr(settings, "EMAIL_DOMAIN_REQUIRE_DOT", True)),
        allow_subdomains=bool(getattr(settings, "EMAIL_DOMAIN_ALLOW_SUBDOMAINS", True)),
        block_subdomains=bool(getattr(settings, "EMAIL_DOMAIN_BLOCK_SUBDOMAINS", True)),
        block_local_domains=bool(getattr(settings, "EMAIL_DOMAIN_BLOCK_LOCAL", True)),
        normalize_idna=bool(getattr(settings, "EMAIL_DOMAIN_NORMALIZE_IDNA", True)),
    )


# ============================================================
# Helpers
# ============================================================
def _normalize_domain(domain: str, normalize_idna: bool) -> Tuple[str, str]:
    """
    Normalise un domaine (email).
    Retourne (domain_normalized, reason_code_if_error).
    """
    d = (domain or "").strip().lower().rstrip(".")
    if not d:
        return "", "missing-domain"

    # caractères/structure basiques
    if any(c in d for c in (" ", "/", "\\", "\t", "\n", "\r")):
        return "", "invalid-domain"

    # évite "a..b.com" ou ".."
    if ".." in d:
        return "", "invalid-domain"

    # IDNA (unicode domains) -> punycode si activé
    if normalize_idna:
        try:
            d = d.encode("idna").decode("ascii")
        except Exception:
            return "", "invalid-domain"

    return d, ""


def _extract_domain(email: str, normalize_idna: bool) -> Tuple[str, str]:
    """
    Extrait le domaine d'un email de manière robuste.
    Supporte : "Nom <user@domain.com>".

    Returns:
        (domain, reason_code_if_error)
    """
    e = (email or "").strip()

    # Format "Name <email@domain.com>"
    if "<" in e and ">" in e:
        inside = e.split("<", 1)[1].split(">", 1)[0].strip()
        e = inside or e

    if "@" not in e:
        return "", "missing-at"

    domain_part = e.split("@", 1)[1]
    return _normalize_domain(domain_part, normalize_idna=normalize_idna)


def _is_subdomain_of(domain: str, root: str) -> bool:
    """
    True si domain == root ou domain est un sous-domaine de root.
    ex: a.mailinator.com est subdomain de mailinator.com
    """
    if not domain or not root:
        return False
    domain = domain.lower().rstrip(".")
    root = root.lower().rstrip(".")
    return domain == root or domain.endswith("." + root)


def _looks_invalid_domain(domain: str, require_dot: bool, block_local: bool) -> Tuple[bool, str]:
    """
    Vérifie si le domaine semble invalide selon la configuration.

    Returns:
        (is_invalid, reason_code)
    """
    if not domain:
        return True, "missing-domain"

    # cas local / intranet
    if block_local and domain in {"localhost", "local", "invalid"}:
        return True, "local-domain"

    # "require_dot": évite user@domain (sans TLD)
    if require_dot and "." not in domain:
        return True, "missing-tld"

    return False, ""


# ============================================================
# Public API
# ============================================================
def is_email_domain_allowed(email: str) -> Tuple[bool, str]:
    """
    Vérifie si un email est autorisé selon la policy.

    Returns:
        (ok, reason_code)

    reason_code possibles:
    - missing-at
    - missing-domain
    - invalid-domain
    - local-domain
    - missing-tld
    - blocked-domain
    - not-allowed-domain
    """
    raw = (email or "").strip()
    if "@" not in raw:
        return False, "missing-at"

    p = _policy()

    domain, err = _extract_domain(raw, normalize_idna=p.normalize_idna)
    if err:
        return False, err

    invalid, reason = _looks_invalid_domain(domain, require_dot=p.require_dot, block_local=p.block_local_domains)
    if invalid:
        return False, reason

    # ----------------------------
    # Blocklist (prioritaire)
    # ----------------------------
    if p.blocklist:
        if p.block_subdomains:
            for b in p.blocklist:
                if _is_subdomain_of(domain, b):
                    return False, "blocked-domain"
        else:
            if domain in p.blocklist:
                return False, "blocked-domain"

    # ----------------------------
    # Allowlist (si définie)
    # ----------------------------
    if p.allowlist:
        if p.allow_subdomains:
            for a in p.allowlist:
                if _is_subdomain_of(domain, a):
                    return True, ""
            return False, "not-allowed-domain"
        else:
            if domain not in p.allowlist:
                return False, "not-allowed-domain"

    return True, ""







# # core/services/email_domain_check.py
# from __future__ import annotations

# from dataclasses import dataclass
# from typing import Optional, Tuple

# from django.conf import settings


# @dataclass(frozen=True)
# class EmailDomainPolicy:
#     allowlist: set[str]
#     blocklist: set[str]
#     require_dot: bool


# def _policy() -> EmailDomainPolicy:
#     allowlist = set(map(str.lower, getattr(settings, "EMAIL_DOMAIN_ALLOWLIST", []) or []))
#     blocklist = set(map(str.lower, getattr(settings, "EMAIL_DOMAIN_BLOCKLIST", []) or []))
#     require_dot = bool(getattr(settings, "EMAIL_DOMAIN_REQUIRE_DOT", True))
#     return EmailDomainPolicy(allowlist=allowlist, blocklist=blocklist, require_dot=require_dot)


# def is_email_domain_allowed(email: str) -> Tuple[bool, str]:
#     """
#     Retourne (ok, reason_code)
#     reason_code: 'missing-at' | 'missing-domain' | 'blocked-domain' | 'not-allowed-domain'
#     """
#     email = (email or "").strip()
#     if "@" not in email:
#         return False, "missing-at"

#     domain = email.split("@", 1)[1].strip().lower()
#     if not domain:
#         return False, "missing-domain"

#     p = _policy()

#     if p.require_dot and "." not in domain:
#         return False, "missing-domain"

#     if domain in p.blocklist:
#         return False, "blocked-domain"

#     if p.allowlist and domain not in p.allowlist:
#         return False, "not-allowed-domain"

#     return True, ""
