# Date formats

The directives understood by `format()` and `strptime()` on `ArDate`, `ArDateTime` and
`HijriDate`. A directive outside this list raises `FormatError`.

| Directive | Meaning | `format` example | `ArDate` | `ArDateTime` | `HijriDate` |
| --- | --- | --- | :---: | :---: | :---: |
| `%A`, `%a` | weekday name | الاثنين | ✓ | ✓ | ✓ |
| `%B`, `%b` | month name, in the chosen style | كانون الثاني / رجب | ✓ | ✓ | ✓ |
| `%d` | day, two digits | 05 | ✓ | ✓ | ✓ |
| `%O` | day as an ordinal | الخامس | ✓ | ✓ | ✓ |
| `%m` | month, two digits | 01 | ✓ | ✓ | ✓ |
| `%Y` | year, four digits | 2026 | ✓ | ✓ | ✓ |
| `%y` | year, two digits | 26 | ✓ | ✓ | |
| `%j` | day of the year, three digits | 005 | ✓ | ✓ | ✓ |
| `%H` | hour, 00–23 | 14 | | ✓ | |
| `%I` | hour, 01–12 | 02 | | ✓ | |
| `%M` | minute | 30 | | ✓ | |
| `%S` | second | 00 | | ✓ | |
| `%p` | صباحًا / مساءً | مساءً | | ✓ | |
| `%%` | a literal `%` | % | ✓ | ✓ | ✓ |

`%a` and `%b` are the same as `%A` and `%B`: Arabic has no standard short names.

## Formatting

- `digits=` (`"latin"`, `"arabic"` or `"persian"`) applies to every numeric directive.
- `months=` picks the Gregorian month-name style (`MonthNames`); `HijriDate` always uses the
  Hijri month names.
- `%O` uses the masculine ordinal (الأول … الحادي والثلاثون), agreeing with «اليوم».

## Parsing

- The whole text must match the format.
- Numbers may be written in any digit set; `%d`, `%m`, `%H`, `%I`, `%M` and `%S` accept one or
  two digits.
- `%B`/`%b` accept every month-name style when `months=None` (the default), or only the given
  style. `HijriDate.strptime` also accepts ربيع الثاني and جمادى الثانية.
- `%A`/`%a` and `%j` are checked against the date: a mismatch raises `ParseError`.
- Missing fields default to 1900-01-01 (Gregorian) or 1400-01-01 (Hijri), as in
  `datetime.strptime`.
- `%I` needs `%p` to tell morning from evening.

```python
from arapy import ArDate, ArDateTime

d = ArDate(2026, 1, 5)

print(d.format("%a %d/%m/%y، اليوم %j من السنة"))  # الاثنين 05/01/26، اليوم 005 من السنة
print(ArDateTime(2026, 1, 5, 9, 5, 7).format("%H:%M:%S %p"))  # 09:05:07 صباحًا
print(d.format("خصم 10%%"))  # خصم 10%
print(repr(ArDate.strptime("الاثنين 5/1/2026", "%A %d/%m/%Y")))  # ArDate(2026, 1, 5)
```
