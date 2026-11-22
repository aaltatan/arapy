"""Arabic ordinals: الأول/الأولى … الحادي عشر … المئة, and list markers أولًا، ثانيًا…"""

from typing import Final

from arapy.errors import OutOfRangeError
from arapy.words.grammar import Case, integer_to_words
from arapy.words.nouns import Gender

_MASCULINE: Final = (
    "", "أول", "ثاني", "ثالث", "رابع", "خامس", "سادس", "سابع", "ثامن", "تاسع", "عاشر",
)  # fmt: skip
_FEMININE: Final = (
    "", "أولى", "ثانية", "ثالثة", "رابعة", "خامسة", "سادسة", "سابعة", "ثامنة", "تاسعة", "عاشرة",
)  # fmt: skip

_TANWEEN_FATH: Final = "ً"  # ـً
_TANWEEN_KASR: Final = "ٍ"  # ـٍ

MAX_ORDINAL: Final = 100


def ordinal(
    n: int,
    gender: Gender = Gender.MASCULINE,
    *,
    definite: bool = True,
    case: Case = Case.NOMINATIVE,
) -> str:
    """The ordinal of `n` (1–100): `ordinal(3, Gender.FEMININE)` → «الثالثة».

    `definite=False` gives the indefinite form («ثالث»), which changes with `case`.
    """
    _check(n)

    feminine = gender is Gender.FEMININE

    prefix = "ال" if definite else ""

    tens, unit = divmod(n, 10)

    if n <= 10:
        return prefix + _unit(n, feminine, definite, case)

    if tens == 1:
        return prefix + _teen(unit, feminine)

    tens_word = prefix + integer_to_words(tens * 10, case=case)

    if unit == 0:
        return tens_word

    return f"{prefix}{_unit(unit, feminine, definite, case, compound=True)} و{tens_word}"


def ordinal_adverb(n: int) -> str:
    """List marker for `n` (1–100): أولًا، ثانيًا … عاشرًا، حادي عشر، عشرون، حادي وعشرون."""
    _check(n)

    tens, unit = divmod(n, 10)

    if n == 1:
        return "أول" + _TANWEEN_FATH + "ا"

    if n <= 10:
        return _unit(n, False, False, Case.ACCUSATIVE)

    if tens == 1:
        return _teen(unit, False)

    tens_word = integer_to_words(tens * 10)

    if unit == 0:
        return tens_word

    return f"{_base(unit, False, compound=True)} و{tens_word}"


def _check(n: int) -> None:
    if not 1 <= n <= MAX_ORDINAL:
        raise OutOfRangeError(f"Ordinals are supported from 1 to {MAX_ORDINAL}, not {n}")


def _base(unit: int, feminine: bool, *, compound: bool = False) -> str:
    """«ثالث»/«ثالثة»; in compounds 1 is «حادي»/«حادية»."""
    if compound and unit == 1:
        return "حادية" if feminine else "حادي"

    return (_FEMININE if feminine else _MASCULINE)[unit]


def _teen(unit: int, feminine: bool) -> str:
    """11–19 never change: «حادي عشر», «ثالثة عشرة»."""
    return _base(unit, feminine, compound=True) + (" عشرة" if feminine else " عشر")


def _unit(unit: int, feminine: bool, definite: bool, case: Case, *, compound: bool = False) -> str:
    base = _base(unit, feminine, compound=compound)

    accusative = case is Case.ACCUSATIVE

    if definite or base in ("أول", "أولى"):
        return base

    if feminine:
        return base + _TANWEEN_FATH if accusative else base

    if base.endswith("ي"):  # ثانٍ / ثانيًا, حادٍ / حاديًا
        return base + _TANWEEN_FATH + "ا" if accusative else base[:-1] + _TANWEEN_KASR

    return base + _TANWEEN_FATH + "ا" if accusative else base
