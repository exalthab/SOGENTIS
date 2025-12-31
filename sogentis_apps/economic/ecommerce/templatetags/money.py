from django import template

register = template.Library()

@register.filter
def money(amount, currency="EUR"):
    if amount is None:
        return ""

    symbols = {
        "EUR": "€",
        "USD": "$",
        "XOF": "FCFA",
        "XAF": "FCFA",
    }

    symbol = symbols.get(currency, currency)

    try:
        amount = float(amount)
    except (TypeError, ValueError):
        return amount

    # Format: 12 345,67
    formatted = f"{amount:,.2f}".replace(",", " ").replace(".", ",")

    return f"{formatted} {symbol}"
