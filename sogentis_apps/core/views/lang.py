# core/views/lang.py
from django.conf import settings
from django.http import HttpRequest, HttpResponseRedirect
from django.urls import translate_url, resolve, Resolver404, reverse
from django.utils import translation
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import get_supported_language_variant
from urllib.parse import urlsplit

from django.views.decorators.http import require_GET

# Clé session selon version Django
SESSION_LANG_KEY = getattr(translation, "LANGUAGE_SESSION_KEY", "django_language")

# ============================== #
#  CURRENCIES E-COMMERCE         #
# ============================== #
ALLOWED_CURRENCIES = set(getattr(settings, "ECOMMERCE_CURRENCIES", ["XOF", "EUR", "USD"]))
DEFAULT_CURRENCY = getattr(settings, "ECOMMERCE_CURRENCY", "XOF")


def _normalize_lang(raw: str) -> str:
    """Normalise le code langue (en-us → en, zh-hans ok) et valide contre LANGUAGES."""
    try:
        lang = get_supported_language_variant(raw, strict=False)
    except LookupError:
        lang = settings.LANGUAGE_CODE

    allowed = {c for c, _ in getattr(settings, "LANGUAGES", [])}
    return lang if (not allowed or lang in allowed) else settings.LANGUAGE_CODE


def _safe_next(request: HttpRequest, default: str = "/") -> str:
    """Récupère une URL next sûre (next, referer, ou défaut)."""
    nxt = request.GET.get("next") or request.META.get("HTTP_REFERER") or default
    if url_has_allowed_host_and_scheme(
        nxt,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return nxt
    return default


def _activate_and_store(request: HttpRequest, lang: str) -> None:
    """Active la langue et la mémorise en session."""
    translation.activate(lang)
    request.LANGUAGE_CODE = lang
    request.session[SESSION_LANG_KEY] = lang
    request.session.modified = True


def _resolvable(path: str) -> bool:
    """Vérifie si une path est résoluble par l'URLconf courant."""
    try:
        resolve(path)
        return True
    except Resolver404:
        return False


def _lang_home(lang: str) -> str:
    """Accueil dans la langue demandée (gère i18n_patterns)."""
    current = translation.get_language()
    try:
        translation.activate(lang)
        return reverse("core:home")
    finally:
        translation.activate(current)


def _path_of(url: str) -> str:
    return urlsplit(url).path or "/"


def _set_cookie(resp: HttpResponseRedirect, lang: str) -> None:
    resp.set_cookie(
        settings.LANGUAGE_COOKIE_NAME,
        lang,
        max_age=getattr(settings, "LANGUAGE_COOKIE_AGE", None),
        path="/",
        secure=getattr(settings, "LANGUAGE_COOKIE_SECURE", False),
        samesite=getattr(settings, "LANGUAGE_COOKIE_SAMESITE", "Lax"),
    )


# ============================== #
#  CURRENCY / COUNTRY            #
# ============================== #
def _store_currency_and_country(request: HttpRequest) -> None:
    """
    Lit currency / country depuis la querystring du sélecteur e-commerce
    et les stocke en session.
    IMPORTANT:
    - currency -> request.session["ECOMMERCE_CURRENCY"]
    - country  -> request.session["country_code"] (compat money tag ecommerce)
              + request.session["ECOMMERCE_COUNTRY"] (optionnel / futur)
    """
    # --- currency ---
    raw_currency = (request.GET.get("currency") or "").strip().upper()
    if raw_currency and raw_currency in ALLOWED_CURRENCIES:
        currency = raw_currency
    else:
        currency = request.session.get("ECOMMERCE_CURRENCY") or DEFAULT_CURRENCY

    request.session["ECOMMERCE_CURRENCY"] = currency

    # --- country ---
    raw_country = (request.GET.get("country") or "").strip().upper()
    if raw_country:
        # compat: ton money.py ecommerce lit "country_code"
        request.session["country_code"] = raw_country
        # optionnel: si tu veux un nom explicite aussi
        request.session["ECOMMERCE_COUNTRY"] = raw_country

    request.session.modified = True


def _switch_to(request: HttpRequest, lang: str, fallback_to_home: bool = True) -> HttpResponseRedirect:
    """
    Traduit l'URL courante vers `lang`.
    Si la route n'existe pas dans cette langue -> fallback vers home(lang).
    """
    current_url = _safe_next(request, "/")
    target = translate_url(current_url, lang)
    path = _path_of(target)

    if fallback_to_home and (not _resolvable(path) or path == "/"):
        target = _lang_home(lang)

    _activate_and_store(request, lang)
    resp = HttpResponseRedirect(target)
    _set_cookie(resp, lang)
    return resp


# ============================== #
#  PUBLIC VIEWS                  #
# ============================== #
@require_GET
def switch_language(request: HttpRequest) -> HttpResponseRedirect:
    """
    - Bascule la langue + réécrit l'URL
    - Stocke aussi la devise/pays (panneau economic/ecommerce).
    """
    lang = _normalize_lang(request.GET.get("language") or settings.LANGUAGE_CODE)
    _store_currency_and_country(request)
    return _switch_to(request, lang, fallback_to_home=True)


@require_GET
def force_language(request: HttpRequest) -> HttpResponseRedirect:
    """
    Debug: pose la langue (session/cookie) SANS réécrire l'URL.
    Stocke aussi la devise/pays.
    """
    lang = _normalize_lang(request.GET.get("language") or settings.LANGUAGE_CODE)
    _store_currency_and_country(request)

    next_url = _safe_next(request, "/")
    _activate_and_store(request, lang)

    resp = HttpResponseRedirect(next_url)
    _set_cookie(resp, lang)
    return resp







# # core/views/lang.py
# from django.conf import settings
# from django.http import HttpRequest, HttpResponseRedirect
# from django.urls import translate_url, resolve, Resolver404, reverse
# from django.utils import translation
# from django.utils.http import url_has_allowed_host_and_scheme
# from django.utils.translation import get_supported_language_variant
# from urllib.parse import urlsplit

# from django.views.decorators.http import require_GET

# # Clé session selon version Django
# SESSION_LANG_KEY = getattr(translation, "LANGUAGE_SESSION_KEY", "django_language")

# # ============================== #
# #  CURRENCIES E-COMMERCE         #
# # ============================== #
# ALLOWED_CURRENCIES = set(
#     getattr(settings, "ECOMMERCE_CURRENCIES", ["XOF", "EUR", "USD"])
# )
# DEFAULT_CURRENCY = getattr(settings, "ECOMMERCE_CURRENCY", "XOF")


# def _normalize_lang(raw: str) -> str:
#     """Normalise le code langue (en-us → en, zh-hans ok) et valide contre LANGUAGES."""
#     try:
#         lang = get_supported_language_variant(raw, strict=False)
#     except LookupError:
#         lang = settings.LANGUAGE_CODE
#     allowed = {c for c, _ in getattr(settings, "LANGUAGES", [])}
#     return lang if not allowed or lang in allowed else settings.LANGUAGE_CODE


# def _safe_next(request: HttpRequest, default: str = "/") -> str:
#     """Récupère une URL next sûre (next, referer, ou défaut)."""
#     nxt = request.GET.get("next") or request.META.get("HTTP_REFERER") or default
#     if url_has_allowed_host_and_scheme(
#         nxt,
#         allowed_hosts={request.get_host()},
#         require_https=request.is_secure(),
#     ):
#         return nxt
#     return default


# def _activate_and_store(request: HttpRequest, lang: str) -> None:
#     """Active la langue et la mémorise en session."""
#     translation.activate(lang)
#     request.LANGUAGE_CODE = lang
#     request.session[SESSION_LANG_KEY] = lang
#     request.session.modified = True


# def _resolvable(path: str) -> bool:
#     """Vérifie si une path est résoluble par l'URLconf courant."""
#     try:
#         resolve(path)
#         return True
#     except Resolver404:
#         return False


# def _lang_home(lang: str) -> str:
#     """
#     Renvoie l'URL d'accueil dans la langue demandée (via reverse dans un contexte activé).
#     Gère automatiquement le préfixe (/wo/, /es/, etc.) selon i18n_patterns.
#     """
#     current = translation.get_language()
#     try:
#         translation.activate(lang)
#         return reverse("core:home")
#     finally:
#         translation.activate(current)


# def _path_of(url: str) -> str:
#     return urlsplit(url).path or "/"


# def _set_cookie(resp: HttpResponseRedirect, lang: str) -> None:
#     resp.set_cookie(
#         settings.LANGUAGE_COOKIE_NAME,
#         lang,
#         max_age=getattr(settings, "LANGUAGE_COOKIE_AGE", None),
#         path="/",
#         secure=getattr(settings, "LANGUAGE_COOKIE_SECURE", False),
#         samesite=getattr(settings, "LANGUAGE_COOKIE_SAMESITE", "Lax"),
#     )


# # ============================== #
# #  CURRENCY / COUNTRY            #
# # ============================== #
# def _store_currency_and_country(request: HttpRequest) -> None:
#     """
#     Lit currency / country depuis la querystring du sélecteur e-commerce
#     et les stocke dans la session pour tout le site.
#     """
#     currency = request.GET.get("currency")
#     if not currency or currency not in ALLOWED_CURRENCIES:
#         # fallback sur ce qu'il y a déjà en session, sinon valeur par défaut
#         currency = request.session.get("ECOMMERCE_CURRENCY", DEFAULT_CURRENCY)

#     request.session["ECOMMERCE_CURRENCY"] = currency

#     country = request.GET.get("country")
#     if country:
#         request.session["ECOMMERCE_COUNTRY"] = country

#     request.session.modified = True


# def _switch_to(
#     request: HttpRequest, lang: str, fallback_to_home: bool = True
# ) -> HttpResponseRedirect:
#     """
#     Logique commune: traduit l'URL courante vers `lang`. Si la route n'existe pas
#     dans cette langue (ex: page comptes/admin hors i18n_patterns), on retombe
#     proprement sur l'accueil de la langue.
#     """
#     current_url = _safe_next(request, "/")
#     # traduit l'URL (ajoute /xx/ si nécessaire)
#     target = translate_url(current_url, lang)
#     path = _path_of(target)

#     # Si la route traduite n'existe pas → fallback vers home(lang)
#     if fallback_to_home and (not _resolvable(path) or path == "/"):
#         target = _lang_home(lang)

#     _activate_and_store(request, lang)
#     resp = HttpResponseRedirect(target)
#     _set_cookie(resp, lang)
#     return resp


# # ============================== #
# #  PUBLIC VIEWS                  #
# # ============================== #
# @require_GET
# def switch_language(request: HttpRequest) -> HttpResponseRedirect:
#     """
#     Vue recommandée: bascule la langue ET réécrit l'URL.
#     - Utilisée aussi par le panneau e-commerce pour stocker la devise.
#     Utiliser avec un <form method="get" action="{% url 'switch_language' %}">.
#     """
#     lang = _normalize_lang(request.GET.get("language") or settings.LANGUAGE_CODE)
#     _store_currency_and_country(request)
#     return _switch_to(request, lang, fallback_to_home=True)


# @require_GET
# def force_language(request: HttpRequest) -> HttpResponseRedirect:
#     """
#     Variante debug: pose la langue (session/cookie) SANS réécrire l'URL.
#     Utile si tu veux juste vérifier /debug/lang/.
#     """
#     lang = _normalize_lang(request.GET.get("language") or settings.LANGUAGE_CODE)
#     _store_currency_and_country(request)
#     next_url = _safe_next(request, "/")
#     _activate_and_store(request, lang)
#     resp = HttpResponseRedirect(next_url)
#     _set_cookie(resp, lang)
#     return resp




# # core/views/lang.py
# from django.conf import settings
# from django.http import HttpRequest, HttpResponseRedirect
# from django.urls import translate_url, resolve, Resolver404, reverse
# from django.utils import translation
# from django.utils.http import url_has_allowed_host_and_scheme
# from django.utils.translation import get_supported_language_variant
# from urllib.parse import urlsplit

# # Clé session selon version Django
# SESSION_LANG_KEY = getattr(translation, "LANGUAGE_SESSION_KEY", "django_language")


# def _normalize_lang(raw: str) -> str:
#     """Normalise le code langue (en-us → en, zh-hans ok) et valide contre LANGUAGES."""
#     try:
#         lang = get_supported_language_variant(raw, strict=False)
#     except LookupError:
#         lang = settings.LANGUAGE_CODE
#     allowed = {c for c, _ in getattr(settings, "LANGUAGES", [])}
#     return lang if not allowed or lang in allowed else settings.LANGUAGE_CODE


# def _safe_next(request: HttpRequest, default: str = "/") -> str:
#     """Récupère une URL next sûre (next, referer, ou défaut)."""
#     nxt = request.GET.get("next") or request.META.get("HTTP_REFERER") or default
#     if url_has_allowed_host_and_scheme(nxt, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
#         return nxt
#     return default


# def _activate_and_store(request: HttpRequest, lang: str) -> None:
#     """Active la langue et la mémorise en session."""
#     translation.activate(lang)
#     request.LANGUAGE_CODE = lang
#     request.session[SESSION_LANG_KEY] = lang
#     request.session.modified = True


# def _resolvable(path: str) -> bool:
#     """Vérifie si une path est résoluble par l'URLconf courant."""
#     try:
#         resolve(path)
#         return True
#     except Resolver404:
#         return False


# def _lang_home(lang: str) -> str:
#     """
#     Renvoie l'URL d'accueil dans la langue demandée (via reverse dans un contexte activé).
#     Gère automatiquement le préfixe (/wo/, /es/, etc.) selon i18n_patterns.
#     """
#     current = translation.get_language()
#     try:
#         translation.activate(lang)
#         return reverse("core:home")
#     finally:
#         translation.activate(current)


# def _path_of(url: str) -> str:
#     return urlsplit(url).path or "/"


# def _set_cookie(resp: HttpResponseRedirect, lang: str) -> None:
#     resp.set_cookie(
#         settings.LANGUAGE_COOKIE_NAME,
#         lang,
#         max_age=getattr(settings, "LANGUAGE_COOKIE_AGE", None),
#         path="/",
#         secure=getattr(settings, "LANGUAGE_COOKIE_SECURE", False),
#         samesite=getattr(settings, "LANGUAGE_COOKIE_SAMESITE", "Lax"),
#     )


# def _switch_to(request: HttpRequest, lang: str, fallback_to_home: bool = True) -> HttpResponseRedirect:
#     """
#     Logique commune: traduit l'URL courante vers `lang`. Si la route n'existe pas
#     dans cette langue (ex: page comptes/admin hors i18n_patterns), on retombe
#     proprement sur l'accueil de la langue.
#     """
#     current_url = _safe_next(request, "/")
#     # traduit l'URL (ajoute /xx/ si nécessaire)
#     target = translate_url(current_url, lang)
#     path = _path_of(target)

#     # Si la route traduite n'existe pas → fallback vers home(lang)
#     if fallback_to_home and (not _resolvable(path) or path == "/"):
#         target = _lang_home(lang)

#     _activate_and_store(request, lang)
#     resp = HttpResponseRedirect(target)
#     _set_cookie(resp, lang)
#     return resp


# from django.views.decorators.http import require_GET

# @require_GET
# def switch_language(request: HttpRequest) -> HttpResponseRedirect:
#     """
#     Vue recommandée: bascule la langue ET réécrit l'URL.
#     - Si la page traduite n'existe pas (ex: comptes/admin), on redirige vers l'accueil dans cette langue.
#     Utiliser avec un <form method="get" action="{% url 'switch_language' %}">.
#     """
#     lang = _normalize_lang(request.GET.get("language") or settings.LANGUAGE_CODE)
#     return _switch_to(request, lang, fallback_to_home=True)


# @require_GET
# def force_language(request: HttpRequest) -> HttpResponseRedirect:
#     """
#     Variante debug: pose la langue (session/cookie) SANS réécrire l'URL.
#     Utile si tu veux juste vérifier /debug/lang/.
#     """
#     lang = _normalize_lang(request.GET.get("language") or settings.LANGUAGE_CODE)
#     next_url = _safe_next(request, "/")
#     _activate_and_store(request, lang)
#     resp = HttpResponseRedirect(next_url)
#     _set_cookie(resp, lang)
#     return resp
