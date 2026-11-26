# arapy

**Strongly typed Arabic text, number and date tools for Python.**

Amounts in words (تفقيط), Arabic and Persian digits, text normalization, alphabetical sorting,
ordinals, Gregorian and Hijri dates, and shaping for images and PDFs, in one package with no
dependencies in its core.

- **Typed:** `mypy --strict` clean, ships `py.typed`.
- **Exact:** numbers are `Decimal`, never `float`; nothing is silently rounded.
- **Light:** zero dependencies in the core; Hijri dates and shaping are optional extras.
- **Correct Arabic:** gender agreement, dual and plural forms, case endings and tanween, checked
  against reviewed golden tables.

## A first taste

A payment order needs the amount in digits and in words, a date, and a line number:

```python
from arapy import (
    ArDate,
    Currency,
    Gender,
    Noun,
    Tafqeet,
    format_money,
    ordinal_adverb,
)

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

print(format_money("1250.50", SYP))  # ١٬٢٥٠٫٥٠ ل.س
print(cheque("1250.50", SYP))  # فقط ألف ومئتان وخمسون ليرةً سوريةً وخمسون قرشًا لا غير
print(ArDate(2026, 1, 5).format("%A %O من %B %Y"))  # الاثنين الخامس من كانون الثاني 2026
print(ordinal_adverb(2))  # ثانيًا
```

Search and sort names the way people read them:

```python
from arapy import SEARCH, ar_equals, ar_sorted

print(SEARCH("أَحْمَدُ   الطَّيِّبَة"))  # احمد الطيبه
print(ar_equals("عبدالله", "عبد اللّه"))  # True
print(ar_sorted(["يوسف", "أحمد", "زينب"]))  # ['أحمد', 'زينب', 'يوسف']
```

## Where it fits

- **Payment orders, cheques and invoices:** amounts in words with the right gender, case and
  currency, and amounts in Arabic digits.
- **Reports and documents:** Arabic dates in Levantine, Egyptian or Maghrebi month names,
  Hijri dates, ordinals and list markers.
- **Search and data cleaning:** fold hamza, alef and teh marbuta variants, strip tashkeel and
  tatweel, compare names.
- **Images, PDFs and label printers:** join and reorder Arabic letters for Pillow, ReportLab
  and ZPL.

## Where to next

<div class="grid cards" markdown>

- [**Installation**](install.md): the core and its two extras.
- [**User guide**](guide/index.md): every module, one page each.
- [**Recipes**](recipes.md): complete real-world programs.
- [**Reference**](reference/index.md): every public name, the date directives and the errors.

</div>
