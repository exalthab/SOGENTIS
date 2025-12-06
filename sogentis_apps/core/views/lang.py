# core/views/lang.py
from django.conf import settings
from django.http import HttpRequest, HttpResponseRedirect
from django.urls import translate_url, resolve, Resolver404, reverse
from django.utils import translation
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import get_supported_language_variant
from urllib.parse import urlsplit

# Clé session selon version Django
SESSION_LANG_KEY = getattr(translation, "LANGUAGE_SESSION_KEY", "django_language")


def _normalize_lang(raw: str) -> str:
    """Normalise le code langue (en-us → en, zh-hans ok) et valide contre LANGUAGES."""
    try:
        lang = get_supported_language_variant(raw, strict=False)
    except LookupError:
        lang = settings.LANGUAGE_CODE
    allowed = {c for c, _ in getattr(settings, "LANGUAGES", [])}
    return lang if not allowed or lang in allowed else settings.LANGUAGE_CODE


def _safe_next(request: HttpRequest, default: str = "/") -> str:
    """Récupère une URL next sûre (next, referer, ou défaut)."""
    nxt = request.GET.get("next") or request.META.get("HTTP_REFERER") or default
    if url_has_allowed_host_and_scheme(nxt, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
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
    """
    Renvoie l'URL d'accueil dans la langue demandée (via reverse dans un contexte activé).
    Gère automatiquement le préfixe (/wo/, /es/, etc.) selon i18n_patterns.
    """
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


def _switch_to(request: HttpRequest, lang: str, fallback_to_home: bool = True) -> HttpResponseRedirect:
    """
    Logique commune: traduit l'URL courante vers `lang`. Si la route n'existe pas
    dans cette langue (ex: page comptes/admin hors i18n_patterns), on retombe
    proprement sur l'accueil de la langue.
    """
    current_url = _safe_next(request, "/")
    # traduit l'URL (ajoute /xx/ si nécessaire)
    target = translate_url(current_url, lang)
    path = _path_of(target)

    # Si la route traduite n'existe pas → fallback vers home(lang)
    if fallback_to_home and (not _resolvable(path) or path == "/"):
        target = _lang_home(lang)

    _activate_and_store(request, lang)
    resp = HttpResponseRedirect(target)
    _set_cookie(resp, lang)
    return resp


from django.views.decorators.http import require_GET

@require_GET
def switch_language(request: HttpRequest) -> HttpResponseRedirect:
    """
    Vue recommandée: bascule la langue ET réécrit l'URL.
    - Si la page traduite n'existe pas (ex: comptes/admin), on redirige vers l'accueil dans cette langue.
    Utiliser avec un <form method="get" action="{% url 'switch_language' %}">.
    """
    lang = _normalize_lang(request.GET.get("language") or settings.LANGUAGE_CODE)
    return _switch_to(request, lang, fallback_to_home=True)


@require_GET
def force_language(request: HttpRequest) -> HttpResponseRedirect:
    """
    Variante debug: pose la langue (session/cookie) SANS réécrire l'URL.
    Utile si tu veux juste vérifier /debug/lang/.
    """
    lang = _normalize_lang(request.GET.get("language") or settings.LANGUAGE_CODE)
    next_url = _safe_next(request, "/")
    _activate_and_store(request, lang)
    resp = HttpResponseRedirect(next_url)
    _set_cookie(resp, lang)
    return resp
