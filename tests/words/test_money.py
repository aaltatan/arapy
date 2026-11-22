from decimal import Decimal

import pytest

from arapy import InvalidNumberError
from arapy.digits import parse_number
from arapy.words import Case, Currency, Gender, Noun, Tafqeet, to_words

from .currencies import KWD, SYP, USD
from .golden_money import (
    DAYS,
    EMPLOYEES,
    HOURS,
    KWD_NOMINATIVE,
    SYP_NOMINATIVE,
    SYP_OBLIQUE,
    USD_NOMINATIVE,
    USD_OBLIQUE,
)

HOUR = Noun.create("ساعة", "ساعتان", "ساعات", gender=Gender.FEMININE)
EMPLOYEE = Noun.create("موظف", "موظفان", "موظفين", gender=Gender.MASCULINE)
DAY = Noun.create("يوم", "يومان", "أيام", gender=Gender.MASCULINE)

_OBLIQUE = [Case.ACCUSATIVE, Case.GENITIVE]


def _amount(text: str) -> Decimal:
    return parse_number(text, decimal=".")


def _rows[K, U](unit: U, table: dict[K, str]) -> list[tuple[U, K, str]]:
    return [(unit, key, expected) for key, expected in table.items()]


@pytest.mark.parametrize(
    ("currency", "amount", "expected"),
    _rows(SYP, SYP_NOMINATIVE) + _rows(USD, USD_NOMINATIVE) + _rows(KWD, KWD_NOMINATIVE),
)
def test_nominative(currency: Currency, amount: str, expected: str) -> None:
    assert to_words(_amount(amount), currency) == expected


@pytest.mark.parametrize("case", _OBLIQUE)
@pytest.mark.parametrize(
    ("currency", "amount", "expected"), _rows(SYP, SYP_OBLIQUE) + _rows(USD, USD_OBLIQUE)
)
def test_oblique(currency: Currency, amount: str, expected: str, case: Case) -> None:
    assert Tafqeet(case=case)(_amount(amount), currency) == expected


@pytest.mark.parametrize(
    ("noun", "n", "expected"), _rows(HOUR, HOURS) + _rows(EMPLOYEE, EMPLOYEES) + _rows(DAY, DAYS)
)
def test_counted_nouns(noun: Noun, n: int, expected: str) -> None:
    assert to_words(n, noun) == expected


def test_counted_noun_dual_oblique() -> None:
    assert Tafqeet(case=Case.GENITIVE)(2, EMPLOYEE) == "موظفين"


def test_str_input_and_prefix_suffix() -> None:
    tafqeet = Tafqeet(prefix="فقط", suffix="لا غير")

    assert tafqeet("١٬٢٥٠٫٥٠", SYP) == "فقط ألف ومئتان وخمسون ليرةً سوريةً وخمسون قرشًا لا غير"


def test_maia_spelling_with_unit() -> None:
    assert Tafqeet(hundreds="مائة")(200, SYP) == "مائتا ليرة سورية"


@pytest.mark.parametrize(
    ("value", "unit"),
    [
        (Decimal("1.005"), SYP),  # finer than 1/100
        (Decimal("1.0005"), KWD),  # finer than 1/1000
        (Decimal("1.5"), HOUR),  # a plain noun has no subunit
        (Decimal("1.5"), None),
    ],
)
def test_rejects_unrepresentable_fractions(value: Decimal, unit: Noun | None) -> None:
    with pytest.raises(InvalidNumberError):
        to_words(value, unit)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("1.500", "دينار كويتي واحد وخمسمئة فلس"),
        ("١٫٥٠٠", "دينار كويتي واحد وخمسمئة فلس"),
        ("1,500", "ألف وخمسمئة دينار كويتي"),
        ("1,250.500", "ألف ومئتان وخمسون دينارًا كويتيًا وخمسمئة فلس"),
    ],
)
def test_fils_currency_reads_dot_as_decimal(text: str, expected: str) -> None:
    assert to_words(text, KWD) == expected


def test_hundred_ratio_currency_stays_strict() -> None:
    with pytest.raises(InvalidNumberError, match="Ambiguous"):
        to_words("1.500", SYP)


def test_trailing_zero_places_are_fine() -> None:
    assert to_words(Decimal("5.000"), SYP) == "خمس ليرات سورية"
