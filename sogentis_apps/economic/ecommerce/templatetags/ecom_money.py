# economic/ecommerce/templatetags/money.py
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from functools import lru_cache
from typing import Any

from django import template
from django.conf import settings

register = template.Library()

# =====================================================
# CONFIG (settings override)
# =====================================================
BASE_CURRENCY: str = getattr(settings, "BASE_CURRENCY", "XOF")
DEFAULT_CURRENCY: str = getattr(settings, "DEFAULT_CURRENCY", BASE_CURRENCY)

DEFAULT_RATES = {
    "XOF": Decimal("1"),
    "XAF": Decimal("1"),
    "EUR": Decimal("0.0015"),
    "USD": Decimal("0.0016"),
    "GBP": Decimal("0.0013"),
}
CURRENCY_RATES: dict[str, Any] = getattr(settings, "CURRENCY_RATES", DEFAULT_RATES)

DEFAULT_COUNTRY_CURRENCY_MAP = {
    "SN": "XOF", "CI": "XOF", "BJ": "XOF", "BF": "XOF", "ML": "XOF", "TG": "XOF", "NE": "XOF", "GW": "XOF",
    "CM": "XAF", "GA": "XAF", "TD": "XAF", "CG": "XAF", "CF": "XAF", "GQ": "XAF",
    "FR": "EUR", "BE": "EUR", "DE": "EUR", "ES": "EUR", "IT": "EUR", "NL": "EUR",
    "US": "USD", "CA": "USD",
    "GB": "GBP",
}
COUNTRY_CURRENCY_MAP: dict[str, str] = getattr(settings, "COUNTRY_CURRENCY_MAP", DEFAULT_COUNTRY_CURRENCY_MAP)

DEFAULT_SYMBOLS = {"EUR": "€", "USD": "$", "GBP": "£", "XOF": "FCFA", "XAF": "FCFA"}
CURRENCY_SYMBOLS: dict[str, str] = getattr(settings, "CURRENCY_SYMBOLS", DEFAULT_SYMBOLS)

DEFAULT_DECIMALS = {"XOF": 0, "XAF": 0, "EUR": 2, "USD": 2, "GBP": 2}
CURRENCY_DECIMALS: dict[str, int] = getattr(settings, "CURRENCY_DECIMALS", DEFAULT_DECIMALS)

THOUSANDS_SEP: str = getattr(settings, "MONEY_THOUSANDS_SEP", " ")
DECIMAL_SEP: str = getattr(settings, "MONEY_DECIMAL_SEP", ",")

# Session keys (compat + menu)
SESSION_KEY: str = getattr(settings, "ECOMMERCE_CURRENCY_SESSION_KEY", "ECOMMERCE_CURRENCY")
COUNTRY_SESSION_KEY: str = getattr(settings, "ECOMMERCE_COUNTRY_SESSION_KEY", "ECOMMERCE_COUNTRY")
FALLBACK_COUNTRY_SESSION_KEY: str = getattr(settings, "COUNTRY_CODE_SESSION_KEY", "country_code")

QUERY_PARAM: str = getattr(settings, "ECOMMERCE_CURRENCY_QUERY_PARAM", "currency")

# =====================================================
# Helpers
# =====================================================
@dataclass(frozen=True)
class MoneyParts:
    number: str
    symbol: str
    currency: str
    formatted: str


def _normalize_currency(code: Any) -> str | None:
    if code is None:
        return None
    c = str(code).strip().upper()
    return c or None


def _normalize_amount(amount: Any) -> Decimal | None:
    if amount is None:
        return None
    try:
        return Decimal(str(amount))
    except (InvalidOperation, TypeError, ValueError):
        return None


@lru_cache(maxsize=128)
def _decimals_for(currency: str) -> int:
    try:
        return int(CURRENCY_DECIMALS.get(currency, 2))
    except Exception:
        return 2


@lru_cache(maxsize=128)
def _symbol_for(currency: str) -> str:
    return str(CURRENCY_SYMBOLS.get(currency, currency))


def _quantize(amount: Decimal, currency: str) -> Decimal:
    d = _decimals_for(currency)
    q = Decimal("1") if d == 0 else Decimal("1").scaleb(-d)
    try:
        return amount.quantize(q, rounding=ROUND_HALF_UP)
    except Exception:
        return amount


def _format_number(amount: Decimal, currency: str) -> str:
    d = _decimals_for(currency)
    if d == 0:
        s = f"{amount:,.0f}"
        return s.replace(",", THOUSANDS_SEP)

    s = f"{amount:,.{d}f}"
    s = s.replace(",", "§")
    s = s.replace(".", DECIMAL_SEP)
    s = s.replace("§", THOUSANDS_SEP)
    return s


def _detect_country_code_from_request(request) -> str | None:
    if not request:
        return None

    # 1) session ECOMMERCE_COUNTRY (ton menu)
    try:
        cc = request.session.get(COUNTRY_SESSION_KEY)
    except Exception:
        cc = None
    if cc:
        return str(cc).strip().upper()

    # 2) session country_code (compat)
    try:
        cc = request.session.get(FALLBACK_COUNTRY_SESSION_KEY)
    except Exception:
        cc = None
    if cc:
        return str(cc).strip().upper()

    # 3) middleware geo
    cc = getattr(request, "COUNTRY_CODE", None)
    if cc:
        return str(cc).strip().upper()

    # 4) profil user (si tu as country/code)
    user = getattr(request, "user", None)
    if user and getattr(user, "is_authenticated", False):
        profile = getattr(user, "profile", None)
        if profile:
            country = getattr(profile, "country", None)
            if country:
                code = getattr(country, "code", None)
                if code:
                    return str(code).strip().upper()
                return str(country).strip().upper()

    return None


def _detect_currency_from_context(context, explicit_currency: Any = None) -> str:
    c = _normalize_currency(explicit_currency)
    if c:
        return c

    request = context.get("request")
    if request:
        # GET param ?currency=
        try:
            q = request.GET.get(QUERY_PARAM)
        except Exception:
            q = None
        c = _normalize_currency(q)
        if c:
            return c

        # Session
        try:
            session_currency = request.session.get(SESSION_KEY)
        except Exception:
            session_currency = None
        c = _normalize_currency(session_currency)
        if c:
            return c

        # Country mapping
        cc = _detect_country_code_from_request(request)
        if cc:
            return COUNTRY_CURRENCY_MAP.get(cc, DEFAULT_CURRENCY)

    return DEFAULT_CURRENCY


def _rate_for(currency: str) -> Decimal | None:
    raw = CURRENCY_RATES.get(currency)
    if raw is None:
        return None
    try:
        return Decimal(str(raw))
    except (InvalidOperation, TypeError, ValueError):
        return None


def _convert_from_base(amount: Decimal, target_currency: str) -> Decimal:
    target_currency = _normalize_currency(target_currency) or DEFAULT_CURRENCY
    if target_currency == BASE_CURRENCY:
        return amount

    rate = _rate_for(target_currency)
    if rate is None:
        return amount

    try:
        return amount * rate
    except Exception:
        return amount


def _format_money(amount: Decimal, currency: str) -> str:
    amount_q = _quantize(amount, currency)
    number = _format_number(amount_q, currency)
    symbol = _symbol_for(currency)
    return f"{number} {symbol}".strip()


# =====================================================
# Tags / filters
# =====================================================
@register.simple_tag(takes_context=True, name="money")
def money(context, amount, currency_code=None):
    amount_dec = _normalize_amount(amount)
    if amount_dec is None:
        return ""
    currency = _detect_currency_from_context(context, currency_code)
    converted = _convert_from_base(amount_dec, currency)
    return _format_money(converted, currency)


@register.simple_tag(takes_context=True, name="money_parts")
def money_parts(context, amount, currency_code=None):
    amount_dec = _normalize_amount(amount)
    if amount_dec is None:
        return {"number": "", "symbol": "", "currency": "", "formatted": ""}

    currency = _detect_currency_from_context(context, currency_code)
    converted = _convert_from_base(amount_dec, currency)
    converted_q = _quantize(converted, currency)

    number = _format_number(converted_q, currency)
    symbol = _symbol_for(currency)
    return {"number": number, "symbol": symbol, "currency": currency, "formatted": f"{number} {symbol}".strip()}


@register.filter(name="moneyf")
def money_filter(amount, currency_code: str | None = None) -> str:
    a = _normalize_amount(amount)
    if a is None:
        return ""
    currency = _normalize_currency(currency_code) or DEFAULT_CURRENCY
    converted = _convert_from_base(a, currency)
    return _format_money(converted, currency)






# # economic/ecommerce/templatetags/money.py
# from __future__ import annotations

# from dataclasses import dataclass
# from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
# from functools import lru_cache
# from typing import Any

# from django import template
# from django.conf import settings

# register = template.Library()


# # =====================================================
# # CONFIGURATION (surchargeable via settings.py)
# # =====================================================

# BASE_CURRENCY: str = getattr(settings, "BASE_CURRENCY", "XOF")
# DEFAULT_CURRENCY: str = getattr(settings, "DEFAULT_CURRENCY", BASE_CURRENCY)

# # Taux de change par rapport à BASE_CURRENCY
# # valeur = combien vaut 1 BASE_CURRENCY dans la devise cible
# DEFAULT_RATES = {
#     "XOF": Decimal("1"),
#     "XAF": Decimal("1"),
#     "EUR": Decimal("0.0015"),  # exemple
#     "USD": Decimal("0.0016"),  # exemple
#     "GBP": Decimal("0.0013"),  # exemple
# }
# CURRENCY_RATES: dict[str, Any] = getattr(settings, "CURRENCY_RATES", DEFAULT_RATES)

# # Pays -> devise
# DEFAULT_COUNTRY_CURRENCY_MAP = {
#     # Zone XOF
#     "SN": "XOF",
#     "CI": "XOF",
#     "BJ": "XOF",
#     "BF": "XOF",
#     "ML": "XOF",
#     "TG": "XOF",
#     "NE": "XOF",
#     "GW": "XOF",

#     # Zone XAF
#     "CM": "XAF",
#     "GA": "XAF",
#     "TD": "XAF",
#     "CG": "XAF",
#     "CF": "XAF",
#     "GQ": "XAF",

#     # Europe
#     "FR": "EUR",
#     "BE": "EUR",
#     "DE": "EUR",
#     "ES": "EUR",
#     "IT": "EUR",
#     "NL": "EUR",

#     # Amérique
#     "US": "USD",
#     "CA": "USD",

#     # Royaume-Uni
#     "GB": "GBP",
# }
# COUNTRY_CURRENCY_MAP: dict[str, str] = getattr(
#     settings, "COUNTRY_CURRENCY_MAP", DEFAULT_COUNTRY_CURRENCY_MAP
# )

# # Symboles
# DEFAULT_SYMBOLS = {
#     "EUR": "€",
#     "USD": "$",
#     "GBP": "£",
#     "XOF": "FCFA",
#     "XAF": "FCFA",
# }
# CURRENCY_SYMBOLS: dict[str, str] = getattr(settings, "CURRENCY_SYMBOLS", DEFAULT_SYMBOLS)

# # Décimales par devise (souvent 0 pour XOF/XAF)
# DEFAULT_DECIMALS = {
#     "XOF": 0,
#     "XAF": 0,
#     "EUR": 2,
#     "USD": 2,
#     "GBP": 2,
# }
# CURRENCY_DECIMALS: dict[str, int] = getattr(settings, "CURRENCY_DECIMALS", DEFAULT_DECIMALS)

# # Format “FR” par défaut (12 345,67). Surcharge possible.
# THOUSANDS_SEP: str = getattr(settings, "MONEY_THOUSANDS_SEP", " ")
# DECIMAL_SEP: str = getattr(settings, "MONEY_DECIMAL_SEP", ",")

# # Session / query params (surcharge possible)
# SESSION_KEY: str = getattr(settings, "ECOMMERCE_CURRENCY_SESSION_KEY", "ECOMMERCE_CURRENCY")
# QUERY_PARAM: str = getattr(settings, "ECOMMERCE_CURRENCY_QUERY_PARAM", "currency")


# # =====================================================
# # DATA / HELPERS
# # =====================================================

# @dataclass(frozen=True)
# class MoneyParts:
#     number: str
#     symbol: str
#     currency: str
#     formatted: str


# def _normalize_currency(code: Any) -> str | None:
#     if code is None:
#         return None
#     c = str(code).strip().upper()
#     return c or None


# def _normalize_amount(amount: Any) -> Decimal | None:
#     """Sécurise et normalise un montant (str/int/float/Decimal)."""
#     if amount is None:
#         return None
#     try:
#         return Decimal(str(amount))
#     except (InvalidOperation, TypeError, ValueError):
#         return None


# @lru_cache(maxsize=128)
# def _decimals_for(currency: str) -> int:
#     return int(CURRENCY_DECIMALS.get(currency, 2))


# @lru_cache(maxsize=128)
# def _symbol_for(currency: str) -> str:
#     return str(CURRENCY_SYMBOLS.get(currency, currency))


# def _quantize(amount: Decimal, currency: str) -> Decimal:
#     """Arrondit selon la devise (ex: XOF => 0 décimales)."""
#     d = _decimals_for(currency)
#     q = Decimal("1") if d == 0 else Decimal("1").scaleb(-d)  # 1 or 0.01 / 0.001 ...
#     try:
#         return amount.quantize(q, rounding=ROUND_HALF_UP)
#     except Exception:
#         return amount


# def _format_number(amount: Decimal, currency: str) -> str:
#     """
#     Format FR: 12 345,67 (ou sans décimales si devise à 0).
#     """
#     d = _decimals_for(currency)
#     if d == 0:
#         # pas de décimales
#         s = f"{amount:,.0f}"
#         return s.replace(",", THOUSANDS_SEP)

#     s = f"{amount:,.{d}f}"
#     # python => "12,345.67"
#     s = s.replace(",", "§")          # temp thousands
#     s = s.replace(".", DECIMAL_SEP)  # decimal
#     s = s.replace("§", THOUSANDS_SEP)
#     return s


# def _detect_country_code_from_request(request) -> str | None:
#     """
#     Détection tolérante :
#     - session 'country_code'
#     - attribut request.COUNTRY_CODE (middleware geo)
#     - profil utilisateur (si disponible)
#     """
#     if not request:
#         return None

#     country_code = request.session.get("country_code") or getattr(request, "COUNTRY_CODE", None)
#     if country_code:
#         return str(country_code).strip().upper()

#     user = getattr(request, "user", None)
#     if user and getattr(user, "is_authenticated", False):
#         profile = getattr(user, "profile", None)
#         if profile:
#             country = getattr(profile, "country", None)
#             if country:
#                 code = getattr(country, "code", None)
#                 if code:
#                     return str(code).strip().upper()
#                 return str(country).strip().upper()

#     return None


# def _detect_currency_from_context(context, explicit_currency: Any = None) -> str:
#     """
#     Ordre de priorité (prod-friendly) :
#     1) explicit_currency (template)
#     2) GET ?currency=XXX
#     3) session ECOMMERCE_CURRENCY
#     4) mapping country_code -> currency
#     5) DEFAULT_CURRENCY
#     """
#     c = _normalize_currency(explicit_currency)
#     if c:
#         return c

#     request = context.get("request")
#     if request:
#         # GET param (utile pour switcher sans casser les pages)
#         try:
#             q = request.GET.get(QUERY_PARAM)
#         except Exception:
#             q = None
#         c = _normalize_currency(q)
#         if c:
#             return c

#         # Session
#         try:
#             session_currency = request.session.get(SESSION_KEY)
#         except Exception:
#             session_currency = None
#         c = _normalize_currency(session_currency)
#         if c:
#             return c

#         # Country mapping
#         cc = _detect_country_code_from_request(request)
#         if cc:
#             return COUNTRY_CURRENCY_MAP.get(cc, DEFAULT_CURRENCY)

#     return DEFAULT_CURRENCY


# def _rate_for(currency: str) -> Decimal | None:
#     raw = CURRENCY_RATES.get(currency)
#     if raw is None:
#         return None
#     try:
#         return Decimal(str(raw))
#     except (InvalidOperation, TypeError, ValueError):
#         return None


# def _convert_from_base(amount: Decimal, target_currency: str) -> Decimal:
#     """
#     Convertit un montant depuis BASE_CURRENCY -> target_currency.
#     Si pas de taux => retourne montant tel quel.
#     """
#     target_currency = _normalize_currency(target_currency) or DEFAULT_CURRENCY

#     if target_currency == BASE_CURRENCY:
#         return amount

#     rate = _rate_for(target_currency)
#     if rate is None:
#         return amount

#     try:
#         return amount * rate
#     except Exception:
#         return amount


# def _format_money(amount: Decimal, currency: str) -> str:
#     amount_q = _quantize(amount, currency)
#     number = _format_number(amount_q, currency)
#     symbol = _symbol_for(currency)
#     return f"{number} {symbol}".strip()


# # =====================================================
# # TAGS / FILTERS
# # =====================================================

# @register.simple_tag(takes_context=True, name="money")
# def money(context, amount, currency_code=None):
#     """
#     Usage :
#         {% load money %}
#         {% money product.price %}
#         {% money product.price "EUR" %}
#     """
#     amount_dec = _normalize_amount(amount)
#     if amount_dec is None:
#         return ""

#     currency = _detect_currency_from_context(context, currency_code)
#     converted = _convert_from_base(amount_dec, currency)
#     return _format_money(converted, currency)


# @register.simple_tag(takes_context=True, name="money_parts")
# def money_parts(context, amount, currency_code=None):
#     """
#     Usage :
#         {% money_parts product.price as p %}
#         {{ p.number }} {{ p.symbol }}
#     """
#     amount_dec = _normalize_amount(amount)
#     if amount_dec is None:
#         return {
#             "number": "",
#             "symbol": "",
#             "currency": "",
#             "formatted": "",
#         }

#     currency = _detect_currency_from_context(context, currency_code)
#     converted = _convert_from_base(amount_dec, currency)
#     converted_q = _quantize(converted, currency)

#     number = _format_number(converted_q, currency)
#     symbol = _symbol_for(currency)

#     return {
#         "number": number,
#         "symbol": symbol,
#         "currency": currency,
#         "formatted": f"{number} {symbol}".strip(),
#     }


# @register.filter(name="moneyf")
# def money_filter(amount, currency_code: str | None = None) -> str:
#     """
#     Filter optionnel (pratique dans certains templates):
#         {{ product.price|moneyf }}
#         {{ product.price|moneyf:"EUR" }}
#     """
#     a = _normalize_amount(amount)
#     if a is None:
#         return ""

#     currency = _normalize_currency(currency_code) or DEFAULT_CURRENCY
#     converted = _convert_from_base(a, currency)
#     return _format_money(converted, currency)





# # economic/ecommerce/templatetags/money.py
# from decimal import Decimal, InvalidOperation

# from django import template
# from django.conf import settings

# register = template.Library()

# # =====================================================
# # CONFIG PAR DÉFAUT (surchargable via settings)
# # =====================================================

# # Devise dans laquelle les prix sont stockés en base
# BASE_CURRENCY = getattr(settings, "BASE_CURRENCY", "XOF")

# # Devise par défaut
# DEFAULT_CURRENCY = getattr(settings, "DEFAULT_CURRENCY", BASE_CURRENCY)

# # Taux de change par rapport à BASE_CURRENCY
# # Clé = devise cible, valeur = combien vaut 1 BASE_CURRENCY dans cette devise
# DEFAULT_RATES = {
#     "XOF": Decimal("1"),        # 1 XOF = 1 XOF
#     "EUR": Decimal("0.0015"),   # EXEMPLES, à adapter
#     "USD": Decimal("0.0016"),
# }

# CURRENCY_RATES = getattr(settings, "CURRENCY_RATES", DEFAULT_RATES)

# # Pays -> devise
# DEFAULT_COUNTRY_CURRENCY_MAP = {
#     "SN": "XOF",  # Sénégal
#     "CI": "XOF",
#     "BJ": "XOF",
#     "BF": "XOF",
#     "ML": "XOF",
#     "TG": "XOF",

#     "CM": "XAF",
#     "GA": "XAF",
#     "TD": "XAF",
#     "CG": "XAF",

#     "FR": "EUR",
#     "BE": "EUR",
#     "DE": "EUR",

#     "US": "USD",
#     "CA": "USD",
#     "GB": "USD",  # UK => GBP normalement (si tu veux, on corrige plus tard)
# }

# COUNTRY_CURRENCY_MAP = getattr(
#     settings,
#     "COUNTRY_CURRENCY_MAP",
#     DEFAULT_COUNTRY_CURRENCY_MAP,
# )

# # Symboles
# DEFAULT_SYMBOLS = {
#     "EUR": "€",
#     "USD": "$",
#     "XOF": "FCFA",
#     "XAF": "FCFA",
# }

# CURRENCY_SYMBOLS = getattr(settings, "CURRENCY_SYMBOLS", DEFAULT_SYMBOLS)


# # =====================================================
# # FONCTIONS UTILITAIRES
# # =====================================================

# def _detect_currency_from_context(context, explicit_currency=None):
#     """
#     1. Si explicit_currency est fourni -> on l'utilise.
#     2. Sinon on regarde d'abord la session ECOMMERCE_CURRENCY
#        (panneau langue/devise e-commerce).
#     3. Sinon on déduit le pays :
#        - user.profile.country
#        - ou request.session['country_code']
#        - ou request.COUNTRY_CODE
#     4. Sinon DEFAULT_CURRENCY.
#     """
#     # 1️⃣ Devise forcée dans le template : {% money price "EUR" %}
#     if explicit_currency:
#         return explicit_currency

#     request = context.get("request")
#     country_code = None

#     if request is not None:
#         # 2️⃣ Devise choisie dans le panneau e-commerce
#         session_currency = request.session.get("ECOMMERCE_CURRENCY")
#         if session_currency:
#             return session_currency

#         # 3️⃣ Fallback : déduction par pays
#         user = getattr(request, "user", None)

#         # Profil utilisateur avec champ country (CountryField)
#         if user is not None and getattr(user, "is_authenticated", False):
#             profile = getattr(user, "profile", None)
#             if profile is not None:
#                 country = getattr(profile, "country", None)
#                 if country:
#                     country_code = getattr(country, "code", None) or str(country)

#         # Fallback : session ou attribut sur la requête
#         if not country_code:
#             country_code = (
#                 request.session.get("country_code")
#                 or getattr(request, "COUNTRY_CODE", None)
#             )

#     # 4️⃣ Pas de pays → devise par défaut
#     if not country_code:
#         return DEFAULT_CURRENCY

#     return COUNTRY_CURRENCY_MAP.get(country_code, DEFAULT_CURRENCY)


# def _convert_from_base(amount: Decimal, target_currency: str) -> Decimal:
#     """
#     Convertit amount depuis BASE_CURRENCY vers target_currency
#     selon CURRENCY_RATES.
#     """
#     if target_currency == BASE_CURRENCY:
#         return amount

#     rate = CURRENCY_RATES.get(target_currency)
#     if rate is None:
#         return amount

#     try:
#         rate = Decimal(str(rate))
#     except (InvalidOperation, TypeError, ValueError):
#         return amount

#     return amount * rate


# def _format_number_fr(amount: Decimal) -> str:
#     # format FR : 12 345,67
#     return f"{amount:,.2f}".replace(",", " ").replace(".", ",")


# def _symbol_for(currency: str) -> str:
#     return CURRENCY_SYMBOLS.get(currency, currency)


# def _format_money(amount: Decimal, currency: str) -> str:
#     symbol = _symbol_for(currency)
#     formatted = _format_number_fr(amount)
#     return f"{formatted} {symbol}"


# def _normalize_amount(amount) -> Decimal | None:
#     if amount is None:
#         return None
#     try:
#         return Decimal(str(amount))
#     except (InvalidOperation, TypeError, ValueError):
#         return None


# # =====================================================
# # TAG PRINCIPAL
# # =====================================================

# @register.simple_tag(takes_context=True, name="money")
# def money(context, amount, currency_code=None):
#     """
#     Usage dans les templates :

#         {% load money %}

#         {% money product.price %}          # devise auto (session -> pays)
#         {% money product.price "EUR" %}    # force EUR

#     Hypothèse : price est stocké en BASE_CURRENCY.
#     """
#     amount_dec = _normalize_amount(amount)
#     if amount_dec is None:
#         return ""

#     currency = _detect_currency_from_context(context, currency_code)
#     converted = _convert_from_base(amount_dec, currency)
#     return _format_money(converted, currency)


# @register.simple_tag(takes_context=True, name="money_parts")
# def money_parts(context, amount, currency_code=None):
#     """
#     Renvoie un dict exploitable dans le template :
#       - number: '150 000,00'
#       - symbol: 'FCFA'
#       - currency: 'XOF'
#       - formatted: '150 000,00 FCFA'

#     Exemple :
#       {% money_parts product.price as p %}
#       <span>{{ p.number }}</span> <span>{{ p.symbol }}</span>
#     """
#     amount_dec = _normalize_amount(amount)
#     if amount_dec is None:
#         return {"number": "", "symbol": "", "currency": "", "formatted": ""}

#     currency = _detect_currency_from_context(context, currency_code)
#     converted = _convert_from_base(amount_dec, currency)
#     number = _format_number_fr(converted)
#     symbol = _symbol_for(currency)
#     return {
#         "number": number,
#         "symbol": symbol,
#         "currency": currency,
#         "formatted": f"{number} {symbol}",
#     }





# # economic/ecommerce/templatetags/money.py
# from decimal import Decimal, InvalidOperation

# from django import template
# from django.conf import settings

# register = template.Library()

# # =====================================================
# # CONFIG PAR DÉFAUT (surchargable via settings)
# # =====================================================

# # Devise dans laquelle les prix sont stockés en base
# BASE_CURRENCY = getattr(settings, "BASE_CURRENCY", "XOF")

# # Devise par défaut
# DEFAULT_CURRENCY = getattr(settings, "DEFAULT_CURRENCY", BASE_CURRENCY)

# # Taux de change par rapport à BASE_CURRENCY
# # Clé = devise cible, valeur = combien vaut 1 BASE_CURRENCY dans cette devise
# DEFAULT_RATES = {
#     "XOF": Decimal("1"),        # 1 XOF = 1 XOF
#     "EUR": Decimal("0.0015"),   # EXEMPLES, à adapter
#     "USD": Decimal("0.0016"),
# }

# CURRENCY_RATES = getattr(settings, "CURRENCY_RATES", DEFAULT_RATES)

# # Pays -> devise
# DEFAULT_COUNTRY_CURRENCY_MAP = {
#     "SN": "XOF",  # Sénégal
#     "CI": "XOF",
#     "BJ": "XOF",
#     "BF": "XOF",
#     "ML": "XOF",
#     "TG": "XOF",

#     "CM": "XAF",
#     "GA": "XAF",
#     "TD": "XAF",
#     "CG": "XAF",

#     "FR": "EUR",
#     "BE": "EUR",
#     "DE": "EUR",

#     "US": "USD",
#     "CA": "USD",  
#     "GB": "USD", #UK GBP
# }


# COUNTRY_CURRENCY_MAP = getattr(
#     settings,
#     "COUNTRY_CURRENCY_MAP",
#     DEFAULT_COUNTRY_CURRENCY_MAP,
# )

# # Symboles
# DEFAULT_SYMBOLS = {
#     "EUR": "€",
#     "USD": "$",
#     "XOF": "FCFA",
#     "XAF": "FCFA",
# }

# CURRENCY_SYMBOLS = getattr(settings, "CURRENCY_SYMBOLS", DEFAULT_SYMBOLS)


# # =====================================================
# # FONCTIONS UTILITAIRES
# # =====================================================

# def _detect_currency_from_context(context, explicit_currency=None):
#     """
#     1. Si explicit_currency est fourni -> on l'utilise.
#     2. Sinon on regarde d'abord la session ECOMMERCE_CURRENCY
#        (panneau langue/devise e-commerce).
#     3. Sinon on déduit le pays :
#        - user.profile.country
#        - ou request.session['country_code']
#        - ou request.COUNTRY_CODE
#     4. Sinon DEFAULT_CURRENCY.
#     """
#     # 1️⃣ Devise forcée dans le template : {% money price "EUR" %}
#     if explicit_currency:
#         return explicit_currency

#     request = context.get("request")
#     country_code = None

#     if request is not None:
#         # 2️⃣ Devise choisie dans le panneau e-commerce
#         session_currency = request.session.get("ECOMMERCE_CURRENCY")
#         if session_currency:
#             return session_currency

#         # 3️⃣ Fallback : déduction par pays
#         user = getattr(request, "user", None)

#         # Profil utilisateur avec champ country (CountryField)
#         if user is not None and getattr(user, "is_authenticated", False):
#             profile = getattr(user, "profile", None)
#             if profile is not None:
#                 country = getattr(profile, "country", None)
#                 if country:
#                     country_code = getattr(country, "code", None) or str(country)

#         # Fallback : session ou attribut sur la requête
#         if not country_code:
#             country_code = (
#                 request.session.get("country_code")
#                 or getattr(request, "COUNTRY_CODE", None)
#             )

#     # 4️⃣ Pas de pays → devise par défaut
#     if not country_code:
#         return DEFAULT_CURRENCY

#     return COUNTRY_CURRENCY_MAP.get(country_code, DEFAULT_CURRENCY)


# def _convert_from_base(amount: Decimal, target_currency: str) -> Decimal:
#     """
#     Convertit amount depuis BASE_CURRENCY vers target_currency
#     selon CURRENCY_RATES.
#     """
#     if target_currency == BASE_CURRENCY:
#         return amount

#     rate = CURRENCY_RATES.get(target_currency)
#     if rate is None:
#         return amount

#     try:
#         rate = Decimal(str(rate))
#     except (InvalidOperation, TypeError, ValueError):
#         return amount

#     return amount * rate


# def _format_money(amount: Decimal, currency: str) -> str:
#     symbol = CURRENCY_SYMBOLS.get(currency, currency)
#     # format FR : 12 345,67
#     formatted = f"{amount:,.2f}".replace(",", " ").replace(".", ",")
#     return f"{formatted} {symbol}"


# # =====================================================
# # TAG PRINCIPAL
# # =====================================================

# @register.simple_tag(takes_context=True, name="money")
# def money(context, amount, currency_code=None):
#     """
#     Usage dans les templates :

#         {% load money %}

#         {% money product.price %}          # devise auto (session -> pays)
#         {% money product.price "EUR" %}    # force EUR

#     Hypothèse : price est stocké en BASE_CURRENCY.
#     """
#     if amount is None:
#         return ""

#     try:
#         amount_dec = Decimal(str(amount))
#     except (InvalidOperation, TypeError, ValueError):
#         return amount

#     currency = _detect_currency_from_context(context, currency_code)
#     converted = _convert_from_base(amount_dec, currency)
#     return _format_money(converted, currency)




# # economic/ecommerce/templatetags/money.py
# from decimal import Decimal, InvalidOperation

# from django import template
# from django.conf import settings

# register = template.Library()

# # =====================================================
# # CONFIG PAR DÉFAUT (tu peux surcharger dans settings)
# # =====================================================

# # Devise dans laquelle les prix sont stockés en base
# BASE_CURRENCY = getattr(settings, "BASE_CURRENCY", "XOF")

# # Devise par défaut si on ne détecte pas de pays
# DEFAULT_CURRENCY = getattr(settings, "DEFAULT_CURRENCY", BASE_CURRENCY)

# # Taux de change par rapport à BASE_CURRENCY
# # Clé = devise cible, valeur = combien vaut 1 BASE_CURRENCY dans cette devise
# DEFAULT_RATES = {
#     "XOF": Decimal("1"),        # 1 XOF = 1 XOF
#     "EUR": Decimal("0.0015"),   # EXEMPLES, à adapter
#     "USD": Decimal("0.0016"),
# }

# CURRENCY_RATES = getattr(settings, "CURRENCY_RATES", DEFAULT_RATES)

# # Pays -> devise
# DEFAULT_COUNTRY_CURRENCY_MAP = {
#     "SN": "XOF",  # Sénégal
#     "CI": "XOF",
#     "BJ": "XOF",
#     "BF": "XOF",
#     "ML": "XOF",
#     "TG": "XOF",
#     "FR": "EUR",
#     "US": "USD",
# }

# COUNTRY_CURRENCY_MAP = getattr(
#     settings,
#     "COUNTRY_CURRENCY_MAP",
#     DEFAULT_COUNTRY_CURRENCY_MAP,
# )

# # Symboles
# DEFAULT_SYMBOLS = {
#     "EUR": "€",
#     "USD": "$",
#     "XOF": "FCFA",
#     "XAF": "FCFA",
# }

# CURRENCY_SYMBOLS = getattr(settings, "CURRENCY_SYMBOLS", DEFAULT_SYMBOLS)


# # =====================================================
# # FONCTIONS UTILITAIRES
# # =====================================================

# def _detect_currency_from_context(context, explicit_currency=None):
#     """
#     1. Si explicit_currency est fourni -> on l'utilise.
#     2. Sinon on déduit le pays :
#        - user.profile.country
#        - ou request.session['country_code']
#        - ou request.COUNTRY_CODE
#     3. Sinon DEFAULT_CURRENCY.
#     """
#     if explicit_currency:
#         return explicit_currency

#     request = context.get("request")
#     country_code = None

#     if request is not None:
#         user = getattr(request, "user", None)

#         # Profil utilisateur avec champ country (CountryField)
#         if user is not None and getattr(user, "is_authenticated", False):
#             profile = getattr(user, "profile", None)
#             if profile is not None:
#                 country = getattr(profile, "country", None)
#                 if country:
#                     country_code = getattr(country, "code", None) or str(country)

#         # Fallback : session ou attribut sur la requête
#         if not country_code:
#             country_code = (
#                 request.session.get("country_code")
#                 or getattr(request, "COUNTRY_CODE", None)
#             )

#     if not country_code:
#         return DEFAULT_CURRENCY

#     return COUNTRY_CURRENCY_MAP.get(country_code, DEFAULT_CURRENCY)


# def _convert_from_base(amount: Decimal, target_currency: str) -> Decimal:
#     """
#     Convertit amount depuis BASE_CURRENCY vers target_currency
#     selon CURRENCY_RATES.
#     """
#     if target_currency == BASE_CURRENCY:
#         return amount

#     rate = CURRENCY_RATES.get(target_currency)
#     if rate is None:
#         return amount

#     try:
#         rate = Decimal(str(rate))
#     except (InvalidOperation, TypeError, ValueError):
#         return amount

#     return amount * rate


# def _format_money(amount: Decimal, currency: str) -> str:
#     symbol = CURRENCY_SYMBOLS.get(currency, currency)
#     formatted = f"{amount:,.2f}".replace(",", " ").replace(".", ",")
#     return f"{formatted} {symbol}"


# # =====================================================
# # TAG PRINCIPAL
# # =====================================================

# @register.simple_tag(takes_context=True)
# def money(context, amount, currency_code=None):
#     """
#     Usage dans les templates :

#         {% money product.price %}          # devise auto + conversion
#         {% money product.price "EUR" %}    # force EUR

#     Hypothèse : price est stocké en BASE_CURRENCY.
#     """
#     if amount is None:
#         return ""

#     try:
#         amount_dec = Decimal(str(amount))
#     except (InvalidOperation, TypeError, ValueError):
#         return amount

#     currency = _detect_currency_from_context(context, currency_code)
#     converted = _convert_from_base(amount_dec, currency)
#     return _format_money(converted, currency)





# # economic/templatetags/money.py
# from django import template

# register = template.Library()

# @register.filter
# def money(amount, currency="EUR"):
#     if amount is None:
#         return ""

#     symbols = {
#         "EUR": "€",
#         "USD": "$",
#         "XOF": "FCFA",
#         "XAF": "FCFA",
#     }

#     symbol = symbols.get(currency, currency)

#     try:
#         amount = float(amount)
#     except (TypeError, ValueError):
#         return amount

#     # Format: 12 345,67
#     formatted = f"{amount:,.2f}".replace(",", " ").replace(".", ",")

#     return f"{formatted} {symbol}"
