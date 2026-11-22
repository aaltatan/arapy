import pytest

from arapy.dates import HIJRI_MONTHS, MONTHS, WEEKDAYS, MonthNames
from arapy.dates.months import month_numbers

from . import golden_dates as G


@pytest.mark.parametrize("style", MonthNames)
def test_month_names(style: MonthNames) -> None:
    assert MONTHS[style] == G.MONTHS[style]


def test_weekdays_and_hijri_months() -> None:
    assert WEEKDAYS == G.WEEKDAYS

    assert HIJRI_MONTHS == G.HIJRI_MONTHS


def test_month_numbers_for_one_style() -> None:
    numbers = month_numbers(MonthNames.MAGHREB)

    assert numbers["جانفي"] == 1

    assert "يناير" not in numbers


def test_month_numbers_for_every_style_agree() -> None:
    numbers = month_numbers()

    assert numbers["مارس"] == 3

    assert numbers["آذار (مارس)"] == 3

    assert len(numbers) == len({name for names in MONTHS.values() for name in names})
