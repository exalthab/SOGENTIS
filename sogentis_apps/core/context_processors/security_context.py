# core/context_processors/security_context.py
from __future__ import annotations

from django.conf import settings


def antispam(request):
    """
    Contexte anti-spam global (safe).
    Fournit uniquement hCaptcha.
    """
    enabled = bool(getattr(settings, "HCAPTCHA_ENABLED", False))
    sitekey = (getattr(settings, "HCAPTCHA_SITEKEY", "") or "").strip()
    secret = (getattr(settings, "HCAPTCHA_SECRETKEY", "") or "").strip()
    theme = (getattr(settings, "HCAPTCHA_THEME", "light") or "light").strip()

    # ✅ On active seulement si la config est complète (évite widget invisible)
    active = bool(enabled and sitekey and secret)

    return {
        "HCAPTCHA_ENABLED": active,
        "HCAPTCHA_SITEKEY": sitekey,
        "HCAPTCHA_THEME": theme,
    }









# # core/context_processors/security_context.py
# from __future__ import annotations

# from django.conf import settings


# def antispam(request):
#     """
#     Contexte anti-spam global (safe).
#     Évite de casser les templates si certaines vars ne sont pas définies.
#     """

#     h_enabled = bool(getattr(settings, "HCAPTCHA_ENABLED", False))
#     h_sitekey = (getattr(settings, "HCAPTCHA_SITEKEY", "") or "").strip()
#     h_secret = (getattr(settings, "HCAPTCHA_SECRETKEY", "") or "").strip()

#     return {
#         # hCaptcha
#         "HCAPTCHA_ENABLED": bool(h_enabled and h_sitekey and h_secret),
#         "HCAPTCHA_SITEKEY": h_sitekey,
#         "HCAPTCHA_THEME": getattr(settings, "HCAPTCHA_THEME", "light"),

#         # (optionnel) Turnstile si tu le réactives plus tard
#         "TURNSTILE_ENABLED": bool(getattr(settings, "TURNSTILE_ENABLED", False)),
#         "TURNSTILE_SITEKEY": (getattr(settings, "TURNSTILE_SITEKEY", "") or "").strip(),
#     }
