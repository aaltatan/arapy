# Recipes

Complete, runnable programs for common jobs. Each one is self-contained.

## A payment order

A payroll system prints one payment order per employee: the amount in digits and in words,
the date in Arabic, and numbered clauses.

```python
from dataclasses import dataclass
from decimal import Decimal

from arapy import ArDate, Currency, Gender, Noun, Tafqeet, format_money, ordinal_adverb

qirsh = Noun.create("قرش", "قرشان", "قروش", gender=Gender.MASCULINE)

SYP = Currency.create(
    code="SYP",
    singular="ليرة سورية",
    dual="ليرتان سوريتان",
    plural="ليرات سورية",
    gender=Gender.FEMININE,
    subunit=qirsh,
    symbol="ل.س",
)

cheque = Tafqeet(prefix="فقط", suffix="لا غير")


@dataclass(frozen=True)
class Payment:
    name: str
    amount: Decimal
    reason: str
    issued: ArDate


def payment_order(payment: Payment) -> str:
    lines = [
        f"التاريخ: {payment.issued.format('%d %B %Y', digits='arabic')}",
        f"{ordinal_adverb(1)}: يصرف للسيد/ة {payment.name}",
        f"{ordinal_adverb(2)}: مبلغ {format_money(payment.amount, SYP)}",
        f"{ordinal_adverb(3)}: {cheque(payment.amount, SYP)}",
        f"{ordinal_adverb(4)}: وذلك {payment.reason}",
    ]

    return "\n".join(lines)


order = payment_order(
    Payment("زينب الأحمد", Decimal("1250000.50"), "أجور شهر كانون الثاني", ArDate(2026, 1, 31))
)

print(order)  # التاريخ: ٣١ كانون الثاني ٢٠٢٦…
```

Prints:

```text
التاريخ: ٣١ كانون الثاني ٢٠٢٦
أولًا: يصرف للسيد/ة زينب الأحمد
ثانيًا: مبلغ ١٬٢٥٠٬٠٠٠٫٥٠ ل.س
ثالثًا: فقط مليون ومئتان وخمسون ألف ليرة سورية وخمسون قرشًا لا غير
رابعًا: وذلك أجور شهر كانون الثاني
```

## Checking an amount typed in words

A cashier types the amount in words; the system checks it against the amount in digits before
printing the cheque.

```python
from arapy import ParseError


def words_match(amount: Decimal, typed: str) -> bool:
    try:
        return cheque.parse(typed, SYP) == amount
    except ParseError:
        return False


print(words_match(Decimal("7500"), "سبعة آلاف وخمسمائة ليرة سورية"))  # True
print(words_match(Decimal("7500"), "فقط سبعة آلاف وخمسمئة ليرة سورية لا غير"))  # True
print(words_match(Decimal("7500"), "سبعة آلاف ليرة سورية"))  # False
print(words_match(Decimal("7500"), "مبلغ غير مقروء"))  # False
```

## Importing numbers from a spreadsheet

Amounts arrive from several branches, some in Arabic digits with Arabic separators, some in
Latin digits. Each branch states its decimal mark, so nothing is guessed.

```python
from arapy import InvalidNumberError, parse_number

rows = [
    ("دمشق", "١٢٥٬٠٠٠٫٥٠", "٫"),
    ("حلب", "98,500.25", "."),
    ("حمص", "1.250,00", ","),
    ("حماة", "12,5O", ","),
]

total = Decimal(0)

for branch, text, mark in rows:
    try:
        total += parse_number(text, decimal=mark)
    except InvalidNumberError:
        print(f"تحقق من مبلغ {branch}")  # تحقق من مبلغ حماة

print(total)  # 224750.75
```

## A search box for names

Users search an employee list without caring about hamza, ة/ه, tashkeel or how a compound
name is spaced. Index once with `NAMES`, then match with the same normalizer.

```python
from arapy import NAMES, ar_sorted

employees = ["عبد الله الأحمد", "أسامة يوسف", "فاطمة الزهراء", "إياد عبدالرحمن"]

index = {name: NAMES(name) for name in employees}


def search(query: str) -> list[str]:
    needle = NAMES(query)

    return ar_sorted(name for name, key in index.items() if needle in key)


print(search("عبدالله"))  # ['عبد الله الأحمد']
print(search("اسامه"))  # ['أسامة يوسف']
print(search("عبد"))  # ['إياد عبدالرحمن', 'عبد الله الأحمد']
print(search("فاطِمة"))  # ['فاطمة الزهراء']
```

## Removing duplicate customers

The same customer was typed twice with different spellings. Group by a normalized key and keep
the first spelling seen:

```python
from arapy import SEARCH, ar_key

customers = ["مؤسسة النور", "مؤسسه النور", "مُؤَسَّسَة  النُّور", "شركة الأمل", "شركه الامل"]

key = ar_key(SEARCH)
unique: dict[str, str] = {}

for customer in customers:
    unique.setdefault(key(customer), customer)

print(list(unique.values()))  # ['مؤسسة النور', 'شركة الأمل']
```

## Dates in a report header, Gregorian and Hijri

```python
from arapy import MonthNames

day = ArDate(2026, 2, 18)

gregorian = day.format("%A %O من %B %Y م", months=MonthNames.LEVANT_WITH_EGYPTIAN)
hijri = day.to_hijri().format("%O من %B %Y هـ")

print(gregorian)  # الأربعاء الثامن عشر من شباط (فبراير) 2026 م
print(hijri)  # الأول من رمضان 1447 هـ
```

## "Last seen" labels

```python
from datetime import datetime, timedelta

from arapy import ar_since

now = datetime(2026, 1, 5, 12)

activity = {
    "زينب": now - timedelta(minutes=5),
    "باسل": now - timedelta(days=2),
    "أحمد": now - timedelta(days=40),
}

labels = [f"{name}: آخر ظهور {ar_since(activity[name], now=now)}" for name in ar_sorted(activity)]

print(labels[0])  # أحمد: آخر ظهور منذ شهر
print(labels[1])  # باسل: آخر ظهور منذ يومين
print(labels[2])  # زينب: آخر ظهور منذ خمس دقائق
```

