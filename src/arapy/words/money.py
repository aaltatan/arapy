"""Amounts in digits with a currency symbol: «١٢٬٥٠٠ ل.س»."""

from decimal import Decimal

from arapy.digits import DigitSet, format_number, parse_number
from arapy.words.nouns import Currency


def format_money(
    value: int | Decimal | str,
    currency: Currency,
    *,
    digits: DigitSet = "arabic",
    grouping: str | None = "٬",
    decimal: str = "٫",
    places: int | None = None,
) -> str:
    """Format an amount with the currency symbol (or its code when it has none).

    Without `places`, whole amounts show no decimals and others are padded to the subunit
    places (2, or 3 for 1000-subunit currencies). Amounts finer than that raise
    `InvalidNumberError`: money is never rounded.
    """
    if isinstance(value, str):
        number = parse_number(value, decimal="." if currency.ratio == 1000 else None)
    else:
        number = Decimal(value)

    if places is None:
        places = 0 if number == number.to_integral_value() else len(str(currency.ratio)) - 1

    text = format_number(number, digits=digits, grouping=grouping, decimal=decimal, places=places)
    return f"{text} {currency.symbol or currency.code}"
