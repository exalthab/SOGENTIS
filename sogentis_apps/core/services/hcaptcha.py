# core/services/hcaptcha.py
from __future__ import annotations

import json
import logging
import urllib.parse
import urllib.request
from typing import Optional, Tuple, List

from django.conf import settings

logger = logging.getLogger(__name__)

HCAPTCHA_VERIFY_URL = "https://hcaptcha.com/siteverify"


def is_hcaptcha_enabled() -> bool:
    return bool(getattr(settings, "HCAPTCHA_ENABLED", False)) and bool(getattr(settings, "HCAPTCHA_SECRETKEY", ""))


def verify_hcaptcha(token: str, remoteip: Optional[str] = None) -> Tuple[bool, List[str], bool]:
    """
    Vérifie le token hCaptcha.
    Retourne: (ok, error_codes, unavailable)
      - ok: True si validé
      - error_codes: codes hCaptcha ou internes
      - unavailable: True si on n'a pas pu joindre hCaptcha (timeout/DNS/etc.)
    """
    if not is_hcaptcha_enabled():
        return True, [], False

    token = (token or "").strip()
    if not token:
        return False, ["missing-input-response"], False

    data = {"secret": settings.HCAPTCHA_SECRETKEY, "response": token}
    if remoteip:
        data["remoteip"] = remoteip

    payload = urllib.parse.urlencode(data).encode("utf-8")

    try:
        req = urllib.request.Request(HCAPTCHA_VERIFY_URL, data=payload, method="POST")
        with urllib.request.urlopen(req, timeout=getattr(settings, "HCAPTCHA_TIMEOUT", 7)) as resp:
            raw = resp.read().decode("utf-8")
        parsed = json.loads(raw or "{}")
    except Exception as exc:
        # Service indisponible
        logger.warning("hCaptcha verify unavailable: %s", exc)
        return False, ["hcaptcha-verify-unavailable"], True

    ok = bool(parsed.get("success", False))
    codes = parsed.get("error-codes") or []
    if isinstance(codes, str):
        codes = [codes]
    return ok, list(codes), False
