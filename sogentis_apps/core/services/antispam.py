# core/services/antispam.py
from __future__ import annotations
import time
from typing import List
from django.core.cache import cache


def rate_limited(key: str, limit: int = 5, window_seconds: int = 300) -> bool:
    """
    Vérifie si une clé (ex: IP) a dépassé le nombre de tentatives autorisées.
    - key : identifiant unique (IP, email, etc.)
    - limit : nombre max de tentatives dans la fenêtre
    - window_seconds : durée de la fenêtre en secondes
    """
    now = int(time.time())
    attempts: List[int] = cache.get(key, [])

    # Nettoyage des timestamps expirés
    attempts = [t for t in attempts if t > now - window_seconds]

    if len(attempts) >= limit:
        # Déjà trop de tentatives
        cache.set(key, attempts, timeout=window_seconds)
        return True

    # Ajout de la tentative et mise à jour du cache
    attempts.append(now)
    cache.set(key, attempts, timeout=window_seconds)
    return False





# # core/services/email_domain_check.py
# from __future__ import annotations

# from typing import Optional

# from django.core.cache import cache

# import dns.resolver
# import dns.exception


# def _idna(domain: str) -> str:
#     domain = (domain or "").strip().lower()
#     try:
#         return domain.encode("idna").decode("ascii")
#     except Exception:
#         return domain


# def domain_accepts_mail(domain: str, cache_seconds: int = 24 * 3600) -> bool:
#     """
#     Vérifie si un domaine peut recevoir des emails:
#     - MX existe -> OK
#     - sinon A/AAAA existe -> OK (cas RFC)
#     - sinon -> KO
#     Cache pour éviter de refaire des DNS en boucle.
#     """
#     domain = _idna(domain)
#     if not domain or "." not in domain:
#         return False

#     key = f"maildom:{domain}"
#     cached = cache.get(key)
#     if cached is not None:
#         return bool(cached)

#     resolver = dns.resolver.Resolver()
#     resolver.lifetime = 2.0  # timeout global
#     resolver.timeout = 1.0

#     def _has_rr(rrtype: str) -> bool:
#         try:
#             ans = resolver.resolve(domain, rrtype)
#             return len(ans) > 0
#         except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers, dns.exception.Timeout, dns.exception.DNSException):
#             return False

#     ok = _has_rr("MX") or _has_rr("A") or _has_rr("AAAA")
#     cache.set(key, ok, cache_seconds)
#     return ok
