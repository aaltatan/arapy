"""Convert, parse and format numbers in Latin, Arabic-Indic and Persian digits."""

import re
from decimal import Decimal
from typing import Literal

from arapy._letters import (
    ARABIC_COMMA,
    ARABIC_DECIMAL_SEPARATOR,
    ARABIC_DIGITS,
    ARABIC_PERCENT,
    ARABIC_THOUSANDS_SEPARATOR,
    LATIN_DIGITS,
    PERSIAN_DIGITS,
)
from arapy.errors import InvalidNumberError

type DigitSet = Literal["latin", "arabic", "persian"]
type DecimalMark = Literal[".", ",", "،", "٫"]

_DIGITS: dict[DigitSet, str] = {
    "latin": LATIN_DIGITS,
    "arabic": ARABIC_DIGITS,
    "persian": PERSIAN_DIGITS,
}

# One translation table per target set; each maps every digit of every set to the target.
_TABLES = {
    name: {ord(d): target[i] for source in _DIGITS.values() for i, d in enumerate(source)}
    for name, target in _DIGITS.items()
}

# Grouped (one consistent separator, groups of three) or plain integer part.
_WHOLE = re.compile(r"[0-9]{1,3}(?:([,.٬])[0-9]{3})?(?:\1[0-9]{3})*|[0-9]+")
_FRACTION = re.compile(r"[0-9]+")


def to_latin_digits(text: str) -> str:
    """Replace Arabic-Indic and Persian digits with Latin digits."""
    return text.translate(_TABLES["latin"])


def to_arabic_digits(text: str) -> str:
    """Replace Latin and Persian digits with Arabic-Indic digits."""
    return text.translate(_TABLES["arabic"])


def to_persian_digits(text: str) -> str:
    """Replace Latin and Arabic-Indic digits with Persian digits."""
    return text.translate(_TABLES["persian"])


def parse_number(text: str, *, decimal: DecimalMark | None = None) -> Decimal:
    """Parse a number written in any digit set into an exact `Decimal`.

    `٬` is always a thousands separator and `٫` always a decimal mark. `,` `.` and `،` can be
    either, and when the text alone cannot tell (`"1,250"`), pass `decimal` to say which one
    is the decimal mark; otherwise `InvalidNumberError` is raised.
    """
    s = to_latin_digits(text.strip()).replace(ARABIC_COMMA, ",")

    sign = ""

    if s.startswith(("-", "−")):
        sign, s = "-", s[1:]

    elif s.startswith("+"):
        s = s[1:]

    mark = _guess_decimal(s, text) if decimal is None else decimal.replace(ARABIC_COMMA, ",")

    whole, sep, fraction = s.partition(mark) if mark else (s, "", "")

    if not _WHOLE.fullmatch(whole) or (sep and not _FRACTION.fullmatch(fraction)):
        raise InvalidNumberError(f"Not a valid number: {text!r}")

    digits = re.sub(r"[^0-9]", "", whole)

    return Decimal(f"{sign}{digits}.{fraction}" if sep else f"{sign}{digits}")


def _guess_decimal(s: str, text: str) -> str | None:
    """Return the decimal mark used in `s`, None if it has none, or raise if it is ambiguous."""
    if ARABIC_DECIMAL_SEPARATOR in s:
        return ARABIC_DECIMAL_SEPARATOR

    found = [c for c in ",." if c in s]

    if len(found) == 2:
        return max(found, key=s.rindex)

    if not found:
        return None

    mark = found[0]

    if ARABIC_THOUSANDS_SEPARATOR in s:
        return mark

    if s.count(mark) > 1:
        return None

    if len(s) - s.index(mark) - 1 == 3:
        raise InvalidNumberError(
            f"Ambiguous number {text!r}: {mark!r} may be a decimal mark or a thousands "
            "separator. Pass decimal=... to say which."
        )

    return mark


def format_number(
    value: int | Decimal | str,
    *,
    digits: DigitSet = "latin",
    grouping: str | None = ",",
    decimal: str = ".",
    places: int | None = None,
) -> str:
    """Format a number with the given digit set, thousands separator and decimal mark.

    `places` pads the fraction to that many digits. A value with more significant decimal
    places raises `InvalidNumberError`: numbers are never rounded.
    """
    number = _to_decimal(value)

    pattern = "," if grouping else ""

    if places is not None:
        if _decimal_places(number) > places:
            raise InvalidNumberError(f"{value!r} has more than {places} decimal places")

        pattern += f".{places}"

    text = format(number, pattern + "f")

    text = text.translate({ord(","): grouping or "", ord("."): decimal})

    return text.translate(_TABLES[digits])


def format_percent(
    value: int | Decimal | str,
    *,
    digits: DigitSet = "latin",
    grouping: str | None = ",",
    decimal: str = ".",
    places: int | None = None,
) -> str:
    """Format a fraction as a percentage with the `٪` sign: `Decimal("0.25")` → `"25٪"`."""
    sign, number_digits, exponent = _to_decimal(value).as_tuple()

    assert isinstance(exponent, int)  # _to_decimal rejects NaN and infinity

    # Shift the exponent rather than multiply, so the result is exact at any precision.
    percent = Decimal((sign, number_digits, exponent + 2))

    text = format_number(percent, digits=digits, grouping=grouping, decimal=decimal, places=places)

    return text + ARABIC_PERCENT


def _to_decimal(value: int | Decimal | str) -> Decimal:
    number = parse_number(value) if isinstance(value, str) else Decimal(value)

    if not number.is_finite():
        raise InvalidNumberError(f"Not a finite number: {value!r}")

    return number


def _decimal_places(number: Decimal) -> int:
    """Count significant decimal places, ignoring trailing zeros: 1.50 → 1."""
    return len(format(number, "f").partition(".")[2].rstrip("0"))
