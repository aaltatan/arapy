"""Counted nouns and currencies: gender, plural forms and the CLDR plural category."""

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType

from arapy.errors import ArapyError


class Gender(StrEnum):
    MASCULINE = "masculine"
    FEMININE = "feminine"


class PluralForm(StrEnum):
    """Arabic CLDR plural categories."""

    ZERO = "zero"
    ONE = "one"
    TWO = "two"
    FEW = "few"
    MANY = "many"
    OTHER = "other"


def plural_form(n: int) -> PluralForm:
    """CLDR category of `n`: 0 zero, 1 one, 2 two, n%100 in 3–10 few, 11–99 many, else other."""
    n = abs(n)

    rest = n % 100

    if n <= 2:
        return (PluralForm.ZERO, PluralForm.ONE, PluralForm.TWO)[n]

    if 3 <= rest <= 10:
        return PluralForm.FEW

    if rest >= 11:
        return PluralForm.MANY

    return PluralForm.OTHER


def noun_forms(
    singular: str, dual: str, plural: str, *, many: str | None = None
) -> Mapping[PluralForm, str]:
    """Build all six forms from three: «ليرة سورية», «ليرتان سوريتان», «ليرات سورية».

    `many` (the تمييز after 11–99) defaults to `singular` with tanween on every word:
    «ليرةً سوريةً», «دولارًا أمريكيًا».
    """
    return MappingProxyType(
        {
            PluralForm.ZERO: singular,
            PluralForm.ONE: singular,
            PluralForm.TWO: dual,
            PluralForm.FEW: plural,
            PluralForm.MANY: many or " ".join(map(_with_tanween, singular.split())),
            PluralForm.OTHER: singular,
        }
    )


def _with_tanween(word: str) -> str:
    if word.endswith("ة"):
        return word + "ً"

    if word.endswith(("ا", "و", "ى")):
        return word

    return word + "ًا"


@dataclass(frozen=True, slots=True, kw_only=True)
class Noun:
    """A counted noun. Adjective agreement lives in each form.

    `dual_oblique` (accusative/genitive dual, «ليرتين سوريتين») is derived from the dual
    when every word of it ends in ان.
    """

    forms: Mapping[PluralForm, str]
    gender: Gender
    dual_oblique: str | None = None

    def __post_init__(self) -> None:
        missing = set(PluralForm) - self.forms.keys()

        if missing:
            raise ArapyError(f"Noun is missing forms: {sorted(missing)}")

        object.__setattr__(self, "forms", MappingProxyType(dict(self.forms)))

        dual = self.forms[PluralForm.TWO].split()

        if self.dual_oblique is None and all(word.endswith("ان") for word in dual):
            object.__setattr__(self, "dual_oblique", " ".join(w[:-2] + "ين" for w in dual))

    @classmethod
    def create(
        cls,
        singular: str,
        dual: str,
        plural: str,
        *,
        gender: Gender,
        many: str | None = None,
    ) -> "Noun":
        """`Noun.create("ساعة", "ساعتان", "ساعات", gender=Gender.FEMININE)`"""
        return Noun(forms=noun_forms(singular, dual, plural, many=many), gender=gender)

    def form(self, category: PluralForm, *, oblique: bool = False) -> str:
        if category is PluralForm.TWO and oblique and self.dual_oblique:
            return self.dual_oblique

        return self.forms[category]


@dataclass(frozen=True, slots=True, kw_only=True)
class Currency(Noun):
    """A currency: a noun with an ISO 4217 code and a subunit worth 1/`ratio` of it."""

    code: str
    subunit: Noun
    ratio: int = 100
