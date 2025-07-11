# settings/components/middleware.py

MIDDLEWARE = [
    # Sécurité de Django
    "django.middleware.security.SecurityMiddleware",
    # Sessions
    "django.contrib.sessions.middleware.SessionMiddleware",
    # Middleware généraux
    "django.middleware.common.CommonMiddleware",
    # Protection CSRF
    "django.middleware.csrf.CsrfViewMiddleware",
    # Authentification utilisateur
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    # Messages
    "django.contrib.messages.middleware.MessageMiddleware",
    # Protection contre le clickjacking
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "accounts_users.middleware.users_tracking_middleware.UsersTrackingMiddleware",

]

# MESSAGE TAGS (optionnel, pour Bootstrap 5)
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.DEBUG: 'secondary',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}