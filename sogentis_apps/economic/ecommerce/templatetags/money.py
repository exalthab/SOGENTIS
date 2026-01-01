# economic/templatetags/money.py
from decimal import Decimal, InvalidOperation

from django import template
from django.conf import settings

register = template.Library()

# =====================================================
# CONFIG PAR DÉFAUT (tu peux surcharger dans settings)
# =====================================================

# Devise dans laquelle les prix sont stockés en base
BASE_CURRENCY = getattr(settings, "BASE_CURRENCY", "XOF")

# Devise par défaut si on ne détecte pas de pays
DEFAULT_CURRENCY = getattr(settings, "DEFAULT_CURRENCY", BASE_CURRENCY)

# Taux de change par rapport à BASE_CURRENCY
# Clé = devise cible, valeur = combien vaut 1 BASE_CURRENCY dans cette devise
DEFAULT_RATES = {
    "XOF": Decimal("1"),        # 1 XOF = 1 XOF
    "EUR": Decimal("0.0015"),   # EXEMPLES, à adapter
    "USD": Decimal("0.0016"),
}

CURRENCY_RATES = getattr(settings, "CURRENCY_RATES", DEFAULT_RATES)

# Pays -> devise
DEFAULT_COUNTRY_CURRENCY_MAP = {
    "SN": "XOF",  # Sénégal
    "CI": "XOF",
    "BJ": "XOF",
    "BF": "XOF",
    "ML": "XOF",
    "TG": "XOF",
    "FR": "EUR",
    "US": "USD",
}

COUNTRY_CURRENCY_MAP = getattr(
    settings,
    "COUNTRY_CURRENCY_MAP",
    DEFAULT_COUNTRY_CURRENCY_MAP,
)

# Symboles
DEFAULT_SYMBOLS = {
    "EUR": "€",
    "USD": "$",
    "XOF": "FCFA",
    "XAF": "FCFA",
}

CURRENCY_SYMBOLS = getattr(settings, "CURRENCY_SYMBOLS", DEFAULT_SYMBOLS)


# =====================================================
# FONCTIONS UTILITAIRES
# =====================================================

def _detect_currency_from_context(context, explicit_currency=None):
    """
    1. Si explicit_currency est fourni -> on l'utilise.
    2. Sinon on déduit le pays :
       - user.profile.country
       - ou request.session['country_code']
       - ou request.COUNTRY_CODE
    3. Sinon DEFAULT_CURRENCY.
    """
    if explicit_currency:
        return explicit_currency

    request = context.get("request")
    country_code = None

    if request is not None:
        user = getattr(request, "user", None)

        # Profil utilisateur avec champ country (CountryField)
        if user is not None and getattr(user, "is_authenticated", False):
            profile = getattr(user, "profile", None)
            if profile is not None:
                country = getattr(profile, "country", None)
                if country:
                    country_code = getattr(country, "code", None) or str(country)

        # Fallback : session ou attribut sur la requête
        if not country_code:
            country_code = (
                request.session.get("country_code")
                or getattr(request, "COUNTRY_CODE", None)
            )

    if not country_code:
        return DEFAULT_CURRENCY

    return COUNTRY_CURRENCY_MAP.get(country_code, DEFAULT_CURRENCY)


def _convert_from_base(amount: Decimal, target_currency: str) -> Decimal:
    """
    Convertit amount depuis BASE_CURRENCY vers target_currency
    selon CURRENCY_RATES.
    """
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


def _format_money(amount: Decimal, currency: str) -> str:
    symbol = CURRENCY_SYMBOLS.get(currency, currency)
    formatted = f"{amount:,.2f}".replace(",", " ").replace(".", ",")
    return f"{formatted} {symbol}"


# =====================================================
# TAG PRINCIPAL
# =====================================================

@register.simple_tag(takes_context=True)
def money(context, amount, currency_code=None):
    """
    Usage dans les templates :

        {% money product.price %}          # devise auto + conversion
        {% money product.price "EUR" %}    # force EUR

    Hypothèse : price est stocké en BASE_CURRENCY.
    """
    if amount is None:
        return ""

    try:
        amount_dec = Decimal(str(amount))
    except (InvalidOperation, TypeError, ValueError):
        return amount

    currency = _detect_currency_from_context(context, currency_code)
    converted = _convert_from_base(amount_dec, currency)
    return _format_money(converted, currency)





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
