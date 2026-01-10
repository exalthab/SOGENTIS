# core/context_processors/global_context.py
from django.conf import settings
from django.utils import timezone
from django.templatetags.static import static
from django.template import TemplateDoesNotExist
from django.template.loader import get_template


def global_variables(request):
    return {
        "PROJECT_NAME": getattr(settings, "PROJECT_NAME", "SOGENTIS"),
        "SLOGAN": getattr(settings, "SLOGAN", "Unir le social et l’économique"),
        "FOOTER_CITATION": getattr(settings, "FOOTER_CITATION", "“Ensemble, faisons la différence.”"),
        "CONTACT_EMAIL": getattr(settings, "CONTACT_EMAIL", "contact@sogentis.org"),
        "CONTACT_PHONE": getattr(settings, "CONTACT_PHONE", "+221 123 456 789"),
        "GITHUB_URL": getattr(settings, "GITHUB_URL", "https://github.com/sogentis"),
        "YEAR": timezone.now().year,
    }


def social_links(request):
    social = getattr(settings, "SOCIAL_LINKS", {}) or {}
    return {
        "FACEBOOK_URL": social.get("facebook"),
        "TWITTER_URL": social.get("twitter"),
        "YOUTUBE_URL": social.get("youtube"),
    }


def theme_context(request):
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return {"user_theme": "light"}

    profile = getattr(user, "profile", None) or getattr(user, "userprofile", None)
    theme = getattr(profile, "theme", None) if profile else None
    return {"user_theme": theme or "light"}


def route_flags(request):
    m = getattr(request, "resolver_match", None)
    namespaces = set(getattr(m, "namespaces", []) or [])
    ns = getattr(m, "namespace", None)
    url_name = getattr(m, "url_name", None)

    is_home = bool(url_name == "home" and (ns == "core" or "core" in namespaces))
    return {
        "is_home": is_home,
        "active_namespace": ns,
        "active_url_name": url_name,
    }


def _template_exists(template_name: str) -> bool:
    if not template_name:
        return False
    try:
        get_template(template_name)
        return True
    except TemplateDoesNotExist:
        return False


def _first_existing_template(candidates):
    for t in candidates or []:
        if _template_exists(t):
            return t
    return None


def _first_path_segment_without_lang(request):
    path = (getattr(request, "path_info", None) or getattr(request, "path", "") or "").strip()
    parts = [p for p in path.split("/") if p]
    if not parts:
        return ""

    lang_codes = {code for code, _ in getattr(settings, "LANGUAGES", [])}
    if parts[0] in lang_codes and len(parts) >= 2:
        return parts[1]
    return parts[0]


def section_menu(request):
    m = getattr(request, "resolver_match", None)
    namespaces = set(getattr(m, "namespaces", []) or [])
    ns = getattr(m, "namespace", "") or ""
    first_seg = _first_path_segment_without_lang(request)

    ECONOMIC_MENU_CANDIDATES = ["economic/partials/_economic_menu.html"]
    RESOURCES_MENU_CANDIDATES = ["economic/resources/partials/_menu_resources.html"]

    SOCIAL_MENU_CANDIDATES = ["social/partials/_social_menu.html", "core/partials/_menu_soci.html"]
    DASHBOARD_MENU_CANDIDATES = ["dashboard/partials/_dashboard_menu.html", "core/partials/_menu_dashboard.html"]

    template = None

    # 1) Priorité au resolver_match (fiable)
    if "resources" in namespaces or ns == "resources":
        template = _first_existing_template(RESOURCES_MENU_CANDIDATES)
    elif "economic" in namespaces or ns in {"economic", "ecommerce", "services", "formations", "b2b", "support"}:
        template = _first_existing_template(ECONOMIC_MENU_CANDIDATES)
    elif "social" in namespaces or ns == "social":
        template = _first_existing_template(SOCIAL_MENU_CANDIDATES)
    elif "dashboard" in namespaces or ns == "dashboard":
        template = _first_existing_template(DASHBOARD_MENU_CANDIDATES)

    # 2) Fallback par segment d’URL (si resolver_match absent)
    if not template:
        if first_seg == "resources":
            template = _first_existing_template(RESOURCES_MENU_CANDIDATES)
        elif first_seg in {"economic", "econ", "ecommerce", "services", "formations", "b2b", "support"}:
            template = _first_existing_template(ECONOMIC_MENU_CANDIDATES)
        elif first_seg == "social":
            template = _first_existing_template(SOCIAL_MENU_CANDIDATES)
        elif first_seg == "dashboard":
            template = _first_existing_template(DASHBOARD_MENU_CANDIDATES)
        elif first_seg in {"admin", "accounts"}:
            template = None

    return {"section_menu": template}


def site_domains(request):
    social = getattr(settings, "SOCIAL_BASE_URL", "https://sogentis.org").rstrip("/")
    business = getattr(settings, "COMMERCIAL_BASE_URL", "https://sogentis.com").rstrip("/")
    inst = getattr(settings, "INSTITUTION_BASE_URL", "https://sogentis.sn").rstrip("/")

    return {
        "SOCIAL_DOMAIN": social,
        "BUSINESS_DOMAIN": business,
        "INSTITUTION_DOMAIN": inst,
    }


def some_other_context(request):
    return {"app_version": getattr(settings, "APP_VERSION", "1.0")}


def seo_context(request):
    default_title = getattr(settings, "SEO_TITLE_DEFAULT", f"{getattr(settings, 'PROJECT_NAME', 'SOGENTIS')} – {getattr(settings, 'SLOGAN', '')}".strip(" –"))
    default_desc = getattr(settings, "SEO_DESCRIPTION_DEFAULT", "")
    og_path = getattr(settings, "SEO_OG_IMAGE_DEFAULT_PATH", "global/image/og_default_sogentis.png")
    default_og = static(og_path)

    return {
        "SEO_TITLE_DEFAULT": default_title,
        "SEO_DESCRIPTION_DEFAULT": default_desc,
        "SEO_OG_IMAGE_DEFAULT": default_og,
    }










# # core/context_processors/global_context.py
# from django.conf import settings
# from django.utils import timezone
# from django.templatetags.static import static
# from django.template import TemplateDoesNotExist
# from django.template.loader import get_template


# def global_variables(request):
#     return {
#         "PROJECT_NAME": getattr(settings, "PROJECT_NAME", "SOGENTIS"),
#         "SLOGAN": "Unir le social et l’économique",
#         "FOOTER_CITATION": "“Ensemble, faisons la différence.”",
#         "CONTACT_EMAIL": getattr(settings, "CONTACT_EMAIL", "contact@sogentis.org"),
#         "CONTACT_PHONE": "+221 123 456 789",
#         "GITHUB_URL": "https://github.com/sogentis",
#         "YEAR": timezone.now().year,
#     }


# def social_links(request):
#     social = getattr(settings, "SOCIAL_LINKS", {}) or {}
#     return {
#         "FACEBOOK_URL": social.get("facebook"),
#         "TWITTER_URL": social.get("twitter"),
#         "YOUTUBE_URL": social.get("youtube"),
#     }


# def theme_context(request):
#     if not getattr(request, "user", None) or not request.user.is_authenticated:
#         return {"user_theme": "light"}

#     profile = getattr(request.user, "profile", None) or getattr(request.user, "userprofile", None)
#     theme = getattr(profile, "theme", None) if profile else None
#     return {"user_theme": theme or "light"}


# def route_flags(request):
#     m = getattr(request, "resolver_match", None)
#     is_home = bool(m and m.namespace == "core" and m.url_name == "home")
#     return {
#         "is_home": is_home,
#         "active_namespace": getattr(m, "namespace", None),
#         "active_url_name": getattr(m, "url_name", None),
#     }


# def _template_exists(template_name: str) -> bool:
#     if not template_name:
#         return False
#     try:
#         get_template(template_name)
#         return True
#     except TemplateDoesNotExist:
#         return False


# def _first_existing_template(candidates):
#     for t in candidates:
#         if _template_exists(t):
#             return t
#     return None


# def _first_path_segment_without_lang(request):
#     path = (getattr(request, "path", "") or "").strip()
#     parts = [p for p in path.split("/") if p]
#     if not parts:
#         return ""

#     lang_codes = {code for code, _ in getattr(settings, "LANGUAGES", [])}
#     if parts[0] in lang_codes and len(parts) >= 2:
#         return parts[1]
#     return parts[0]


# def section_menu(request):
#     m = getattr(request, "resolver_match", None)
#     namespaces = set(getattr(m, "namespaces", []) or [])
#     ns = getattr(m, "namespace", "") or ""
#     first_seg = _first_path_segment_without_lang(request)

#     ECONOMIC_MENU_CANDIDATES = ["economic/partials/_economic_menu.html"]
#     RESOURCES_MENU_CANDIDATES = ["economic/resources/partials/_menu_resources.html"]

#     SOCIAL_MENU_CANDIDATES = ["social/partials/_social_menu.html", "core/partials/_menu_soci.html"]
#     DASHBOARD_MENU_CANDIDATES = ["dashboard/partials/_dashboard_menu.html", "core/partials/_menu_dashboard.html"]

#     template = None

#     if "resources" in namespaces or ns == "resources":
#         template = _first_existing_template(RESOURCES_MENU_CANDIDATES)
#     elif "economic" in namespaces or ns in {"economic", "ecommerce", "services", "formations", "b2b", "support"}:
#         template = _first_existing_template(ECONOMIC_MENU_CANDIDATES)
#     elif "social" in namespaces or ns == "social":
#         template = _first_existing_template(SOCIAL_MENU_CANDIDATES)
#     elif "dashboard" in namespaces or ns == "dashboard":
#         template = _first_existing_template(DASHBOARD_MENU_CANDIDATES)

#     if not template:
#         if first_seg in {"resources"}:
#             template = _first_existing_template(RESOURCES_MENU_CANDIDATES)
#         elif first_seg in {"economic", "econ", "ecommerce", "services", "formations", "b2b", "support"}:
#             template = _first_existing_template(ECONOMIC_MENU_CANDIDATES)
#         elif first_seg in {"social"}:
#             template = _first_existing_template(SOCIAL_MENU_CANDIDATES)
#         elif first_seg in {"dashboard"}:
#             template = _first_existing_template(DASHBOARD_MENU_CANDIDATES)
#         elif first_seg in {"admin", "accounts"}:
#             template = None

#     return {"section_menu": template}


# def site_domains(request):
#     social = getattr(settings, "SOCIAL_BASE_URL", getattr(settings, "SOCIAL_DOMAIN", "https://sogentis.org")).rstrip("/")
#     business = getattr(settings, "COMMERCIAL_BASE_URL", getattr(settings, "BUSINESS_DOMAIN", "https://sogentis.com")).rstrip("/")
#     inst = getattr(settings, "INSTITUTION_BASE_URL", getattr(settings, "INSTITUTION_DOMAIN", "https://sogentis.sn")).rstrip("/")

#     return {
#         "SOCIAL_DOMAIN": social,
#         "BUSINESS_DOMAIN": business,
#         "INSTITUTION_DOMAIN": inst,
#     }


# def some_other_context(request):
#     return {"app_version": getattr(settings, "APP_VERSION", "1.0")}


# def seo_context(request):
#     default_title = "SOGENTIS – Unir le social et l’économique"
#     default_desc = (
#         "SOGENTIS est une plateforme sociale et économique dédiée à l'enfance, "
#         "aux mamans, aux communautés et aux projets de développement."
#     )
#     default_og = static("global/image/og_default_sogentis.png")

#     return {
#         "SEO_TITLE_DEFAULT": default_title,
#         "SEO_DESCRIPTION_DEFAULT": default_desc,
#         "SEO_OG_IMAGE_DEFAULT": default_og,
#     }






# # core/context_processors/global_context.py
# from django.conf import settings
# from django.utils import timezone
# from django.templatetags.static import static

# from django.template import TemplateDoesNotExist
# from django.template.loader import get_template


# # ======================================================
# # 🔹 Variables globales disponibles dans tous les templates
# # ======================================================
# def global_variables(request):
#     return {
#         "PROJECT_NAME": getattr(settings, "PROJECT_NAME", "SOGENTIS"),
#         "SLOGAN": "Unir le social et l’économique",
#         "FOOTER_CITATION": "“Ensemble, faisons la différence.”",
#         "CONTACT_EMAIL": getattr(settings, "CONTACT_EMAIL", "contact@sogentis.org"),
#         "CONTACT_PHONE": "+221 123 456 789",
#         "GITHUB_URL": "https://github.com/sogentis",
#         "YEAR": timezone.now().year,
#     }


# def social_links(request):
#     social = getattr(settings, "SOCIAL_LINKS", {}) or {}
#     return {
#         "FACEBOOK_URL": social.get("facebook"),
#         "TWITTER_URL": social.get("twitter"),
#         "YOUTUBE_URL": social.get("youtube"),
#         # "LINKEDIN_URL": social.get("linkedin"),
#     }


# # ======================================================
# # 🔹 Anti-bot / Captcha (hCaptcha)
# # ======================================================
# def antispam_context(request):
#     return {
#         "HCAPTCHA_ENABLED": bool(getattr(settings, "HCAPTCHA_ENABLED", False)),
#         "HCAPTCHA_SITEKEY": getattr(settings, "HCAPTCHA_SITEKEY", ""),
#         "HCAPTCHA_THEME": getattr(settings, "HCAPTCHA_THEME", "light"),
#         "HCAPTCHA_TIMEOUT": getattr(settings, "HCAPTCHA_TIMEOUT", 5),
#         # Ne jamais exposer la secretkey au template
#     }


# # ======================================================
# # 🔹 Thème utilisateur (dark/light)
# # ======================================================
# def theme_context(request):
#     if not getattr(request, "user", None) or not request.user.is_authenticated:
#         return {"user_theme": "light"}

#     profile = getattr(request.user, "profile", None) or getattr(request.user, "userprofile", None)
#     theme = getattr(profile, "theme", None) if profile else None
#     return {"user_theme": theme or "light"}


# # ======================================================
# # 🔹 Indicateurs de route (utile pour base.html : topbar, padding…)
# # ======================================================
# def route_flags(request):
#     m = getattr(request, "resolver_match", None)
#     is_home = bool(m and m.namespace == "core" and m.url_name == "home")
#     return {
#         "is_home": is_home,
#         "active_namespace": getattr(m, "namespace", None),
#         "active_url_name": getattr(m, "url_name", None),
#     }


# # ======================================================
# # Helpers (menus)
# # ======================================================
# def _template_exists(template_name: str) -> bool:
#     if not template_name:
#         return False
#     try:
#         get_template(template_name)
#         return True
#     except TemplateDoesNotExist:
#         return False


# def _first_existing_template(candidates):
#     for t in candidates:
#         if _template_exists(t):
#             return t
#     return None


# def _first_path_segment_without_lang(request):
#     """
#     Ignore un éventuel préfixe langue:
#     /fr/economic/... -> "economic"
#     /en/resources/... -> "resources"
#     """
#     path = (getattr(request, "path", "") or "").strip()
#     parts = [p for p in path.split("/") if p]
#     if not parts:
#         return ""

#     lang_codes = {code for code, _ in getattr(settings, "LANGUAGES", [])}
#     if parts[0] in lang_codes and len(parts) >= 2:
#         return parts[1]
#     return parts[0]


# # ======================================================
# # 🔹 Menu secondaire dynamique selon la section visitée
# # ======================================================
# def section_menu(request):
#     m = getattr(request, "resolver_match", None)
#     namespaces = set(getattr(m, "namespaces", []) or [])
#     ns = getattr(m, "namespace", "") or ""
#     first_seg = _first_path_segment_without_lang(request)

#     ECONOMIC_MENU_CANDIDATES = [
#         "economic/partials/_economic_menu.html",
#     ]
#     RESOURCES_MENU_CANDIDATES = [
#         "economic/resources/partials/_menu_resources.html",
#     ]

#     SOCIAL_MENU_CANDIDATES = [
#         "social/partials/_social_menu.html",
#         "core/partials/_menu_soci.html",
#     ]
#     DASHBOARD_MENU_CANDIDATES = [
#         "dashboard/partials/_dashboard_menu.html",
#         "core/partials/_menu_dashboard.html",
#     ]

#     template = None

#     # 1) Détection par namespaces (fiable i18n)
#     if "resources" in namespaces or ns == "resources":
#         template = _first_existing_template(RESOURCES_MENU_CANDIDATES)

#     elif "economic" in namespaces or ns in {"economic", "ecommerce", "services", "formations", "b2b", "support"}:
#         template = _first_existing_template(ECONOMIC_MENU_CANDIDATES)

#     elif "social" in namespaces or ns == "social":
#         template = _first_existing_template(SOCIAL_MENU_CANDIDATES)

#     elif "dashboard" in namespaces or ns == "dashboard":
#         template = _first_existing_template(DASHBOARD_MENU_CANDIDATES)

#     # 2) Fallback par path (quand resolver_match est absent)
#     if not template:
#         if first_seg in {"resources"}:
#             template = _first_existing_template(RESOURCES_MENU_CANDIDATES)
#         elif first_seg in {"economic", "econ", "ecommerce", "services", "formations", "b2b", "support"}:
#             template = _first_existing_template(ECONOMIC_MENU_CANDIDATES)
#         elif first_seg in {"social"}:
#             template = _first_existing_template(SOCIAL_MENU_CANDIDATES)
#         elif first_seg in {"dashboard"}:
#             template = _first_existing_template(DASHBOARD_MENU_CANDIDATES)
#         elif first_seg in {"admin", "accounts"}:
#             template = None

#     return {"section_menu": template}


# # ======================================================
# # 🔹 Domaines / Base URLs (cohérent avec modules/base.py)
# # ======================================================
# def site_domains(request):
#     social = getattr(settings, "SOCIAL_BASE_URL", getattr(settings, "SOCIAL_DOMAIN", "https://sogentis.org")).rstrip("/")
#     business = getattr(settings, "COMMERCIAL_BASE_URL", getattr(settings, "BUSINESS_DOMAIN", "https://sogentis.com")).rstrip("/")
#     inst = getattr(settings, "INSTITUTION_BASE_URL", getattr(settings, "INSTITUTION_DOMAIN", "https://sogentis.sn")).rstrip("/")

#     return {
#         "SOCIAL_DOMAIN": social,
#         "BUSINESS_DOMAIN": business,
#         "INSTITUTION_DOMAIN": inst,
#     }


# # ======================================================
# # 🔹 Autres variables techniques
# # ======================================================
# def some_other_context(request):
#     return {"app_version": getattr(settings, "APP_VERSION", "1.0")}


# # ======================================================
# # 🔹 Contexte SEO global
# # ======================================================
# def seo_context(request):
#     default_title = "SOGENTIS – Unir le social et l’économique"
#     default_desc = (
#         "SOGENTIS est une plateforme sociale et économique dédiée à l'enfance, "
#         "aux mamans, aux communautés et aux projets de développement."
#     )
#     default_og = static("global/image/og_default_sogentis.png")

#     return {
#         "SEO_TITLE_DEFAULT": default_title,
#         "SEO_DESCRIPTION_DEFAULT": default_desc,
#         "SEO_OG_IMAGE_DEFAULT": default_og,
#     }







# # core/context_processors/global_context.py
# from django.conf import settings
# from django.utils import timezone
# from django.templatetags.static import static

# from django.template import TemplateDoesNotExist
# from django.template.loader import get_template


# # ======================================================
# # 🔹 Variables globales disponibles dans tous les templates
# # ======================================================
# def global_variables(request):
#     return {
#         "PROJECT_NAME": getattr(settings, "PROJECT_NAME", "SOGENTIS"),
#         "SLOGAN": "Unir le social et l’économique",
#         "FOOTER_CITATION": "“Ensemble, faisons la différence.”",
#         "CONTACT_EMAIL": getattr(settings, "CONTACT_EMAIL", "contact@sogentis.sn"),
#         "CONTACT_PHONE": "+221 123 456 789",
#         "GITHUB_URL": "https://github.com/sogentis",
#         "YEAR": timezone.now().year,  # timezone-aware
#     }


# def social_links(request):
#     social = getattr(settings, "SOCIAL_LINKS", {}) or {}
#     return {
#         "FACEBOOK_URL": social.get("facebook"),
#         "TWITTER_URL": social.get("twitter"),
#         "YOUTUBE_URL": social.get("youtube"),
#         # "LINKEDIN_URL": social.get("linkedin"),
#     }


# # ======================================================
# # 🔹 Thème utilisateur (dark/light)
# # ======================================================
# def theme_context(request):
#     if not getattr(request, "user", None) or not request.user.is_authenticated:
#         return {"user_theme": "light"}

#     # Supporte user.profile (recommandé) OU user.userprofile (ancien)
#     profile = getattr(request.user, "profile", None) or getattr(request.user, "userprofile", None)
#     theme = getattr(profile, "theme", None) if profile else None
#     return {"user_theme": theme or "light"}


# # ======================================================
# # 🔹 Indicateurs de route (utile pour base.html : topbar, padding…)
# # ======================================================
# def route_flags(request):
#     m = getattr(request, "resolver_match", None)
#     is_home = bool(m and m.namespace == "core" and m.url_name == "home")
#     return {
#         "is_home": is_home,
#         "active_namespace": getattr(m, "namespace", None),
#         "active_url_name": getattr(m, "url_name", None),
#     }


# # ======================================================
# # Helpers (menus)
# # ======================================================
# def _template_exists(template_name: str) -> bool:
#     if not template_name:
#         return False
#     try:
#         get_template(template_name)
#         return True
#     except TemplateDoesNotExist:
#         return False


# def _first_existing_template(candidates):
#     for t in candidates:
#         if _template_exists(t):
#             return t
#     return None


# def _first_path_segment_without_lang(request):
#     """
#     Ignore un éventuel préfixe langue:
#     /fr/economic/... -> "economic"
#     /en/resources/... -> "resources"
#     """
#     path = (getattr(request, "path", "") or "").strip()
#     parts = [p for p in path.split("/") if p]
#     if not parts:
#         return ""

#     lang_codes = {code for code, _ in getattr(settings, "LANGUAGES", [])}
#     if parts[0] in lang_codes and len(parts) >= 2:
#         return parts[1]
#     return parts[0]


# # ======================================================
# # 🔹 Menu secondaire dynamique selon la section visitée
# # ======================================================
# def section_menu(request):
#     """
#     Retourne le template du menu secondaire dans 'section_menu'
#     (utilisé par main.html: `{% if section_menu %}{% include section_menu %}{% endif %}`)

#     ✅ Corrigé selon tes nouveaux emplacements:
#     - Économique: economic/partials/_economic_menu.html
#     - Resources: economic/resources/partials/_menu_resources.html

#     🔒 Sécurisé: ne renvoie que si le template existe (évite TemplateDoesNotExist en prod)
#     """
#     m = getattr(request, "resolver_match", None)
#     namespaces = set(getattr(m, "namespaces", []) or [])
#     ns = getattr(m, "namespace", "") or ""
#     first_seg = _first_path_segment_without_lang(request)

#     # ✅ NOUVEAUX EMPLACEMENTS (ceux que tu as montrés)
#     ECONOMIC_MENU_CANDIDATES = [
#         "economic/partials/_economic_menu.html",
#     ]
#     RESOURCES_MENU_CANDIDATES = [
#         "economic/resources/partials/_menu_resources.html",
#     ]

#     # Social & Dashboard (on garde fallback legacy si tu l'utilises encore)
#     SOCIAL_MENU_CANDIDATES = [
#         "social/partials/_social_menu.html",
#         "core/partials/_menu_soci.html",
#     ]
#     DASHBOARD_MENU_CANDIDATES = [
#         "dashboard/partials/_dashboard_menu.html",
#         "core/partials/_menu_dashboard.html",
#     ]

#     template = None

#     # 1) Détection par namespaces (fiable i18n)
#     if "resources" in namespaces or ns == "resources":
#         template = _first_existing_template(RESOURCES_MENU_CANDIDATES)

#     elif "economic" in namespaces or ns in {"economic", "ecommerce", "services", "formations", "b2b", "support"}:
#         template = _first_existing_template(ECONOMIC_MENU_CANDIDATES)

#     elif "social" in namespaces or ns == "social":
#         template = _first_existing_template(SOCIAL_MENU_CANDIDATES)

#     elif "dashboard" in namespaces or ns == "dashboard":
#         template = _first_existing_template(DASHBOARD_MENU_CANDIDATES)

#     # 2) Fallback par path (quand resolver_match est absent)
#     if not template:
#         if first_seg in {"resources"}:
#             template = _first_existing_template(RESOURCES_MENU_CANDIDATES)
#         elif first_seg in {"economic", "econ", "ecommerce", "services", "formations", "b2b", "support"}:
#             template = _first_existing_template(ECONOMIC_MENU_CANDIDATES)
#         elif first_seg in {"social"}:
#             template = _first_existing_template(SOCIAL_MENU_CANDIDATES)
#         elif first_seg in {"dashboard"}:
#             template = _first_existing_template(DASHBOARD_MENU_CANDIDATES)
#         elif first_seg in {"admin", "accounts"}:
#             template = None

#     return {"section_menu": template}

# def site_domains(request):
#     return {
#         "SOCIAL_DOMAIN": getattr(settings, "SOCIAL_DOMAIN", "https://sogentis.org").rstrip("/"),
#         "BUSINESS_DOMAIN": getattr(settings, "BUSINESS_DOMAIN", "https://sogentis.com").rstrip("/"),
#         "INSTITUTION_DOMAIN": getattr(settings, "INSTITUTION_DOMAIN", "https://sogentis.sn").rstrip("/"),
#     }
    
# # ======================================================
# # 🔹 Autres variables techniques
# # ======================================================
# def some_other_context(request):
#     return {"app_version": getattr(settings, "APP_VERSION", "1.0")}


# # ======================================================
# # 🔹 Contexte SEO global
# # ======================================================
# def seo_context(request):
#     default_title = "SOGENTIS – Unir le social et l’économique"
#     default_desc = (
#         "SOGENTIS est une plateforme sociale et économique dédiée à l'enfance, "
#         "aux mamans, aux communautés et aux projets de développement."
#     )

#     # Image OG par défaut
#     default_og = static("global/image/og_default_sogentis.png")

#     return {
#         "SEO_TITLE_DEFAULT": default_title,
#         "SEO_DESCRIPTION_DEFAULT": default_desc,
#         "SEO_OG_IMAGE_DEFAULT": default_og,
#     }








# # core/context_processors/global_context.py
# from django.conf import settings
# from django.utils import timezone


# # 🔹 Variables globales disponibles dans tous les templates
# def global_variables(request):
#     return {
#         "PROJECT_NAME": getattr(settings, "PROJECT_NAME", "SOGENTIS"),
#         "SLOGAN": "Unir le social et l’économique",
#         "FOOTER_CITATION": "“Ensemble, faisons la différence.”",
#         "CONTACT_EMAIL": getattr(settings, "CONTACT_EMAIL", "contact@sogentis.sn"),
#         "CONTACT_PHONE": "+221 123 456 789",
#         # "LINKEDIN_URL": "https://linkedin.com/company/sogentis",
#         "GITHUB_URL": "https://github.com/sogentis",
#         "YEAR": timezone.now().year,  # timezone-aware
#     }

# def social_links(request):
#     social = getattr(settings, "SOCIAL_LINKS", {})

#     return {
#         "FACEBOOK_URL": social.get("facebook"),
#         "TWITTER_URL": social.get("twitter"),
#         "YOUTUBE_URL": social.get("youtube"),
#         "LINKEDIN_URL": social.get("linkedin"),
#     }

# # 🔹 Thème utilisateur (dark/light)
# def theme_context(request):
#     if request.user.is_authenticated:
#         try:
#             return {"user_theme": request.user.userprofile.theme}
#         except AttributeError:
#             return {"user_theme": "light"}
#     return {"user_theme": "light"}


# # 🔹 Indicateurs de route (utile pour base.html : topbar, padding…)
# def route_flags(request):
#     m = getattr(request, "resolver_match", None)
#     is_home = bool(m and m.namespace == "core" and m.url_name == "home")
#     return {
#         "is_home": is_home,
#         "active_namespace": getattr(m, "namespace", None),
#         "active_url_name": getattr(m, "url_name", None),
#     }


# # 🔹 Menu secondaire dynamique selon la section visitée
# def section_menu(request):
#     """
#     Retourne le template du menu secondaire dans la variable 'section_menu'
#     (utilisée par les templates : `{% if section_menu %}{% include section_menu %}{% endif %}`).
#     Détection basée d'abord sur le namespace (fiable avec i18n), puis fallback sur le path.
#     """
#     m = getattr(request, "resolver_match", None)
#     ns = getattr(m, "namespace", "") or ""
#     path = request.path or ""

#     template = None

#     # Mappage par namespace (recommandé)
#     if ns == "social":
#         template = "core/partials/_menu_soci.html"
#     elif ns in {"econ", "ecommerce", "services"}:
#         template = "core/partials/_menu_eco.html"
#     elif ns in {"educ", "formations"}:
#         template = "core/partials/_menu_educ.html"
#     elif ns == "dashboard":
#         template = "core/partials/_menu_dashboard.html"
#     else:
#         # Fallback par path (si pas de resolver_match, ou namespaces non définis)
#         if path.startswith("/social"):
#             template = "core/partials/_menu_soci.html"
#         elif path.startswith("/econ") or path.startswith("/ecommerce") or path.startswith("/services"):
#             template = "core/partials/_menu_eco.html"
#         elif path.startswith("/formations") or path.startswith("/educ"):
#             template = "core/partials/_menu_educ.html"
#         elif path.startswith("/dashboard"):
#             template = "core/partials/_menu_dashboard.html"
#         elif path.startswith("/admin") or path.startswith("/accounts"):
#             template = None  # pas de menu pour admin/comptes

#     return {"section_menu": template}



# # 🔹 Autres variables techniques
# def some_other_context(request):
#     return {"app_version": getattr(settings, "APP_VERSION", "1.0")}


# # 🔹 Contexte SEO global
# from django.templatetags.static import static

# def seo_context(request):
#     """
#     Variables SEO de base pour tout le site :
#     - SEO_TITLE: titre par défaut si non fourni dans un template
#     - SEO_DESCRIPTION: description par défaut
#     - SEO_OG_IMAGE: image OpenGraph par défaut
#     """
#     default_title = "SOGENTIS – Unir le social et l’économique"
#     default_desc = (
#         "SOGENTIS est une plateforme sociale et économique dédiée à l'enfance, "
#         "aux mamans, aux communautés et aux projets de développement."
#     )

#     # Image OG par défaut
#     default_og = static("global/image/og_default_sogentis.png")

#     return {
#         "SEO_TITLE_DEFAULT": default_title,
#         "SEO_DESCRIPTION_DEFAULT": default_desc,
#         "SEO_OG_IMAGE_DEFAULT": default_og,
#     }