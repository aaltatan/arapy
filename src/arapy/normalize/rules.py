"""Individual normalization rules. Each rule is a small, pure `str -> str` function."""

import re
from collections.abc import Callable, Iterable

from arapy._letters import (
    ALEF,
    ALEF_FORMS,
    ALEF_MAQSURA,
    HEH,
    INVISIBLE,
    QURANIC_MARKS,
    TASHKEEL,
    TATWEEL,
    TEH_MARBUTA,
    WAW,
    WAW_HAMZA,
    YEH,
    YEH_HAMZA,
)
from arapy.digits import to_latin_digits

type Rule = Callable[[str], str]


def _removal(chars: Iterable[str]) -> dict[int, None]:
    return dict.fromkeys(map(ord, chars))


_ALEF = str.maketrans(dict.fromkeys(ALEF_FORMS, ALEF))
_HAMZA_CARRIERS = str.maketrans({WAW_HAMZA: WAW, YEH_HAMZA: YEH})
_LOOKALIKES = str.maketrans({"ی": YEH, "ک": "ك", "ہ": HEH})
_TASHKEEL = _removal(TASHKEEL)
_QURANIC = _removal(QURANIC_MARKS)
_INVISIBLE = _removal(INVISIBLE)

# عبد glued to a following ال…, or ابو/أبو glued to a name of three or more letters.
_COMPOUND = re.compile(r"(?<!\S)(عبد(?=ال\S)|[اأ]بو(?=\S{3}))")


def fold_alef(text: str) -> str:
    """أ إ آ ٱ → ا"""
    return text.translate(_ALEF)


def fold_alef_maqsura(text: str) -> str:
    """ى → ي"""
    return text.replace(ALEF_MAQSURA, YEH)


def fold_teh_marbuta(text: str) -> str:
    """ة → ه"""
    return text.replace(TEH_MARBUTA, HEH)


def fold_hamza_carriers(text: str) -> str:
    """ؤ → و, ئ → ي"""
    return text.translate(_HAMZA_CARRIERS)


def fold_lookalikes(text: str) -> str:
    """Persian/Urdu ی ک ہ → Arabic ي ك ه"""
    return text.translate(_LOOKALIKES)


def fold_digits(text: str) -> str:
    """Arabic-Indic and Persian digits → Latin digits."""
    return to_latin_digits(text)


def remove_tashkeel(text: str) -> str:
    """Remove harakat, tanween, shadda and sukun."""
    return text.translate(_TASHKEEL)


def remove_tatweel(text: str) -> str:
    """Remove tatweel (ـ)."""
    return text.replace(TATWEEL, "")


def remove_quranic_marks(text: str) -> str:
    """Remove Quranic annotation signs and superscript alef."""
    return text.translate(_QURANIC)


def remove_invisible(text: str) -> str:
    """Remove zero-width characters and bidi controls."""
    return text.translate(_INVISIBLE)


def split_compound_names(text: str) -> str:
    """عبدالله → عبد الله, ابوبكر → ابو بكر"""
    # Repeat so chains like ابوعبدالله split fully and the rule stays idempotent.
    while (split := _COMPOUND.sub(r"\1 ", text)) != text:
        text = split

    return text


def collapse_spaces(text: str) -> str:
    """Collapse runs of whitespace to one space and strip both ends."""
    return " ".join(text.split())
