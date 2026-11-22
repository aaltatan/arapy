from types import MappingProxyType

import pytest

from arapy import ArapyError
from arapy.words import Gender, Noun, PluralForm, currencies, noun_forms, plural_form


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


def test_registry() -> None:
    assert set(currencies.CURRENCIES) == {
        "SYP", "USD", "EUR", "SAR", "AED", "EGP", "JOD", "LBP",
        "TRY", "KWD", "IQD", "QAR", "BHD", "OMR", "GBP",
    }  # fmt: skip

    assert currencies.CURRENCIES["SYP"] is currencies.SYP

    assert {c.code for c in currencies.CURRENCIES.values() if c.ratio == 1000} == {
        "JOD", "KWD", "IQD", "BHD", "OMR",
    }  # fmt: skip

    with pytest.raises(TypeError):
        currencies.CURRENCIES["XXX"] = currencies.SYP  # type: ignore[index]
