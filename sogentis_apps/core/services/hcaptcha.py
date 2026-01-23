# core/services/hcaptcha.py
from __future__ import annotations

import json
import logging
import urllib.parse
import urllib.request
from typing import List, Optional, Tuple

from django.conf import settings

logger = logging.getLogger(__name__)

HCAPTCHA_VERIFY_URL = "https://hcaptcha.com/siteverify"

# hCaptcha error codes officiels (utile pour debug/log)
# https://docs.hcaptcha.com/
_HCAPTCHA_MISSING = "missing-input-response"
_INTERNAL_UNAVAILABLE = "hcaptcha-verify-unavailable"


# ============================================================
# Settings helpers
# ============================================================
def is_hcaptcha_enabled() -> bool:
    """
    hCaptcha actif si:
      - HCAPTCHA_ENABLED = True
      - HCAPTCHA_SECRETKEY défini
    """
    enabled = bool(getattr(settings, "HCAPTCHA_ENABLED", False))
    secret = (getattr(settings, "HCAPTCHA_SECRETKEY", "") or "").strip()
    return enabled and bool(secret)


def get_hcaptcha_sitekey() -> str:
    """
    Pour les templates.
    """
    return (getattr(settings, "HCAPTCHA_SITEKEY", "") or "").strip()


def get_hcaptcha_timeout() -> int:
    """
    Timeout réseau (secondes).
    """
    try:
        return int(getattr(settings, "HCAPTCHA_TIMEOUT", 7))
    except Exception:
        return 7


def fail_open_enabled() -> bool:
    """
    Si True: en cas d'indisponibilité hCaptcha (DNS/timeout), on laisse passer.
    """
    return bool(getattr(settings, "HCAPTCHA_FAIL_OPEN", False))


# ============================================================
# Public API
# ============================================================
def verify_hcaptcha(token: str, remoteip: Optional[str] = None) -> Tuple[bool, List[str], bool]:
    """
    Vérifie le token hCaptcha.

    Returns:
      (ok, error_codes, unavailable)

      - ok: True si validé
      - error_codes: codes hCaptcha ou internes
      - unavailable: True si hCaptcha est injoignable (timeout/DNS/etc.)

    Notes:
      - Si hCaptcha est désactivé => ok=True (bypass).
      - En cas d'échec réseau => unavailable=True et ok=False (c'est la view qui décide fail_open).
    """
    if not is_hcaptcha_enabled():
        return True, [], False

    token = (token or "").strip()
    if not token:
        return False, [_HCAPTCHA_MISSING], False

    data = {
        "secret": (getattr(settings, "HCAPTCHA_SECRETKEY", "") or "").strip(),
        "response": token,
    }
    if remoteip:
        data["remoteip"] = remoteip

    payload = urllib.parse.urlencode(data).encode("utf-8")
    timeout = get_hcaptcha_timeout()

    try:
        req = urllib.request.Request(HCAPTCHA_VERIFY_URL, data=payload, method="POST")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
        parsed = json.loads(raw or "{}")
    except Exception as exc:
        # Service indisponible
        logger.warning("hCaptcha verify unavailable: %s", exc)
        return False, [_INTERNAL_UNAVAILABLE], True

    ok = bool(parsed.get("success", False))
    codes = parsed.get("error-codes") or []
    if isinstance(codes, str):
        codes = [codes]
    return ok, list(codes), False


def verify_hcaptcha_or_fail_open(token: str, remoteip: Optional[str] = None) -> Tuple[bool, List[str], bool]:
    """
    Helper pratique:
    - Si fail_open est activé et hCaptcha indisponible => ok=True.
    - Sinon => respecte verify_hcaptcha.

    Returns:
      (ok, error_codes, unavailable)
    """
    ok, codes, unavailable = verify_hcaptcha(token=token, remoteip=remoteip)
    if not ok and unavailable and fail_open_enabled():
        return True, codes, unavailable
    return ok, codes, unavailable






# # core/services/hcaptcha.py
# from __future__ import annotations

# import json
# import logging
# import urllib.parse
# import urllib.request
# from typing import Optional, Tuple, List

# from django.conf import settings

# logger = logging.getLogger(__name__)

# HCAPTCHA_VERIFY_URL = "https://hcaptcha.com/siteverify"


# def is_hcaptcha_enabled() -> bool:
#     return bool(getattr(settings, "HCAPTCHA_ENABLED", False)) and bool(getattr(settings, "HCAPTCHA_SECRETKEY", ""))


# def verify_hcaptcha(token: str, remoteip: Optional[str] = None) -> Tuple[bool, List[str], bool]:
#     """
#     Vérifie le token hCaptcha.
#     Retourne: (ok, error_codes, unavailable)
#       - ok: True si validé
#       - error_codes: codes hCaptcha ou internes
#       - unavailable: True si on n'a pas pu joindre hCaptcha (timeout/DNS/etc.)
#     """
#     if not is_hcaptcha_enabled():
#         return True, [], False

#     token = (token or "").strip()
#     if not token:
#         return False, ["missing-input-response"], False

#     data = {"secret": settings.HCAPTCHA_SECRETKEY, "response": token}
#     if remoteip:
#         data["remoteip"] = remoteip

#     payload = urllib.parse.urlencode(data).encode("utf-8")

#     try:
#         req = urllib.request.Request(HCAPTCHA_VERIFY_URL, data=payload, method="POST")
#         with urllib.request.urlopen(req, timeout=getattr(settings, "HCAPTCHA_TIMEOUT", 7)) as resp:
#             raw = resp.read().decode("utf-8")
#         parsed = json.loads(raw or "{}")
#     except Exception as exc:
#         # Service indisponible
#         logger.warning("hCaptcha verify unavailable: %s", exc)
#         return False, ["hcaptcha-verify-unavailable"], True

#     ok = bool(parsed.get("success", False))
#     codes = parsed.get("error-codes") or []
#     if isinstance(codes, str):
#         codes = [codes]
#     return ok, list(codes), False
