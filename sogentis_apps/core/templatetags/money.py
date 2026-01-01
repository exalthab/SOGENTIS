# core/templatetags/money.py
from decimal import Decimal, InvalidOperation

from django import template
from django.conf import settings

register = template.Library()

# =====================================================
# CONFIG (surchargable via settings.py)
# =====================================================

BASE_CURRENCY = getattr(settings, "BASE_CURRENCY", "XOF")
DEFAULT_CURRENCY = getattr(settings, "DEFAULT_CURRENCY", getattr(settings, "ECOMMERCE_CURRENCY", BASE_CURRENCY))

DEFAULT_RATES = {
    "XOF": Decimal("1"),
    "EUR": Decimal("0.0015"),  # exemples
    "USD": Decimal("0.0016"),
    "XAF": Decimal("1"),
}
CURRENCY_RATES = getattr(settings, "CURRENCY_RATES", DEFAULT_RATES)

DEFAULT_COUNTRY_CURRENCY_MAP = {
    "SN": "XOF",
    "CI": "XOF",
    "BJ": "XOF",
    "BF": "XOF",
    "ML": "XOF",
    "TG": "XOF",

    "CM": "XAF",
    "GA": "XAF",
    "TD": "XAF",
    "CG": "XAF",

    "FR": "EUR",
    "BE": "EUR",
    "DE": "EUR",

    "US": "USD",
    "CA": "USD",  # ou CAD si tu gères CAD
    "GB": "USD",  # ou GBP si tu gères GBP
}
COUNTRY_CURRENCY_MAP = getattr(settings, "COUNTRY_CURRENCY_MAP", DEFAULT_COUNTRY_CURRENCY_MAP)

DEFAULT_SYMBOLS = {
    "EUR": "€",
    "USD": "$",
    "XOF": "FCFA",
    "XAF": "FCFA",
}
CURRENCY_SYMBOLS = getattr(settings, "CURRENCY_SYMBOLS", DEFAULT_SYMBOLS)


# =====================================================
# HELPERS
# =====================================================

def _to_decimal(amount) -> Decimal:
    if amount is None:
        return Decimal("0")
    if isinstance(amount, Decimal):
        return amount
    try:
        return Decimal(str(amount))
    except (InvalidOperation, TypeError, ValueError):
        return Decimal("0")


def _detect_currency(context, explicit_code=None) -> str:
    """
    Ordre:
    1) explicit_code (ex: {% money amount "EUR" %})
    2) request.session["ECOMMERCE_CURRENCY"]
    3) pays: user.profile.country / session country_code / request.COUNTRY_CODE
    4) settings.ECOMMERCE_CURRENCY
    5) DEFAULT_CURRENCY
    """
    if explicit_code:
        return explicit_code

    request = context.get("request")
    country_code = None

    if request is not None:
        # 2) session currency choisie via panneau
        session_cur = request.session.get("ECOMMERCE_CURRENCY")
        if session_cur:
            return session_cur

        # 3) déduction par pays
        user = getattr(request, "user", None)
        if user is not None and getattr(user, "is_authenticated", False):
            profile = getattr(user, "profile", None)
            if profile is not None:
                country = getattr(profile, "country", None)
                if country:
                    country_code = getattr(country, "code", None) or str(country)

        if not country_code:
            country_code = request.session.get("country_code") or getattr(request, "COUNTRY_CODE", None)

    if country_code:
        return COUNTRY_CURRENCY_MAP.get(country_code, getattr(settings, "ECOMMERCE_CURRENCY", DEFAULT_CURRENCY))

    return getattr(settings, "ECOMMERCE_CURRENCY", DEFAULT_CURRENCY)


def _convert_from_base(amount: Decimal, target_currency: str) -> Decimal:
    if target_currency == BASE_CURRENCY:
        return amount

    rate = CURRENCY_RATES.get(target_currency)
    if rate is None:
        return amount

    try:
        rate = Decimal(str(rate))
    except (InvalidOperation, TypeError, ValueError):
        return amount

    return amount * rate


def _format_money(amount: Decimal, currency_code: str) -> str:
    symbol = CURRENCY_SYMBOLS.get(currency_code, currency_code)
    formatted = f"{amount:,.2f}".replace(",", " ").replace(".", ",")
    return f"{formatted} {symbol}"


# =====================================================
# TEMPLATE API
# =====================================================

@register.simple_tag(takes_context=True, name="money")
def money_tag(context, amount, currency_code=None):
    amount_dec = _to_decimal(amount)
    code = _detect_currency(context, currency_code)
    converted = _convert_from_base(amount_dec, code)
    return _format_money(converted, code)


@register.filter(name="money")
def money_filter(amount, currency_code=None):
    """
    Attention: un filtre n'a pas accès au context.
    Donc: si tu veux la session currency -> utilise le tag {% money ... %}
    Sinon: ce filtre utilise currency_code ou settings.ECOMMERCE_CURRENCY.
    """
    amount_dec = _to_decimal(amount)
    code = currency_code or getattr(settings, "ECOMMERCE_CURRENCY", DEFAULT_CURRENCY)
    converted = _convert_from_base(amount_dec, code)
    return _format_money(converted, code)






# # core/templatetags/money.py
# from decimal import Decimal, InvalidOperation

# from django import template
# from django.conf import settings

# register = template.Library()

# CURRENCY_SYMBOLS = {
#     "XOF": "FCFA",
#     "EUR": "€",
# }


# def _normalize_amount(amount):
#     if amount is None:
#         return Decimal("0")
#     if isinstance(amount, Decimal):
#         return amount
#     try:
#         return Decimal(str(amount))
#     except (InvalidOperation, TypeError, ValueError):
#         return Decimal("0")


# def _get_currency_from_request(request, explicit_code=None):
#     """
#     1) code passé en argument
#     2) devise en session (ECOMMERCE_CURRENCY)
#     3) settings.ECOMMERCE_CURRENCY
#     4) XOF par défaut
#     """
#     if explicit_code:
#         return explicit_code

#     if request is not None:
#         code = request.session.get("ECOMMERCE_CURRENCY")
#         if code:
#             return code

#     return getattr(settings, "ECOMMERCE_CURRENCY", "XOF")


# def _format_money(amount, currency_code):
#     amount = _normalize_amount(amount)
#     code = currency_code or getattr(settings, "ECOMMERCE_CURRENCY", "XOF")
#     symbol = CURRENCY_SYMBOLS.get(code, code)
#     return f"{amount:,.2f} {symbol}"


# # ============================== #
# #  TAG : {% money amount %}      #
# # ============================== #
# @register.simple_tag(takes_context=True, name="money")
# def money_tag(context, amount, currency_code=None):
#     request = context.get("request")
#     code = _get_currency_from_request(request, currency_code)
#     return _format_money(amount, code)


# # ============================== #
# #  FILTRE : {{ amount|money }}   #
# # ============================== #
# @register.filter(name="money")
# def money_filter(amount, currency_code=None):
#     code = currency_code or getattr(settings, "ECOMMERCE_CURRENCY", "XOF")
#     return _format_money(amount, code)
