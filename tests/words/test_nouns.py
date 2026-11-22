from types import MappingProxyType

import pytest

from arapy import ArapyError
from arapy.words import Currency, Gender, Noun, PluralForm, noun_forms, plural_form


@pytest.mark.parametrize(
    ("n", "expected"),
    [
        (0, PluralForm.ZERO),
        (1, PluralForm.ONE),
        (2, PluralForm.TWO),
        (3, PluralForm.FEW),
        (10, PluralForm.FEW),
        (103, PluralForm.FEW),
        (11, PluralForm.MANY),
        (99, PluralForm.MANY),
        (1011, PluralForm.MANY),
        (100, PluralForm.OTHER),
        (101, PluralForm.OTHER),
        (102, PluralForm.OTHER),
        (1000, PluralForm.OTHER),
    ],
)
def test_plural_form(n: int, expected: PluralForm) -> None:
    assert plural_form(n) is expected


@pytest.mark.parametrize(
    ("singular", "many"),
    [
        ("ليرة سورية", "ليرةً سوريةً"),
        ("دولار أمريكي", "دولارًا أمريكيًا"),
        ("يورو", "يورو"),
        ("هللة", "هللةً"),
    ],
)
def test_default_many_form(singular: str, many: str) -> None:
    assert noun_forms(singular, "", "")[PluralForm.MANY] == many


def test_dual_oblique_derived() -> None:
    noun = Noun.create("ليرة سورية", "ليرتان سوريتان", "ليرات سورية", gender=Gender.FEMININE)

    assert noun.dual_oblique == "ليرتين سوريتين"


def test_dual_oblique_not_guessed() -> None:
    noun = Noun(forms=noun_forms("أ", "ب", "ج"), gender=Gender.MASCULINE)

    assert noun.dual_oblique is None

    assert noun.form(PluralForm.TWO, oblique=True) == "ب"


def test_missing_forms() -> None:
    with pytest.raises(ArapyError, match="missing forms"):
        Noun(forms={PluralForm.ONE: "يوم"}, gender=Gender.MASCULINE)


def test_forms_are_read_only() -> None:
    forms = {form: "يوم" for form in PluralForm}

    noun = Noun(forms=forms, gender=Gender.MASCULINE)

    forms[PluralForm.ONE] = "changed"

    assert noun.forms[PluralForm.ONE] == "يوم"

    assert isinstance(noun.forms, MappingProxyType)


def test_currency_create() -> None:
    fils = Noun.create("فلس", "فلسان", "فلوس", gender=Gender.MASCULINE)

    kwd = Currency.create(
        code="KWD",
        singular="دينار كويتي",
        dual="ديناران كويتيان",
        plural="دنانير كويتية",
        gender=Gender.MASCULINE,
        subunit=fils,
        ratio=1000,
        symbol="د.ك",
    )

    assert (kwd.code, kwd.ratio, kwd.symbol, kwd.subunit) == ("KWD", 1000, "د.ك", fils)

    assert kwd.form(PluralForm.MANY) == "دينارًا كويتيًا"

    assert kwd.dual_oblique == "دينارين كويتيين"
