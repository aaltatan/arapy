# arapy

[![PyPI](https://img.shields.io/pypi/v/arapy)](https://pypi.org/project/arapy/)
[![Python](https://img.shields.io/pypi/pyversions/arapy)](https://pypi.org/project/arapy/)
[![CI](https://github.com/aaltatan/arapy/actions/workflows/ci.yml/badge.svg)](https://github.com/aaltatan/arapy/actions/workflows/ci.yml)

Strongly typed Arabic text, number and date tools for Python: amounts in words (تفقيط), Arabic and
Persian digits, text normalization, alphabetical sorting, ordinals, Gregorian and Hijri dates, and
shaping for images and PDFs.

- **Typed:** `mypy --strict` clean, ships `py.typed`.
- **Exact:** numbers are `Decimal`, never `float`; nothing is silently rounded.
- **Light:** zero dependencies in the core; Hijri dates and shaping are optional extras.
- **Correct Arabic:** gender agreement, dual and plural forms, case endings and tanween, checked
  against reviewed golden tables.

```bash
uv add arapy                 # core, zero dependencies
pip install arapy            # core, zero dependencies
pip install "arapy[hijri]"   # Hijri dates (Umm al-Qura)
pip install "arapy[shape]"   # reshaping and bidi for drawing Arabic text
```

Documentation: <https://aaltatan.github.io/arapy/>

Every example below is a Python script; the comment after each `print()` is its output. The test
suite runs them all.

## Contents

- [Quick start](#quick-start)
- [Amounts in words (تفقيط)](#amounts-in-words-تفقيط)
  - [Numbers](#numbers)
  - [Defining currencies](#defining-currencies)
  - [Money in words](#money-in-words)
  - [Counting any noun](#counting-any-noun)
  - [Reading words back into numbers](#reading-words-back-into-numbers)
  - [Formatting money](#formatting-money)
- [Digits](#digits)
- [Normalization](#normalization)
- [Sorting](#sorting)
- [Ordinals](#ordinals)
- [Dates](#dates)
  - [ArDate](#ardate)
  - [ArDateTime](#ardatetime)
  - [HijriDate](#hijridate)
  - [Relative times and durations](#relative-times-and-durations)
- [Shaping for images and PDFs](#shaping-for-images-and-pdfs)
- [Errors](#errors)
- [arapy بالعربية](#arapy-بالعربية)

## Quick start

```python
from arapy import ArDate, Gender, ar_sorted, format_number, ordinal, to_words

print(to_words(2026))  # ألفان وستة وعشرون
print(format_number("1250000.75", digits="arabic", grouping="٬", decimal="٫"))  # ١٬٢٥٠٬٠٠٠٫٧٥
print(ordinal(1))  # الأول
print(ordinal(1, gender=Gender.FEMININE))  # الأولى
print(ar_sorted(["يوسف", "أحمد", "زينب"]))  # ['أحمد', 'زينب', 'يوسف']
print(ArDate(2026, 1, 5).format("%A %d %B %Y"))  # الاثنين 05 كانون الثاني 2026
```

## Amounts in words (تفقيط)

### Numbers

`to_words` is a ready-made `Tafqeet()`. It takes `int`, `Decimal` or a string in any digit set:

```python
from arapy import Case, Gender, Tafqeet, to_words

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

A `Tafqeet` is a frozen config object. Choose the hundreds spelling, the grammatical case, and a
prefix and suffix for cheques and payment orders:

```python
print(Tafqeet(hundreds="مائة")(300))  # ثلاثمائة
print(Tafqeet(case=Case.ACCUSATIVE)(12))  # اثني عشر
print(Tafqeet(case=Case.GENITIVE)(22))  # اثنين وعشرين

cheque = Tafqeet(prefix="فقط", suffix="لا غير")

print(cheque(7500))  # فقط سبعة آلاف وخمسمئة لا غير
```

### Defining currencies

arapy ships no built-in currencies. Define the ones you use once, with their singular, dual and
plural forms (adjectives included) and their subunit, then pass them around as values:

```python
from arapy import Currency, Noun

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
```

The form used after 11–99 (التمييز) is derived with tanween («ليرةً سوريةً»), and the oblique dual
(«ليرتين سوريتين») is derived from the dual. Pass `many=` when the derived form is not right.

### Money in words

Number words agree with the currency's gender; 1 and 2 follow the noun as adjectives; fractions are
written in subunit words:

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

Amounts are never rounded. A fraction that does not fit the subunit raises an error:

```python
from decimal import Decimal

from arapy import InvalidNumberError

try:
    to_words(Decimal("10.005"), SYP)
except InvalidNumberError as error:
    print(error)  # Decimal('10.005') has more decimal places than SYP subunits allow
```

### Counting any noun

```python
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

### Reading words back into numbers

`parse` returns a `Decimal`. It accepts مئة and مائة, every case, tashkeel, and the object's own
prefix and suffix:

```python
print(to_words.parse("مائة وخمسة وعشرون"))  # 125
print(to_words.parse("ثَلَاثَةُ آلَافٍ"))  # 3000
print(to_words.parse("ألف ومئتان وخمسون ليرةً سوريةً وخمسون قرشًا", SYP))  # 1250.5
print(cheque.parse("فقط سبعة آلاف وخمسمئة لا غير"))  # 7500
```

### Formatting money

`format_money` writes the amount in digits with the currency symbol (or its code when it has none).
Arabic digits and separators are the default:

```python
from arapy import format_money

print(format_money(12500, SYP))  # ١٢٬٥٠٠ ل.س
print(format_money("1250.5", SYP))  # ١٬٢٥٠٫٥٠ ل.س
print(format_money("1.5", KWD))  # ١٫٥٠٠ د.ك
print(format_money("99.9", USD, digits="latin", grouping=",", decimal="."))  # 99.90 $
```

## Digits

```python
from arapy import to_arabic_digits, to_latin_digits, to_persian_digits

print(to_arabic_digits("2026-01-05"))  # ٢٠٢٦-٠١-٠٥
print(to_persian_digits("2026"))  # ۲۰۲۶
print(to_latin_digits("٢٠٢٦ / ۲۰۲۶"))  # 2026 / 2026
```

`parse_number` reads any digit set into an exact `Decimal`. `٬` is always a thousands separator and
`٫` always a decimal mark; when `,` or `.` could mean either, it refuses to guess:

```python
from arapy import InvalidNumberError, parse_number

print(parse_number("١٢٥٬٠٠٠٫٥"))  # 125000.5
print(parse_number("1,250.75"))  # 1250.75
print(parse_number("1,250", decimal="."))  # 1250
print(parse_number("1,250", decimal=","))  # 1.250

try:
    parse_number("1,250")
except InvalidNumberError as error:
    print(error)  # Ambiguous number '1,250': ',' may be a decimal mark or a thousands separator…
```

`format_number` and `format_percent` choose the digits, separators and decimal places, and never
round:

```python
from decimal import Decimal

from arapy import format_number, format_percent

print(format_number(1250000))  # 1,250,000
print(format_number("1250.5", digits="arabic", grouping="٬", decimal="٫"))  # ١٬٢٥٠٫٥
print(format_number("1250.5", places=2, grouping=None))  # 1250.50
print(format_percent("0.25", digits="arabic"))  # ٢٥٪
print(format_percent(Decimal("0.125"), places=2))  # 12.50٪

try:
    format_number(Decimal("1.234"), places=2)
except InvalidNumberError as error:
    print(error)  # Decimal('1.234') has more than 2 decimal places
```

## Normalization

Presets fold the letters people write in different ways, and remove tashkeel, tatweel and
invisible characters:

```python
from arapy import NAMES, SEARCH, Normalizer, ar_equals, ar_key

print(SEARCH("أَحْمَدُ   الطَّيِّبَة"))  # احمد الطيبه
print(SEARCH("إسـلام مؤمن ٢٠٢٦"))  # اسلام مومن 2026
print(NAMES("عبدالله  أبوبكر"))  # عبد الله ابو بكر
```

Build your own pipeline from the rules, or extend a preset with `+`:

```python
from arapy.normalize.rules import collapse_spaces, fold_alef, remove_tashkeel

light = Normalizer([remove_tashkeel, fold_alef, collapse_spaces])
upper = SEARCH + str.upper

print(light("أَحْمَد  إبراهيم"))  # احمد ابراهيم
print(upper("Café ـأحمد"))  # CAFÉ احمد
```

Compare and group text with `ar_equals` and `ar_key`:

```python
key = ar_key(SEARCH)

print(ar_equals("عبدالله", "عبد اللّه"))  # True
print(ar_equals("أسامة", "اسامه"))  # True
print({key(name) for name in ["أحمد", "احمد", "أَحمد"]})  # {'احمد'}
```

## Sorting

`ar_sorted` follows Arabic alphabetical order, not code point order:

```python
from arapy import ar_sort_key, ar_sorted

names = ["يوسف", "أحمد", "زينب", "آمنة", "باسل", "إياد"]

print(sorted(names))  # ['آمنة', 'أحمد', 'إياد', 'باسل', 'زينب', 'يوسف']
print(ar_sorted(names))  # ['أحمد', 'آمنة', 'إياد', 'باسل', 'زينب', 'يوسف']
print(ar_sorted(names, reverse=True)[:2])  # ['يوسف', 'زينب']
```

Sort any objects with `key=`, or use `ar_sort_key` directly:

```python
employees = [("زينب", 3), ("باسل", 1), ("أحمد", 2)]

print(ar_sorted(employees, key=lambda e: e[0]))  # [('أحمد', 2), ('باسل', 1), ('زينب', 3)]
print(sorted(["ي", "ب"], key=ar_sort_key))  # ['ب', 'ي']
```

## Ordinals

```python
from arapy import Case, Gender, ordinal, ordinal_adverb

print(ordinal(1))  # الأول
print(ordinal(10))  # العاشر
print(ordinal(3, Gender.FEMININE))  # الثالثة
print(ordinal(11, Gender.FEMININE))  # الحادية عشرة
print(ordinal(11))  # الحادي عشر
print(ordinal(21))  # الحادي والعشرون
print(ordinal(100))  # المئة
print(ordinal(20, case=Case.GENITIVE))  # العشرين
print(ordinal(3, definite=False))  # ثالث
print(ordinal(3, definite=False, case=Case.ACCUSATIVE))  # ثالثًا
```

List markers:

```python
print([ordinal_adverb(n) for n in range(1, 5)])  # ['أولًا', 'ثانيًا', 'ثالثًا', 'رابعًا']
```

## Dates

### ArDate

`ArDate` is a real `date` subclass: arithmetic, `replace` and the class methods keep returning
`ArDate`, and `strftime` keeps its standard behaviour. `format` writes Arabic:

```python
from datetime import date, timedelta

from arapy import ArDate, MonthNames

d = ArDate(2026, 1, 5)

print(d.format("%A %O من %B %Y"))  # الاثنين الخامس من كانون الثاني 2026
print(d.format("%A %d %B %Y", digits="arabic"))  # الاثنين ٠٥ كانون الثاني ٢٠٢٦
print(d.format("%d/%m/%Y", digits="persian"))  # ۰۵/۰۱/۲۰۲۶
print(d.weekday_name)  # الاثنين
print(d.month_name(MonthNames.EGYPTIAN))  # يناير
```

Four month-name styles:

```python
print(d.format("%B", months=MonthNames.LEVANT))  # كانون الثاني
print(d.format("%B", months=MonthNames.EGYPTIAN))  # يناير
print(d.format("%B", months=MonthNames.MAGHREB))  # جانفي
print(d.format("%B", months=MonthNames.LEVANT_WITH_EGYPTIAN))  # كانون الثاني (يناير)
```

| Directive | Meaning | Example |
|-----------|---------|---------|
| `%A`, `%a` | weekday name | الاثنين |
| `%B`, `%b` | month name | كانون الثاني |
| `%d` | day, two digits | 05 |
| `%O` | ordinal day | الخامس |
| `%m` | month, two digits | 01 |
| `%Y` / `%y` | year, four / two digits | 2026 / 26 |
| `%j` | day of the year | 005 |
| `%H`, `%I` | hour, 24 / 12 | 14 / 02 |
| `%M`, `%S` | minute, second | 30 |
| `%p` | صباحًا / مساءً | مساءً |

`strptime` is strict, accepts any digit set and, by default, any month-name style. Arithmetic keeps
the `ArDate` type:

```python
print(repr(ArDate.strptime("٥ كانون الثاني ٢٠٢٦", "%d %B %Y")))  # ArDate(2026, 1, 5)
print(repr(ArDate.strptime("5 يناير 2026", "%d %B %Y")))  # ArDate(2026, 1, 5)
print(repr(ArDate.strptime("۰۵/۰۱/۲۰۲۶", "%d/%m/%Y")))  # ArDate(2026, 1, 5)
print(repr(d + timedelta(days=30)))  # ArDate(2026, 2, 4)
print(d - date(2025, 12, 25))  # 11 days, 0:00:00
print(ArDate.from_date(date(2026, 3, 1)).format("%B", months=MonthNames.MAGHREB))  # مارس
```

### ArDateTime

```python
from arapy import ArDateTime

dt = ArDateTime(2026, 1, 5, 14, 30)

print(dt.format("%I:%M %p"))  # 02:30 مساءً
print(dt.format("%d %B %Y، الساعة %H:%M", digits="arabic"))  # ٠٥ كانون الثاني ٢٠٢٦، الساعة ١٤:٣٠

morning = ArDateTime.strptime("٥ كانون الثاني ٢٠٢٦ ٠٩:١٥ صباحًا", "%d %B %Y %I:%M %p")

print(repr(morning))  # ArDateTime(2026, 1, 5, 9, 15)
print(repr(dt + timedelta(hours=12)))  # ArDateTime(2026, 1, 6, 2, 30)
```

### HijriDate

`HijriDate` (Umm al-Qura, needs `arapy[hijri]`) mirrors the `date` API and compares with plain dates:

```python
from arapy import HijriDate

h = d.to_hijri()

print(h)  # 1447-07-16
print(h.format("%A %d %B %Y هـ"))  # الاثنين 16 رجب 1447 هـ
print(h.format("%O من %B %Y", digits="arabic"))  # السادس عشر من رجب ١٤٤٧
print(HijriDate(1447, 9, 1).to_gregorian())  # 2026-02-18
print(HijriDate.strptime("١ رمضان ١٤٤٧", "%d %B %Y"))  # 1447-09-01
print(h + timedelta(days=30))  # 1447-08-16
print(h == date(2026, 1, 5))  # True
print(h < HijriDate(1447, 9, 1))  # True
```

### Relative times and durations

```python
from datetime import datetime

from arapy import ar_duration, ar_since

now = datetime(2026, 1, 5, 12)

print(ar_since(now, now=now))  # الآن
print(ar_since(now - timedelta(seconds=40), now=now))  # منذ أربعين ثانيةً
print(ar_since(now - timedelta(minutes=1), now=now))  # منذ دقيقة
print(ar_since(now - timedelta(hours=2), now=now))  # منذ ساعتين
print(ar_since(now - timedelta(days=3), now=now))  # منذ ثلاثة أيام
print(ar_since(now - timedelta(days=15), now=now))  # منذ أسبوعين
print(ar_since(now + timedelta(days=60), now=now))  # بعد شهرين
print(ar_since(datetime(2015, 1, 1), now=now))  # منذ إحدى عشرة سنةً
```

`ar_duration` takes a `timedelta`, or any object with `years`, `months`, `days`, `hours`,
`minutes` and `seconds` (such as `dateutil.relativedelta`):

```python
from dataclasses import dataclass


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
print(ar_duration(Delta(years=1, months=3)))  # سنة وثلاثة أشهر
```

## Shaping for images and PDFs

Pillow, ReportLab and ZPL printers draw each letter on its own and left to right, so Arabic comes
out unjoined and backwards. `shape()` (needs `arapy[shape]`) joins the letters and puts the text in
visual order. `reshape_only()` joins the letters but keeps logical order, for renderers that apply
the bidi algorithm themselves:

```python
from arapy import reshape_only, shape

print(reshape_only("سلام"))  # ﺳﻼﻡ
print(shape("سلام"))  # ﻡﻼﺳ
print(shape("رقم 123"))  # 123 ﻢﻗﺭ
```

With Pillow:

```py
from PIL import Image, ImageDraw, ImageFont

from arapy import shape

image = Image.new("RGB", (400, 100), "white")
font = ImageFont.truetype("NotoNaskhArabic-Regular.ttf", 40)

ImageDraw.Draw(image).text((20, 20), shape("مرحبًا بالعالم"), font=font, fill="black")

image.save("hello.png")
```

With ReportLab:

```py
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from arapy import shape

pdfmetrics.registerFont(TTFont("Naskh", "NotoNaskhArabic-Regular.ttf"))

pdf = canvas.Canvas("invoice.pdf")
pdf.setFont("Naskh", 16)
pdf.drawRightString(550, 800, shape("فاتورة رقم ١٢٥"))
pdf.save()
```

## Errors

Every error subclasses `ArapyError`, and also the matching built-in exception, so
`except ValueError` keeps working:

| Error | Also a | Raised when |
|-------|--------|-------------|
| `InvalidNumberError` | `ValueError` | a number is malformed, ambiguous or has too many decimal places |
| `OutOfRangeError` | `ValueError` | a value is outside the supported range |
| `ParseError` | `ValueError` | text cannot be parsed as words or as a date |
| `FormatError` | `ValueError` | a format string uses an unsupported directive |
| `MissingExtraError` | `ImportError` | an optional extra is not installed |

```python
from arapy import ArapyError, OutOfRangeError

try:
    to_words(10**15)
except OutOfRangeError as error:
    print(error)  # 1000000000000000 is outside the supported range ±999999999999999

try:
    ArDate.strptime("٣٠ شباط ٢٠٢٦", "%d %B %Y")
except ArapyError as error:
    print(type(error).__name__)  # ParseError
```

---

<div dir="rtl">

## arapy بالعربية

مكتبة بايثون بأنواع صارمة لمعالجة النصوص والأرقام والتواريخ العربية.

- **تفقيط المبالغ والأعداد** مع مطابقة التذكير والتأنيث والجمع والإعراب، والعملات وأجزائها،
  وقراءة النص المكتوب بالحروف وتحويله إلى رقم. لا تأتي المكتبة بعملات جاهزة: تعرّف العملات التي
  تحتاجها مرة واحدة ثم تمررها.
- **الأرقام:** التحويل بين الأرقام العربية والفارسية واللاتينية، وقراءة الأرقام وتنسيقها بدقة
  تامة دون تقريب.
- **توحيد النصوص:** قواعد قابلة للتركيب لتوحيد الهمزات والتاء المربوطة وحذف التشكيل والتطويل،
  مع دوال للمقارنة والبحث.
- **الترتيب الأبجدي** العربي الصحيح بدلًا من ترتيب رموز يونيكود.
- **الأعداد الترتيبية:** الأول، الأولى، الحادي عشر، أولًا، ثانيًا.
- **التواريخ:** الأنواع `ArDate` و`ArDateTime` و`HijriDate` بأسماء أشهر شامية ومصرية ومغاربية،
  وقراءة صارمة للتواريخ بأي أرقام، وعبارات مثل «منذ ثلاثة أيام» و«سنة وثلاثة أشهر».
- **تشكيل الحروف** ووصلها لرسم النص العربي في الصور وملفات PDF وطابعات الملصقات.

```bash
pip install arapy
```

```python
from arapy import Currency, Gender, Noun, Tafqeet

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

print(cheque("1250.50", SYP))  # فقط ألف ومئتان وخمسون ليرةً سوريةً وخمسون قرشًا لا غير
```

</div>

## License

MIT
