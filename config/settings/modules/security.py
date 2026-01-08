# config/settings/modules/security.py

from decouple import config, Csv

DEBUG = config("DEBUG", default=False, cast=bool)

# ==========================
# HTTPS & cookies
# ==========================
SECURE_SSL_REDIRECT = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = False  # ✅ IMPORTANT (Django requirement)

# ==========================
# Security headers
# ==========================
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True

# ==========================
# Sessions
# ==========================
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 3600  # 1 heure

# ==========================
# Admins
# ==========================
ADMINS = [("Admin SOGENTIS", "contact@sogentis.org")]
MANAGERS = ADMINS

# ==========================
# Production-only hardening
# ==========================
if not DEBUG:
    SECURE_HSTS_SECONDS = 31536000  # 1 an
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    DATA_UPLOAD_MAX_MEMORY_SIZE = 2_621_440  # 2.5 MB
    FILE_UPLOAD_MAX_MEMORY_SIZE = 2_621_440

    SERVER_EMAIL = config("SERVER_EMAIL", default="server@sogentis.org")

# ==========================
# Auth
# ==========================
PASSWORD_RESET_TIMEOUT = 60 * 60 * 48  # 48h

# ==========================
# Proxy (si derrière CDN / reverse proxy)
# ==========================
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# ==========================
# CSRF
# ==========================
CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS",
    default="https://sogentis.org,https://www.sogentis.org",
    cast=Csv(),
)

# ==========================
# Anti-bot
# ==========================
TURNSTILE_ENABLED = config("TURNSTILE_ENABLED", cast=bool, default=False)
TURNSTILE_SITEKEY = config("TURNSTILE_SITEKEY", default="")
TURNSTILE_SECRETKEY = config("TURNSTILE_SECRETKEY", default="")
TURNSTILE_TIMEOUT = config("TURNSTILE_TIMEOUT", cast=int, default=5)
TURNSTILE_SEND_REMOTEIP = config("TURNSTILE_SEND_REMOTEIP", cast=bool, default=False)

HCAPTCHA_ENABLED = config("HCAPTCHA_ENABLED", cast=bool, default=False)
HCAPTCHA_SITEKEY = config("HCAPTCHA_SITEKEY", default="")
HCAPTCHA_SECRETKEY = config("HCAPTCHA_SECRETKEY", default="")
HCAPTCHA_TIMEOUT = config("HCAPTCHA_TIMEOUT", cast=int, default=5)
HCAPTCHA_THEME = config("HCAPTCHA_THEME", default="light")

CONTACT_HCAPTCHA_MODE = config("CONTACT_HCAPTCHA_MODE", default="fallback")

# ==========================
# Anti-spam contact
# ==========================
CONTACT_RATE_LIMIT_WINDOW = config("CONTACT_RATE_LIMIT_WINDOW", cast=int, default=300)
CONTACT_RATE_LIMIT_MAX = config("CONTACT_RATE_LIMIT_MAX", cast=int, default=3)
CONTACT_VERIFY_TOKEN_HOURS = config("CONTACT_VERIFY_TOKEN_HOURS", cast=int, default=24)

CONTACT_NOTIFY_EMAILS = ["contact@sogentis.org"]

# ✅ UNIFIÉ
DEFAULT_FROM_EMAIL = config("CONTACT_FROM_EMAIL", default="contact@sogentis.org")

CONTACT_BLOCKED_EMAIL_DOMAINS = [
    "mailinator.com",
    "10minutemail.com",
    "tempmail.com",
]







# # config/settings/modules/security.py

# from decouple import config, Csv

# DEBUG = config("DEBUG", default=False, cast=bool)

# # === HTTPS & cookies ===
# SECURE_SSL_REDIRECT = not DEBUG
# SESSION_COOKIE_SECURE = not DEBUG
# CSRF_COOKIE_SECURE = not DEBUG

# SESSION_COOKIE_HTTPONLY = True
# CSRF_COOKIE_HTTPONLY = True

# # === Security headers ===
# X_FRAME_OPTIONS = "DENY"
# SECURE_CONTENT_TYPE_NOSNIFF = True
# SECURE_BROWSER_XSS_FILTER = True

# # === Sessions ===
# SESSION_EXPIRE_AT_BROWSER_CLOSE = True
# SESSION_COOKIE_AGE = 3600  # 1 heure

# # === Admins ===
# ADMINS = [("Admin SOGENTIS", "contact@sogentis.org")]
# MANAGERS = ADMINS

# # === Production-only hardening ===
# if not DEBUG:
#     SECURE_HSTS_SECONDS = 31536000  # 1 an
#     SECURE_HSTS_INCLUDE_SUBDOMAINS = True
#     SECURE_HSTS_PRELOAD = True

#     DATA_UPLOAD_MAX_MEMORY_SIZE = 2_621_440  # 2.5 MB
#     FILE_UPLOAD_MAX_MEMORY_SIZE = 2_621_440

#     SERVER_EMAIL = config("SERVER_EMAIL", default="server@sogentis.org")

# # === Auth ===
# PASSWORD_RESET_TIMEOUT = 60 * 60 * 48  # 48h

# # === Proxy (si applicable) ===
# SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# # === CSRF ===
# CSRF_TRUSTED_ORIGINS = config(
#     "CSRF_TRUSTED_ORIGINS",
#     default="",
#     cast=Csv(),
# )


# # === Anti-bot ===
# TURNSTILE_ENABLED = config("TURNSTILE_ENABLED", cast=bool, default=False)
# TURNSTILE_SITEKEY = config("TURNSTILE_SITEKEY", default="")
# TURNSTILE_SECRETKEY = config("TURNSTILE_SECRETKEY", default="")
# TURNSTILE_TIMEOUT = config("TURNSTILE_TIMEOUT", cast=int, default=5)

# TURNSTILE_SEND_REMOTEIP = config("TURNSTILE_SEND_REMOTEIP", cast=bool, default=False)
# TURNSTILE_EXPECTED_HOSTNAME = config("TURNSTILE_EXPECTED_HOSTNAME", default="")

# HCAPTCHA_ENABLED = config("HCAPTCHA_ENABLED", cast=bool, default=False)
# HCAPTCHA_SITEKEY = config("HCAPTCHA_SITEKEY", default="")
# HCAPTCHA_SECRETKEY = config("HCAPTCHA_SECRETKEY", default="")
# HCAPTCHA_TIMEOUT = config("HCAPTCHA_TIMEOUT", cast=int, default=5)
# HCAPTCHA_THEME = config("HCAPTCHA_THEME", default="light")

# CONTACT_HCAPTCHA_MODE = config("CONTACT_HCAPTCHA_MODE", default="fallback")

# # === Anti-spam contact ===
# CONTACT_RATE_LIMIT_WINDOW = config("CONTACT_RATE_LIMIT_WINDOW", cast=int, default=300)
# CONTACT_RATE_LIMIT_MAX = config("CONTACT_RATE_LIMIT_MAX", cast=int, default=3)
# CONTACT_VERIFY_TOKEN_HOURS = config("CONTACT_VERIFY_TOKEN_HOURS", cast=int, default=24)

# CONTACT_NOTIFY_EMAILS = ["contact@sogentis.org"]
# CONTACT_FROM_EMAIL = config("CONTACT_FROM_EMAIL", default="")

# CONTACT_BLOCKED_EMAIL_DOMAINS = [
#     "mailinator.com",
#     "10minutemail.com",
#     "tempmail.com",
# ]




# # config/settings/modules/security.py

# from decouple import config

# DEBUG = config("DEBUG", default=False, cast=bool)

# # === HTTPS and secure cookies ===
# SECURE_SSL_REDIRECT = not DEBUG
# SESSION_COOKIE_SECURE = not DEBUG
# CSRF_COOKIE_SECURE = not DEBUG

# # === HTTPOnly cookies for security ===
# SESSION_COOKIE_HTTPONLY = True
# CSRF_COOKIE_HTTPONLY = True

# # === Clickjacking protection ===
# X_FRAME_OPTIONS = "DENY"

# # === XSS and content type sniffing protection ===
# SECURE_BROWSER_XSS_FILTER = True
# SECURE_CONTENT_TYPE_NOSNIFF = True

# # === Session settings ===
# # Expire session à la fermeture du navigateur (utile pour plus de sécurité)
# SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# # Durée de vie du cookie de session en secondes (1 heure)
# SESSION_COOKIE_AGE = 3600

# # === HTTP Strict Transport Security (HSTS) ===
# # Actif uniquement en production

# # === Define ADMINS ===

# ADMINS = [("Admin SOGENTIS", "contact@sogentis.org")]

# # === SECURITY HEADERS (production only) ===
# if not DEBUG:
#     SECURE_SSL_REDIRECT = True
#     SESSION_COOKIE_SECURE = True
#     CSRF_COOKIE_SECURE = True
#     SECURE_HSTS_SECONDS = 31536000 # 1 an
#     SECURE_HSTS_INCLUDE_SUBDOMAINS = True
#     SECURE_HSTS_PRELOAD = True
#     SECURE_BROWSER_XSS_FILTER = True
#     SECURE_CONTENT_TYPE_NOSNIFF = True
#     DATA_UPLOAD_MAX_MEMORY_SIZE = 2621440
#     FILE_UPLOAD_MAX_MEMORY_SIZE = 2621440
#     MANAGERS = ADMINS
#     SERVER_EMAIL = config("SERVER_EMAIL", default="server@sogentis.org")


# # === Durée de validité du token de réinitialisation de mot de passe ===
# PASSWORD_RESET_TIMEOUT = 60 * 60 * 48  # 48 heures
