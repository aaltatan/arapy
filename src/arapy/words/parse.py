"""Arabic words → number: the inverse of `Tafqeet`."""

import re
from decimal import Decimal
from typing import Final, Literal

from arapy.errors import ParseError
from arapy.normalize import Normalizer
from arapy.normalize.rules import (
    collapse_spaces,
    fold_alef,
    remove_invisible,
    remove_tashkeel,
    remove_tatweel,
)
from arapy.words.nouns import Currency, Noun, PluralForm


def _fold_maia(text: str) -> str:
    return text.replace("مائ", "مئ")


# Tanween and harakat go, alef forms fold, and مائة is read as مئة.
_normalize: Final = Normalizer(
    (remove_invisible, remove_tashkeel, remove_tatweel, fold_alef, _fold_maia, collapse_spaces)
)


def _vocabulary() -> dict[str, int]:
    words: dict[str, int] = {"صفر": 0}

    ones = (
        ("واحد", "واحدة", "احد", "احدى"),
        ("اثنان", "اثنين", "اثنا", "اثني", "اثنتان", "اثنتين", "اثنتا", "اثنتي"),
        ("ثلاثة", "ثلاث"),
        ("اربعة", "اربع"),
        ("خمسة", "خمس"),
        ("ستة", "ست"),
        ("سبعة", "سبع"),
        ("ثمانية", "ثماني", "ثمان"),
        ("تسعة", "تسع"),
        ("عشرة", "عشر"),
    )

    for value, forms in enumerate(ones, start=1):
        words |= dict.fromkeys(forms, value)

    tens = ("عشر", "ثلاث", "اربع", "خمس", "ست", "سبع", "ثمان", "تسع")

    for value, stem in enumerate(tens, start=2):
        words[stem + "ون"] = words[stem + "ين"] = value * 10

    words["مئة"] = 100
    words |= dict.fromkeys(("مئتان", "مئتين", "مئتا", "مئتي"), 200)

    for value, stem in enumerate(("ثلاث", "اربع", "خمس", "ست", "سبع", "ثمان", "تسع"), start=3):
        words[stem + "مئة"] = value * 100

    words["ثمانيمئة"] = 800

    return words


type _ScaleKind = Literal["one", "a", "dual", "plural"]


def _scales() -> dict[str, tuple[_ScaleKind, int]]:
    """Scale word → (kind, value). "الفا" is 2000 in construct or ألفًا without its tanween."""
    scales: dict[str, tuple[_ScaleKind, int]] = {}

    for value, singular, plural in (
        (10**3, "الف", "الاف"),
        (10**6, "مليون", "ملايين"),
        (10**9, "مليار", "مليارات"),
        (10**12, "تريليون", "تريليونات"),
    ):
        scales[singular] = ("one", value)
        scales[singular + "ا"] = ("a", value)
        scales |= dict.fromkeys((singular + "ان", singular + "ين", singular + "ي"), ("dual", value))
        scales[plural] = ("plural", value)

    return scales


_NUMBERS: Final = _vocabulary()
_SCALES: Final = _scales()

_ONE_WORDS: Final = ("واحد", "واحدة")


def parse_words(
    text: str,
    unit: Noun | None = None,
    *,
    prefix: str = "",
    suffix: str = "",
) -> Decimal:
    """Read an amount written in Arabic words.

    Accepts مئة and مائة, every case, text with or without `prefix`/`suffix`, and ignores
    tashkeel. With a `Currency`, subunit words are read as fractions of `unit.ratio`.
    """
    clean = _normalize(text).removeprefix(_normalize(prefix)).removesuffix(_normalize(suffix))

    clean = clean.strip()
    negative = clean.startswith("سالب ")
    clean = clean.removeprefix("سالب ")

    if not clean:
        raise ParseError(f"No number in {text!r}")

    nouns = _noun_markers(unit)

    for pattern, marker in nouns:
        clean = pattern.sub(rf"\1{marker}", clean)

    amounts = _Reader(text).read(clean.split())
    value = Decimal(amounts.main)

    if amounts.sub:
        assert isinstance(unit, Currency)  # only currencies get subunit markers

        if amounts.sub >= unit.ratio:
            raise ParseError(f"{amounts.sub} subunits is not less than one {unit.code}: {text!r}")

        value += Decimal(amounts.sub) / unit.ratio

    return -value if negative else value


def _noun_markers(unit: Noun | None) -> list[tuple[re.Pattern[str], str]]:
    """Patterns that swap each written form of the unit (and subunit) for a marker token."""
    if unit is None:
        return []

    nouns: list[tuple[Noun, str]] = [(unit, "U")]

    if isinstance(unit, Currency):
        nouns.append((unit.subunit, "S"))

    forms: dict[str, str] = {}

    for noun, key in nouns:
        for category, form in noun.forms.items():
            kind = "2" if category is PluralForm.TWO else "1"
            forms[_normalize(form)] = f"<{key}{kind}>"

        if noun.dual_oblique:
            forms[_normalize(noun.dual_oblique)] = f"<{key}2>"

    return [
        (re.compile(rf"(?<!\S)(و?){re.escape(form)}(?!\S)"), marker)
        for form, marker in sorted(forms.items(), key=lambda item: -len(item[0]))
    ]


class _Amounts:
    __slots__ = ("main", "sub")

    def __init__(self) -> None:
        self.main = 0
        self.sub = 0


class _Reader:
    """Left-to-right reader: groups below 1000 build up in `current`, scales flush them."""

    def __init__(self, text: str) -> None:
        self.text = text
        self.total = 0
        self.current = 0
        self.pending = False
        self.amounts = _Amounts()
        self.last_noun: str | None = None

    def read(self, tokens: list[str]) -> _Amounts:
        previous_was_bare_noun = False

        for token in tokens:
            word, conjunction = self._split_conjunction(token)

            if previous_was_bare_noun and word in _ONE_WORDS and not conjunction:
                previous_was_bare_noun = False  # «ليرة سورية واحدة»: the one is already counted

                continue

            previous_was_bare_noun = False

            if word.startswith("<"):
                previous_was_bare_noun = self._noun(word, conjunction)

            elif word in _SCALES:
                self._scale(*_SCALES[word])

            elif word in _NUMBERS:
                self.current += _NUMBERS[word]
                self.pending = True

            else:
                raise ParseError(f"Unknown word {token!r} in {self.text!r}")

        if self.pending:
            self._add("U", self.total + self.current)

        return self.amounts

    def _split_conjunction(self, token: str) -> tuple[str, bool]:
        known = token in _NUMBERS or token in _SCALES or token.startswith("<")

        if not known and token.startswith("و") and len(token) > 1:
            return token[1:], True

        return token, False

    def _scale(self, kind: _ScaleKind, value: int) -> None:
        if kind == "dual" or (kind == "a" and not self.current):
            count = 2

        elif kind == "plural" or kind == "a":
            count = self.current

        else:
            count = self.current or 1

        self.total += count * value
        self.current = 0
        self.pending = True

    def _noun(self, marker: str, conjunction: bool) -> bool:
        """Count a unit/subunit marker. True means a bare noun that واحد may follow."""
        key, kind = marker[1], marker[2]

        if self.pending and kind == "2":
            raise ParseError(f"A dual noun cannot follow a number: {self.text!r}")

        bare = False

        if self.pending:
            self._add(key, self.total + self.current)

        elif kind == "2":
            self._add(key, 2)

        else:
            # «ليرة سورية (واحدة)», «وقرش (واحد)», or «وليرة» after a hundred.
            self._add(key, 1)
            bare = True

        self.total = self.current = 0
        self.pending = False

        return bare

    def _add(self, key: str, value: int) -> None:
        if key == "S":
            self.amounts.sub += value
        else:
            self.amounts.main += value
