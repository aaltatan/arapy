from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import pytest

from arapy import InvalidNumberError
from arapy.dates import ar_duration, ar_since

from . import golden_phase8 as G

_NOW = datetime(2026, 7, 15, 12)


@dataclass(frozen=True)
class _Delta:
    years: int = 0
    months: int = 0
    days: int = 0
    hours: int = 0
    minutes: int = 0
    seconds: int = 0


@pytest.mark.parametrize(("delta", "expected"), G.SINCE)
def test_since_past(delta: timedelta, expected: str) -> None:
    assert ar_since(_NOW - delta, now=_NOW) == expected


@pytest.mark.parametrize(("delta", "expected"), G.SINCE)
def test_since_future(delta: timedelta, expected: str) -> None:
    assert ar_since(_NOW + delta, now=_NOW) == expected.replace("منذ ", "بعد ")


def test_since_uses_calendar_months() -> None:
    assert ar_since(datetime(2026, 1, 31), now=datetime(2026, 2, 28)) == "منذ أربعة أسابيع"

    assert ar_since(datetime(2026, 1, 31), now=datetime(2026, 3, 1)) == "منذ شهر"

    assert ar_since(datetime(2025, 7, 15, 13), now=_NOW) == "منذ أحد عشر شهرًا"


def test_since_defaults_to_now_in_the_same_time_zone() -> None:
    assert ar_since(datetime.now(UTC) - timedelta(days=3, minutes=1)) == "منذ ثلاثة أيام"


@pytest.mark.parametrize(("delta", "expected"), G.DURATIONS)
def test_duration_from_timedelta(delta: timedelta, expected: str) -> None:
    assert ar_duration(delta) == expected


@pytest.mark.parametrize(("fields", "expected"), G.CALENDAR_DURATIONS)
def test_duration_from_relativedelta_like(
    fields: tuple[int, int, int, int, int, int], expected: str
) -> None:
    assert ar_duration(_Delta(*fields)) == expected


@pytest.mark.parametrize("value", [timedelta(seconds=-1), _Delta(months=-1)])
def test_negative_duration(value: timedelta | _Delta) -> None:
    with pytest.raises(InvalidNumberError):
        ar_duration(value)
