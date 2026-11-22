"""`ArDateTime`: a `datetime` with Arabic formatting and parsing."""

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Self, overload

from arapy.dates.ardate import parse_gregorian
from arapy.dates.formatting import (
    DATE_DIRECTIVES,
    TIME_DIRECTIVES,
    clock,
    date_fields,
    format_fields,
    time_fields,
)
from arapy.dates.months import MONTHS, WEEKDAYS, MonthNames
from arapy.digits import DigitSet
from arapy.errors import ParseError

if TYPE_CHECKING:
    from arapy.dates.hijri import HijriDate


class ArDateTime(datetime):
    """A `datetime` that formats and parses Arabic text.

    Like `ArDate`, arithmetic, `replace()` and the classmethods (`now`, `combine`, …) return the
    subclass, and `strftime()` and `format()`-protocol output are standard. `.format()` adds the
    time directives %H %I %M %S and %p (صباحًا / مساءً).

    >>> ArDateTime(2026, 1, 5, 14, 30).format("%I:%M %p", digits="arabic")
    '٠٢:٣٠ مساءً'
    """

    __slots__ = ()

    # typeshed types `datetime - datetime` only for the same class; accept any `datetime`.
    @overload  # type: ignore[override]
    def __sub__(self, other: timedelta, /) -> Self: ...

    @overload
    def __sub__(self, other: datetime, /) -> timedelta: ...

    def __sub__(self, other: timedelta | datetime, /) -> Self | timedelta:
        if isinstance(other, timedelta):
            return super().__sub__(other)

        plain: datetime = self  # call the base method with `Self` = datetime

        return datetime.__sub__(plain, other)

    @classmethod
    def from_datetime(cls, dt: datetime) -> Self:
        """Convert a plain `datetime`, keeping its time zone and `fold`."""
        return cls.combine(dt.date(), dt.timetz()).replace(fold=dt.fold)

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
        """Format with Arabic names: date directives, %O, and %H %I %M %S %p."""
        fields = date_fields(
            year=self.year,
            month=self.month,
            day=self.day,
            weekday=self.weekday(),
            yday=self.timetuple().tm_yday,
            months=MONTHS[months],
            digits=digits,
        )

        fields |= time_fields(hour=self.hour, minute=self.minute, second=self.second, digits=digits)

        return format_fields(fmt, fields)

    @classmethod
    def strptime(cls, text: str, fmt: str, *, months: MonthNames | None = None) -> Self:
        """Strictly parse `text` written with `fmt`, in any digit set.

        The rules are those of `ArDate.strptime`; missing time fields default to midnight.
        """
        d, fields = parse_gregorian(
            text, fmt, months=months, directives=DATE_DIRECTIVES + TIME_DIRECTIVES
        )

        try:
            return cls(d.year, d.month, d.day, *clock(fields, text))

        except ValueError as err:
            raise ParseError(f"{text!r} is not a valid time: {err}") from err

    def to_hijri(self) -> "HijriDate":
        """The date part in the Hijri (Umm al-Qura) calendar. Needs `arapy[hijri]`."""
        from arapy.dates.hijri import HijriDate

        return HijriDate.from_date(self)
