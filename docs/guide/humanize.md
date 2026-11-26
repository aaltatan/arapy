# Relative times and durations

Two functions write time spans in Arabic words, with the right number–noun agreement:

- `ar_since(dt, now=None)`: how long ago, or how far ahead, a moment is: «منذ ثلاثة أيام»,
  «بعد شهرين».
- `ar_duration(value)`: a length of time: «سنة وثلاثة أشهر».

## `ar_since`

`ar_since` uses the largest whole unit: years, months, weeks, days, hours, minutes or seconds.
Under one second it returns «الآن». `now` defaults to the current time in `dt`'s time zone;
pass it to get stable output.

```python
from datetime import datetime, timedelta

from arapy import ar_since

now = datetime(2026, 1, 5, 12)

print(ar_since(now, now=now))  # الآن
print(ar_since(now - timedelta(seconds=3), now=now))  # منذ ثلاث ثوانٍ
print(ar_since(now - timedelta(seconds=40), now=now))  # منذ أربعين ثانيةً
print(ar_since(now - timedelta(minutes=1), now=now))  # منذ دقيقة
print(ar_since(now - timedelta(hours=2), now=now))  # منذ ساعتين
print(ar_since(now - timedelta(days=3), now=now))  # منذ ثلاثة أيام
print(ar_since(now - timedelta(days=15), now=now))  # منذ أسبوعين
print(ar_since(now + timedelta(days=60), now=now))  # بعد شهرين
print(ar_since(datetime(2015, 1, 1), now=now))  # منذ إحدى عشرة سنةً
```

Months and years are counted on the calendar, not as 30 or 365 days: a month has passed only
once the same day of the next month is reached.

## `ar_duration`

`ar_duration` lists every non-zero unit, largest first. It takes a `timedelta`, or any object
with `years`, `months`, `days`, `hours`, `minutes` and `seconds` attributes (the
`RelativeDeltaLike` protocol), such as `dateutil.relativedelta.relativedelta`.

A `timedelta` has no months or years, so its days are split into weeks and days only. Zero is
«صفر ثانية». Sub-second parts are ignored, and negative durations raise `InvalidNumberError`.

```python
from dataclasses import dataclass

from arapy import ar_duration


@dataclass
class Delta:
    years: int = 0
    months: int = 0
    days: int = 0
    hours: int = 0
    minutes: int = 0
    seconds: int = 0


print(ar_duration(timedelta(days=9, hours=2)))  # أسبوع ويومان وساعتان
print(ar_duration(timedelta(hours=1, minutes=30)))  # ساعة وثلاثون دقيقةً
print(ar_duration(timedelta(0)))  # صفر ثانية
print(ar_duration(Delta(years=1, months=3)))  # سنة وثلاثة أشهر
print(ar_duration(Delta(years=2, days=10)))  # سنتان وأسبوع وثلاثة أيام
```

Exactly one of a unit is the bare noun («سنة», «ساعة»), not «سنة واحدة».
