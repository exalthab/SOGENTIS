# core/rate_limit.py
from __future__ import annotations

from django.core.cache import cache


def rate_limited(key: str, limit: int, window_seconds: int) -> bool:
    """
    Retourne True si dépassement.
    Implémentation simple: compteur dans cache.
    """
    current = cache.get(key)
    if current is None:
        cache.set(key, 1, timeout=window_seconds)
        return False

    try:
        current = cache.incr(key)
    except ValueError:
        cache.set(key, 1, timeout=window_seconds)
        current = 1

    return int(current) > int(limit)
