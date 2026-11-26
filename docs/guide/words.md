# Amounts in words (تفقيط)

`arapy.words` writes numbers in Arabic words, alone, counting a noun, or as money with a
currency and its subunit. It also reads the words back into a number.

## Numbers

`to_words` is a ready-made `Tafqeet()`. It takes an `int`, a `Decimal` or a string in any
digit set:

```python
from arapy import to_words

print(to_words(0))  # صفر
print(to_words(11))  # أحد عشر
print(to_words(12))  # اثنا عشر
print(to_words(21))  # واحد وعشرون
print(to_words(125000))  # مئة وخمسة وعشرون ألفًا
print(to_words(3_000_000))  # ثلاثة ملايين
print(to_words(1_002_003_004))  # مليار ومليونان وثلاثة آلاف وأربعة
print(to_words("٩٩٩"))  # تسعمئة وتسعة وتسعون
print(to_words(-15))  # سالب خمسة عشر
```

The range is ±999,999,999,999,999 (up to trillions). Anything larger raises
`OutOfRangeError`. A bare number must be whole: a fraction needs a currency to be written in
subunits.

## The `Tafqeet` object

A `Tafqeet` is a frozen config object with four fields. Call it like a function.

| Field | Default | Meaning |
| --- | --- | --- |
| `hundreds` | `"مئة"` | the spelling of hundreds: `"مئة"` or `"مائة"` |
| `case` | `Case.NOMINATIVE` | the grammatical case: `NOMINATIVE`, `ACCUSATIVE` or `GENITIVE` |
| `prefix` | `""` | text before the words, such as «فقط» |
| `suffix` | `""` | text after the words, such as «لا غير» |

```python
from arapy import Case, Tafqeet

print(Tafqeet(hundreds="مائة")(300))  # ثلاثمائة
print(Tafqeet(case=Case.ACCUSATIVE)(12))  # اثني عشر
print(Tafqeet(case=Case.GENITIVE)(22))  # اثنين وعشرين

cheque = Tafqeet(prefix="فقط", suffix="لا غير")

print(cheque(7500))  # فقط سبعة آلاف وخمسمئة لا غير
```

Accusative and genitive share their forms for numbers, so `Case.ACCUSATIVE` and
`Case.GENITIVE` give the same words; choose the one that matches your sentence.

## Counting nouns

Pass a `Noun` as the second argument. A noun has a gender and three forms: singular, dual and
plural. Adjectives go inside each form.

```python
from arapy import Gender, Noun

hour = Noun.create("ساعة", "ساعتان", "ساعات", gender=Gender.FEMININE)
employee = Noun.create("موظف", "موظفان", "موظفين", gender=Gender.MASCULINE)

print(to_words(1, hour))  # ساعة واحدة
print(to_words(2, hour))  # ساعتان
print(to_words(3, hour))  # ثلاث ساعات
print(to_words(15, hour))  # خمس عشرة ساعةً
print(to_words(5, employee))  # خمسة موظفين
print(to_words(20, employee))  # عشرون موظفًا
print(to_words(1000, employee))  # ألف موظف
```

The rules arapy applies:

- Numbers 3–10 take the opposite gender of the noun (ثلاث ساعات، خمسة موظفين).
- 1 and 2 follow the noun as adjectives (ساعة واحدة، ساعتان).
- 11–99 take the singular with tanween, the تمييز (خمس عشرة ساعةً، عشرون موظفًا).
- Hundreds, thousands and above take the singular (ألف موظف).

### The six plural forms

Under the hood a noun has one form per Arabic [CLDR plural
category](https://cldr.unicode.org/index/cldr-spec/plural-rules). `plural_form` tells you which
one a number takes, and `noun_forms` builds all six from three:

```python
from arapy.words import PluralForm, noun_forms, plural_form

print(plural_form(0), plural_form(1), plural_form(2))  # zero one two
print(plural_form(7), plural_form(15), plural_form(100))  # few many other
print(plural_form(103), plural_form(111))  # few many

forms = noun_forms("دولار أمريكي", "دولاران أمريكيان", "دولارات أمريكية")

print(forms[PluralForm.MANY])  # دولارًا أمريكيًا
```

The `MANY` form (after 11–99) is the singular with tanween on every word. When that is not
right, pass `many=`:

```python
book = Noun.create("كتاب", "كتابان", "كتب", gender=Gender.MASCULINE, many="كتابًا")

print(to_words(12, book))  # اثنا عشر كتابًا
```

The oblique dual («ليرتين سوريتين») is derived from the dual when every word of it ends in ان.
To build a noun by hand, give `Noun` all six forms and, if needed, `dual_oblique`.

## Defining currencies

arapy ships no built-in currencies. Define the ones you use once, with their singular, dual
and plural forms and their subunit, then pass them around as values. `Currency.create` takes
keyword arguments only.

```python
from arapy import Currency

qirsh = Noun.create("قرش", "قرشان", "قروش", gender=Gender.MASCULINE)
cent = Noun.create("سنت", "سنتان", "سنتات", gender=Gender.MASCULINE)
fils = Noun.create("فلس", "فلسان", "فلوس", gender=Gender.MASCULINE)

SYP = Currency.create(
    code="SYP",
    singular="ليرة سورية",
    dual="ليرتان سوريتان",
    plural="ليرات سورية",
    gender=Gender.FEMININE,
    subunit=qirsh,
    symbol="ل.س",
)

USD = Currency.create(
    code="USD",
    singular="دولار أمريكي",
    dual="دولاران أمريكيان",
    plural="دولارات أمريكية",
    gender=Gender.MASCULINE,
    subunit=cent,
    symbol="$",
)

KWD = Currency.create(
    code="KWD",
    singular="دينار كويتي",
    dual="ديناران كويتيان",
    plural="دنانير كويتية",
    gender=Gender.MASCULINE,
    subunit=fils,
    ratio=1000,
    symbol="د.ك",
)

print(SYP.form(PluralForm.MANY))  # ليرةً سوريةً
print(SYP.dual_oblique)  # ليرتين سوريتين
```

| Argument | Meaning |
| --- | --- |
| `code` | the ISO 4217 code, shown by `format_money` when there is no symbol |
| `singular`, `dual`, `plural` | the three main forms, adjectives included |
| `gender` | the gender of the currency noun |
| `subunit` | a `Noun` for the subunit (قرش، سنت، فلس) |
| `ratio` | subunits per unit: `100` by default, `1000` for KWD, JOD, BHD, OMR and IQD |
| `symbol` | used by `format_money`, such as «ل.س» or «$» |
| `many` | overrides the derived تمييز form, as for `Noun.create` |

## Money in words

Number words agree with the currency's gender, and the fraction is written in subunit words:

```python
print(to_words(1, SYP))  # ليرة سورية واحدة
print(to_words(2, SYP))  # ليرتان سوريتان
print(to_words(3, SYP))  # ثلاث ليرات سورية
print(to_words(15, SYP))  # خمس عشرة ليرةً سوريةً
print(to_words(1, USD))  # دولار أمريكي واحد
print(to_words(3, USD))  # ثلاثة دولارات أمريكية
print(to_words(100, USD))  # مئة دولار أمريكي
print(to_words("1250.50", SYP))  # ألف ومئتان وخمسون ليرةً سوريةً وخمسون قرشًا
print(to_words("0.75", USD))  # خمسة وسبعون سنتًا
print(to_words("1.500", KWD))  # دينار كويتي واحد وخمسمئة فلس
print(Tafqeet(case=Case.GENITIVE)(2, SYP))  # ليرتين سوريتين
print(cheque("1250.50", SYP))  # فقط ألف ومئتان وخمسون ليرةً سوريةً وخمسون قرشًا لا غير
```

For a currency with 1000 subunits, a string such as `"1.500"` reads `.` as the decimal mark,
since three decimal places are normal there.

Amounts are never rounded. A fraction that does not fit the subunit raises an error:

```python
from decimal import Decimal

from arapy import InvalidNumberError

try:
    to_words(Decimal("10.005"), SYP)
except InvalidNumberError as error:
    print(error)  # Decimal('10.005') has more decimal places than SYP subunits allow
```

## Reading words back into numbers

`Tafqeet.parse` returns a `Decimal`. It accepts مئة and مائة, every case, tashkeel, and the
object's own prefix and suffix. Pass the unit that was counted so its words can be read:

```python
print(to_words.parse("مائة وخمسة وعشرون"))  # 125
print(to_words.parse("ثَلَاثَةُ آلَافٍ"))  # 3000
print(to_words.parse("سالب خمسة عشر"))  # -15
print(to_words.parse("ألف ومئتان وخمسون ليرةً سوريةً وخمسون قرشًا", SYP))  # 1250.5
print(cheque.parse("فقط سبعة آلاف وخمسمئة لا غير"))  # 7500
```

Text that is not a number raises `ParseError`:

```python
from arapy import ParseError

try:
    to_words.parse("")
except ParseError as error:
    print(error)  # No number in ''
```

## Formatting money in digits

`format_money` writes the amount in digits followed by the currency symbol, or its code when
it has none. Arabic digits with `٬` and `٫` are the default. Whole amounts show no decimals;
others are padded to the subunit's places (2, or 3 for 1000-subunit currencies):

```python
from arapy import format_money

print(format_money(12500, SYP))  # ١٢٬٥٠٠ ل.س
print(format_money("1250.5", SYP))  # ١٬٢٥٠٫٥٠ ل.س
print(format_money("1.5", KWD))  # ١٫٥٠٠ د.ك
print(format_money("99.9", USD, digits="latin", grouping=",", decimal="."))  # 99.90 $
print(format_money(100, USD, digits="latin", grouping=",", decimal=".", places=2))  # 100.00 $
```

`digits`, `grouping`, `decimal` and `places` work as in
[`format_number`](digits.md#formatting-numbers).
