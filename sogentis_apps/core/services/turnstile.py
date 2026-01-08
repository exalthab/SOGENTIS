# core/services/turnstile.py
from __future__ import annotations

import json
import urllib.parse
import urllib.request
from typing import Optional, Tuple, List

from django.conf import settings

TURNSTILE_VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"


def is_turnstile_enabled() -> bool:
    return bool(getattr(settings, "TURNSTILE_ENABLED", False)) and bool(
        (getattr(settings, "TURNSTILE_SECRETKEY", "") or "").strip()
    )


def verify_turnstile(token: str, remoteip: Optional[str] = None) -> Tuple[bool, List[str]]:
    if not is_turnstile_enabled():
        return True, []

    token = (token or "").strip()
    if not token:
        return False, ["missing-input-response"]

    secret = (getattr(settings, "TURNSTILE_SECRETKEY", "") or "").strip()
    if not secret:
        return False, ["missing-input-secret"]

    data = {"secret": secret, "response": token}

    # ✅ Ne pas envoyer remoteip par défaut (souvent source d’échec derrière proxy)
    send_ip = bool(getattr(settings, "TURNSTILE_SEND_REMOTEIP", False))
    if send_ip and remoteip:
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





# # core/services/turnstile.py
# from __future__ import annotations

# import json
# import urllib.parse
# import urllib.request
# from typing import Optional, Tuple, List

# from django.conf import settings
# from django.utils.crypto import constant_time_compare

# TURNSTILE_VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"


# def is_turnstile_enabled() -> bool:
#     return bool(getattr(settings, "TURNSTILE_ENABLED", False)) and bool(
#         (getattr(settings, "TURNSTILE_SECRETKEY", "") or "").strip()
#     )


# def verify_turnstile(token: str, remoteip: Optional[str] = None) -> Tuple[bool, List[str]]:
#     """
#     Vérifie Turnstile côté serveur.
#     Retour: (success, error_codes)

#     Notes:
#     - Ne passe remoteip que si tu es sûr de l'IP client (sinon mieux vaut None).
#     - En cas d'erreur réseau: retourne (False, ['network-error'])
#     """
#     if not is_turnstile_enabled():
#         return True, []

#     token = (token or "").strip()
#     if not token:
#         return False, ["missing-input-response"]

#     secret = (getattr(settings, "TURNSTILE_SECRETKEY", "") or "").strip()
#     if not secret:
#         return False, ["missing-input-secret"]

#     data = {
#         "secret": secret,
#         "response": token,
#     }

#     # Option : n'envoyer remoteip que si explicitement autorisé
#     send_ip = bool(getattr(settings, "TURNSTILE_SEND_REMOTEIP", False))
#     if send_ip and remoteip:
#         data["remoteip"] = remoteip

#     payload = urllib.parse.urlencode(data).encode("utf-8")
#     req = urllib.request.Request(
#         TURNSTILE_VERIFY_URL,
#         data=payload,
#         method="POST",
#         headers={"Content-Type": "application/x-www-form-urlencoded"},
#     )

#     timeout = int(getattr(settings, "TURNSTILE_TIMEOUT", 5))
#     try:
#         with urllib.request.urlopen(req, timeout=timeout) as resp:
#             raw = resp.read().decode("utf-8", errors="replace")
#             result = json.loads(raw or "{}")
#     except Exception:
#         return False, ["network-error"]

#     success = bool(result.get("success", False))

#     # Cloudflare renvoie "error-codes" (liste). Parfois aussi "messages".
#     errors = result.get("error-codes") or []
#     msgs = result.get("messages") or []
#     if isinstance(msgs, list):
#         # on concatène dans errors si utile
#         errors = list(errors) + [f"msg:{m}" for m in msgs if isinstance(m, str) and m]

#     # Optionnel: si tu veux vérifier l'action/hostname (Turnstile peut fournir "hostname" selon config)
#     expected_hostname = (getattr(settings, "TURNSTILE_EXPECTED_HOSTNAME", "") or "").strip().lower()
#     if success and expected_hostname:
#         hostname = (result.get("hostname") or "").strip().lower()
#         if hostname and not constant_time_compare(hostname, expected_hostname):
#             return False, ["hostname-mismatch"]

#     return success, errors






# # core/services/turnstile.py
# from __future__ import annotations

# import json
# import urllib.parse
# import urllib.request
# from typing import Optional, Tuple, List

# from django.conf import settings

# TURNSTILE_VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"


# def is_turnstile_enabled() -> bool:
#     return bool(getattr(settings, "TURNSTILE_ENABLED", False)) and bool(getattr(settings, "TURNSTILE_SECRETKEY", ""))


# def verify_turnstile(token: str, remoteip: Optional[str] = None) -> Tuple[bool, List[str]]:
#     if not is_turnstile_enabled():
#         return True, []

#     token = (token or "").strip()
#     if not token:
#         return False, ["missing-input-response"]

#     data = {"secret": settings.TURNSTILE_SECRETKEY, "response": token}
#     if remoteip:
#         data["remoteip"] = remoteip

#     payload = urllib.parse.urlencode(data).encode("utf-8")
#     req = urllib.request.Request(
#         TURNSTILE_VERIFY_URL,
#         data=payload,
#         method="POST",
#         headers={"Content-Type": "application/x-www-form-urlencoded"},
#     )

#     timeout = int(getattr(settings, "TURNSTILE_TIMEOUT", 5))
#     try:
#         with urllib.request.urlopen(req, timeout=timeout) as resp:
#             result = json.loads(resp.read().decode("utf-8"))
#     except Exception:
#         return False, ["network-error"]

#     return bool(result.get("success", False)), (result.get("error-codes") or [])
