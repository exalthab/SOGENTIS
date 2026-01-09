# config/settings/modules/antispam.py
import time
from typing import List

from decouple import config
from django.core.cache import cache


# ============================================================
# hCaptcha settings
# ============================================================
HCAPTCHA_ENABLED = config("HCAPTCHA_ENABLED", cast=bool, default=False)
HCAPTCHA_SITEKEY = config("HCAPTCHA_SITEKEY", default="")
HCAPTCHA_SECRETKEY = config("HCAPTCHA_SECRETKEY", default="")
HCAPTCHA_TIMEOUT = config("HCAPTCHA_TIMEOUT", cast=int, default=7)

# Fallback si hCaptcha indisponible (timeout, DNS...)
HCAPTCHA_FAIL_OPEN = config("HCAPTCHA_FAIL_OPEN", cast=bool, default=False)


# ============================================================
# Rate limiting (contact)
# ============================================================
CONTACT_RATE_LIMIT_ENABLED = config("CONTACT_RATE_LIMIT_ENABLED", cast=bool, default=True)
CONTACT_RATE_LIMIT_WINDOW_SECONDS = config("CONTACT_RATE_LIMIT_WINDOW_SECONDS", cast=int, default=300)
CONTACT_RATE_LIMIT_MAX_ATTEMPTS = config("CONTACT_RATE_LIMIT_MAX_ATTEMPTS", cast=int, default=5)


def rate_limited(key: str, limit: int = 5, window_seconds: int = 300) -> bool:
    """
    Rate limit simple basé sur cache.
    - key: ex "contact:ip:1.2.3.4" ou "contact:ip:1.2.3.4:email:a@b.com"
    - limit: nombre max de tentatives dans la fenêtre
    - window_seconds: durée fenêtre (secondes)
    """
    now = int(time.time())
    bucket = (now // max(1, window_seconds))  # bucket par fenêtre

    cache_key = f"rl:{key}:{bucket}"
    attempts = cache.get(cache_key, 0)

    if attempts >= limit:
        return True

    # Incrémente et garde jusqu'à la fin de fenêtre (+ petite marge)
    ttl = window_seconds + 5
    cache.set(cache_key, int(attempts) + 1, timeout=ttl)
    return False


def rate_limit_reason_codes(ip: str, email: str | None = None) -> List[str]:
    """
    Renvoie une liste de codes qui expliquent quel rate-limit a bloqué.
    """
    codes: List[str] = []
    if not CONTACT_RATE_LIMIT_ENABLED:
        return codes

    window = CONTACT_RATE_LIMIT_WINDOW_SECONDS
    limit = CONTACT_RATE_LIMIT_MAX_ATTEMPTS

    ip = (ip or "").strip()
    email = (email or "").strip().lower()

    if ip and rate_limited(f"contact:ip:{ip}", limit=limit, window_seconds=window):
        codes.append("rate-limit-ip")

    # Optionnel: limiter aussi par paire IP+email (utile contre spam ciblé)
    if ip and email and rate_limited(f"contact:ip:{ip}:email:{email}", limit=limit, window_seconds=window):
        codes.append("rate-limit-ip-email")

    return codes
