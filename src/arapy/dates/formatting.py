"""Format and strict-parse engine shared by the Arabic date types.

Supported directives: %a %A (weekday), %b %B (month name), %d, %m, %y, %Y, %j, %O (ordinal day:
الخامس) and %%. Any other directive raises `FormatError`.
"""

import re
from collections.abc import Callable, Mapping, Sequence

from arapy.dates.months import WEEKDAYS
from arapy.digits import DigitSet, to_arabic_digits, to_latin_digits, to_persian_digits
from arapy.errors import FormatError, ParseError
from arapy.ordinals import ordinal

_TO_DIGITS: Mapping[DigitSet, Callable[[str], str]] = {
    "latin": to_latin_digits,
    "arabic": to_arabic_digits,
    "persian": to_persian_digits,
}

_DIRECTIVE = re.compile(r"%(.?)", re.DOTALL)

_NUMERIC = {
    "d": "[0-9]{1,2}", "m": "[0-9]{1,2}", "y": "[0-9]{2}", "Y": "[0-9]{4}", "j": "[0-9]{1,3}",
}  # fmt: skip

# Directive → the field it sets.
_FIELD = {
    "d": "day", "O": "day", "m": "month", "b": "month", "B": "month",
    "y": "year", "Y": "year", "a": "weekday", "A": "weekday", "j": "yday",
}  # fmt: skip

_WEEKDAY_NUMBERS = {name: i for i, name in enumerate(WEEKDAYS)}

_ORDINAL_DAYS = {ordinal(day): day for day in range(1, 32)}


def date_fields(
    *,
    year: int,
    month: int,
    day: int,
    weekday: int,
    yday: int,
    months: Sequence[str],
    digits: DigitSet,
) -> dict[str, str]:
    """The text of every date directive. `weekday` is Monday = 0, `months` January first."""
    to_digits = _TO_DIGITS[digits]

    return {
        "a": WEEKDAYS[weekday],
        "A": WEEKDAYS[weekday],
        "b": months[month - 1],
        "B": months[month - 1],
        "d": to_digits(f"{day:02d}"),
        "m": to_digits(f"{month:02d}"),
        "y": to_digits(f"{year % 100:02d}"),
        "Y": to_digits(f"{year:04d}"),
        "j": to_digits(f"{yday:03d}"),
        "O": ordinal(day),
        "%": "%",
    }


def format_fields(fmt: str, fields: Mapping[str, str]) -> str:
    """Replace each directive in `fmt` with its text from `fields`."""

    def replace(match: re.Match[str]) -> str:
        directive = match.group(1)

        if directive not in fields:
            raise FormatError(f"Unsupported directive %{directive} in {fmt!r}")

        return fields[directive]

    return _DIRECTIVE.sub(replace, fmt)


def parse_date_fields(text: str, fmt: str, *, months: Mapping[str, int]) -> dict[str, int]:
    """Strictly match `text` against `fmt` and return the fields it sets.

    Keys are `year`, `month`, `day`, `weekday` (Monday = 0) and `yday`; only fields named in
    `fmt` are present. Digits may be in any digit set. Raises `ParseError` when the text does
    not match or a field is given twice with different values.
    """
    names: Mapping[str, Mapping[str, int]] = {
        "a": _WEEKDAY_NUMBERS,
        "A": _WEEKDAY_NUMBERS,
        "b": months,
        "B": months,
        "O": _ORDINAL_DAYS,
    }

    pattern, directives, pos = [], [], 0

    for match in _DIRECTIVE.finditer(fmt):
        pattern.append(re.escape(fmt[pos : match.start()]))

        pos = match.end()

        directive = match.group(1)

        if directive == "%":
            pattern.append("%")

        elif directive in _NUMERIC:
            pattern.append(f"({_NUMERIC[directive]})")

            directives.append(directive)

        elif directive in names:
            # Longest first, so «كانون الثاني (يناير)» wins over «كانون الثاني».
            choices = sorted(names[directive], key=len, reverse=True)
            pattern.append(f"({'|'.join(map(re.escape, choices))})")

            directives.append(directive)

        else:
            raise FormatError(f"Unsupported directive %{directive} in {fmt!r}")

    pattern.append(re.escape(fmt[pos:]))

    found = re.fullmatch("".join(pattern), to_latin_digits(text))

    if found is None:
        raise ParseError(f"{text!r} does not match the format {fmt!r}")

    fields: dict[str, int] = {}

    for directive, value in zip(directives, found.groups(), strict=True):
        number = names[directive][value] if directive in names else int(value)

        if directive == "y":
            number += 2000 if number < 69 else 1900  # the same pivot as time.strptime

        field = _FIELD[directive]

        if fields.setdefault(field, number) != number:
            raise ParseError(f"{text!r} gives two different values for the {field}")

    return fields
