import sys
from datetime import date, datetime, timedelta

import pytest
from hypothesis import given
from hypothesis import strategies as st

from arapy import FormatError, MissingExtraError, OutOfRangeError, ParseError
from arapy.dates import ArDate, ArDateTime, HijriDate
from arapy.digits import DigitSet

from . import golden_phase8 as G


def test_missing_extra(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(sys.modules, "hijridate", None)  # makes the import fail

    with pytest.raises(MissingExtraError, match="hijri"):
        HijriDate(1447, 1, 1)


pytest.importorskip("hijridate")

_FIRST, _LAST = date(1924, 8, 1), date(2077, 11, 15)


@pytest.mark.parametrize(("gregorian", "hijri"), G.HIJRI_CONVERSIONS)
def test_conversion(gregorian: tuple[int, int, int], hijri: tuple[int, int, int]) -> None:
    g, h = date(*gregorian), HijriDate(*hijri)

    assert HijriDate.from_date(g) == h

    assert ArDate.from_date(g).to_hijri() == h

    assert ArDateTime(*gregorian, 12).to_hijri() == h

    assert h.to_gregorian() == g

    assert type(h.to_gregorian()) is ArDate


@pytest.mark.parametrize(("args", "expected"), G.HIJRI_FORMATS)
def test_format_and_parse(args: tuple[int, int, int, str, DigitSet], expected: str) -> None:
    *fields, fmt, digits = args

    h = HijriDate(*fields)

    assert h.format(fmt, digits=digits) == expected

    assert HijriDate.strptime(expected, fmt) == h


def test_strptime_accepts_alternative_month_names() -> None:
    assert HijriDate.strptime("1 ربيع الثاني 1447", "%d %B %Y") == HijriDate(1447, 4, 1)

    assert HijriDate.strptime("1 جمادى الثانية 1447", "%d %B %Y") == HijriDate(1447, 6, 1)

    assert HijriDate.strptime("٠٠١ ١٤٤٧", "%j %Y") == HijriDate(1447, 1, 1)


@pytest.mark.parametrize(
    ("text", "fmt"),
    [
        ("30 صفر 1447", "%d %B %Y"),  # صفر 1447 has 29 days
        ("1 محرم 1600", "%d %B %Y"),  # outside Umm al-Qura
        ("الاثنين 01 رمضان 1447", "%A %d %B %Y"),  # 1 Ramadan 1447 is a Wednesday
        ("1 رمضان 1447", "%d %B %y"),
    ],
)
def test_strptime_is_strict(text: str, fmt: str) -> None:
    with pytest.raises((ParseError, FormatError)):
        HijriDate.strptime(text, fmt)


def test_two_digit_year_is_unsupported() -> None:
    with pytest.raises(FormatError):
        HijriDate(1447, 9, 1).format("%y")


def test_date_like_api() -> None:
    h = HijriDate(1447, 9, 1)

    assert (h.year, h.month, h.day) == (1447, 9, 1)

    assert h.weekday() == 2

    assert h.isoweekday() == 3

    assert h.weekday_name == "الأربعاء"

    assert h.month_name() == "رمضان"

    assert str(h) == h.isoformat() == "1447-09-01"

    assert h.replace(month=10) == HijriDate(1447, 10, 1)

    assert HijriDate.fromordinal(h.toordinal()) == h

    assert HijriDate.today() == date.today()


def test_arithmetic_and_comparison_with_date() -> None:
    h, g = HijriDate(1447, 9, 1), date(2026, 2, 18)

    assert h + timedelta(29) == timedelta(29) + h == HijriDate(1447, 9, 30)

    assert h - timedelta(1) == HijriDate(1447, 8, 29)

    assert h - HijriDate(1447, 8, 1) == timedelta(29)  # شعبان 1447 has 29 days

    assert h - date(2026, 2, 1) == timedelta(17)

    assert date(2026, 3, 1) - h == timedelta(11)

    assert h == g and g == h

    assert hash(h) == hash(g) == hash(ArDate.from_date(g))

    assert h < date(2026, 2, 19) and date(2026, 2, 17) < h

    assert h <= g and h >= g and HijriDate(1447, 9, 2) > h

    assert h != datetime(2026, 2, 18)

    with pytest.raises(TypeError):
        _ = h < datetime(2026, 2, 18)


def test_out_of_range() -> None:
    with pytest.raises(OutOfRangeError):
        HijriDate(1447, 2, 30)

    with pytest.raises(OutOfRangeError):
        HijriDate.from_date(date(1900, 1, 1))


_HIJRI = st.dates(min_value=_FIRST, max_value=_LAST).map(HijriDate.from_date)


@given(st.dates(min_value=_FIRST, max_value=_LAST))
def test_conversion_round_trip(d: date) -> None:
    assert HijriDate.from_date(d).to_gregorian() == d


@given(
    _HIJRI,
    st.sampled_from(["%Y-%m-%d", "%A %O من %B %Y هـ", "%j/%Y"]),
    st.sampled_from(["latin", "arabic", "persian"]),
)
def test_format_round_trip(h: HijriDate, fmt: str, digits: DigitSet) -> None:
    assert HijriDate.strptime(h.format(fmt, digits=digits), fmt) == h
