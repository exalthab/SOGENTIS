# config/settings/modules/middleware.py

# ==========================================================
# Django middleware stack
# Order is IMPORTANT – do not reorder blindly
# ==========================================================
MIDDLEWARE = [

    # ------------------------------------------------------
    # Security (MUST be first)
    # ------------------------------------------------------
    "django.middleware.security.SecurityMiddleware",

    # ------------------------------------------------------
    # Early custom middlewares (before sessions)
    # ------------------------------------------------------

    # Cross-domain redirections (GET / HEAD only)
    "common.middlewares.cross_domain_redirect.CrossDomainRedirectMiddleware",

    # Detect active site (social / business / institution) from host
    "common.middlewares.domain_middleware.DomainSiteMiddleware",

    # ------------------------------------------------------
    # Sessions & internationalization
    # ------------------------------------------------------
    "django.contrib.sessions.middleware.SessionMiddleware",

    # Language detection (requires sessions)
    "django.middleware.locale.LocaleMiddleware",

    # ------------------------------------------------------
    # Common HTTP behavior
    # ------------------------------------------------------
    "django.middleware.common.CommonMiddleware",

    # ------------------------------------------------------
    # CSRF protection
    # ------------------------------------------------------
    "django.middleware.csrf.CsrfViewMiddleware",

    # ------------------------------------------------------
    # Authentication & messages
    # ------------------------------------------------------
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",

    # ------------------------------------------------------
    # Security headers
    # ------------------------------------------------------
    "django.middleware.clickjacking.XFrameOptionsMiddleware",

    # ------------------------------------------------------
    # Application-level middlewares
    # ------------------------------------------------------

    # User activity tracking
    "accounts_users.middleware.users_tracking_middleware.UsersTrackingMiddleware",

    # Profile status enforcement (AFTER auth + messages)
    "common.middlewares.middlewares.ProfileStatusMiddleware",
]

# ==========================================================
# Django messages → Bootstrap mapping
# ==========================================================
from django.contrib.messages import constants as messages

MESSAGE_TAGS = {
    messages.DEBUG: "secondary",
    messages.INFO: "info",
    messages.SUCCESS: "success",
    messages.WARNING: "warning",
    messages.ERROR: "danger",
}






# # config/settings/modules/middleware.py 10/01/2026

# MIDDLEWARE = [
#     # Sécurité générale (doit rester en premier)
#     "django.middleware.security.SecurityMiddleware",

#     # ✅ Redirections cross-domain (GET/HEAD seulement – voir fichier corrigé)
#     "common.middlewares.cross_domain_redirect.CrossDomainRedirectMiddleware",

#     # ✅ Détecte le type de site (social/business/institution) via host
#     "common.middlewares.domain_middleware.DomainSiteMiddleware",

#     # Sessions
#     "django.contrib.sessions.middleware.SessionMiddleware",

#     # Langues
#     "django.middleware.locale.LocaleMiddleware",

#     # Common
#     "django.middleware.common.CommonMiddleware",

#     # CSRF
#     "django.middleware.csrf.CsrfViewMiddleware",

#     # Auth
#     "django.contrib.auth.middleware.AuthenticationMiddleware",

#     # Messages
#     "django.contrib.messages.middleware.MessageMiddleware",

#     # Clickjacking
#     "django.middleware.clickjacking.XFrameOptionsMiddleware",

#     # Tracking
#     "accounts_users.middleware.users_tracking_middleware.UsersTrackingMiddleware",

#     # ✅ Profil pending/refused (DOIT être après Auth + Messages)
#     "common.middlewares.middlewares.ProfileStatusMiddleware",
# ]

# from django.contrib.messages import constants as messages

# MESSAGE_TAGS = {
#     messages.DEBUG: "secondary",
#     messages.INFO: "info",
#     messages.SUCCESS: "success",
#     messages.WARNING: "warning",
#     messages.ERROR: "danger",
# }






# # config/settings/modules/middleware.py 09/01/2026

# MIDDLEWARE = [
#     # Sécurité générale
#     "django.middleware.security.SecurityMiddleware",

#     # ✅ Cross-domain (FORCE economic sur .com etc.)
#     "common.middlewares.cross_domain_redirect.CrossDomainRedirectMiddleware",

#     # ✅ Router multi-domain (URLConf par host)
#     # "config.middlewares.domain_router.DomainRouterMiddleware",

#     # Sessions
#     "django.contrib.sessions.middleware.SessionMiddleware",

#     # Langues
#     "django.middleware.locale.LocaleMiddleware",

#     # Common
#     "django.middleware.common.CommonMiddleware",

#     # CSRF
#     "django.middleware.csrf.CsrfViewMiddleware",

#     # Auth
#     "django.contrib.auth.middleware.AuthenticationMiddleware",

#     # Messages
#     "django.contrib.messages.middleware.MessageMiddleware",

#     # Clickjacking
#     "django.middleware.clickjacking.XFrameOptionsMiddleware",

#     # Tracking
#     "accounts_users.middleware.users_tracking_middleware.UsersTrackingMiddleware",

#     # ✅ Profil pending/refused
#     "common.middlewares.middlewares.ProfileStatusMiddleware",
# ]

# from django.contrib.messages import constants as messages

# MESSAGE_TAGS = {
#     messages.DEBUG: "secondary",
#     messages.INFO: "info",
#     messages.SUCCESS: "success",
#     messages.WARNING: "warning",
#     messages.ERROR: "danger",
# }





# # config/settings/modules/middleware.py

# MIDDLEWARE = [
#     # Sécurité générale (doit être en début de liste)
#     "django.middleware.security.SecurityMiddleware",
#     "common.middlewares.cross_domain_redirect.CrossDomainRedirectMiddleware",
#     "common.middlewares.domain_router.DomainRouterMiddleware",

#     # Sessions utilisateur
#     "django.contrib.sessions.middleware.SessionMiddleware",

#     # Gestion des langues (DOIT être ici)
#     "django.middleware.locale.LocaleMiddleware",

#     # ✅ Nouveau: domaines (.com/.org/.sn)
#     "common.middlewates.domain_middleware.DomainSiteMiddleware",

#     # Middleware général Django
#     "django.middleware.common.CommonMiddleware",

#     # Protection CSRF
#     "django.middleware.csrf.CsrfViewMiddleware",

#     # Authentification (NE PAS déplacer)
#     "django.contrib.auth.middleware.AuthenticationMiddleware",

#     # Messages Django
#     "django.contrib.messages.middleware.MessageMiddleware",

#     # Protection contre clickjacking
#     "django.middleware.clickjacking.XFrameOptionsMiddleware",

#     # === ⚠️ Ton tracking middleware (OK) ===
#     "accounts_users.middleware.users_tracking_middleware.UsersTrackingMiddleware",

#     # === ✅ Nouveau : interdiction Dashboard si profil pending/refused ===
#     "common.middlewares.middlewares.ProfileStatusMiddleware",
    
# ]

# # === Bootstrap Messages Tags ===
# from django.contrib.messages import constants as messages

# MESSAGE_TAGS = {
#     messages.DEBUG: "secondary",
#     messages.INFO: "info",
#     messages.SUCCESS: "success",
#     messages.WARNING: "warning",
#     messages.ERROR: "danger",
# }





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
