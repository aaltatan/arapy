# Digits and numbers

`arapy.digits` converts between digit sets, parses numbers written in any of them into an
exact `Decimal`, and formats numbers with the digits and separators you choose.

Three digit sets are supported, named by the `DigitSet` literal:

| Name | Digits |
| --- | --- |
| `"latin"` | 0123456789 |
| `"arabic"` | ٠١٢٣٤٥٦٧٨٩ (Arabic-Indic) |
| `"persian"` | ۰۱۲۳۴۵۶۷۸۹ (Extended Arabic-Indic) |

## Converting digits

Each function replaces the digits of the other two sets and leaves everything else alone:

```python
from arapy import to_arabic_digits, to_latin_digits, to_persian_digits

print(to_arabic_digits("2026-01-05"))  # ٢٠٢٦-٠١-٠٥
print(to_persian_digits("2026"))  # ۲۰۲۶
print(to_latin_digits("٢٠٢٦ / ۲۰۲۶"))  # 2026 / 2026
print(to_latin_digits("هاتف: ٠٩٣٣ ١٢٣ ٤٥٦"))  # هاتف: 0933 123 456
```

## Parsing numbers

`parse_number` reads a number in any digit set into an exact `Decimal`:

- `٬` (Arabic thousands separator) is always a thousands separator.
- `٫` (Arabic decimal separator) is always the decimal mark.
- `,`, `.` and `،` (Arabic comma) can be either. When both `,` and `.` appear, the last one is
  the decimal mark. When the text alone cannot tell, such as `"1,250"`, arapy refuses to guess
  and raises `InvalidNumberError`. Pass `decimal=` to say which one is the decimal mark.
- A leading `-`, `−` or `+` sets the sign.

```python
from arapy import InvalidNumberError, parse_number

print(parse_number("١٢٥٬٠٠٠٫٥"))  # 125000.5
print(parse_number("1,250.75"))  # 1250.75
print(parse_number("1.250,75"))  # 1250.75
print(parse_number("1,250", decimal="."))  # 1250
print(parse_number("1,250", decimal=","))  # 1.250
print(parse_number("1,5"))  # 1.5
print(parse_number("-۱۲"))  # -12

try:
    parse_number("1,250")
except InvalidNumberError as error:
    print(error)  # Ambiguous number '1,250': ',' may be a decimal mark or a thousands separator…
```

The rule looks only at the text, so `"0.075"` is ambiguous too (three digits after the
mark). When your input always uses one decimal mark, say so:

```python
print(parse_number("0.075", decimal="."))  # 0.075
```

Groups must be three digits with one consistent separator, so malformed input is rejected
rather than misread:

```python
try:
    parse_number("12,50,000")
except InvalidNumberError as error:
    print(error)  # Not a valid number: '12,50,000'
```

## Formatting numbers

`format_number` writes a number with the digit set, thousands separator and decimal mark you
choose:

| Argument | Default | Meaning |
| --- | --- | --- |
| `digits` | `"latin"` | the digit set |
| `grouping` | `","` | the thousands separator, or `None` for no grouping |
| `decimal` | `"."` | the decimal mark |
| `places` | `None` | pad the fraction to this many digits |

```python
from decimal import Decimal

from arapy import format_number

print(format_number(1250000))  # 1,250,000
print(format_number("1250.5", digits="arabic", grouping="٬", decimal="٫"))  # ١٬٢٥٠٫٥
print(format_number("1250.5", places=2, grouping=None))  # 1250.50
print(format_number(Decimal("1250.50")))  # 1,250.50
print(format_number(-42, digits="persian"))  # -۴۲
```

`places` pads but never rounds. A value with more significant decimal places raises:

```python
try:
    format_number(Decimal("1.234"), places=2)
except InvalidNumberError as error:
    print(error)  # Decimal('1.234') has more than 2 decimal places
```

## Percentages

`format_percent` takes a fraction, multiplies it by 100 exactly, and adds the Arabic percent
sign `٪`. It takes the same arguments as `format_number`:

```python
from arapy import format_percent

print(format_percent("0.25"))  # 25٪
print(format_percent("0.25", digits="arabic"))  # ٢٥٪
print(format_percent(Decimal("0.125"), places=2))  # 12.50٪
print(format_percent(Decimal("0.075"), digits="arabic", decimal="٫"))  # ٧٫٥٪
```

For amounts with a currency symbol, see
[`format_money`](words.md#formatting-money-in-digits).
