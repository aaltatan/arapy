"""`HijriDate`: an Umm al-Qura Hijri date with a `date`-like API. Needs `arapy[hijri]`."""

import dataclasses
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Self, overload

from arapy._extras import require
from arapy.dates.ardate import ArDate
from arapy.dates.formatting import check_date, date_fields, format_fields, parse_fields
from arapy.dates.months import HIJRI_MONTHS, WEEKDAYS
from arapy.digits import DigitSet
from arapy.errors import OutOfRangeError, ParseError

# %y is left out: a two-digit Hijri year cannot be read back.
_DIRECTIVES = "aAbBdmYjO"

_MONTH_NUMBERS = {name: i for i, name in enumerate(HIJRI_MONTHS, start=1)} | {
    "ربيع الثاني": 4,
    "جمادى الثانية": 6,
}


def _to_ordinal(year: int, month: int, day: int) -> int:
    hijridate = require("hijri", "hijridate")

    try:
        return int(hijridate.Hijri(year, month, day).to_gregorian().toordinal())

    except (OverflowError, ValueError) as err:
        raise OutOfRangeError(f"Not a valid Hijri date {year}-{month}-{day}: {err}") from err


def _from_ordinal(n: int) -> tuple[int, int, int]:
    hijridate = require("hijri", "hijridate")

    g = date.fromordinal(n)

    try:
        h = hijridate.Gregorian(g.year, g.month, g.day).to_hijri()

    except OverflowError as err:
        raise OutOfRangeError(f"{g} is outside the Hijri calendar's range: {err}") from err

    return int(h.year), int(h.month), int(h.day)


@dataclass(frozen=True, slots=True, eq=False)
class HijriDate:
    """A Hijri date (Umm al-Qura, 1343–1500 AH). Compares and subtracts with `date` by day.

    ```python
    from arapy import HijriDate

    ramadan = HijriDate(1447, 9, 1)

    print(ramadan.format("%O من %B %Y هـ", digits="arabic"))  # الأول من رمضان ١٤٤٧ هـ
    print(ramadan.to_gregorian())  # 2026-02-18
    ```
    """

    year: int
    month: int
    day: int
    _ordinal: int = field(init=False, repr=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "_ordinal", _to_ordinal(self.year, self.month, self.day))

    @classmethod
    def fromordinal(cls, n: int) -> Self:
        return cls(*_from_ordinal(n))

    @classmethod
    def from_date(cls, d: date) -> Self:
        """The Hijri date of a `date` (or the date part of a `datetime`)."""
        return cls.fromordinal(d.toordinal())

    @classmethod
    def today(cls) -> Self:
        return cls.from_date(date.today())

    def toordinal(self) -> int:
        return self._ordinal

    def to_gregorian(self) -> ArDate:
        return ArDate.fromordinal(self._ordinal)

    def weekday(self) -> int:
        """Monday = 0 … Sunday = 6, as in `date.weekday()`."""
        return (self._ordinal - 1) % 7

    def isoweekday(self) -> int:
        return self.weekday() + 1

    def isoformat(self) -> str:
        return f"{self.year:04d}-{self.month:02d}-{self.day:02d}"

    __str__ = isoformat

    def replace(
        self, *, year: int | None = None, month: int | None = None, day: int | None = None
    ) -> Self:
        return dataclasses.replace(
            self,
            year=self.year if year is None else year,
            month=self.month if month is None else month,
            day=self.day if day is None else day,
        )

    @property
    def weekday_name(self) -> str:
        """«الاثنين» … «الأحد»."""
        return WEEKDAYS[self.weekday()]

    def month_name(self) -> str:
        """«محرم» … «ذو الحجة»."""
        return HIJRI_MONTHS[self.month - 1]

    def format(self, fmt: str, *, digits: DigitSet = "latin") -> str:
        """Format with Arabic names: %a %A %b %B %d %m %Y %j %O %%."""
        fields = date_fields(
            year=self.year,
            month=self.month,
            day=self.day,
            weekday=self.weekday(),
            yday=self._ordinal - _to_ordinal(self.year, 1, 1) + 1,
            months=HIJRI_MONTHS,
            digits=digits,
        )

        del fields["y"]

        return format_fields(fmt, fields)

    @classmethod
    def strptime(cls, text: str, fmt: str) -> Self:
        """Strictly parse `text` written with `fmt`, in any digit set.

        Accepts ربيع الثاني and جمادى الثانية as well. Missing fields default to the first day of
        the year 1400, and a weekday or day of year that does not match raises `ParseError`.
        """
        fields = parse_fields(text, fmt, months=_MONTH_NUMBERS, directives=_DIRECTIVES)

        year = fields.get("year", 1400)

        try:
            if "yday" in fields and "month" not in fields and "day" not in fields:
                result = cls.fromordinal(_to_ordinal(year, 1, 1) + fields["yday"] - 1)

            else:
                result = cls(year, fields.get("month", 1), fields.get("day", 1))

        except OutOfRangeError as err:
            raise ParseError(f"{text!r} is not a valid Hijri date: {err}") from err

        yday = result._ordinal - _to_ordinal(result.year, 1, 1) + 1

        check_date(fields, text, year=result.year, yday=yday, weekday=result.weekday())

        return result

    def __add__(self, other: timedelta) -> Self:
        if not isinstance(other, timedelta):
            return NotImplemented

        return self.fromordinal(self._ordinal + other.days)

    __radd__ = __add__

    @overload
    def __sub__(self, other: timedelta) -> Self: ...

    @overload
    def __sub__(self, other: "HijriDate | date") -> timedelta: ...

    def __sub__(self, other: "timedelta | HijriDate | date") -> "Self | timedelta":
        if isinstance(other, timedelta):
            return self.fromordinal(self._ordinal - other.days)

        ordinal = _ordinal_of(other)

        if ordinal is None:
            return NotImplemented

        return timedelta(days=self._ordinal - ordinal)

    def __rsub__(self, other: date) -> timedelta:
        ordinal = _ordinal_of(other)

        if ordinal is None:
            return NotImplemented

        return timedelta(days=ordinal - self._ordinal)

    def __eq__(self, other: object) -> bool:
        ordinal = _ordinal_of(other)

        return NotImplemented if ordinal is None else self._ordinal == ordinal

    def __hash__(self) -> int:
        return hash(self.to_gregorian())  # equal to the `date` of the same day, so hash alike

    def __lt__(self, other: "HijriDate | date") -> bool:
        ordinal = _ordinal_of(other)

        return NotImplemented if ordinal is None else self._ordinal < ordinal

    def __le__(self, other: "HijriDate | date") -> bool:
        ordinal = _ordinal_of(other)

        return NotImplemented if ordinal is None else self._ordinal <= ordinal

    def __gt__(self, other: "HijriDate | date") -> bool:
        ordinal = _ordinal_of(other)

        return NotImplemented if ordinal is None else self._ordinal > ordinal

    def __ge__(self, other: "HijriDate | date") -> bool:
        ordinal = _ordinal_of(other)

        return NotImplemented if ordinal is None else self._ordinal >= ordinal


def _ordinal_of(other: object) -> int | None:
    """The day number of a `HijriDate` or plain `date`; None for anything else (`datetime`)."""
    if isinstance(other, HijriDate):
        return other.toordinal()

    if isinstance(other, date) and not isinstance(other, datetime):
        return other.toordinal()

    return None
