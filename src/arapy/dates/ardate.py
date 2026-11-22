"""`ArDate`: a `date` with Arabic formatting and parsing."""

from datetime import date, datetime, timedelta
from typing import NoReturn, Self, overload

from arapy.dates.formatting import date_fields, format_fields, parse_date_fields
from arapy.dates.months import MONTHS, WEEKDAYS, MonthNames, month_numbers
from arapy.digits import DigitSet
from arapy.errors import ParseError


class ArDate(date):
    """A `date` that formats and parses Arabic text.

    Arithmetic, `replace()` and the classmethods (`today`, `fromisoformat`, …) already return
    the subclass in the standard library, so the result stays an `ArDate`; `date - date` is still
    a `timedelta`. `strftime()` and `format()`-protocol output are standard.

    >>> ArDate(2026, 1, 5).format("%O من %B %Y", digits="arabic")
    'الخامس من كانون الثاني ٢٠٢٦'
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
        fields = parse_date_fields(text, fmt, months=month_numbers(months))

        year = fields.get("year", 1900)

        try:
            if "yday" in fields and "month" not in fields and "day" not in fields:
                result = cls.fromordinal(cls(year, 1, 1).toordinal() + fields["yday"] - 1)

            else:
                result = cls(year, fields.get("month", 1), fields.get("day", 1))

        except (ValueError, OverflowError) as err:
            raise ParseError(f"{text!r} is not a valid date: {err}") from err

        yday = result.timetuple().tm_yday

        if result.year != year or fields.get("yday", yday) != yday:
            raise ParseError(f"{text!r}: the day of the year does not match the date")

        if fields.get("weekday", result.weekday()) != result.weekday():
            raise ParseError(f"{text!r}: the weekday does not match the date")

        return result
