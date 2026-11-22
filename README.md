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

```bash
pip install arapy            # core, zero dependencies
pip install "arapy[hijri]"   # Hijri dates
pip install "arapy[shape]"   # reshaping and bidi for drawing Arabic text
```

Documentation: <https://aaltatan.github.io/arapy/>

## Amounts in words (تفقيط)

Gender agreement, plurals, case, currencies and subunits:

```python
>>> from arapy import Tafqeet, to_words
>>> from arapy.words.currencies import KWD, SYP
>>> to_words(125000)
'مئة وخمسة وعشرون ألفًا'
>>> Tafqeet(prefix="فقط", suffix="لا غير")("1250.50", SYP)
'فقط ألف ومئتان وخمسون ليرةً سوريةً وخمسون قرشًا لا غير'
>>> to_words("1.500", KWD)
'دينار كويتي واحد وخمسمئة فلس'
>>> to_words.parse("مائة وخمسة وعشرون")
Decimal('125')

```

Count any noun:

```python
>>> from arapy import Gender, Noun
>>> hour = Noun.create("ساعة", "ساعتان", "ساعات", gender=Gender.FEMININE)
>>> to_words(3, hour), to_words(15, hour)
('ثلاث ساعات', 'خمس عشرة ساعةً')

```

## Digits

```python
>>> from arapy import format_money, format_number, format_percent, parse_number, to_arabic_digits
>>> to_arabic_digits("2026")
'٢٠٢٦'
>>> parse_number("١٢٥٬٠٠٠٫٥")
Decimal('125000.5')
>>> format_number("1250.5", digits="arabic", grouping="٬", decimal="٫")
'١٬٢٥٠٫٥'
>>> format_percent("0.25", digits="arabic")
'٢٥٪'
>>> format_money("1250.5", SYP)
'١٬٢٥٠٫٥٠ ل.س'

```

## Normalization and sorting

```python
>>> from arapy import SEARCH, ar_equals, ar_sorted
>>> SEARCH("أَحْمَدُ   الطَّيِّبَة")
'احمد الطيبه'
>>> ar_equals("عبدالله", "عبد اللّه")
True
>>> ar_sorted(["يوسف", "أحمد", "زينب", "آمنة", "باسل"])
['أحمد', 'آمنة', 'باسل', 'زينب', 'يوسف']

```

## Ordinals

```python
>>> from arapy import ordinal, ordinal_adverb
>>> ordinal(3, Gender.FEMININE), ordinal(21), ordinal_adverb(2)
('الثالثة', 'الحادي والعشرون', 'ثانيًا')

```

## Dates

`ArDate` and `ArDateTime` are real `date` and `datetime` subclasses with Arabic formatting and
strict parsing in any digit set. Month names come in Levantine, Egyptian and Maghrebi styles.

```python
>>> from arapy import ArDate, ArDateTime, MonthNames
>>> d = ArDate(2026, 1, 5)
>>> d.format("%A %O من %B %Y", digits="arabic")
'الاثنين الخامس من كانون الثاني ٢٠٢٦'
>>> d.format("%d %B %Y", months=MonthNames.EGYPTIAN)
'05 يناير 2026'
>>> ArDate.strptime("٥ كانون الثاني ٢٠٢٦", "%d %B %Y")
ArDate(2026, 1, 5)
>>> ArDateTime(2026, 1, 5, 14, 30).format("%I:%M %p")
'02:30 مساءً'

```

Hijri dates (Umm al-Qura, needs `arapy[hijri]`) and relative times:

```python
>>> from datetime import datetime, timedelta
>>> from arapy import ar_duration, ar_since
>>> d.to_hijri().format("%d %B %Y هـ")
'16 رجب 1447 هـ'
>>> now = datetime(2026, 1, 5, 12)
>>> ar_since(now - timedelta(days=3), now=now), ar_since(now + timedelta(days=60), now=now)
('منذ ثلاثة أيام', 'بعد شهرين')
>>> ar_duration(timedelta(days=9, hours=2))
'أسبوع ويومان وساعتان'

```

## Shaping

Pillow, ReportLab and ZPL printers draw letters unjoined and left to right. `shape()` (needs
`arapy[shape]`) joins the letters and puts the text in visual order:

```python
from PIL import Image, ImageDraw, ImageFont
from arapy import shape

image = Image.new("RGB", (400, 100), "white")
font = ImageFont.truetype("NotoNaskhArabic-Regular.ttf", 40)
ImageDraw.Draw(image).text((20, 20), shape("مرحبًا بالعالم"), font=font, fill="black")
```

---

<div dir="rtl">

## arapy بالعربية

مكتبة بايثون بأنواع صارمة لمعالجة النصوص والأرقام والتواريخ العربية.

- **تفقيط المبالغ والأعداد** مع مطابقة التذكير والتأنيث والجمع والإعراب، والعملات وأجزائها،
  وقراءة النص المكتوب بالحروف وتحويله إلى رقم.
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
from arapy import to_words
from arapy.words.currencies import SYP

to_words("1250.50", SYP)
# ألف ومئتان وخمسون ليرةً سوريةً وخمسون قرشًا
```

</div>

## License

MIT
