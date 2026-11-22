"""Relative times and durations in Arabic words: «منذ ثلاثة أيام», «سنة وثلاثة أشهر»."""

from datetime import datetime, timedelta
from typing import Protocol

from arapy.errors import InvalidNumberError
from arapy.words.grammar import Case
from arapy.words.nouns import Gender, Noun, PluralForm
from arapy.words.tafqeet import Tafqeet

_M, _F = Gender.MASCULINE, Gender.FEMININE

YEAR = Noun.create("سنة", "سنتان", "سنوات", gender=_F)
MONTH = Noun.create("شهر", "شهران", "أشهر", gender=_M)
WEEK = Noun.create("أسبوع", "أسبوعان", "أسابيع", gender=_M)
DAY = Noun.create("يوم", "يومان", "أيام", gender=_M)
HOUR = Noun.create("ساعة", "ساعتان", "ساعات", gender=_F)
MINUTE = Noun.create("دقيقة", "دقيقتان", "دقائق", gender=_F)
SECOND = Noun.create("ثانية", "ثانيتان", "ثوانٍ", gender=_F)


class RelativeDeltaLike(Protocol):
    """Anything with calendar fields, such as `dateutil.relativedelta.relativedelta`."""

    @property
    def years(self) -> int: ...

    @property
    def months(self) -> int: ...

    @property
    def days(self) -> int: ...

    @property
    def hours(self) -> int: ...

    @property
    def minutes(self) -> int: ...

    @property
    def seconds(self) -> int: ...


def ar_since(dt: datetime, now: datetime | None = None) -> str:
    """How long ago (or how far ahead) `dt` is, in its largest whole unit.

    «منذ ثلاثة أيام», «بعد شهرين», «منذ ثلاث ثوانٍ»; «الآن» when under one second. `now`
    defaults to the current time in `dt`'s time zone.
    """
    if now is None:
        now = datetime.now(dt.tzinfo)

    start, end = sorted((dt, now))

    months = (end.year - start.year) * 12 + end.month - start.month

    if (end.day, end.timetz()) < (start.day, start.timetz()):
        months -= 1  # the last month is not complete yet

    delta = end - start

    seconds = delta.seconds

    if months >= 12:
        n, unit = months // 12, YEAR

    elif months:
        n, unit = months, MONTH

    elif delta.days >= 7:
        n, unit = delta.days // 7, WEEK

    elif delta.days:
        n, unit = delta.days, DAY

    elif seconds >= 3600:
        n, unit = seconds // 3600, HOUR

    elif seconds >= 60:
        n, unit = seconds // 60, MINUTE

    elif seconds:
        n, unit = seconds, SECOND

    else:
        return "الآن"

    return ("بعد " if dt > now else "منذ ") + _count(n, unit, Case.GENITIVE)


def ar_duration(value: timedelta | RelativeDeltaLike) -> str:
    """A duration in words, largest unit first: «سنة وثلاثة أشهر», «أسبوعان ويومان».

    A `timedelta` has no months or years, so its days are split into weeks and days only.
    Zero is «صفر ثانية». Sub-second parts are ignored; negative parts raise.
    """
    if isinstance(value, timedelta):
        if value < timedelta(0):
            raise InvalidNumberError(f"A duration cannot be negative: {value!r}")

        years, months, days = 0, 0, value.days
        hours, rest = divmod(value.seconds, 3600)
        minutes, seconds = divmod(rest, 60)

    else:
        years, months, days = value.years, value.months, value.days
        hours, minutes, seconds = value.hours, value.minutes, value.seconds

    weeks, days = divmod(days, 7)

    amounts = (years, months, weeks, days, hours, minutes, seconds)

    if any(n < 0 for n in amounts):
        raise InvalidNumberError(f"A duration cannot be negative: {value!r}")

    units = (YEAR, MONTH, WEEK, DAY, HOUR, MINUTE, SECOND)

    parts = [_count(n, unit, Case.NOMINATIVE) for n, unit in zip(amounts, units, strict=True) if n]

    return " و".join(parts) or _count(0, SECOND, Case.NOMINATIVE)


def _count(n: int, unit: Noun, case: Case) -> str:
    """Like `Tafqeet`, but exactly one is the bare noun: «سنة», not «سنة واحدة»."""
    if n == 1:
        return unit.form(PluralForm.ONE)

    return Tafqeet(case=case)(n, unit)
