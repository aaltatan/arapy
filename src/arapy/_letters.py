"""Arabic letter constants and character classes shared across modules."""

from typing import Final

ALEF: Final = "ا"  # ا
ALEF_HAMZA_ABOVE: Final = "أ"  # أ
ALEF_HAMZA_BELOW: Final = "إ"  # إ
ALEF_MADDA: Final = "آ"  # آ
ALEF_WASLA: Final = "ٱ"  # ٱ
ALEF_FORMS: Final = frozenset({ALEF_HAMZA_ABOVE, ALEF_HAMZA_BELOW, ALEF_MADDA, ALEF_WASLA})

TEH: Final = "ت"  # ت
TEH_MARBUTA: Final = "ة"  # ة
HEH: Final = "ه"  # ه
WAW: Final = "و"  # و
WAW_HAMZA: Final = "ؤ"  # ؤ
YEH: Final = "ي"  # ي
YEH_HAMZA: Final = "ئ"  # ئ
ALEF_MAQSURA: Final = "ى"  # ى

TATWEEL: Final = "ـ"  # ـ

# Fathatan … sukun (U+064B–U+0652).
TASHKEEL: Final = frozenset(chr(c) for c in range(0x064B, 0x0653))

# Quranic annotation signs, extended marks and superscript alef.
QURANIC_MARKS: Final = frozenset(
    chr(c)
    for start, end in ((0x0610, 0x061A), (0x0653, 0x065F), (0x0670, 0x0670), (0x06D6, 0x06ED))
    for c in range(start, end + 1)
)

# Zero-width characters, bidi controls, Arabic letter mark and byte order mark.
INVISIBLE: Final = frozenset(
    chr(c)
    for start, end in ((0x200B, 0x200F), (0x202A, 0x202E), (0x2066, 0x2069))
    for c in range(start, end + 1)
) | {"؜", "﻿"}

# Index i holds the digit with value i.
LATIN_DIGITS: Final = "0123456789"
ARABIC_DIGITS: Final = "٠١٢٣٤٥٦٧٨٩"
PERSIAN_DIGITS: Final = "۰۱۲۳۴۵۶۷۸۹"

ARABIC_DECIMAL_SEPARATOR: Final = "٫"  # ٫
ARABIC_THOUSANDS_SEPARATOR: Final = "٬"  # ٬
ARABIC_COMMA: Final = "،"  # ،
ARABIC_PERCENT: Final = "٪"  # ٪
