# core/services/email_domain_check.py
from __future__ import annotations

import socket
import time
from typing import Optional

from django.core.cache import cache
import dns.resolver
import dns.exception


def _idna(domain: str) -> str:
    """Convertit un domaine en ASCII compatible (punycode)."""
    domain = (domain or "").strip().lower()
    try:
        return domain.encode("idna").decode("ascii")
    except Exception:
        return domain


def domain_accepts_mail(domain: str, cache_seconds: int = 24 * 3600) -> bool:
    """
    Vérifie si un domaine peut recevoir des emails.

    Règles :
      - MX existe -> OK
      - Sinon A/AAAA existe -> OK (RFC autorise)
      - Sinon -> KO

    Optimisé pour :
      - Résilience DNS
      - Réponse rapide
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

    def _has_rr(rrtype: str) -> bool:
        """Vérifie si le domaine a un enregistrement DNS de type `rrtype`."""
        try:
            answers = resolver.resolve(domain, rrtype)
            return bool(answers)
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers):
            return False
        except (dns.exception.Timeout, dns.exception.DNSException, socket.gaierror):
            # Échec réseau/DNS → considérer temporairement comme invalide
            return False

    start = time.time()
    ok = _has_rr("MX") or _has_rr("A") or _has_rr("AAAA")
    elapsed = time.time() - start

    # Ajuste la durée du cache si DNS lent
    ttl = cache_seconds
    if elapsed > 1.0:
        ttl = min(ttl, 300)  # 5 minutes pour réponses lentes
    cache.set(cache_key, ok, ttl)

    return ok
