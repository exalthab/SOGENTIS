# core/services/hcaptcha.py
from __future__ import annotations

import json
import urllib.parse
import urllib.request
from typing import Optional, Tuple, List

from django.conf import settings

HCAPTCHA_VERIFY_URL = "https://api.hcaptcha.com/siteverify"


def is_hcaptcha_enabled() -> bool:
    return bool(getattr(settings, "HCAPTCHA_ENABLED", False)) and bool(
        getattr(settings, "HCAPTCHA_SECRETKEY", "")
    )


def verify_hcaptcha(token: str, remoteip: Optional[str] = None) -> Tuple[bool, List[str]]:
    """
    Vérifie le token hCaptcha côté serveur.
    Retourne: (success, error_codes)
    """
    if not is_hcaptcha_enabled():
        return True, []

    token = (token or "").strip()
    if not token:
        return False, ["missing-input-response"]

    data = {
        "secret": getattr(settings, "HCAPTCHA_SECRETKEY", ""),
        "response": token,  # token hCaptcha
    }
    if remoteip:
        data["remoteip"] = remoteip

    payload = urllib.parse.urlencode(data).encode("utf-8")
    req = urllib.request.Request(
        HCAPTCHA_VERIFY_URL,
        data=payload,
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    timeout = int(getattr(settings, "HCAPTCHA_TIMEOUT", 5))

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            result = json.loads(body)
    except Exception:
        return False, ["network-error"]

    success = bool(result.get("success", False))
    errors = result.get("error-codes") or result.get("error_codes") or []
    return success, errors
