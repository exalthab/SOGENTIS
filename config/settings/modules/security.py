from decouple import config

DEBUG = config("DEBUG", default=False, cast=bool)

# Redirections HTTPS
SECURE_SSL_REDIRECT = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

# Cookies HTTPOnly
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# Sécurité de base
X_FRAME_OPTIONS = "DENY"
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Session expire après fermeture du navigateur (empêche "rappel fantôme" de session)
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 3600  # 1h

# Headers HSTS activés uniquement en production
if not DEBUG:
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# Token valide pendant 2 jours (en secondes)
PASSWORD_RESET_TIMEOUT = 60 * 60 * 48  # 48 heures
