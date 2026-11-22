"""Integer → Arabic words engine: gender agreement, case endings and hundreds spelling."""

from enum import StrEnum
from typing import Final, Literal

from arapy.errors import OutOfRangeError
from arapy.words.nouns import Gender


class Case(StrEnum):
    NOMINATIVE = "nominative"
    ACCUSATIVE = "accusative"
    GENITIVE = "genitive"


type Hundreds = Literal["مئة", "مائة"]

MAX_INTEGER: Final = 10**15 - 1

_TANWEEN_FATH: Final = "ًا"  # ـًا

_ONES_MASCULINE: Final = (
    "", "واحد", "اثنان", "ثلاثة", "أربعة", "خمسة", "ستة", "سبعة", "ثمانية", "تسعة", "عشرة",
)  # fmt: skip
_ONES_FEMININE: Final = (
    "", "واحدة", "اثنتان", "ثلاث", "أربع", "خمس", "ست", "سبع", "ثماني", "تسع", "عشر",
)  # fmt: skip
_TENS: Final = (
    "", "", "عشرون", "ثلاثون", "أربعون", "خمسون", "ستون", "سبعون", "ثمانون", "تسعون",
)  # fmt: skip
_HUNDREDS_PREFIX: Final = ("", "", "", "ثلاث", "أربع", "خمس", "ست", "سبع", "ثمان", "تسع")

# (value, singular, plural for 3–10), largest first.
_SCALES: Final = (
    (10**12, "تريليون", "تريليونات"),
    (10**9, "مليار", "مليارات"),
    (10**6, "مليون", "ملايين"),
    (10**3, "ألف", "آلاف"),
)


def integer_to_words(
    n: int,
    *,
    gender: Gender = Gender.MASCULINE,
    case: Case = Case.NOMINATIVE,
    hundreds: Hundreds = "مئة",
    construct: bool = False,
) -> str:
    """Write an integer in Arabic words: 125000 → «مئة وخمسة وعشرون ألفًا».

    `gender` sets agreement for the last group (below 1000); scale words are masculine.
    `construct` writes the last word as it stands before a counted noun: «ألفا», «مئتا»,
    and «ألف» instead of «ألفًا».
    """
    if abs(n) > MAX_INTEGER:
        raise OutOfRangeError(f"{n} is outside the supported range ±{MAX_INTEGER}")

    if n < 0:
        positive = integer_to_words(
            -n, gender=gender, case=case, hundreds=hundreds, construct=construct
        )
        return "سالب " + positive

    if n == 0:
        return "صفر"

    oblique = case is not Case.NOMINATIVE

    parts = []

    for value, singular, plural in _SCALES:
        group, n = divmod(n, value)

        if group:
            last = construct and n == 0
            parts.append(_scale_group(group, singular, plural, oblique, hundreds, construct=last))

    if n:
        feminine = gender is Gender.FEMININE
        parts.append(_below_1000(n, feminine, oblique, hundreds, construct=construct))

    return " و".join(parts)


def _dual(word: str, oblique: bool, *, construct: bool = False) -> str:
    if construct:
        return word + ("ي" if oblique else "ا")

    return word + ("ين" if oblique else "ان")


def _two(feminine: bool, oblique: bool) -> str:
    return _dual("اثنت" if feminine else "اثن", oblique)


def _below_100(n: int, feminine: bool, oblique: bool) -> str:
    ones = _ONES_FEMININE if feminine else _ONES_MASCULINE

    if n == 2:
        return _two(feminine, oblique)

    if n <= 10:
        return ones[n]

    if n == 11:
        return "إحدى عشرة" if feminine else "أحد عشر"

    if n == 12:
        stem = "اثنت" if feminine else "اثن"
        return stem + ("ي" if oblique else "ا") + (" عشرة" if feminine else " عشر")

    tens, unit = divmod(n, 10)

    if tens == 1:
        return ones[unit] + (" عشرة" if feminine else " عشر")

    tens_word = _TENS[tens][:-2] + "ين" if oblique else _TENS[tens]

    if unit == 0:
        return tens_word

    if unit == 1:
        unit_word = "إحدى" if feminine else "واحد"

    elif unit == 2:
        unit_word = _two(feminine, oblique)

    else:
        unit_word = ones[unit]

    return f"{unit_word} و{tens_word}"


def _hundreds(h: int, oblique: bool, spelling: Hundreds, *, construct: bool = False) -> str:
    if h == 1:
        return spelling

    if h == 2:
        return _dual(spelling[:-1] + "ت", oblique, construct=construct)  # مئت / مائت

    return _HUNDREDS_PREFIX[h] + spelling


def _below_1000(
    n: int, feminine: bool, oblique: bool, spelling: Hundreds, *, construct: bool = False
) -> str:
    h, rest = divmod(n, 100)

    parts = []

    if h:
        parts.append(_hundreds(h, oblique, spelling, construct=construct and rest == 0))

    if rest:
        parts.append(_below_100(rest, feminine, oblique))

    return " و".join(parts)


def _scale_group(
    g: int,
    singular: str,
    plural: str,
    oblique: bool,
    spelling: Hundreds,
    *,
    construct: bool = False,
) -> str:
    """Words for `g` (1–999) of one scale: 3 → «ثلاثة آلاف», 101 → «مئة ألف وألف»."""
    if g == 1:
        return singular

    if g == 2:
        return _dual(singular, oblique, construct=construct)

    h, rest = divmod(g, 100)

    if rest <= 2:
        head = f"{_hundreds(h, oblique, spelling, construct=True)} {singular}"

        if rest == 0:
            return head

        tail = _scale_group(rest, singular, plural, oblique, spelling, construct=construct)
        return f"{head} و{tail}"

    if rest <= 10:
        noun = plural

    elif construct:
        noun = singular

    else:
        noun = singular + _TANWEEN_FATH

    counted = f"{_below_100(rest, False, oblique)} {noun}"
    return f"{_hundreds(h, oblique, spelling)} و{counted}" if h else counted
