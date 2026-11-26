# Dates

`arapy.dates` has three date types:

| Type | Is a | Calendar |
| --- | --- | --- |
| `ArDate` | `datetime.date` subclass | Gregorian |
| `ArDateTime` | `datetime.datetime` subclass | Gregorian |
| `HijriDate` | frozen class that mirrors `date` | Hijri (Umm al-Qura), needs `arapy[hijri]` |

All three add `format()` for Arabic output and a strict `strptime()` that reads Arabic text in
any digit set. The full list of directives is in [Date formats](../reference/date-formats.md).

## ArDate

`ArDate` is a real `date`: it works anywhere a `date` does. Arithmetic, `replace()` and the
class methods (`today`, `fromisoformat`, `fromordinal`, `fromtimestamp`) keep returning
`ArDate`, and `ArDate - date` is a `timedelta` as usual.

```python
from datetime import date, timedelta

from arapy import ArDate

d = ArDate(2026, 1, 5)

print(repr(d + timedelta(days=30)))  # ArDate(2026, 2, 4)
print(repr(d.replace(day=1)))  # ArDate(2026, 1, 1)
print(repr(ArDate.fromisoformat("2026-03-01")))  # ArDate(2026, 3, 1)
print(d - date(2025, 12, 25))  # 11 days, 0:00:00
print(isinstance(d, date))  # True
print(repr(ArDate.from_date(date(2026, 3, 1))))  # ArDate(2026, 3, 1)
```

`strftime()` and f-string formatting keep their standard behaviour, so code that expects a
plain `date` is not surprised. Arabic output goes through `format()`.

### Formatting

`format(fmt, *, months=MonthNames.LEVANT, digits="latin")`:

```python
from arapy import MonthNames

print(d.format("%A %d %B %Y"))  # الاثنين 05 كانون الثاني 2026
print(d.format("%A %O من %B %Y"))  # الاثنين الخامس من كانون الثاني 2026
print(d.format("%A %d %B %Y", digits="arabic"))  # الاثنين ٠٥ كانون الثاني ٢٠٢٦
print(d.format("%d/%m/%Y", digits="persian"))  # ۰۵/۰۱/۲۰۲۶
print(d.strftime("%d %B %Y"))  # 05 January 2026
```

`weekday_name` and `month_name()` give the names alone:

```python
print(d.weekday_name)  # الاثنين
print(d.month_name())  # كانون الثاني
print(d.month_name(MonthNames.EGYPTIAN))  # يناير
```

### Month names

Arab countries name the Gregorian months differently. `MonthNames` has four styles:

| Style | January | Used in |
| --- | --- | --- |
| `LEVANT` (default) | كانون الثاني | Syria, Lebanon, Jordan, Palestine, Iraq |
| `EGYPTIAN` | يناير | Egypt, the Gulf, Sudan |
| `MAGHREB` | جانفي | Tunisia, Algeria |
| `LEVANT_WITH_EGYPTIAN` | كانون الثاني (يناير) | documents read across the region |

```python
print(d.format("%B", months=MonthNames.LEVANT))  # كانون الثاني
print(d.format("%B", months=MonthNames.EGYPTIAN))  # يناير
print(d.format("%B", months=MonthNames.MAGHREB))  # جانفي
print(d.format("%B", months=MonthNames.LEVANT_WITH_EGYPTIAN))  # كانون الثاني (يناير)
```

The names themselves are in `arapy.dates.MONTHS` (per style), `WEEKDAYS` (Monday first, like
`date.weekday()`) and `HIJRI_MONTHS`:

```python
from arapy.dates import HIJRI_MONTHS, MONTHS, WEEKDAYS

print(MONTHS[MonthNames.MAGHREB][2])  # مارس
print(WEEKDAYS[4])  # الجمعة
print(HIJRI_MONTHS[8])  # رمضان
```

### Parsing

`ArDate.strptime(text, fmt, *, months=None)` is strict: the whole text must match. It accepts
any digit set and, with `months=None`, the month names of every style. A weekday or day of the
year that does not match the date raises `ParseError`.

```python
from arapy import ParseError

print(repr(ArDate.strptime("٥ كانون الثاني ٢٠٢٦", "%d %B %Y")))  # ArDate(2026, 1, 5)
print(repr(ArDate.strptime("5 يناير 2026", "%d %B %Y")))  # ArDate(2026, 1, 5)
print(repr(ArDate.strptime("۰۵/۰۱/۲۰۲۶", "%d/%m/%Y")))  # ArDate(2026, 1, 5)
print(repr(ArDate.strptime("الخامس من آذار 2026", "%O من %B %Y")))  # ArDate(2026, 3, 5)

try:
    ArDate.strptime("5 يناير 2026", "%d %B %Y", months=MonthNames.LEVANT)
except ParseError:
    print("not a Levantine month name")  # not a Levantine month name

try:
    ArDate.strptime("٣٠ شباط ٢٠٢٦", "%d %B %Y")
except ParseError:
    print("no 30 February")  # no 30 February
```

Formatting then parsing with the same format gives the date back:
`ArDate.strptime(d.format(f), f) == d`.

## ArDateTime

`ArDateTime` follows the same rules for `datetime`, and adds the time directives `%H`, `%I`,
`%M`, `%S` and `%p` (صباحًا / مساءً):

```python
from arapy import ArDateTime

dt = ArDateTime(2026, 1, 5, 14, 30)

print(dt.format("%I:%M %p"))  # 02:30 مساءً
print(dt.format("%d %B %Y، الساعة %H:%M", digits="arabic"))  # ٠٥ كانون الثاني ٢٠٢٦، الساعة ١٤:٣٠

morning = ArDateTime.strptime("٥ كانون الثاني ٢٠٢٦ ٠٩:١٥ صباحًا", "%d %B %Y %I:%M %p")

print(repr(morning))  # ArDateTime(2026, 1, 5, 9, 15)
print(repr(dt + timedelta(hours=12)))  # ArDateTime(2026, 1, 6, 2, 30)
print(dt.weekday_name)  # الاثنين
```

## HijriDate

`HijriDate` (Umm al-Qura, years 1343–1500 AH) needs `arapy[hijri]`. It is not a `date`
subclass, but it mirrors the `date` API: `year`, `month`, `day`, `weekday()`, `isoformat()`,
`replace()`, `today()`, `fromordinal()`, `± timedelta`, and comparison and subtraction with
both `HijriDate` and plain `date`.

```python
from arapy import HijriDate

h = d.to_hijri()

print(h)  # 1447-07-16
print(h.format("%A %d %B %Y هـ"))  # الاثنين 16 رجب 1447 هـ
print(h.format("%O من %B %Y", digits="arabic"))  # السادس عشر من رجب ١٤٤٧
print(HijriDate(1447, 9, 1).to_gregorian())  # 2026-02-18
print(repr(HijriDate.from_date(date(2026, 2, 18))))  # HijriDate(year=1447, month=9, day=1)
print(HijriDate.strptime("١ رمضان ١٤٤٧", "%d %B %Y"))  # 1447-09-01
print(h + timedelta(days=30))  # 1447-08-16
print(h == date(2026, 1, 5))  # True
print(h < HijriDate(1447, 9, 1))  # True
print(HijriDate(1447, 9, 1) - h)  # 44 days, 0:00:00
```

`to_gregorian()` returns an `ArDate`. `HijriDate.strptime` also accepts the alternative
spellings ربيع الثاني and جمادى الثانية. The Hijri `format` supports the date directives
except `%y`, and has no `months=` argument.

A date outside the supported range raises `OutOfRangeError`.
