"""Checked by mypy in test_typing.py: results keep the `ArDate` type."""

from datetime import date, timedelta
from typing import assert_type

from arapy.dates import ArDate

d = ArDate(2026, 1, 5)

assert_type(d + timedelta(1), ArDate)
assert_type(timedelta(1) + d, ArDate)
assert_type(d - timedelta(1), ArDate)
assert_type(d - d, timedelta)
assert_type(d - date(2026, 1, 1), timedelta)
assert_type(d.replace(day=1), ArDate)
assert_type(ArDate.today(), ArDate)
assert_type(ArDate.fromisoformat("2026-01-05"), ArDate)
assert_type(ArDate.from_date(date(2026, 1, 5)), ArDate)
assert_type(ArDate.strptime("2026", "%Y"), ArDate)
