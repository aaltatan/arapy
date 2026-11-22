from datetime import date, datetime, timedelta

import pytest
from hypothesis import given
from hypothesis import strategies as st

from arapy import FormatError, ParseError
from arapy.dates import ArDate, MonthNames
from arapy.digits import DigitSet

from . import golden_dates as G

type FormatArgs = tuple[int, int, int, str, MonthNames, DigitSet]


@pytest.mark.parametrize(("args", "expected"), G.FORMATS)
def test_format(args: FormatArgs, expected: str) -> None:
    year, month, day, fmt, months, digits = args

    assert ArDate(year, month, day).format(fmt, months=months, digits=digits) == expected


@pytest.mark.parametrize(
    ("args", "expected"), [row for row in G.FORMATS if "%Y" in row[0][3] or "%y" in row[0][3]]
)
def test_strptime_reads_golden_output(args: FormatArgs, expected: str) -> None:
    year, month, day, fmt, months, _ = args

    assert ArDate.strptime(expected, fmt) == date(year, month, day)

    assert ArDate.strptime(expected, fmt, months=months) == date(year, month, day)


def test_results_stay_ardate() -> None:
    d = ArDate(2026, 1, 31)

    for result in (
        d + timedelta(1),
        timedelta(1) + d,
        d - timedelta(1),
        d.replace(day=1),
        ArDate.today(),
        ArDate.fromisoformat("2026-01-05"),
        ArDate.fromordinal(1),
        ArDate.fromtimestamp(0),
        ArDate.from_date(datetime(2026, 1, 5, 10, 30)),
    ):
        assert type(result) is ArDate

    assert d - ArDate(2026, 1, 1) == timedelta(30)

    assert d - date(2026, 1, 1) == timedelta(30)

    with pytest.raises(TypeError):
        d - datetime(2026, 1, 1)


def test_standard_formatting_is_unchanged() -> None:
    d = ArDate(2026, 1, 5)

    assert d.strftime("%A %B") == "Monday January"

    assert f"{d:%d/%m/%Y}" == "05/01/2026"

    assert str(d) == "2026-01-05"


def test_names() -> None:
    d = ArDate(2026, 1, 5)

    assert d.weekday_name == "الاثنين"

    assert d.month_name() == "كانون الثاني"

    assert d.month_name(MonthNames.EGYPTIAN) == "يناير"


def test_strptime_accepts_any_digit_set_and_day_of_year() -> None:
    assert ArDate.strptime("٢٠٢٦-۰۱-05", "%Y-%m-%d") == date(2026, 1, 5)

    assert ArDate.strptime("032 2026", "%j %Y") == date(2026, 2, 1)

    assert ArDate.strptime("01/02/26", "%d/%m/%y") == date(2026, 2, 1)

    assert ArDate.strptime("01/02/70", "%d/%m/%y") == date(1970, 2, 1)

    assert ArDate.strptime("آذار", "%B") == date(1900, 3, 1)


@pytest.mark.parametrize(
    ("text", "fmt", "months"),
    [
        ("الثلاثاء 05 كانون الثاني 2026", "%A %d %B %Y", None),  # wrong weekday
        ("31 شباط 2026", "%d %B %Y", None),  # no such day
        ("05 يناير 2026", "%d %B %Y", MonthNames.LEVANT),  # wrong style
        ("05 كانون الثاني 2026 ", "%d %B %Y", None),  # trailing space
        ("05/01/2026", "%d-%m-%Y", None),
        ("05 01 2026 006", "%d %m %Y %j", None),  # day of year does not match
        ("366 2026", "%j %Y", None),  # past the end of the year
        ("05 06 2026 07", "%d %m %Y %m", None),  # two different months
        ("الخامس 06", "%O %d", None),  # two different days
    ],
)
def test_strptime_is_strict(text: str, fmt: str, months: MonthNames | None) -> None:
    with pytest.raises(ParseError):
        ArDate.strptime(text, fmt, months=months)


@pytest.mark.parametrize("fmt", ["%H:%M", "%d %", "%U"])
def test_unsupported_directives(fmt: str) -> None:
    with pytest.raises(FormatError):
        ArDate(2026, 1, 5).format(fmt)

    with pytest.raises(FormatError):
        ArDate.strptime("x", fmt)


_FORMATS = ["%Y-%m-%d", "%A %d %B %Y", "%O من %B %Y", "%a، %b %d، %Y", "%j/%Y", "%d%m%Y"]


@given(
    st.dates().map(ArDate.from_date),
    st.sampled_from(_FORMATS),
    st.sampled_from(MonthNames),
    st.sampled_from(["latin", "arabic", "persian"]),
)
def test_round_trip(d: ArDate, fmt: str, months: MonthNames, digits: DigitSet) -> None:
    assert ArDate.strptime(d.format(fmt, months=months, digits=digits), fmt) == d
