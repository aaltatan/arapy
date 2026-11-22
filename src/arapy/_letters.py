"""Arabic letter constants and character classes shared across modules."""

from typing import Final

ALEF: Final = "ا"  # ا
ALEF_HAMZA_ABOVE: Final = "أ"  # أ
ALEF_HAMZA_BELOW: Final = "إ"  # إ
ALEF_MADDA: Final = "آ"  # آ
ALEF_WASLA: Final = "ٱ"  # ٱ
ALEF_FORMS: Final = frozenset({ALEF_HAMZA_ABOVE, ALEF_HAMZA_BELOW, ALEF_MADDA, ALEF_WASLA})

TATWEEL: Final = "ـ"  # ـ

# Fathatan … sukun (U+064B–U+0652).
TASHKEEL: Final = frozenset(chr(c) for c in range(0x064B, 0x0653))

# Index i holds the digit with value i.
LATIN_DIGITS: Final = "0123456789"
ARABIC_DIGITS: Final = "٠١٢٣٤٥٦٧٨٩"
PERSIAN_DIGITS: Final = "۰۱۲۳۴۵۶۷۸۹"
