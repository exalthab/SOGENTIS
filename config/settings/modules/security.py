# config/settings/modules/security.py

from decouple import config

DEBUG = config("DEBUG", default=False, cast=bool)

# === HTTPS and secure cookies ===
SECURE_SSL_REDIRECT = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

# === HTTPOnly cookies for security ===
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# === Clickjacking protection ===
X_FRAME_OPTIONS = "DENY"

# === XSS and content type sniffing protection ===
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# === Session settings ===
# Expire session à la fermeture du navigateur (utile pour plus de sécurité)
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Durée de vie du cookie de session en secondes (1 heure)
SESSION_COOKIE_AGE = 3600

# === HTTP Strict Transport Security (HSTS) ===
# Actif uniquement en production

# === Define ADMINS ===

ADMINS = [("Admin SOGENTIS", "contact@sogentis.org")]

# === SECURITY HEADERS (production only) ===
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000 # 1 an
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    DATA_UPLOAD_MAX_MEMORY_SIZE = 2621440
    FILE_UPLOAD_MAX_MEMORY_SIZE = 2621440
    MANAGERS = ADMINS
    SERVER_EMAIL = config("SERVER_EMAIL", default="server@sogentis.org")


# === Durée de validité du token de réinitialisation de mot de passe ===
PASSWORD_RESET_TIMEOUT = 60 * 60 * 48  # 48 heures
