from datetime import UTC, datetime, timedelta

import pytest
from hypothesis import given
from hypothesis import strategies as st

from arapy import FormatError, ParseError
from arapy.dates import ArDate, ArDateTime, MonthNames
from arapy.digits import DigitSet

from . import golden_phase8 as G

type Args = tuple[int, int, int, int, int, int, str, DigitSet]


@pytest.mark.parametrize(("args", "expected"), G.DATETIME_FORMATS)
def test_format(args: Args, expected: str) -> None:
    year, month, day, hour, minute, second, fmt, digits = args

    dt = ArDateTime(year, month, day, hour, minute, second)

    assert dt.format(fmt, digits=digits) == expected


@pytest.mark.parametrize(("args", "expected"), G.DATETIME_FORMATS)
def test_strptime_reads_golden_output(args: Args, expected: str) -> None:
    year, month, day, hour, minute, second, fmt, _ = args

    parsed = ArDateTime.strptime(expected, fmt)

    assert (parsed.hour, parsed.minute, parsed.second) == (hour, minute, second)

    if "%Y" in fmt:
        assert parsed == datetime(year, month, day, hour, minute, second)


def test_results_stay_ardatetime() -> None:
    dt = ArDateTime(2026, 1, 5, 10, 30)

    for result in (
        dt + timedelta(hours=1),
        timedelta(hours=1) + dt,
        dt - timedelta(hours=1),
        dt.replace(hour=1),
        ArDateTime.now(),
        ArDateTime.combine(ArDate(2026, 1, 5), datetime.min.time()),
        ArDateTime.fromisoformat("2026-01-05T10:30"),
        ArDateTime.from_datetime(datetime(2026, 1, 5, 10, 30)),
    ):
        assert type(result) is ArDateTime

    assert dt - datetime(2026, 1, 5, 10) == timedelta(minutes=30)

    assert dt - ArDateTime(2026, 1, 5, 10) == timedelta(minutes=30)


def test_from_datetime_keeps_time_zone() -> None:
    aware = datetime(2026, 1, 5, 10, 30, tzinfo=UTC)

    assert ArDateTime.from_datetime(aware) == aware

    assert ArDateTime.from_datetime(aware).tzinfo is UTC


def test_standard_formatting_and_names() -> None:
    dt = ArDateTime(2026, 1, 5, 14, 30)

    assert dt.strftime("%A %p") == "Monday PM"

    assert dt.weekday_name == "الاثنين"

    assert dt.month_name(MonthNames.MAGHREB) == "جانفي"


def test_strptime_hours() -> None:
    assert ArDateTime.strptime("12:00 صباحًا", "%I:%M %p").hour == 0

    assert ArDateTime.strptime("12:00 مساءً", "%I:%M %p").hour == 12

    assert ArDateTime.strptime("07", "%I").hour == 7  # %I without %p is morning

    assert ArDateTime.strptime("مساءً 14", "%p %H").hour == 14  # %p without %I is ignored

    assert ArDateTime.strptime("٢٠٢٦-٠١-٠٥ ١٤:٣٠", "%Y-%m-%d %H:%M") == datetime(2026, 1, 5, 14, 30)


@pytest.mark.parametrize(
    ("text", "fmt"),
    [
        ("13:00 مساءً", "%I:%M %p"),  # %I is 1–12
        ("00:00 صباحًا", "%I:%M %p"),
        ("25:00", "%H:%M"),
        ("14 02 صباحًا", "%H %I %p"),  # the two hours disagree
        ("10:61", "%H:%M"),
    ],
)
def test_strptime_is_strict(text: str, fmt: str) -> None:
    with pytest.raises(ParseError):
        ArDateTime.strptime(text, fmt)


def test_ardate_rejects_time_directives() -> None:
    with pytest.raises(FormatError):
        ArDate.strptime("10:30", "%H:%M")


_FORMATS = ["%Y-%m-%d %H:%M:%S", "%A %O من %B %Y، %I:%M:%S %p", "%d/%m/%Y %p %I %M %S"]


@given(
    st.datetimes().map(lambda dt: ArDateTime.from_datetime(dt.replace(microsecond=0))),
    st.sampled_from(_FORMATS),
    st.sampled_from(MonthNames),
    st.sampled_from(["latin", "arabic", "persian"]),
)
def test_round_trip(dt: ArDateTime, fmt: str, months: MonthNames, digits: DigitSet) -> None:
    assert ArDateTime.strptime(dt.format(fmt, months=months, digits=digits), fmt) == dt
