# core/services/turnstile.py
from __future__ import annotations

import json
import urllib.parse
import urllib.request
from typing import Optional, Tuple, List

from django.conf import settings

TURNSTILE_VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"


def is_turnstile_enabled() -> bool:
    return bool(getattr(settings, "TURNSTILE_ENABLED", False)) and bool(getattr(settings, "TURNSTILE_SECRETKEY", ""))


def verify_turnstile(token: str, remoteip: Optional[str] = None) -> Tuple[bool, List[str]]:
    if not is_turnstile_enabled():
        return True, []

    token = (token or "").strip()
    if not token:
        return False, ["missing-input-response"]

    data = {"secret": settings.TURNSTILE_SECRETKEY, "response": token}
    if remoteip:
        data["remoteip"] = remoteip

    payload = urllib.parse.urlencode(data).encode("utf-8")
    req = urllib.request.Request(
        TURNSTILE_VERIFY_URL,
        data=payload,
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    timeout = int(getattr(settings, "TURNSTILE_TIMEOUT", 5))
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except Exception:
        return False, ["network-error"]

    return bool(result.get("success", False)), (result.get("error-codes") or [])
