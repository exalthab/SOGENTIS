# config/settings/modules/middleware.py

MIDDLEWARE = [
    # Sécurité générale (doit être en début de liste)
    "django.middleware.security.SecurityMiddleware",

    # Sessions utilisateur
    "django.contrib.sessions.middleware.SessionMiddleware",

    # Gestion des langues (DOIT être ici)
    "django.middleware.locale.LocaleMiddleware",

    # ✅ Nouveau: domaines (.com/.org/.sn)
    "common.domain_middleware.DomainSiteMiddleware",

    # Middleware général Django
    "django.middleware.common.CommonMiddleware",

    # Protection CSRF
    "django.middleware.csrf.CsrfViewMiddleware",

    # Authentification (NE PAS déplacer)
    "django.contrib.auth.middleware.AuthenticationMiddleware",

    # Messages Django
    "django.contrib.messages.middleware.MessageMiddleware",

    # Protection contre clickjacking
    "django.middleware.clickjacking.XFrameOptionsMiddleware",

    # === ⚠️ Ton tracking middleware (OK) ===
    "accounts_users.middleware.users_tracking_middleware.UsersTrackingMiddleware",

    # === ✅ Nouveau : interdiction Dashboard si profil pending/refused ===
    "common.middleware.ProfileStatusMiddleware",
    
]

# === Bootstrap Messages Tags ===
from django.contrib.messages import constants as messages

MESSAGE_TAGS = {
    messages.DEBUG: "secondary",
    messages.INFO: "info",
    messages.SUCCESS: "success",
    messages.WARNING: "warning",
    messages.ERROR: "danger",
}





# # config/settings/modules/middleware.py

# MIDDLEWARE = [
#     # Sécurité générale (doit être en début de liste)
#     "django.middleware.security.SecurityMiddleware",

#     # Gestion des sessions utilisateur
#     "django.contrib.sessions.middleware.SessionMiddleware",
    
#     # Ajout du middleware de gestion des langues
#     "django.middleware.locale.LocaleMiddleware",  # <= entre Session et Common

#     # Middleware général pour diverses fonctionnalités
#     "django.middleware.common.CommonMiddleware",

#     # Protection CSRF (Cross-Site Request Forgery)
#     "django.middleware.csrf.CsrfViewMiddleware",

#     # Gestion de l’authentification utilisateur
#     "django.contrib.auth.middleware.AuthenticationMiddleware",

#     # Gestion des messages flash
#     "django.contrib.messages.middleware.MessageMiddleware",

#     # Protection contre le clickjacking via l’en-tête X-Frame-Options
#     "django.middleware.clickjacking.XFrameOptionsMiddleware",

#     # Middleware personnalisé pour le suivi des utilisateurs
#     "accounts_users.middleware.users_tracking_middleware.UsersTrackingMiddleware",
    
# ]

# # === Configuration optionnelle des tags messages pour Bootstrap 5 ===
# from django.contrib.messages import constants as messages

# MESSAGE_TAGS = {
#     messages.DEBUG: "secondary",
#     messages.INFO: "info",
#     messages.SUCCESS: "success",
#     messages.WARNING: "warning",
#     messages.ERROR: "danger",
# }
