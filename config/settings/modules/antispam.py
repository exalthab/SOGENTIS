# config/settings/modules/antispam.py
import time
from typing import List

from django.core.cache import cache
from decouple import config


def rate_limited(key: str, limit: int = 5, window_seconds: int = 300) -> bool:
    """
    Vérifie si une clé (ex: IP) a dépassé le nombre de tentatives autorisées.
    """
    now = int(time.time())
    attempts: List[int] = cache.get(key, [])

    attempts = [t for t in attempts if t > now - window_seconds]

    if len(attempts) >= limit:
        cache.set(key, attempts, timeout=window_seconds)
        return True

    attempts.append(now)
    cache.set(key, attempts, timeout=window_seconds)
    return False


# Turnstile
TURNSTILE_ENABLED = config("TURNSTILE_ENABLED", cast=bool, default=False)
TURNSTILE_SITEKEY = config("TURNSTILE_SITEKEY", default="")
TURNSTILE_SECRETKEY = config("TURNSTILE_SECRETKEY", default="")
TURNSTILE_TIMEOUT = config("TURNSTILE_TIMEOUT", cast=int, default=5)

# hCaptcha
HCAPTCHA_ENABLED = config("HCAPTCHA_ENABLED", cast=bool, default=False)
HCAPTCHA_SITEKEY = config("HCAPTCHA_SITEKEY", default="")
HCAPTCHA_SECRETKEY = config("HCAPTCHA_SECRETKEY", default="")
HCAPTCHA_TIMEOUT = config("HCAPTCHA_TIMEOUT", cast=int, default=5)
HCAPTCHA_THEME = config("HCAPTCHA_THEME", default="light")

# off | fallback | always
CONTACT_HCAPTCHA_MODE = config("CONTACT_HCAPTCHA_MODE", default="fallback").lower().strip()

# Rate limit
CONTACT_RATE_LIMIT_WINDOW = config("CONTACT_RATE_LIMIT_WINDOW", cast=int, default=300)
CONTACT_RATE_LIMIT_MAX = config("CONTACT_RATE_LIMIT_MAX", cast=int, default=3)

CONTACT_VERIFY_TOKEN_HOURS = config("CONTACT_VERIFY_TOKEN_HOURS", cast=int, default=24)






# # config/settings/modules/antispam.py
# import time
# from typing import List
# from django.core.cache import cache
# from decouple import config



# def rate_limited(key: str, limit: int = 5, window_seconds: int = 300) -> bool:
#     """
#     Vérifie si une clé (ex: IP) a dépassé le nombre de tentatives autorisées.
#     - key : identifiant unique (IP, email, etc.)
#     - limit : nombre max de tentatives dans la fenêtre
#     - window_seconds : durée de la fenêtre en secondes
#     """
#     now = int(time.time())
#     attempts: List[int] = cache.get(key, [])

#     # Nettoyage des timestamps expirés
#     attempts = [t for t in attempts if t > now - window_seconds]

#     if len(attempts) >= limit:
#         # Déjà trop de tentatives
#         cache.set(key, attempts, timeout=window_seconds)
#         return True

#     # Ajout de la tentative et mise à jour du cache
#     attempts.append(now)
#     cache.set(key, attempts, timeout=window_seconds)
#     return False


# # Turnstile
# TURNSTILE_ENABLED = config("TURNSTILE_ENABLED", cast=bool, default=False)
# TURNSTILE_SITEKEY = config("TURNSTILE_SITEKEY", default="")
# TURNSTILE_SECRETKEY = config("TURNSTILE_SECRETKEY", default="")
# TURNSTILE_TIMEOUT = config("TURNSTILE_TIMEOUT", cast=int, default=5)

# # hCaptcha
# HCAPTCHA_ENABLED = config("HCAPTCHA_ENABLED", cast=bool, default=False)
# HCAPTCHA_SITEKEY = config("HCAPTCHA_SITEKEY", default="")
# HCAPTCHA_SECRETKEY = config("HCAPTCHA_SECRETKEY", default="")
# HCAPTCHA_TIMEOUT = config("HCAPTCHA_TIMEOUT", cast=int, default=5)
# HCAPTCHA_THEME = config("HCAPTCHA_THEME", default="light")

# # off | fallback | always
# CONTACT_HCAPTCHA_MODE = config("CONTACT_HCAPTCHA_MODE", default="off").lower().strip()

# # Rate limit
# CONTACT_RATE_LIMIT_WINDOW = config("CONTACT_RATE_LIMIT_WINDOW", cast=int, default=300)
# CONTACT_RATE_LIMIT_MAX = config("CONTACT_RATE_LIMIT_MAX", cast=int, default=3)

# # (si tu l'utilises ailleurs)
# CONTACT_VERIFY_TOKEN_HOURS = config("CONTACT_VERIFY_TOKEN_HOURS", cast=int, default=24)
