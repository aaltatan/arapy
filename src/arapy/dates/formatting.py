"""Format and strict-parse engine shared by the Arabic date types.

Date directives: %a %A (weekday), %b %B (month name), %d, %m, %y, %Y, %j, %O (ordinal day:
الخامس). Time directives: %H, %I, %M, %S, %p (صباحًا / مساءً). And %%. Each type passes the
directives it supports; any other raises `FormatError`.
"""

import re
from collections.abc import Callable, Mapping, Sequence

from arapy.dates.months import WEEKDAYS
from arapy.digits import DigitSet, to_arabic_digits, to_latin_digits, to_persian_digits
from arapy.errors import FormatError, ParseError
from arapy.ordinals import ordinal

DATE_DIRECTIVES = "aAbBdmyYjO"
TIME_DIRECTIVES = "HIMSp"

AM, PM = "صباحًا", "مساءً"

_TO_DIGITS: Mapping[DigitSet, Callable[[str], str]] = {
    "latin": to_latin_digits,
    "arabic": to_arabic_digits,
    "persian": to_persian_digits,
}

_DIRECTIVE = re.compile(r"%(.?)", re.DOTALL)

_TWO_DIGITS = "[0-9]{1,2}"

_NUMERIC = {
    "d": _TWO_DIGITS, "m": _TWO_DIGITS, "y": "[0-9]{2}", "Y": "[0-9]{4}", "j": "[0-9]{1,3}",
    "H": _TWO_DIGITS, "I": _TWO_DIGITS, "M": _TWO_DIGITS, "S": _TWO_DIGITS,
}  # fmt: skip

# Directive → the field it sets.
_FIELD = {
    "d": "day", "O": "day", "m": "month", "b": "month", "B": "month",
    "y": "year", "Y": "year", "a": "weekday", "A": "weekday", "j": "yday",
    "H": "hour", "I": "hour12", "M": "minute", "S": "second", "p": "pm",
}  # fmt: skip

_WEEKDAY_NUMBERS = {name: i for i, name in enumerate(WEEKDAYS)}

_ORDINAL_DAYS = {ordinal(day): day for day in range(1, 32)}

_HALVES = {AM: 0, PM: 1}


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


def time_fields(*, hour: int, minute: int, second: int, digits: DigitSet) -> dict[str, str]:
    """The text of every time directive."""
    to_digits = _TO_DIGITS[digits]

    return {
        "H": to_digits(f"{hour:02d}"),
        "I": to_digits(f"{hour % 12 or 12:02d}"),
        "M": to_digits(f"{minute:02d}"),
        "S": to_digits(f"{second:02d}"),
        "p": PM if hour >= 12 else AM,
    }


def format_fields(fmt: str, fields: Mapping[str, str]) -> str:
    """Replace each directive in `fmt` with its text from `fields`."""

    def replace(match: re.Match[str]) -> str:
        directive = match.group(1)

        if directive not in fields:
            raise FormatError(f"Unsupported directive %{directive} in {fmt!r}")

        return fields[directive]

    return _DIRECTIVE.sub(replace, fmt)


def parse_fields(
    text: str, fmt: str, *, months: Mapping[str, int], directives: str
) -> dict[str, int]:
    """Strictly match `text` against `fmt` and return the fields it sets.

    Keys are `year`, `month`, `day`, `weekday` (Monday = 0), `yday`, `hour`, `hour12`,
    `minute`, `second` and `pm` (0 or 1); only fields named in `fmt` are present. Digits may be
    in any digit set. Only `directives` (and %%) are allowed in `fmt`. Raises `ParseError` when
    the text does not match or a field is given twice with different values.
    """
    names: Mapping[str, Mapping[str, int]] = {
        "a": _WEEKDAY_NUMBERS,
        "A": _WEEKDAY_NUMBERS,
        "b": months,
        "B": months,
        "O": _ORDINAL_DAYS,
        "p": _HALVES,
    }

    pattern, found_directives, pos = [], [], 0

    for match in _DIRECTIVE.finditer(fmt):
        pattern.append(re.escape(fmt[pos : match.start()]))

        pos = match.end()

        directive = match.group(1)

        if directive == "%":
            pattern.append("%")

            continue

        if not directive or directive not in directives:
            raise FormatError(f"Unsupported directive %{directive} in {fmt!r}")

        if directive in _NUMERIC:
            pattern.append(f"({_NUMERIC[directive]})")

        else:
            # Longest first, so «كانون الثاني (يناير)» wins over «كانون الثاني».
            choices = sorted(names[directive], key=len, reverse=True)
            pattern.append(f"({'|'.join(map(re.escape, choices))})")

        found_directives.append(directive)

    pattern.append(re.escape(fmt[pos:]))

    found = re.fullmatch("".join(pattern), to_latin_digits(text))

    if found is None:
        raise ParseError(f"{text!r} does not match the format {fmt!r}")

    fields: dict[str, int] = {}

    for directive, value in zip(found_directives, found.groups(), strict=True):
        number = names[directive][value] if directive in names else int(value)

        if directive == "y":
            number += 2000 if number < 69 else 1900  # the same pivot as time.strptime

        field = _FIELD[directive]

        if fields.setdefault(field, number) != number:
            raise ParseError(f"{text!r} gives two different values for the {field}")

    return fields


def check_date(fields: Mapping[str, int], text: str, *, year: int, yday: int, weekday: int) -> None:
    """Raise `ParseError` if a parsed year, day of year or weekday disagrees with the date."""
    if fields.get("year", year) != year or fields.get("yday", yday) != yday:
        raise ParseError(f"{text!r}: the day of the year does not match the date")

    if fields.get("weekday", weekday) != weekday:
        raise ParseError(f"{text!r}: the weekday does not match the date")


def clock(fields: Mapping[str, int], text: str) -> tuple[int, int, int]:
    """(hour, minute, second) from parsed fields. %p without %I is ignored, as in strptime."""
    hour = fields.get("hour", 0)

    if "hour12" in fields:
        if not 1 <= fields["hour12"] <= 12:
            raise ParseError(f"{text!r}: %I must be 1–12")

        hour12 = fields["hour12"] % 12 + 12 * fields.get("pm", 0)

        if fields.get("hour", hour12) != hour12:
            raise ParseError(f"{text!r} gives two different values for the hour")

        hour = hour12

    return hour, fields.get("minute", 0), fields.get("second", 0)
