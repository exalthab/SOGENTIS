# config/settings/modules/security.py

from decouple import config, Csv

# ==========================================================
# Environment
# ==========================================================
DEBUG = config("DEBUG", cast=bool, default=False)

# ==========================================================
# HTTPS & Cookies
# ==========================================================
SECURE_SSL_REDIRECT = config(
    "SECURE_SSL_REDIRECT",
    cast=bool,
    default=not DEBUG,
)

SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = False  # requis par Django

SESSION_COOKIE_SAMESITE = config("SESSION_COOKIE_SAMESITE", default="Lax")
CSRF_COOKIE_SAMESITE = config("CSRF_COOKIE_SAMESITE", default="Lax")

# ==========================================================
# Security headers
# ==========================================================
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = config(
    "SECURE_REFERRER_POLICY",
    default="strict-origin-when-cross-origin",
)

# ==========================================================
# Sessions
# ==========================================================
SESSION_EXPIRE_AT_BROWSER_CLOSE = config(
    "SESSION_EXPIRE_AT_BROWSER_CLOSE",
    cast=bool,
    default=True,
)
SESSION_COOKIE_AGE = config("SESSION_COOKIE_AGE", cast=int, default=3600)

# ==========================================================
# Admins / Managers
# ==========================================================
_admins_raw = config(
    "ADMINS",
    default="Admin SOGENTIS:contact@sogentis.org",
)

ADMINS = []
for item in (x.strip() for x in _admins_raw.split(",") if x.strip()):
    if ":" in item:
        name, email = item.split(":", 1)
        ADMINS.append((name.strip(), email.strip()))
    else:
        ADMINS.append(("Admin", item))

MANAGERS = ADMINS

# ==========================================================
# Production-only hardening
# ==========================================================
if not DEBUG:
    SECURE_HSTS_SECONDS = config(
        "SECURE_HSTS_SECONDS",
        cast=int,
        default=31536000,  # 1 an
    )
    SECURE_HSTS_INCLUDE_SUBDOMAINS = config(
        "SECURE_HSTS_INCLUDE_SUBDOMAINS",
        cast=bool,
        default=True,
    )
    SECURE_HSTS_PRELOAD = config(
        "SECURE_HSTS_PRELOAD",
        cast=bool,
        default=True,
    )

    # Upload limits (~2.5 MB)
    DATA_UPLOAD_MAX_MEMORY_SIZE = config(
        "DATA_UPLOAD_MAX_MEMORY_SIZE",
        cast=int,
        default=2_621_440,
    )
    FILE_UPLOAD_MAX_MEMORY_SIZE = config(
        "FILE_UPLOAD_MAX_MEMORY_SIZE",
        cast=int,
        default=2_621_440,
    )

# ==========================================================
# Auth
# ==========================================================
PASSWORD_RESET_TIMEOUT = config(
    "PASSWORD_RESET_TIMEOUT",
    cast=int,
    default=60 * 60 * 48,  # 48h
)

# ==========================================================
# Reverse proxy (Nginx / Traefik / Cloudflare)
# ==========================================================
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

USE_X_FORWARDED_HOST = config(
    "USE_X_FORWARDED_HOST",
    cast=bool,
    default=True,
)

# ==========================================================
# CSRF
# ==========================================================
CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS",
    cast=Csv(),
    default=",".join([
        "https://sogentis.org",
        "https://www.sogentis.org",
        "https://sogentis.com",
        "https://www.sogentis.com",
        "https://sogentis.sn",
        "https://www.sogentis.sn",
    ]),
)

# ==========================================================
# Anti-spam / Contact
# ==========================================================
CONTACT_RATE_LIMIT_WINDOW = config(
    "CONTACT_RATE_LIMIT_WINDOW",
    cast=int,
    default=300,  # 5 min
)
CONTACT_RATE_LIMIT_MAX = config(
    "CONTACT_RATE_LIMIT_MAX",
    cast=int,
    default=3,
)
CONTACT_VERIFY_TOKEN_HOURS = config(
    "CONTACT_VERIFY_TOKEN_HOURS",
    cast=int,
    default=24,
)

CONTACT_NOTIFY_EMAILS = config(
    "CONTACT_NOTIFY_EMAILS",
    cast=Csv(),
    default="contact@sogentis.org",
)

# IMPORTANT:
# DEFAULT_FROM_EMAIL est défini dans modules/email.py
CONTACT_FROM_EMAIL = config(
    "CONTACT_FROM_EMAIL",
    default="contact@sogentis.org",
)

CONTACT_BLOCKED_EMAIL_DOMAINS = config(
    "CONTACT_BLOCKED_EMAIL_DOMAINS",
    cast=Csv(),
    default="mailinator.com,10minutemail.com,tempmail.com",
)





# # config/settings/modules/security.py 09/01/2026
# from decouple import config, Csv

# DEBUG = config("DEBUG", cast=bool, default=False)

# # ==========================
# # HTTPS & cookies
# # ==========================
# SECURE_SSL_REDIRECT = not DEBUG
# SESSION_COOKIE_SECURE = not DEBUG
# CSRF_COOKIE_SECURE = not DEBUG

# SESSION_COOKIE_HTTPONLY = True
# CSRF_COOKIE_HTTPONLY = False  # Django requirement

# SESSION_COOKIE_SAMESITE = config("SESSION_COOKIE_SAMESITE", default="Lax")
# CSRF_COOKIE_SAMESITE = config("CSRF_COOKIE_SAMESITE", default="Lax")

# # ==========================
# # Security headers
# # ==========================
# X_FRAME_OPTIONS = "DENY"
# SECURE_CONTENT_TYPE_NOSNIFF = True
# SECURE_REFERRER_POLICY = config("SECURE_REFERRER_POLICY", default="strict-origin-when-cross-origin")

# # ==========================
# # Sessions
# # ==========================
# SESSION_EXPIRE_AT_BROWSER_CLOSE = config("SESSION_EXPIRE_AT_BROWSER_CLOSE", cast=bool, default=True)
# SESSION_COOKIE_AGE = config("SESSION_COOKIE_AGE", cast=int, default=3600)

# # ==========================
# # Admins / Managers
# # ==========================
# _admins_raw = config("ADMINS", default="Admin SOGENTIS:contact@sogentis.org")
# ADMINS = []
# for item in [x.strip() for x in _admins_raw.split(",") if x.strip()]:
#     if ":" in item:
#         name, email = item.split(":", 1)
#         ADMINS.append((name.strip(), email.strip()))
#     else:
#         ADMINS.append(("Admin", item.strip()))
# MANAGERS = ADMINS

# # ==========================
# # Production-only hardening
# # ==========================
# if not DEBUG:
#     SECURE_HSTS_SECONDS = config("SECURE_HSTS_SECONDS", cast=int, default=31536000)
#     SECURE_HSTS_INCLUDE_SUBDOMAINS = config("SECURE_HSTS_INCLUDE_SUBDOMAINS", cast=bool, default=True)
#     SECURE_HSTS_PRELOAD = config("SECURE_HSTS_PRELOAD", cast=bool, default=True)

#     DATA_UPLOAD_MAX_MEMORY_SIZE = config("DATA_UPLOAD_MAX_MEMORY_SIZE", cast=int, default=2_621_440)
#     FILE_UPLOAD_MAX_MEMORY_SIZE = config("FILE_UPLOAD_MAX_MEMORY_SIZE", cast=int, default=2_621_440)

# # ==========================
# # Auth
# # ==========================
# PASSWORD_RESET_TIMEOUT = config("PASSWORD_RESET_TIMEOUT", cast=int, default=60 * 60 * 48)

# # ==========================
# # Proxy (si derrière reverse proxy)
# # ==========================
# SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
# USE_X_FORWARDED_HOST = True

# # ==========================
# # CSRF
# # ==========================
# CSRF_TRUSTED_ORIGINS = config(
#     "CSRF_TRUSTED_ORIGINS",
#     default=",".join([
#         "https://sogentis.org",
#         "https://www.sogentis.org",
#         "https://sogentis.com",
#         "https://www.sogentis.com",
#         "https://sogentis.sn",
#         "https://www.sogentis.sn",
#     ]),
#     cast=Csv(),
# )

# # ==========================
# # Anti-spam contact
# # ==========================
# CONTACT_RATE_LIMIT_WINDOW = config("CONTACT_RATE_LIMIT_WINDOW", cast=int, default=300)
# CONTACT_RATE_LIMIT_MAX = config("CONTACT_RATE_LIMIT_MAX", cast=int, default=3)
# CONTACT_VERIFY_TOKEN_HOURS = config("CONTACT_VERIFY_TOKEN_HOURS", cast=int, default=24)

# CONTACT_NOTIFY_EMAILS = config(
#     "CONTACT_NOTIFY_EMAILS",
#     default="contact@sogentis.org",
#     cast=Csv(),
# )

# # IMPORTANT : on ne touche PAS à DEFAULT_FROM_EMAIL ici.
# # Email global -> modules/email.py
# CONTACT_FROM_EMAIL = config("CONTACT_FROM_EMAIL", default="contact@sogentis.org")

# CONTACT_BLOCKED_EMAIL_DOMAINS = config(
#     "CONTACT_BLOCKED_EMAIL_DOMAINS",
#     default="mailinator.com,10minutemail.com,tempmail.com",
#     cast=Csv(),
# )





# # config/settings/modules/security.py
# from decouple import config, Csv

# DEBUG = config("DEBUG", cast=bool, default=False)

# # ==========================
# # HTTPS & cookies
# # ==========================
# SECURE_SSL_REDIRECT = not DEBUG
# SESSION_COOKIE_SECURE = not DEBUG
# CSRF_COOKIE_SECURE = not DEBUG

# SESSION_COOKIE_HTTPONLY = True
# CSRF_COOKIE_HTTPONLY = False  # Django requirement

# # Lax = bon compromis (anti-CSRF + compat login)
# SESSION_COOKIE_SAMESITE = config("SESSION_COOKIE_SAMESITE", default="Lax")
# CSRF_COOKIE_SAMESITE = config("CSRF_COOKIE_SAMESITE", default="Lax")

# # ==========================
# # Security headers
# # ==========================
# X_FRAME_OPTIONS = "DENY"
# SECURE_CONTENT_TYPE_NOSNIFF = True
# SECURE_REFERRER_POLICY = config("SECURE_REFERRER_POLICY", default="strict-origin-when-cross-origin")

# # ==========================
# # Sessions
# # ==========================
# SESSION_EXPIRE_AT_BROWSER_CLOSE = config("SESSION_EXPIRE_AT_BROWSER_CLOSE", cast=bool, default=True)
# SESSION_COOKIE_AGE = config("SESSION_COOKIE_AGE", cast=int, default=3600)  # 1 heure

# # ==========================
# # Admins / Managers
# # ==========================
# # Format .env: ADMINS="Admin SOGENTIS:contact@sogentis.org,Other:other@mail.com"
# _admins_raw = config("ADMINS", default="Admin SOGENTIS:contact@sogentis.org")
# ADMINS = []
# for item in [x.strip() for x in _admins_raw.split(",") if x.strip()]:
#     if ":" in item:
#         name, email = item.split(":", 1)
#         ADMINS.append((name.strip(), email.strip()))
#     else:
#         ADMINS.append(("Admin", item.strip()))
# MANAGERS = ADMINS

# # ==========================
# # Production-only hardening
# # ==========================
# if not DEBUG:
#     SECURE_HSTS_SECONDS = config("SECURE_HSTS_SECONDS", cast=int, default=31536000)  # 1 an
#     SECURE_HSTS_INCLUDE_SUBDOMAINS = config("SECURE_HSTS_INCLUDE_SUBDOMAINS", cast=bool, default=True)
#     SECURE_HSTS_PRELOAD = config("SECURE_HSTS_PRELOAD", cast=bool, default=True)

#     DATA_UPLOAD_MAX_MEMORY_SIZE = config("DATA_UPLOAD_MAX_MEMORY_SIZE", cast=int, default=2_621_440)  # ~2.5MB
#     FILE_UPLOAD_MAX_MEMORY_SIZE = config("FILE_UPLOAD_MAX_MEMORY_SIZE", cast=int, default=2_621_440)

#     SERVER_EMAIL = config("SERVER_EMAIL", default="server@sogentis.org")

# # ==========================
# # Auth
# # ==========================
# PASSWORD_RESET_TIMEOUT = config("PASSWORD_RESET_TIMEOUT", cast=int, default=60 * 60 * 48)  # 48h

# # ==========================
# # Proxy (si derrière CDN / reverse proxy)
# # ==========================
# SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
# USE_X_FORWARDED_HOST = True

# # ==========================
# # CSRF
# # ==========================
# CSRF_TRUSTED_ORIGINS = config(
#     "CSRF_TRUSTED_ORIGINS",
#     default=",".join([
#         "https://sogentis.org",
#         "https://www.sogentis.org",
#         "https://sogentis.com",
#         "https://www.sogentis.com",
#         "https://sogentis.sn",
#         "https://www.sogentis.sn",
#     ]),
#     cast=Csv(),
# )

# # ==========================
# # Anti-spam contact
# # ==========================
# CONTACT_RATE_LIMIT_WINDOW = config("CONTACT_RATE_LIMIT_WINDOW", cast=int, default=300)
# CONTACT_RATE_LIMIT_MAX = config("CONTACT_RATE_LIMIT_MAX", cast=int, default=3)
# CONTACT_VERIFY_TOKEN_HOURS = config("CONTACT_VERIFY_TOKEN_HOURS", cast=int, default=24)

# CONTACT_NOTIFY_EMAILS = config(
#     "CONTACT_NOTIFY_EMAILS",
#     default="contact@sogentis.org",
#     cast=Csv(),
# )

# # Unifié (contact)
# DEFAULT_FROM_EMAIL = config("CONTACT_FROM_EMAIL", default="contact@sogentis.org")

# CONTACT_BLOCKED_EMAIL_DOMAINS = config(
#     "CONTACT_BLOCKED_EMAIL_DOMAINS",
#     default="mailinator.com,10minutemail.com,tempmail.com",
#     cast=Csv(),
# )






# # config/settings/modules/security.py
# from decouple import config, Csv

# DEBUG = config("DEBUG", cast=bool, default=False)

# # ==========================
# # HTTPS & cookies
# # ==========================
# SECURE_SSL_REDIRECT = not DEBUG
# SESSION_COOKIE_SECURE = not DEBUG
# CSRF_COOKIE_SECURE = not DEBUG

# SESSION_COOKIE_HTTPONLY = True
# CSRF_COOKIE_HTTPONLY = False  # Django requirement (CSRF cookie accessible by JS if needed)

# # Lax = bon compromis (anti-CSRF + compat login)
# SESSION_COOKIE_SAMESITE = config("SESSION_COOKIE_SAMESITE", default="Lax")
# CSRF_COOKIE_SAMESITE = config("CSRF_COOKIE_SAMESITE", default="Lax")

# # ==========================
# # Security headers
# # ==========================
# X_FRAME_OPTIONS = "DENY"
# SECURE_CONTENT_TYPE_NOSNIFF = True
# SECURE_REFERRER_POLICY = config("SECURE_REFERRER_POLICY", default="strict-origin-when-cross-origin")

# # ==========================
# # Sessions
# # ==========================
# SESSION_EXPIRE_AT_BROWSER_CLOSE = config("SESSION_EXPIRE_AT_BROWSER_CLOSE", cast=bool, default=True)
# SESSION_COOKIE_AGE = config("SESSION_COOKIE_AGE", cast=int, default=3600)  # 1 heure

# # ==========================
# # Admins / Managers
# # ==========================
# # Format .env: ADMINS="Admin SOGENTIS:contact@sogentis.org,Other:other@mail.com"
# _admins_raw = config("ADMINS", default="Admin SOGENTIS:contact@sogentis.org")
# ADMINS = []
# for item in [x.strip() for x in _admins_raw.split(",") if x.strip()]:
#     if ":" in item:
#         name, email = item.split(":", 1)
#         ADMINS.append((name.strip(), email.strip()))
#     else:
#         ADMINS.append(("Admin", item.strip()))
# MANAGERS = ADMINS

# # ==========================
# # Production-only hardening
# # ==========================
# if not DEBUG:
#     SECURE_HSTS_SECONDS = config("SECURE_HSTS_SECONDS", cast=int, default=31536000)  # 1 an
#     SECURE_HSTS_INCLUDE_SUBDOMAINS = config("SECURE_HSTS_INCLUDE_SUBDOMAINS", cast=bool, default=True)
#     SECURE_HSTS_PRELOAD = config("SECURE_HSTS_PRELOAD", cast=bool, default=True)

#     DATA_UPLOAD_MAX_MEMORY_SIZE = config("DATA_UPLOAD_MAX_MEMORY_SIZE", cast=int, default=2_621_440)  # ~2.5MB
#     FILE_UPLOAD_MAX_MEMORY_SIZE = config("FILE_UPLOAD_MAX_MEMORY_SIZE", cast=int, default=2_621_440)

#     SERVER_EMAIL = config("SERVER_EMAIL", default="server@sogentis.org")

# # ==========================
# # Auth
# # ==========================
# PASSWORD_RESET_TIMEOUT = config("PASSWORD_RESET_TIMEOUT", cast=int, default=60 * 60 * 48)  # 48h

# # ==========================
# # Proxy (si derrière CDN / reverse proxy)
# # ==========================
# SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
# USE_X_FORWARDED_HOST = True

# # ==========================
# # CSRF
# # ==========================
# # IMPORTANT: origins séparées par virgules (pas de concat involontaire)
# CSRF_TRUSTED_ORIGINS = config(
#     "CSRF_TRUSTED_ORIGINS",
#     default=",".join([
#         "https://sogentis.org",
#         "https://www.sogentis.org",
#         "https://sogentis.com",
#         "https://www.sogentis.com",
#         "https://sogentis.sn",
#         "https://www.sogentis.sn",
#     ]),
#     cast=Csv(),
# )

# # ==========================
# # Anti-bot (env)
# # ==========================
# HCAPTCHA_ENABLED = config("HCAPTCHA_ENABLED", cast=bool, default=False)
# HCAPTCHA_SITEKEY = config("HCAPTCHA_SITEKEY", default="")
# HCAPTCHA_SECRETKEY = config("HCAPTCHA_SECRETKEY", default="")
# HCAPTCHA_TIMEOUT = config("HCAPTCHA_TIMEOUT", cast=int, default=5)
# HCAPTCHA_THEME = config("HCAPTCHA_THEME", default="light")

# # ==========================
# # Anti-spam contact
# # ==========================
# CONTACT_RATE_LIMIT_WINDOW = config("CONTACT_RATE_LIMIT_WINDOW", cast=int, default=300)
# CONTACT_RATE_LIMIT_MAX = config("CONTACT_RATE_LIMIT_MAX", cast=int, default=3)
# CONTACT_VERIFY_TOKEN_HOURS = config("CONTACT_VERIFY_TOKEN_HOURS", cast=int, default=24)

# CONTACT_NOTIFY_EMAILS = config(
#     "CONTACT_NOTIFY_EMAILS",
#     default="contact@sogentis.org",
#     cast=Csv(),
# )

# # Unifié
# DEFAULT_FROM_EMAIL = config("CONTACT_FROM_EMAIL", default="contact@sogentis.org")

# CONTACT_BLOCKED_EMAIL_DOMAINS = config(
#     "CONTACT_BLOCKED_EMAIL_DOMAINS",
#     default="mailinator.com,10minutemail.com,tempmail.com",
#     cast=Csv(),
# )






# # config/settings/modules/security.py
# from decouple import config, Csv

# DEBUG = config("DEBUG", default=False, cast=bool)

# # ==========================
# # HTTPS & cookies
# # ==========================
# SECURE_SSL_REDIRECT = not DEBUG
# SESSION_COOKIE_SECURE = not DEBUG
# CSRF_COOKIE_SECURE = not DEBUG

# SESSION_COOKIE_HTTPONLY = True
# CSRF_COOKIE_HTTPONLY = False  # ✅ Django requirement

# # ==========================
# # Security headers
# # ==========================
# X_FRAME_OPTIONS = "DENY"
# SECURE_CONTENT_TYPE_NOSNIFF = True

# # ==========================
# # Sessions
# # ==========================
# SESSION_EXPIRE_AT_BROWSER_CLOSE = True
# SESSION_COOKIE_AGE = 3600  # 1 heure

# # ==========================
# # Admins
# # ==========================
# ADMINS = [("Admin SOGENTIS", "contact@sogentis.org")]
# MANAGERS = ADMINS

# # ==========================
# # Production-only hardening
# # ==========================
# if not DEBUG:
#     SECURE_HSTS_SECONDS = 31536000  # 1 an
#     SECURE_HSTS_INCLUDE_SUBDOMAINS = True
#     SECURE_HSTS_PRELOAD = True

#     DATA_UPLOAD_MAX_MEMORY_SIZE = 2_621_440  # 2.5 MB
#     FILE_UPLOAD_MAX_MEMORY_SIZE = 2_621_440

#     SERVER_EMAIL = config("SERVER_EMAIL", default="server@sogentis.org")

# # ==========================
# # Auth
# # ==========================
# PASSWORD_RESET_TIMEOUT = 60 * 60 * 48  # 48h

# # ==========================
# # Proxy (si derrière CDN / reverse proxy)
# # ==========================
# SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
# USE_X_FORWARDED_HOST = True

# # ==========================
# # CSRF
# # ==========================
# CSRF_TRUSTED_ORIGINS = config(
#     "CSRF_TRUSTED_ORIGINS",
#     default="https://sogentis.org,https://www.sogentis.org",
#             "https://sogentis.com,https://www.sogentis.com",
#             "https://sogentis.sn,https://www.sogentis.sn",
#     cast=Csv(),
# )

# # ==========================
# # Anti-bot (env)
# # ==========================
# # TURNSTILE_ENABLED = config("TURNSTILE_ENABLED", cast=bool, default=False)
# # TURNSTILE_SITEKEY = config("TURNSTILE_SITEKEY", default="")
# # TURNSTILE_SECRETKEY = config("TURNSTILE_SECRETKEY", default="")
# # TURNSTILE_TIMEOUT = config("TURNSTILE_TIMEOUT", cast=int, default=5)
# # TURNSTILE_SEND_REMOTEIP = config("TURNSTILE_SEND_REMOTEIP", cast=bool, default=False)

# HCAPTCHA_ENABLED = config("HCAPTCHA_ENABLED", cast=bool, default=False)
# HCAPTCHA_SITEKEY = config("HCAPTCHA_SITEKEY", default="")
# HCAPTCHA_SECRETKEY = config("HCAPTCHA_SECRETKEY", default="")
# HCAPTCHA_TIMEOUT = config("HCAPTCHA_TIMEOUT", cast=int, default=5)
# HCAPTCHA_THEME = config("HCAPTCHA_THEME", default="light")

# # CONTACT_HCAPTCHA_MODE = config("CONTACT_HCAPTCHA_MODE", default="fallback").lower().strip()

# # ==========================
# # Anti-spam contact
# # ==========================
# CONTACT_RATE_LIMIT_WINDOW = config("CONTACT_RATE_LIMIT_WINDOW", cast=int, default=300)
# CONTACT_RATE_LIMIT_MAX = config("CONTACT_RATE_LIMIT_MAX", cast=int, default=3)
# CONTACT_VERIFY_TOKEN_HOURS = config("CONTACT_VERIFY_TOKEN_HOURS", cast=int, default=24)

# CONTACT_NOTIFY_EMAILS = ["contact@sogentis.org"]

# # ✅ UNIFIÉ
# DEFAULT_FROM_EMAIL = config("CONTACT_FROM_EMAIL", default="contact@sogentis.org")

# CONTACT_BLOCKED_EMAIL_DOMAINS = [
#     "mailinator.com",
#     "10minutemail.com",
#     "tempmail.com",
# ]






# # config/settings/modules/security.py

# from decouple import config, Csv

# DEBUG = config("DEBUG", default=False, cast=bool)

# # ==========================
# # HTTPS & cookies
# # ==========================
# SECURE_SSL_REDIRECT = not DEBUG
# SESSION_COOKIE_SECURE = not DEBUG
# CSRF_COOKIE_SECURE = not DEBUG

# SESSION_COOKIE_HTTPONLY = True
# CSRF_COOKIE_HTTPONLY = False  # ✅ IMPORTANT (Django requirement)

# # ==========================
# # Security headers
# # ==========================
# X_FRAME_OPTIONS = "DENY"
# SECURE_CONTENT_TYPE_NOSNIFF = True

# # ==========================
# # Sessions
# # ==========================
# SESSION_EXPIRE_AT_BROWSER_CLOSE = True
# SESSION_COOKIE_AGE = 3600  # 1 heure

# # ==========================
# # Admins
# # ==========================
# ADMINS = [("Admin SOGENTIS", "contact@sogentis.org")]
# MANAGERS = ADMINS

# # ==========================
# # Production-only hardening
# # ==========================
# if not DEBUG:
#     SECURE_HSTS_SECONDS = 31536000  # 1 an
#     SECURE_HSTS_INCLUDE_SUBDOMAINS = True
#     SECURE_HSTS_PRELOAD = True

#     DATA_UPLOAD_MAX_MEMORY_SIZE = 2_621_440  # 2.5 MB
#     FILE_UPLOAD_MAX_MEMORY_SIZE = 2_621_440

#     SERVER_EMAIL = config("SERVER_EMAIL", default="server@sogentis.org")

# # ==========================
# # Auth
# # ==========================
# PASSWORD_RESET_TIMEOUT = 60 * 60 * 48  # 48h

# # ==========================
# # Proxy (si derrière CDN / reverse proxy)
# # ==========================
# SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# # ==========================
# # CSRF
# # ==========================
# CSRF_TRUSTED_ORIGINS = config(
#     "CSRF_TRUSTED_ORIGINS",
#     default="https://sogentis.org,https://www.sogentis.org",
#     cast=Csv(),
# )

# # ==========================
# # Anti-bot
# # ==========================
# TURNSTILE_ENABLED = config("TURNSTILE_ENABLED", cast=bool, default=False)
# TURNSTILE_SITEKEY = config("TURNSTILE_SITEKEY", default="")
# TURNSTILE_SECRETKEY = config("TURNSTILE_SECRETKEY", default="")
# TURNSTILE_TIMEOUT = config("TURNSTILE_TIMEOUT", cast=int, default=5)
# TURNSTILE_SEND_REMOTEIP = config("TURNSTILE_SEND_REMOTEIP", cast=bool, default=False)

# HCAPTCHA_ENABLED = config("HCAPTCHA_ENABLED", cast=bool, default=False)
# HCAPTCHA_SITEKEY = config("HCAPTCHA_SITEKEY", default="")
# HCAPTCHA_SECRETKEY = config("HCAPTCHA_SECRETKEY", default="")
# HCAPTCHA_TIMEOUT = config("HCAPTCHA_TIMEOUT", cast=int, default=5)
# HCAPTCHA_THEME = config("HCAPTCHA_THEME", default="light")

# CONTACT_HCAPTCHA_MODE = config("CONTACT_HCAPTCHA_MODE", default="fallback")

# # ==========================
# # Anti-spam contact
# # ==========================
# CONTACT_RATE_LIMIT_WINDOW = config("CONTACT_RATE_LIMIT_WINDOW", cast=int, default=300)
# CONTACT_RATE_LIMIT_MAX = config("CONTACT_RATE_LIMIT_MAX", cast=int, default=3)
# CONTACT_VERIFY_TOKEN_HOURS = config("CONTACT_VERIFY_TOKEN_HOURS", cast=int, default=24)

# CONTACT_NOTIFY_EMAILS = ["contact@sogentis.org"]

# # ✅ UNIFIÉ
# DEFAULT_FROM_EMAIL = config("CONTACT_FROM_EMAIL", default="contact@sogentis.org")

# CONTACT_BLOCKED_EMAIL_DOMAINS = [
#     "mailinator.com",
#     "10minutemail.com",
#     "tempmail.com",
# ]







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
