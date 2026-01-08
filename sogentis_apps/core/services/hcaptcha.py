from __future__ import annotations
import json
import urllib.parse
import urllib.request
from typing import Optional, Tuple, List
from django.conf import settings

HCAPTCHA_VERIFY_URL = "https://hcaptcha.com/siteverify"


# === hCaptcha ===
def is_hcaptcha_enabled() -> bool:
    """Retourne True si hCaptcha est activé et la clé secrète est définie."""
    secret = (getattr(settings, "HCAPTCHA_SECRETKEY", "") or "").strip()
    return bool(getattr(settings, "HCAPTCHA_ENABLED", False)) and bool(secret)


def extract_hcaptcha_token(post_data: dict) -> str:
    """Récupère le token hCaptcha envoyé dans le formulaire."""
    return (post_data.get("h-captcha-response") or post_data.get("hcaptcha_token") or "").strip()


def verify_hcaptcha(token: Optional[str], remoteip: Optional[str] = None) -> Tuple[bool, List[str]]:
    """Vérifie le token hCaptcha côté serveur."""
    if not is_hcaptcha_enabled():
        return True, []

    token = (token or "").strip()
    if not token:
        return False, ["missing-input-response"]

    secret = (getattr(settings, "HCAPTCHA_SECRETKEY", "") or "").strip()
    if not secret:
        return False, ["missing-input-secret"]

    data = {"secret": secret, "response": token}
    if remoteip:
        data["remoteip"] = remoteip

    payload = urllib.parse.urlencode(data).encode("utf-8")
    timeout = int(getattr(settings, "HCAPTCHA_TIMEOUT", 5))

    req = urllib.request.Request(
        HCAPTCHA_VERIFY_URL,
        data=payload,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "sogentis-hcaptcha/1.0",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            parsed = json.loads(resp.read().decode("utf-8") or "{}")
    except Exception:
        return False, ["hcaptcha-unreachable"]

    success = bool(parsed.get("success", False))
    errors: List[str] = parsed.get("error-codes") or parsed.get("error_codes") or []

    return (success, [] if success else [str(e) for e in errors] or ["hcaptcha-failed"])






# core/services/hcaptcha.py
# from __future__ import annotations

# import json
# import urllib.parse
# import urllib.request
# from typing import Optional, Tuple, List

# from django.conf import settings

# HCAPTCHA_VERIFY_URL = "https://hcaptcha.com/siteverify"


# def is_hcaptcha_enabled() -> bool:
#     return bool(getattr(settings, "HCAPTCHA_ENABLED", False)) and bool(
#         (getattr(settings, "HCAPTCHA_SECRETKEY", "") or "").strip()
#     )


# def extract_hcaptcha_token(post_data) -> str:
#     """
#     hCaptcha poste le token dans 'h-captcha-response'
#     """
#     return (post_data.get("h-captcha-response") or "").strip()


# def verify_hcaptcha(token: str, remoteip: Optional[str] = None) -> Tuple[bool, List[str]]:
#     if not is_hcaptcha_enabled():
#         return True, []

#     token = (token or "").strip()
#     if not token:
#         return False, ["missing-input-response"]

#     secret = (getattr(settings, "HCAPTCHA_SECRETKEY", "") or "").strip()
#     if not secret:
#         return False, ["missing-input-secret"]

#     data = {
#         "secret": secret,
#         "response": token,
#     }
#     if remoteip:
#         data["remoteip"] = remoteip

#     payload = urllib.parse.urlencode(data).encode("utf-8")
#     timeout = int(getattr(settings, "HCAPTCHA_TIMEOUT", 5) or 5)

#     req = urllib.request.Request(
#         HCAPTCHA_VERIFY_URL,
#         data=payload,
#         headers={
#             "Content-Type": "application/x-www-form-urlencoded",
#             "User-Agent": "sogentis-hcaptcha/1.0",
#         },
#         method="POST",
#     )

#     try:
#         with urllib.request.urlopen(req, timeout=timeout) as resp:
#             parsed = json.loads(resp.read().decode("utf-8"))
#     except Exception:
#         return False, ["hcaptcha-unreachable"]

#     success = bool(parsed.get("success", False))
#     errors = parsed.get("error-codes") or parsed.get("error_codes") or []

#     if success:
#         return True, []
#     return False, [str(e) for e in errors] or ["hcaptcha-failed"]




# # core/services/hcaptcha.py
# from __future__ import annotations

# import json
# import urllib.parse
# import urllib.request
# from typing import Optional, Tuple, List

# from django.conf import settings

# HCAPTCHA_VERIFY_URL = "https://hcaptcha.com/siteverify"


# def is_hcaptcha_enabled() -> bool:
#     return bool(getattr(settings, "HCAPTCHA_ENABLED", False)) and bool(getattr(settings, "HCAPTCHA_SECRETKEY", ""))


# def extract_hcaptcha_token(post_data) -> str:
#     """
#     hCaptcha poste le token dans 'h-captcha-response' (standard).
#     """
#     return (post_data.get("h-captcha-response") or post_data.get("hcaptcha_token") or "").strip()


# def verify_hcaptcha(token: str, remoteip: Optional[str] = None) -> Tuple[bool, List[str]]:
#     if not is_hcaptcha_enabled():
#         return True, []

#     token = (token or "").strip()
#     if not token:
#         return False, ["missing-input-response"]

#     data = {"secret": settings.HCAPTCHA_SECRETKEY, "response": token}
#     if remoteip:
#         data["remoteip"] = remoteip

#     payload = urllib.parse.urlencode(data).encode("utf-8")
#     timeout = int(getattr(settings, "HCAPTCHA_TIMEOUT", 5) or 5)

#     req = urllib.request.Request(
#         HCAPTCHA_VERIFY_URL,
#         data=payload,
#         headers={
#             "Content-Type": "application/x-www-form-urlencoded",
#             "User-Agent": "sogentis-hcaptcha/1.0",
#         },
#         method="POST",
#     )

#     try:
#         with urllib.request.urlopen(req, timeout=timeout) as resp:
#             raw = resp.read().decode("utf-8")
#         parsed = json.loads(raw or "{}")
#     except Exception:
#         return False, ["hcaptcha-unreachable"]

#     success = bool(parsed.get("success", False))
#     # hCaptcha renvoie parfois "error-codes"
#     errors = parsed.get("error-codes") or []
#     if success:
#         return True, []
#     return False, [str(e) for e in errors] or ["hcaptcha-failed"]





# # core/services/hcaptcha.py
# from __future__ import annotations

# import json
# import urllib.parse
# import urllib.request
# from typing import Optional, Tuple, List

# from django.conf import settings

# HCAPTCHA_VERIFY_URL = "https://api.hcaptcha.com/siteverify"


# def is_hcaptcha_enabled() -> bool:
#     return bool(getattr(settings, "HCAPTCHA_ENABLED", False)) and bool(
#         getattr(settings, "HCAPTCHA_SECRETKEY", "")
#     )


# def verify_hcaptcha(token: str, remoteip: Optional[str] = None) -> Tuple[bool, List[str]]:
#     """
#     Vérifie le token hCaptcha côté serveur.
#     Retourne: (success, error_codes)
#     """
#     if not is_hcaptcha_enabled():
#         return True, []

#     token = (token or "").strip()
#     if not token:
#         return False, ["missing-input-response"]

#     data = {
#         "secret": getattr(settings, "HCAPTCHA_SECRETKEY", ""),
#         "response": token,  # token hCaptcha
#     }
#     if remoteip:
#         data["remoteip"] = remoteip

#     payload = urllib.parse.urlencode(data).encode("utf-8")
#     req = urllib.request.Request(
#         HCAPTCHA_VERIFY_URL,
#         data=payload,
#         method="POST",
#         headers={"Content-Type": "application/x-www-form-urlencoded"},
#     )

#     timeout = int(getattr(settings, "HCAPTCHA_TIMEOUT", 5))

#     try:
#         with urllib.request.urlopen(req, timeout=timeout) as resp:
#             body = resp.read().decode("utf-8")
#             result = json.loads(body)
#     except Exception:
#         return False, ["network-error"]

#     success = bool(result.get("success", False))
#     errors = result.get("error-codes") or result.get("error_codes") or []
#     return success, errors
