# config/settings/modules/apps.py

INSTALLED_APPS = [
    # Django Core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",

    # UI / UX
    "dashboard",
    "bootstrap4",
    "widget_tweaks",

    # Local Apps
    "core",
    "accounts_users",
    "accounts_users.authentication",
    "accounts_users.global_permissions",
    "economic",
    "economic.ecommerce",
    "economic.formations",
    "economic.gestion_projets",
    "social",
    "social.aid",
    "stakeholders",
    "stakeholders.beneficiaries",
    "stakeholders.volunteers",
    "stakeholders.members",
    "stakeholders.friends",
    "documents",
    "search",
    "donations",

    # Multilingue
    "parler",

    # About
    "about.apps.AboutConfig",

    "adminsortable2",

    # CKEditor
    # "ckeditor",
    # "ckeditor_uploader",
    "django_ckeditor_5",



    # Development only
    # "sslserver",
]
