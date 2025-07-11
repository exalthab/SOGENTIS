# core/context_processors/global_context.py

from datetime import datetime
from django.conf import settings

# 🔹 Variables globales disponibles dans tous les templates
def global_variables(request):
    return {
        "PROJECT_NAME": getattr(settings, "PROJECT_NAME", "SOGENTIS"),
        "SLOGAN": "Unir le social et l’économique",
        "FOOTER_CITATION": "“Ensemble, faisons la différence.”",
        "CONTACT_EMAIL": getattr(settings, "CONTACT_EMAIL", "contact@sogentis.sn"),
        "CONTACT_PHONE": "+221 123 456 789",
        "LINKEDIN_URL": "https://linkedin.com/company/sogentis",
        "GITHUB_URL": "https://github.com/sogentis",
        "YEAR": datetime.now().year,
    }

# 🔹 Thème utilisateur (dark/light)
def theme_context(request):
    if request.user.is_authenticated:
        try:
            return {"user_theme": request.user.userprofile.theme}
        except AttributeError:
            return {"user_theme": "light"}
    return {"user_theme": "light"}

# 🔹 Menu secondaire dynamique selon la section visitée
def section_menu(request):
    path = request.path

    if path.startswith('/soci'):
        template = 'core/partials/_menu_soci.html'
    elif path.startswith('/econ'):
        template = 'core/partials/_menu_eco.html'
    elif path.startswith('/dashboard'):
        template = 'core/partials/_menu_dashboard.html'
    elif path.startswith('/educ'):
        template = 'core/partials/_menu_educ.html'
    elif path.startswith('/admin') or path.startswith('/accounts_users'):
        template = None
    else:
        template = None

    return {'section_menu_template': template}

# 🔹 Autres variables techniques
def some_other_context(request):
    return {"app_version": getattr(settings, "APP_VERSION", "1.0")}









# from datetime import datetime

# # 🔹 Variables globales disponibles dans tous les templates
# def global_variables(request):
#     return {
#         "PROJECT_NAME": "SOGENTIS",
#         "SLOGAN": "Unir le social et l’économique",
#         "FOOTER_CITATION": "“Ensemble, faisons la différence.”",
#         "CONTACT_EMAIL": "contact@sogen.org",
#         "CONTACT_PHONE": "+221 123 456 789",
#         "LINKEDIN_URL": "https://linkedin.com/company/sogentis",
#         "GITHUB_URL": "https://github.com/sogentis",
#         "YEAR": datetime.now().year,
#     }

# # 🔹 Thème utilisateur (dark/light)
# def theme_context(request):
#     if request.user.is_authenticated:
#         try:
#             return {"user_theme": request.user.userprofile.theme}
#         except AttributeError:
#             return {"user_theme": "light"}
#     return {"user_theme": "light"}

# # 🔹 Menu secondaire dynamique selon la section visitée
# def section_menu(request):
#     path = request.path

#     # Menu selon les préfixes d’URL
#     if path.startswith('/soci'):
#         template = 'core/partials/_menu_soci.html'
#     elif path.startswith('/econ'):
#         template = 'core/partials/_menu_eco.html'
#     elif path.startswith('/dashboard'):
#         template = 'core/partials/_menu_dashboard.html'
#     elif path.startswith('/educ'):
#         template = 'core/partials/_menu_educ.html'
#     elif path.startswith('/admin') or path.startswith('/accounts_users'):
#         template = None
#     else:
#         template = None

#     return {'section_menu_template': template}

# # 🔹 Autres variables techniques
# def some_other_context(request):
#     return {"app_version": "1.0"}
