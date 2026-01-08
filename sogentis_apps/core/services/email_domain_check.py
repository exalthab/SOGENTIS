# core/services/email_domain_check.py
from __future__ import annotations

from typing import Optional
from django.core.cache import cache
import dns.resolver
import dns.exception
import socket
import time

def _idna(domain: str) -> str:
    """Convertit un domaine en ASCII compatible (punycode)."""
    domain = (domain or "").strip().lower()
    try:
        return domain.encode("idna").decode("ascii")
    except Exception:
        return domain

def domain_accepts_mail(domain: str, cache_seconds: int = 24 * 3600) -> bool:
    """
    Vérifie si un domaine peut recevoir des emails :
      - MX existe -> OK
      - Sinon A/AAAA existe -> OK (cas RFC)
      - Sinon -> KO
    Optimisé pour :
      - Résilience DNS
      - Temps de réponse rapide
      - Cache efficace pour réduire les requêtes DNS répétées
    """
    domain = _idna(domain)
    if not domain or "." not in domain:
        return False

    cache_key = f"maildom:{domain}"
    cached = cache.get(cache_key)
    if cached is not None:
        return bool(cached)

    resolver = dns.resolver.Resolver()
    resolver.lifetime = 2.0
    resolver.timeout = 1.0

    # Vérifie un type d'enregistrement DNS
    def _has_rr(rrtype: str) -> bool:
        try:
            ans = resolver.resolve(domain, rrtype)
            return bool(ans)
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers):
            return False
        except (dns.exception.Timeout, dns.exception.DNSException, socket.gaierror):
            # Échec réseau / DNS → considérer temporairement comme invalide
            return False

    start = time.time()
    ok = _has_rr("MX") or _has_rr("A") or _has_rr("AAAA")
    elapsed = time.time() - start

    # Si DNS trop lent (> 1s), cache temporaire plus courte
    ttl = cache_seconds
    if elapsed > 1.0:
        ttl = min(ttl, 300)  # 5 min
    cache.set(cache_key, ok, ttl)
    return ok








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
