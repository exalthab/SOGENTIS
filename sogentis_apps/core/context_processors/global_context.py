# core/context_processors/global_context.py
from django.conf import settings
from django.utils import timezone


# 🔹 Variables globales disponibles dans tous les templates
def global_variables(request):
    return {
        "PROJECT_NAME": getattr(settings, "PROJECT_NAME", "SOGENTIS"),
        "SLOGAN": "Unir le social et l’économique",
        "FOOTER_CITATION": "“Ensemble, faisons la différence.”",
        "CONTACT_EMAIL": getattr(settings, "CONTACT_EMAIL", "contact@sogentis.sn"),
        "CONTACT_PHONE": "+221 123 456 789",
        # "LINKEDIN_URL": "https://linkedin.com/company/sogentis",
        "GITHUB_URL": "https://github.com/sogentis",
        "YEAR": timezone.now().year,  # timezone-aware
    }

def social_links(request):
    social = getattr(settings, "SOCIAL_LINKS", {})

    return {
        "FACEBOOK_URL": social.get("facebook"),
        "TWITTER_URL": social.get("twitter"),
        "YOUTUBE_URL": social.get("youtube"),
        "LINKEDIN_URL": social.get("linkedin"),
    }

# 🔹 Thème utilisateur (dark/light)
def theme_context(request):
    if request.user.is_authenticated:
        try:
            return {"user_theme": request.user.userprofile.theme}
        except AttributeError:
            return {"user_theme": "light"}
    return {"user_theme": "light"}


# 🔹 Indicateurs de route (utile pour base.html : topbar, padding…)
def route_flags(request):
    m = getattr(request, "resolver_match", None)
    is_home = bool(m and m.namespace == "core" and m.url_name == "home")
    return {
        "is_home": is_home,
        "active_namespace": getattr(m, "namespace", None),
        "active_url_name": getattr(m, "url_name", None),
    }


# 🔹 Menu secondaire dynamique selon la section visitée
def section_menu(request):
    """
    Retourne le template du menu secondaire dans la variable 'section_menu'
    (utilisée par les templates : `{% if section_menu %}{% include section_menu %}{% endif %}`).
    Détection basée d'abord sur le namespace (fiable avec i18n), puis fallback sur le path.
    """
    m = getattr(request, "resolver_match", None)
    ns = getattr(m, "namespace", "") or ""
    path = request.path or ""

    template = None

    # Mappage par namespace (recommandé)
    if ns == "social":
        template = "core/partials/_menu_soci.html"
    elif ns in {"econ", "ecommerce", "services"}:
        template = "core/partials/_menu_eco.html"
    elif ns in {"educ", "formations"}:
        template = "core/partials/_menu_educ.html"
    elif ns == "dashboard":
        template = "core/partials/_menu_dashboard.html"
    else:
        # Fallback par path (si pas de resolver_match, ou namespaces non définis)
        if path.startswith("/social"):
            template = "core/partials/_menu_soci.html"
        elif path.startswith("/econ") or path.startswith("/ecommerce") or path.startswith("/services"):
            template = "core/partials/_menu_eco.html"
        elif path.startswith("/formations") or path.startswith("/educ"):
            template = "core/partials/_menu_educ.html"
        elif path.startswith("/dashboard"):
            template = "core/partials/_menu_dashboard.html"
        elif path.startswith("/admin") or path.startswith("/accounts"):
            template = None  # pas de menu pour admin/comptes

    return {"section_menu": template}


# 🔹 Autres variables techniques
def some_other_context(request):
    return {"app_version": getattr(settings, "APP_VERSION", "1.0")}


# 🔹 Contexte SEO global
from django.templatetags.static import static

def seo_context(request):
    """
    Variables SEO de base pour tout le site :
    - SEO_TITLE: titre par défaut si non fourni dans un template
    - SEO_DESCRIPTION: description par défaut
    - SEO_OG_IMAGE: image OpenGraph par défaut
    """
    default_title = "SOGENTIS – Unir le social et l’économique"
    default_desc = (
        "SOGENTIS est une plateforme sociale et économique dédiée à l'enfance, "
        "aux mamans, aux communautés et aux projets de développement."
    )

    # Image OG par défaut
    default_og = static("global/image/og_default_sogentis.png")

    return {
        "SEO_TITLE_DEFAULT": default_title,
        "SEO_DESCRIPTION_DEFAULT": default_desc,
        "SEO_OG_IMAGE_DEFAULT": default_og,
    }