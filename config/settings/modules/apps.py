# config/settings/modules/apps.py

INSTALLED_APPS = [
    # =====================================================
    # Django core
    # =====================================================
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",

    # =====================================================
    # UI / UX
    # =====================================================
    "dashboard",
    "bootstrap4",
    "widget_tweaks",
    # "captcha",
    "phonenumber_field",


    # =====================================================
    # Core projet
    # =====================================================
    "core",

    # =====================================================
    # Comptes & sécurité
    # =====================================================
    "accounts_users.apps.AccountsUsersConfig",
    "accounts_users.authentication",
    "accounts_users.global_permissions",

    # =====================================================
    # 🔹 PÔLE ÉCONOMIQUE (ARCHITECTURE SAINE)
    # =====================================================
    # Hub (pas de modèles, uniquement urls / views)
    "economic",

    # Apps métier (modèles + migrations)
    "economic.ecommerce",
    "economic.formations",
    "economic.services",
    "economic.b2b",
    "economic.resources",
    "economic.support",
    
    "economic.ecommerce.articles",


    # =====================================================
    # 🔹 PÔLE SOCIAL (DÉJÀ STABLE)
    # =====================================================
    "social",
    "social.aid",

    # =====================================================
    # Stakeholders
    # =====================================================
    "stakeholders",
    "stakeholders.beneficiaries",
    "stakeholders.volunteers",
    "stakeholders.members",
    "stakeholders.friends",

    # =====================================================
    # Autres modules
    # =====================================================
    "documents",
    "search",
    "donations",

    # =====================================================
    # Internationalisation
    # =====================================================
    "parler",

    # =====================================================
    # About
    # =====================================================
    "about.apps.AboutConfig",

    # =====================================================
    # Admin helpers
    # =====================================================
    "adminsortable2",

    # =====================================================
    # Rich text editor
    # =====================================================
    "django_ckeditor_5",
]





# # config/settings/modules/apps.py

# INSTALLED_APPS = [
#     # Django Core
#     "django.contrib.admin",
#     "django.contrib.auth",
#     "django.contrib.contenttypes",
#     "django.contrib.sessions",
#     "django.contrib.messages",
#     "django.contrib.staticfiles",
#     "django.contrib.humanize",

#     # UI / UX
#     "dashboard",
#     "bootstrap4",
#     "widget_tweaks",

#     # Local Apps
#     "core",
#     # "accounts_users",
#     "accounts_users.apps.AccountsUsersConfig",  # PAS juste "accounts_users"
#     "accounts_users.authentication",
#     "accounts_users.global_permissions",
#     "economic",
#     "economic.b2b",
#     "sogentis_apps.economic.ecommerce.apps.EcommerceConfig",
#     "economic.formations",
#     "economic.resources",
#     "economic.services",
#     "economic.support",
#     # "economic.gestion_projets",
#     "social",
#     "social.aid",
#     "stakeholders",
#     "stakeholders.beneficiaries",
#     "stakeholders.volunteers",
#     "stakeholders.members",
#     "stakeholders.friends",
#     "documents",
#     "search",
#     "donations",

#     # Multilingue
#     "parler",

#     # About
#     "about.apps.AboutConfig",

#     "adminsortable2",

#     # CKEditor
#     # "ckeditor",
#     # "ckeditor_uploader",
#     "django_ckeditor_5",



#     # Development only
#     # "sslserver",
# ]
