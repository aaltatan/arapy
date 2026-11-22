"""`ArDate`: a `date` with Arabic formatting and parsing."""

from datetime import date, datetime, timedelta
from typing import TYPE_CHECKING, NoReturn, Self, overload

from arapy.dates.formatting import (
    DATE_DIRECTIVES,
    check_date,
    date_fields,
    format_fields,
    parse_fields,
)
from arapy.dates.months import MONTHS, WEEKDAYS, MonthNames, month_numbers
from arapy.digits import DigitSet
from arapy.errors import ParseError

if TYPE_CHECKING:
    from arapy.dates.hijri import HijriDate


class ArDate(date):
    """A `date` that formats and parses Arabic text.

    Arithmetic, `replace()` and the classmethods (`today`, `fromisoformat`, …) already return
    the subclass in the standard library, so the result stays an `ArDate`; `date - date` is still
    a `timedelta`. `strftime()` and `format()`-protocol output are standard.

    ```python
    from arapy import ArDate

    d = ArDate(2026, 1, 5)

    print(d.format("%O من %B %Y", digits="arabic"))  # الخامس من كانون الثاني ٢٠٢٦
    ```
    """

    __slots__ = ()

    # typeshed types `date - date` only for the same class; also accept a plain `date`.
    @overload  # type: ignore[override]
    def __sub__(self, other: datetime, /) -> NoReturn: ...

    @overload
    def __sub__(self, other: timedelta, /) -> Self: ...

    @overload
    def __sub__(self, other: date, /) -> timedelta: ...

    def __sub__(self, other: timedelta | date, /) -> Self | timedelta:
        if isinstance(other, timedelta):
            return super().__sub__(other)

        if isinstance(other, datetime):
            return NotImplemented

        return timedelta(days=self.toordinal() - other.toordinal())

    @classmethod
    def from_date(cls, d: date) -> Self:
        """Convert a plain `date` (or the date part of a `datetime`)."""
        return cls(d.year, d.month, d.day)

    @property
    def weekday_name(self) -> str:
        """«الاثنين» … «الأحد»."""
        return WEEKDAYS[self.weekday()]

    def month_name(self, style: MonthNames = MonthNames.LEVANT) -> str:
        """The month's name in `style`: «كانون الثاني», «يناير», …"""
        return MONTHS[style][self.month - 1]

    def format(
        self, fmt: str, *, months: MonthNames = MonthNames.LEVANT, digits: DigitSet = "latin"
    ) -> str:
        """Format with Arabic names: strftime date directives plus %O for the ordinal day."""
        fields = date_fields(
            year=self.year,
            month=self.month,
            day=self.day,
            weekday=self.weekday(),
            yday=self.timetuple().tm_yday,
            months=MONTHS[months],
            digits=digits,
        )

        return format_fields(fmt, fields)

    @classmethod
    def strptime(cls, text: str, fmt: str, *, months: MonthNames | None = None) -> Self:
        """Strictly parse `text` written with `fmt`, in any digit set.

        `months=None` accepts the month names of every style. Missing fields default to
        1900-01-01, as in `datetime.strptime`. A weekday or day of year that does not match the
        date raises `ParseError`.
        """
        d, _ = parse_gregorian(text, fmt, months=months, directives=DATE_DIRECTIVES)

        return cls.from_date(d)

    def to_hijri(self) -> "HijriDate":
        """The same day in the Hijri (Umm al-Qura) calendar. Needs `arapy[hijri]`."""
        from arapy.dates.hijri import HijriDate

        return HijriDate.from_date(self)


def parse_gregorian(
    text: str, fmt: str, *, months: MonthNames | None, directives: str
) -> tuple[date, dict[str, int]]:
    """Parse the date part of `text`; also return the parsed fields (for the time part)."""
    fields = parse_fields(text, fmt, months=month_numbers(months), directives=directives)

    year = fields.get("year", 1900)

    try:
        if "yday" in fields and "month" not in fields and "day" not in fields:
            result = date.fromordinal(date(year, 1, 1).toordinal() + fields["yday"] - 1)

        else:
            result = date(year, fields.get("month", 1), fields.get("day", 1))

    except (ValueError, OverflowError) as err:
        raise ParseError(f"{text!r} is not a valid date: {err}") from err

    check_date(
        fields, text, year=result.year, yday=result.timetuple().tm_yday, weekday=result.weekday()
    )

    return result, fields
