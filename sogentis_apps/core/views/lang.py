# core/views/lang.py
from __future__ import annotations

from urllib.parse import urlsplit

from django.conf import settings
from django.http import HttpRequest, HttpResponseRedirect
from django.urls import Resolver404, resolve, translate_url
from django.utils import translation
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import get_supported_language_variant
from django.views.decorators.http import require_http_methods

# ============================================================
# Session keys (alignés avec ton menu + money.py)
# ============================================================
SESSION_LANG_KEY = getattr(translation, "LANGUAGE_SESSION_KEY", "django_language")

ECOMMERCE_CURRENCY_SESSION_KEY = getattr(settings, "ECOMMERCE_CURRENCY_SESSION_KEY", "ECOMMERCE_CURRENCY")
ECOMMERCE_COUNTRY_SESSION_KEY = getattr(settings, "ECOMMERCE_COUNTRY_SESSION_KEY", "ECOMMERCE_COUNTRY")
COUNTRY_FALLBACK_SESSION_KEY = getattr(settings, "COUNTRY_CODE_SESSION_KEY", "country_code")

ECOMMERCE_CURRENCY_QUERY_PARAM = getattr(settings, "ECOMMERCE_CURRENCY_QUERY_PARAM", "currency")
ECOMMERCE_COUNTRY_QUERY_PARAM = getattr(settings, "ECOMMERCE_COUNTRY_QUERY_PARAM", "country")

ALLOWED_CURRENCIES = set(getattr(settings, "ECOMMERCE_CURRENCIES", ["XOF", "XAF", "EUR", "USD"]))
DEFAULT_CURRENCY = getattr(settings, "ECOMMERCE_CURRENCY", "XOF")
DEFAULT_COUNTRY = getattr(settings, "ECOMMERCE_DEFAULT_COUNTRY", "SN")


# ============================================================
# Helpers
# ============================================================
def _default_lang() -> str:
    try:
        return get_supported_language_variant(settings.LANGUAGE_CODE, strict=False)
    except LookupError:
        return "fr"


def _normalize_lang(raw: str) -> str:
    raw = (raw or "").strip()
    try:
        lang = get_supported_language_variant(raw, strict=False)
    except LookupError:
        lang = _default_lang()

    allowed = {c for c, _ in getattr(settings, "LANGUAGES", [])}
    if allowed and lang not in allowed:
        # fallback stable
        return _default_lang().split("-", 1)[0]
    return lang


def _normalize_currency(raw: str) -> str | None:
    c = (raw or "").strip().upper()
    if not c:
        return None
    return c if c in ALLOWED_CURRENCIES else None


def _normalize_country(raw: str) -> str | None:
    c = (raw or "").strip().upper()
    if not c:
        return None
    # ISO2 simple (SN, FR, CI, ...)
    if len(c) != 2 or not c.isalpha():
        return None
    return c


def _path_query_only(raw_url: str) -> str:
    parts = urlsplit(raw_url)
    path = parts.path or "/"
    query = parts.query or ""
    return path + (("?" + query) if query else "")


def _safe_next(request: HttpRequest, default: str = "/") -> str:
    raw = (
        (request.POST.get("next") if request.method == "POST" else None)
        or request.GET.get("next")
        or request.META.get("HTTP_REFERER")
        or default
    )
    raw = (raw or "").strip()

    # accepte URL absolue OU path relatif, mais uniquement sur l’host courant
    if not url_has_allowed_host_and_scheme(
        raw,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return default

    return _path_query_only(raw) or default


def _activate_and_store(request: HttpRequest, lang: str) -> None:
    translation.activate(lang)
    request.LANGUAGE_CODE = lang
    if hasattr(request, "session"):
        request.session[SESSION_LANG_KEY] = lang
        request.session.modified = True


def _set_cookie(resp: HttpResponseRedirect, lang: str) -> None:
    resp.set_cookie(
        settings.LANGUAGE_COOKIE_NAME,
        lang,
        max_age=getattr(settings, "LANGUAGE_COOKIE_AGE", None),
        path=getattr(settings, "LANGUAGE_COOKIE_PATH", "/"),
        domain=getattr(settings, "LANGUAGE_COOKIE_DOMAIN", None),
        secure=getattr(settings, "LANGUAGE_COOKIE_SECURE", False),
        httponly=getattr(settings, "LANGUAGE_COOKIE_HTTPONLY", False),
        samesite=getattr(settings, "LANGUAGE_COOKIE_SAMESITE", "Lax"),
    )


def _store_currency_and_country(request: HttpRequest) -> None:
    """
    Stocke currency/country en session (prod) :
    - currency : GET ?currency= / POST currency
    - country  : GET ?country= / POST country
    Clés: ECOMMERCE_CURRENCY + ECOMMERCE_COUNTRY (+ fallback country_code)
    """
    if not hasattr(request, "session"):
        return

    data = request.POST if request.method == "POST" else request.GET

    # currency
    cur = _normalize_currency(data.get(ECOMMERCE_CURRENCY_QUERY_PARAM))
    if cur:
        request.session[ECOMMERCE_CURRENCY_SESSION_KEY] = cur
    else:
        request.session[ECOMMERCE_CURRENCY_SESSION_KEY] = (
            request.session.get(ECOMMERCE_CURRENCY_SESSION_KEY) or DEFAULT_CURRENCY
        )

    # country
    ctry = _normalize_country(data.get(ECOMMERCE_COUNTRY_QUERY_PARAM))
    if ctry:
        request.session[ECOMMERCE_COUNTRY_SESSION_KEY] = ctry
        request.session[COUNTRY_FALLBACK_SESSION_KEY] = ctry
    else:
        # garde existant ou défaut
        existing = (
            request.session.get(ECOMMERCE_COUNTRY_SESSION_KEY)
            or request.session.get(COUNTRY_FALLBACK_SESSION_KEY)
            or DEFAULT_COUNTRY
        )
        existing = _normalize_country(existing) or DEFAULT_COUNTRY
        request.session[ECOMMERCE_COUNTRY_SESSION_KEY] = existing
        request.session[COUNTRY_FALLBACK_SESSION_KEY] = existing

    request.session.modified = True


def _resolves(path_with_query: str) -> bool:
    path = (path_with_query or "/").split("?", 1)[0] or "/"
    try:
        resolve(path)
        return True
    except Resolver404:
        return False


def _strip_lang_prefix_if_default(target: str, lang: str) -> str:
    """
    Anti-404 : si la langue cible est la langue par défaut et que ton site
    n’a pas de préfixe pour défaut, on tente de retirer /<lang>/.
    """
    base = (lang or "").split("-", 1)[0]
    dflt = (_default_lang() or "").split("-", 1)[0]
    if base and base == dflt and target.startswith(f"/{base}/"):
        stripped = "/" + target[len(base) + 2 :]  # enlève "/fr/"
        return stripped
    return target


# ============================================================
# Views
# ============================================================
@require_http_methods(["GET", "POST"])
def switch_language(request: HttpRequest) -> HttpResponseRedirect:
    """
    Change la langue + réécrit l'URL (FR <-> /en/...) et reste sur la même page.
    + anti-404 si la langue par défaut n'est pas préfixée.
    + conserve currency/country en session (menu économique).
    """
    data = request.POST if request.method == "POST" else request.GET

    lang = _normalize_lang(data.get("language") or _default_lang())
    _store_currency_and_country(request)

    next_url = _safe_next(request, "/")
    target = translate_url(next_url, lang) or next_url

    # anti-404 : retirer /fr/ si fr est la langue par défaut sans préfixe
    if not _resolves(target):
        stripped = _strip_lang_prefix_if_default(target, lang)
        if stripped != target and _resolves(stripped):
            target = stripped

    _activate_and_store(request, lang)
    resp = HttpResponseRedirect(target)
    _set_cookie(resp, lang)
    return resp


@require_http_methods(["GET", "POST"])
def force_language(request: HttpRequest) -> HttpResponseRedirect:
    """
    Force uniquement la langue sans translate_url (garde l’URL actuelle).
    + conserve currency/country en session.
    """
    data = request.POST if request.method == "POST" else request.GET

    lang = _normalize_lang(data.get("language") or _default_lang())
    _store_currency_and_country(request)

    next_url = _safe_next(request, "/")
    _activate_and_store(request, lang)

    resp = HttpResponseRedirect(next_url)
    _set_cookie(resp, lang)
    return resp




# # core/views/lang.py
# from __future__ import annotations

# from urllib.parse import urlsplit

# from django.conf import settings
# from django.http import HttpRequest, HttpResponseRedirect
# from django.urls import translate_url, resolve, Resolver404
# from django.utils import translation
# from django.utils.http import url_has_allowed_host_and_scheme
# from django.utils.translation import get_supported_language_variant
# from django.views.decorators.http import require_http_methods

# SESSION_LANG_KEY = getattr(translation, "LANGUAGE_SESSION_KEY", "django_language")

# # ✅ Ajoute XAF si tu l'utilises dans money.py
# ALLOWED_CURRENCIES = set(getattr(settings, "ECOMMERCE_CURRENCIES", ["XOF", "XAF", "EUR", "USD"]))
# DEFAULT_CURRENCY = getattr(settings, "ECOMMERCE_CURRENCY", "XOF")


# def _normalize_lang(raw: str) -> str:
#     raw = (raw or "").strip()
#     try:
#         lang = get_supported_language_variant(raw, strict=False)
#     except LookupError:
#         # ⚠️ normalise aussi le LANGUAGE_CODE du settings
#         try:
#             lang = get_supported_language_variant(settings.LANGUAGE_CODE, strict=False)
#         except LookupError:
#             lang = "fr"

#     allowed = {c for c, _ in getattr(settings, "LANGUAGES", [])}
#     return lang if (not allowed or lang in allowed) else (allowed.pop() if allowed else "fr")


# def _default_lang() -> str:
#     try:
#         return get_supported_language_variant(settings.LANGUAGE_CODE, strict=False)
#     except LookupError:
#         return "fr"


# def _path_query_only(raw_url: str) -> str:
#     parts = urlsplit(raw_url)
#     path = parts.path or "/"
#     query = parts.query or ""
#     return path + (("?" + query) if query else "")


# def _safe_next(request: HttpRequest, default: str = "/") -> str:
#     raw = (
#         (request.POST.get("next") if request.method == "POST" else None)
#         or request.GET.get("next")
#         or request.META.get("HTTP_REFERER")
#         or default
#     )
#     raw = (raw or "").strip()

#     if not url_has_allowed_host_and_scheme(
#         raw,
#         allowed_hosts={request.get_host()},
#         require_https=request.is_secure(),
#     ):
#         return default

#     return _path_query_only(raw) or default


# def _activate_and_store(request: HttpRequest, lang: str) -> None:
#     translation.activate(lang)
#     request.LANGUAGE_CODE = lang
#     if hasattr(request, "session"):
#         request.session[SESSION_LANG_KEY] = lang
#         request.session.modified = True


# def _set_cookie(resp: HttpResponseRedirect, lang: str) -> None:
#     resp.set_cookie(
#         settings.LANGUAGE_COOKIE_NAME,
#         lang,
#         max_age=getattr(settings, "LANGUAGE_COOKIE_AGE", None),
#         path=getattr(settings, "LANGUAGE_COOKIE_PATH", "/"),
#         domain=getattr(settings, "LANGUAGE_COOKIE_DOMAIN", None),
#         secure=getattr(settings, "LANGUAGE_COOKIE_SECURE", False),
#         httponly=getattr(settings, "LANGUAGE_COOKIE_HTTPONLY", False),
#         samesite=getattr(settings, "LANGUAGE_COOKIE_SAMESITE", "Lax"),
#     )


# def _store_currency_and_country(request: HttpRequest) -> None:
#     """Optionnel ecommerce: conserve currency/country (GET ou POST)."""
#     if not hasattr(request, "session"):
#         return

#     data = request.POST if request.method == "POST" else request.GET

#     raw_currency = (data.get("currency") or "").strip().upper()
#     if raw_currency and raw_currency in ALLOWED_CURRENCIES:
#         request.session["ECOMMERCE_CURRENCY"] = raw_currency
#     else:
#         request.session["ECOMMERCE_CURRENCY"] = request.session.get("ECOMMERCE_CURRENCY") or DEFAULT_CURRENCY

#     raw_country = (data.get("country") or "").strip().upper()
#     if raw_country:
#         request.session["country_code"] = raw_country
#         request.session["ECOMMERCE_COUNTRY"] = raw_country

#     request.session.modified = True


# def _resolves(path_with_query: str) -> bool:
#     path = (path_with_query or "/").split("?", 1)[0] or "/"
#     try:
#         resolve(path)
#         return True
#     except Resolver404:
#         return False


# @require_http_methods(["GET", "POST"])
# def switch_language(request: HttpRequest) -> HttpResponseRedirect:
#     """
#     Change la langue + réécrit l'URL (FR <-> /en/...) et reste sur la même page.
#     + fallback anti-404 si /fr/ n'existe pas (FR langue par défaut sans préfixe).
#     """
#     data = request.POST if request.method == "POST" else request.GET

#     raw_lang = data.get("language")
#     lang = _normalize_lang(raw_lang or _default_lang())

#     _store_currency_and_country(request)

#     next_url = _safe_next(request, "/")
#     target = translate_url(next_url, lang) or next_url

#     # ✅ Anti-404 : si la cible ne resolve pas, tente de retirer /<lang>/
#     if not _resolves(target):
#         base = (lang or "").split("-", 1)[0]  # "fr-fr" -> "fr"
#         dflt = (_default_lang() or "").split("-", 1)[0]
#         if base == dflt and target.startswith(f"/{base}/"):
#             stripped = "/" + target[len(base) + 2:]  # enlève "/fr/"
#             if _resolves(stripped):
#                 target = stripped

#     _activate_and_store(request, lang)
#     resp = HttpResponseRedirect(target)
#     _set_cookie(resp, lang)
#     return resp


# @require_http_methods(["GET", "POST"])
# def force_language(request: HttpRequest) -> HttpResponseRedirect:
#     raw_lang = request.POST.get("language") if request.method == "POST" else request.GET.get("language")
#     lang = _normalize_lang(raw_lang or _default_lang())

#     _store_currency_and_country(request)

#     next_url = _safe_next(request, "/")
#     _activate_and_store(request, lang)

#     resp = HttpResponseRedirect(next_url)
#     _set_cookie(resp, lang)
#     return resp








# # core/views/lang.py
# from __future__ import annotations

# from urllib.parse import urlsplit

# from django.conf import settings
# from django.http import HttpRequest, HttpResponseRedirect
# from django.urls import translate_url
# from django.utils import translation
# from django.utils.http import url_has_allowed_host_and_scheme
# from django.utils.translation import get_supported_language_variant
# from django.views.decorators.http import require_http_methods

# SESSION_LANG_KEY = getattr(translation, "LANGUAGE_SESSION_KEY", "django_language")

# ALLOWED_CURRENCIES = set(getattr(settings, "ECOMMERCE_CURRENCIES", ["XOF", "EUR", "USD"]))
# DEFAULT_CURRENCY = getattr(settings, "ECOMMERCE_CURRENCY", "XOF")


# def _normalize_lang(raw: str) -> str:
#     raw = (raw or "").strip()
#     try:
#         lang = get_supported_language_variant(raw, strict=False)
#     except LookupError:
#         lang = settings.LANGUAGE_CODE

#     allowed = {c for c, _ in getattr(settings, "LANGUAGES", [])}
#     return lang if (not allowed or lang in allowed) else settings.LANGUAGE_CODE


# def _path_query_only(raw_url: str) -> str:
#     """Convertit une URL absolue en path+query (translate_url doit recevoir une URL relative)."""
#     parts = urlsplit(raw_url)
#     path = parts.path or "/"
#     query = parts.query or ""
#     return path + (("?" + query) if query else "")


# def _safe_next(request: HttpRequest, default: str = "/") -> str:
#     raw = (
#         (request.POST.get("next") if request.method == "POST" else None)
#         or request.GET.get("next")
#         or request.META.get("HTTP_REFERER")
#         or default
#     )
#     raw = (raw or "").strip()

#     if not url_has_allowed_host_and_scheme(
#         raw,
#         allowed_hosts={request.get_host()},
#         require_https=request.is_secure(),
#     ):
#         return default

#     return _path_query_only(raw) or default


# def _activate_and_store(request: HttpRequest, lang: str) -> None:
#     translation.activate(lang)
#     request.LANGUAGE_CODE = lang
#     if hasattr(request, "session"):
#         request.session[SESSION_LANG_KEY] = lang
#         request.session.modified = True


# def _set_cookie(resp: HttpResponseRedirect, lang: str) -> None:
#     resp.set_cookie(
#         settings.LANGUAGE_COOKIE_NAME,
#         lang,
#         max_age=getattr(settings, "LANGUAGE_COOKIE_AGE", None),
#         path=getattr(settings, "LANGUAGE_COOKIE_PATH", "/"),
#         domain=getattr(settings, "LANGUAGE_COOKIE_DOMAIN", None),
#         secure=getattr(settings, "LANGUAGE_COOKIE_SECURE", False),
#         httponly=getattr(settings, "LANGUAGE_COOKIE_HTTPONLY", False),
#         samesite=getattr(settings, "LANGUAGE_COOKIE_SAMESITE", "Lax"),
#     )


# def _store_currency_and_country(request: HttpRequest) -> None:
#     """Optionnel ecommerce: conserve currency/country si présent dans la querystring."""
#     if not hasattr(request, "session"):
#         return

#     raw_currency = (request.GET.get("currency") or "").strip().upper()
#     if raw_currency and raw_currency in ALLOWED_CURRENCIES:
#         request.session["ECOMMERCE_CURRENCY"] = raw_currency
#     else:
#         request.session["ECOMMERCE_CURRENCY"] = request.session.get("ECOMMERCE_CURRENCY") or DEFAULT_CURRENCY

#     raw_country = (request.GET.get("country") or "").strip().upper()
#     if raw_country:
#         request.session["country_code"] = raw_country
#         request.session["ECOMMERCE_COUNTRY"] = raw_country

#     request.session.modified = True


# @require_http_methods(["GET", "POST"])
# def switch_language(request: HttpRequest) -> HttpResponseRedirect:
#     """
#     Change la langue + réécrit l'URL (FR <-> /en/...) et reste sur la même page.
#     """
#     raw_lang = request.POST.get("language") if request.method == "POST" else request.GET.get("language")
#     lang = _normalize_lang(raw_lang or settings.LANGUAGE_CODE)

#     _store_currency_and_country(request)

#     next_url = _safe_next(request, "/")
#     target = translate_url(next_url, lang) or next_url

#     _activate_and_store(request, lang)
#     resp = HttpResponseRedirect(target)
#     _set_cookie(resp, lang)
#     return resp


# @require_http_methods(["GET", "POST"])
# def force_language(request: HttpRequest) -> HttpResponseRedirect:
#     """
#     Change la langue sans réécrire l'URL (debug / cas spécial).
#     """
#     raw_lang = request.POST.get("language") if request.method == "POST" else request.GET.get("language")
#     lang = _normalize_lang(raw_lang or settings.LANGUAGE_CODE)

#     _store_currency_and_country(request)

#     next_url = _safe_next(request, "/")
#     _activate_and_store(request, lang)

#     resp = HttpResponseRedirect(next_url)
#     _set_cookie(resp, lang)
#     return resp








# # core/views/lang.py
# from __future__ import annotations

# from urllib.parse import urlsplit, urlunsplit

# from django.conf import settings
# from django.http import HttpRequest, HttpResponseRedirect
# from django.urls import Resolver404, resolve, reverse, translate_url
# from django.utils import translation
# from django.utils.http import url_has_allowed_host_and_scheme
# from django.utils.translation import get_supported_language_variant
# from django.views.decorators.http import require_http_methods

# SESSION_LANG_KEY = getattr(translation, "LANGUAGE_SESSION_KEY", "django_language")

# ALLOWED_CURRENCIES = set(getattr(settings, "ECOMMERCE_CURRENCIES", ["XOF", "EUR", "USD"]))
# DEFAULT_CURRENCY = getattr(settings, "ECOMMERCE_CURRENCY", "XOF")


# def _normalize_lang(raw: str) -> str:
#     raw = (raw or "").strip()
#     try:
#         lang = get_supported_language_variant(raw, strict=False)
#     except LookupError:
#         lang = settings.LANGUAGE_CODE

#     allowed = {c for c, _ in getattr(settings, "LANGUAGES", [])}
#     return lang if (not allowed or lang in allowed) else settings.LANGUAGE_CODE


# def _path_query_only(raw_url: str) -> str:
#     """Convertit une URL absolue en path+query. Garde aussi les URLs déjà relatives."""
#     parts = urlsplit(raw_url)
#     path = parts.path or "/"
#     query = parts.query or ""
#     return path + (("?" + query) if query else "")


# def _safe_next(request: HttpRequest, default: str = "/") -> str:
#     raw = (
#         (request.POST.get("next") if request.method == "POST" else None)
#         or request.GET.get("next")
#         or request.META.get("HTTP_REFERER")
#         or default
#     )
#     raw = (raw or "").strip()

#     # sécurité anti-open-redirect
#     if not url_has_allowed_host_and_scheme(
#         raw,
#         allowed_hosts={request.get_host()},
#         require_https=request.is_secure(),
#     ):
#         return default

#     return _path_query_only(raw) or default


# def _activate_and_store(request: HttpRequest, lang: str) -> None:
#     translation.activate(lang)
#     request.LANGUAGE_CODE = lang
#     if hasattr(request, "session"):
#         request.session[SESSION_LANG_KEY] = lang
#         request.session.modified = True


# def _set_cookie(resp: HttpResponseRedirect, lang: str) -> None:
#     resp.set_cookie(
#         settings.LANGUAGE_COOKIE_NAME,
#         lang,
#         max_age=getattr(settings, "LANGUAGE_COOKIE_AGE", None),
#         path=getattr(settings, "LANGUAGE_COOKIE_PATH", "/"),
#         domain=getattr(settings, "LANGUAGE_COOKIE_DOMAIN", None),
#         secure=getattr(settings, "LANGUAGE_COOKIE_SECURE", False),
#         httponly=getattr(settings, "LANGUAGE_COOKIE_HTTPONLY", False),
#         samesite=getattr(settings, "LANGUAGE_COOKIE_SAMESITE", "Lax"),
#     )


# def _store_currency_and_country(request: HttpRequest) -> None:
#     if not hasattr(request, "session"):
#         return

#     raw_currency = (request.GET.get("currency") or "").strip().upper()
#     if raw_currency and raw_currency in ALLOWED_CURRENCIES:
#         currency = raw_currency
#     else:
#         currency = request.session.get("ECOMMERCE_CURRENCY") or DEFAULT_CURRENCY
#     request.session["ECOMMERCE_CURRENCY"] = currency

#     raw_country = (request.GET.get("country") or "").strip().upper()
#     if raw_country:
#         request.session["country_code"] = raw_country
#         request.session["ECOMMERCE_COUNTRY"] = raw_country

#     request.session.modified = True


# def _rebuild_same_view_in_lang(next_url: str, lang: str) -> str | None:
#     """
#     Reconstruit la même page dans la langue demandée via resolve() + reverse()
#     => très fiable avec i18n_patterns.
#     """
#     parts = urlsplit(next_url)
#     path = parts.path or "/"
#     query = parts.query or ""

#     try:
#         match = resolve(path)
#     except Resolver404:
#         return None

#     with translation.override(lang):
#         try:
#             new_path = reverse(match.view_name, args=match.args, kwargs=match.kwargs)
#         except Exception:
#             return None

#     return new_path + (("?" + query) if query else "")


# def _switch_to(request: HttpRequest, lang: str) -> HttpResponseRedirect:
#     next_url = _safe_next(request, "/")

#     # 1) meilleure méthode : resolve + reverse dans la langue
#     target = _rebuild_same_view_in_lang(next_url, lang)

#     # 2) fallback : translate_url (moins fiable si URL absolue/edge cases)
#     if not target:
#         target = translate_url(next_url, lang) or next_url

#     # 3) dernier fallback : si on a perdu la page (retour /), on reste sur next_url
#     if urlsplit(target).path == "/" and urlsplit(next_url).path != "/":
#         target = next_url

#     _activate_and_store(request, lang)
#     resp = HttpResponseRedirect(target)
#     _set_cookie(resp, lang)
#     return resp


# @require_http_methods(["GET", "POST"])
# def switch_language(request: HttpRequest) -> HttpResponseRedirect:
#     raw_lang = request.POST.get("language") if request.method == "POST" else request.GET.get("language")
#     lang = _normalize_lang(raw_lang or settings.LANGUAGE_CODE)

#     _store_currency_and_country(request)
#     return _switch_to(request, lang)


# @require_http_methods(["GET", "POST"])
# def force_language(request: HttpRequest) -> HttpResponseRedirect:
#     raw_lang = request.POST.get("language") if request.method == "POST" else request.GET.get("language")
#     lang = _normalize_lang(raw_lang or settings.LANGUAGE_CODE)

#     _store_currency_and_country(request)

#     next_url = _safe_next(request, "/")
#     _activate_and_store(request, lang)

#     resp = HttpResponseRedirect(next_url)
#     _set_cookie(resp, lang)
#     return resp







# # core/views/lang.py
# from __future__ import annotations

# from urllib.parse import urlsplit

# from django.conf import settings
# from django.http import HttpRequest, HttpResponseRedirect
# from django.urls import translate_url, resolve, Resolver404, reverse
# from django.utils import translation
# from django.utils.http import url_has_allowed_host_and_scheme
# from django.utils.translation import get_supported_language_variant
# from django.views.decorators.http import require_http_methods

# # Clé session selon version Django
# SESSION_LANG_KEY = getattr(translation, "LANGUAGE_SESSION_KEY", "django_language")

# # ============================== #
# #  CURRENCIES E-COMMERCE         #
# # ============================== #
# ALLOWED_CURRENCIES = set(getattr(settings, "ECOMMERCE_CURRENCIES", ["XOF", "EUR", "USD"]))
# DEFAULT_CURRENCY = getattr(settings, "ECOMMERCE_CURRENCY", "XOF")


# def _normalize_lang(raw: str) -> str:
#     """Normalise le code langue (en-us → en) et valide contre LANGUAGES."""
#     raw = (raw or "").strip()
#     try:
#         lang = get_supported_language_variant(raw, strict=False)
#     except LookupError:
#         lang = settings.LANGUAGE_CODE

#     allowed = {c for c, _ in getattr(settings, "LANGUAGES", [])}
#     return lang if (not allowed or lang in allowed) else settings.LANGUAGE_CODE


# def _safe_next(request: HttpRequest, default: str = "/") -> str:
#     """
#     Récupère une URL next sûre (POST/GET/Referer), et la normalise en path+query.
#     Cela évite que translate_url reçoive une URL absolue.
#     """
#     raw = (
#         (request.POST.get("next") if hasattr(request, "POST") else None)
#         or request.GET.get("next")
#         or request.META.get("HTTP_REFERER")
#         or default
#     )
#     raw = (raw or "").strip()

#     # Sécurité redirection (si raw est absolu)
#     if not url_has_allowed_host_and_scheme(
#         raw,
#         allowed_hosts={request.get_host()},
#         require_https=request.is_secure(),
#     ):
#         return default

#     parts = urlsplit(raw)
#     # Convertit une URL absolue en path+query
#     if parts.scheme or parts.netloc:
#         raw = (parts.path or "/") + (("?" + parts.query) if parts.query else "")

#     return raw or default


# def _activate_and_store(request: HttpRequest, lang: str) -> None:
#     """Active la langue et la mémorise en session."""
#     translation.activate(lang)
#     request.LANGUAGE_CODE = lang

#     if hasattr(request, "session"):
#         request.session[SESSION_LANG_KEY] = lang
#         request.session.modified = True


# def _resolvable(path: str) -> bool:
#     """Vérifie si une path est résoluble par l'URLconf courant."""
#     try:
#         resolve(path)
#         return True
#     except Resolver404:
#         return False


# def _lang_home(lang: str) -> str:
#     """Accueil dans la langue demandée (gère i18n_patterns)."""
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
#         path=getattr(settings, "LANGUAGE_COOKIE_PATH", "/"),
#         domain=getattr(settings, "LANGUAGE_COOKIE_DOMAIN", None),
#         secure=getattr(settings, "LANGUAGE_COOKIE_SECURE", False),
#         httponly=getattr(settings, "LANGUAGE_COOKIE_HTTPONLY", False),
#         samesite=getattr(settings, "LANGUAGE_COOKIE_SAMESITE", "Lax"),
#     )


# # ============================== #
# #  CURRENCY / COUNTRY            #
# # ============================== #
# def _store_currency_and_country(request: HttpRequest) -> None:
#     """
#     Lit currency / country depuis la querystring du sélecteur e-commerce
#     et les stocke en session.
#     """
#     if not hasattr(request, "session"):
#         return

#     # --- currency ---
#     raw_currency = (request.GET.get("currency") or "").strip().upper()
#     if raw_currency and raw_currency in ALLOWED_CURRENCIES:
#         currency = raw_currency
#     else:
#         currency = request.session.get("ECOMMERCE_CURRENCY") or DEFAULT_CURRENCY

#     request.session["ECOMMERCE_CURRENCY"] = currency

#     # --- country ---
#     raw_country = (request.GET.get("country") or "").strip().upper()
#     if raw_country:
#         request.session["country_code"] = raw_country
#         request.session["ECOMMERCE_COUNTRY"] = raw_country

#     request.session.modified = True


# def _switch_to(request: HttpRequest, lang: str, fallback_to_home: bool = True) -> HttpResponseRedirect:
#     """
#     Traduit l'URL courante vers `lang`.
#     Si la route n'existe pas -> fallback intelligent :
#     - d'abord rester sur l'URL courante (mais langue changée)
#     - sinon home(lang)
#     """
#     current_url = _safe_next(request, "/")
#     current_path = _path_of(current_url)

#     target = translate_url(current_url, lang) or current_url
#     target_path = _path_of(target)

#     if fallback_to_home:
#         # Si translate_url donne "/" alors que l’URL courante n’est pas "/",
#         # on reste sur la page courante plutôt que forcer home.
#         if target_path == "/" and current_path != "/":
#             target = current_url
#             target_path = current_path

#         # Si la cible ne se résout pas, on reste sur current_url (qui est normalement valide)
#         if not _resolvable(target_path):
#             target = current_url if _resolvable(current_path) else _lang_home(lang)

#     _activate_and_store(request, lang)
#     resp = HttpResponseRedirect(target)
#     _set_cookie(resp, lang)
#     return resp


# # ============================== #
# #  PUBLIC VIEWS                  #
# # ============================== #
# @require_http_methods(["GET", "POST"])
# def switch_language(request: HttpRequest) -> HttpResponseRedirect:
#     """
#     - Bascule la langue + réécrit l'URL
#     - Stocke aussi devise/pays (GET) si présent (panneau economic/ecommerce)
#     """
#     raw_lang = request.POST.get("language") if request.method == "POST" else request.GET.get("language")
#     lang = _normalize_lang(raw_lang or settings.LANGUAGE_CODE)

#     _store_currency_and_country(request)
#     return _switch_to(request, lang, fallback_to_home=True)


# @require_http_methods(["GET", "POST"])
# def force_language(request: HttpRequest) -> HttpResponseRedirect:
#     """
#     Debug: pose la langue (session/cookie) SANS réécrire l'URL.
#     Stocke aussi devise/pays.
#     """
#     raw_lang = request.POST.get("language") if request.method == "POST" else request.GET.get("language")
#     lang = _normalize_lang(raw_lang or settings.LANGUAGE_CODE)

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

# from django.views.decorators.http import require_GET

# # Clé session selon version Django
# SESSION_LANG_KEY = getattr(translation, "LANGUAGE_SESSION_KEY", "django_language")

# # ============================== #
# #  CURRENCIES E-COMMERCE         #
# # ============================== #
# ALLOWED_CURRENCIES = set(getattr(settings, "ECOMMERCE_CURRENCIES", ["XOF", "EUR", "USD"]))
# DEFAULT_CURRENCY = getattr(settings, "ECOMMERCE_CURRENCY", "XOF")


# def _normalize_lang(raw: str) -> str:
#     """Normalise le code langue (en-us → en, zh-hans ok) et valide contre LANGUAGES."""
#     try:
#         lang = get_supported_language_variant(raw, strict=False)
#     except LookupError:
#         lang = settings.LANGUAGE_CODE

#     allowed = {c for c, _ in getattr(settings, "LANGUAGES", [])}
#     return lang if (not allowed or lang in allowed) else settings.LANGUAGE_CODE


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
#     """Accueil dans la langue demandée (gère i18n_patterns)."""
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
#     et les stocke en session.
#     IMPORTANT:
#     - currency -> request.session["ECOMMERCE_CURRENCY"]
#     - country  -> request.session["country_code"] (compat money tag ecommerce)
#               + request.session["ECOMMERCE_COUNTRY"] (optionnel / futur)
#     """
#     # --- currency ---
#     raw_currency = (request.GET.get("currency") or "").strip().upper()
#     if raw_currency and raw_currency in ALLOWED_CURRENCIES:
#         currency = raw_currency
#     else:
#         currency = request.session.get("ECOMMERCE_CURRENCY") or DEFAULT_CURRENCY

#     request.session["ECOMMERCE_CURRENCY"] = currency

#     # --- country ---
#     raw_country = (request.GET.get("country") or "").strip().upper()
#     if raw_country:
#         # compat: ton money.py ecommerce lit "country_code"
#         request.session["country_code"] = raw_country
#         # optionnel: si tu veux un nom explicite aussi
#         request.session["ECOMMERCE_COUNTRY"] = raw_country

#     request.session.modified = True


# def _switch_to(request: HttpRequest, lang: str, fallback_to_home: bool = True) -> HttpResponseRedirect:
#     """
#     Traduit l'URL courante vers `lang`.
#     Si la route n'existe pas dans cette langue -> fallback vers home(lang).
#     """
#     current_url = _safe_next(request, "/")
#     target = translate_url(current_url, lang)
#     path = _path_of(target)

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
#     - Bascule la langue + réécrit l'URL
#     - Stocke aussi la devise/pays (panneau economic/ecommerce).
#     """
#     lang = _normalize_lang(request.GET.get("language") or settings.LANGUAGE_CODE)
#     _store_currency_and_country(request)
#     return _switch_to(request, lang, fallback_to_home=True)


# @require_GET
# def force_language(request: HttpRequest) -> HttpResponseRedirect:
#     """
#     Debug: pose la langue (session/cookie) SANS réécrire l'URL.
#     Stocke aussi la devise/pays.
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
