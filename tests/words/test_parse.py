from decimal import Decimal

import pytest
from hypothesis import given
from hypothesis import strategies as st

from arapy import ParseError
from arapy.words import Case, Currency, Gender, Noun, Tafqeet, to_words
from arapy.words.currencies import CURRENCIES, KWD, SYP, USD
from arapy.words.grammar import MAX_INTEGER

from .golden_integers import MASCULINE_NOMINATIVE
from .golden_money import SYP_NOMINATIVE

HOUR = Noun.create("ساعة", "ساعتان", "ساعات", gender=Gender.FEMININE)
DAY = Noun.create("يوم", "يومان", "أيام", gender=Gender.MASCULINE)


@pytest.mark.parametrize(("n", "words"), MASCULINE_NOMINATIVE.items())
def test_parses_golden_integers(n: int, words: str) -> None:
    assert to_words.parse(words) == n


@pytest.mark.parametrize(("amount", "words"), SYP_NOMINATIVE.items())
def test_parses_golden_syp(amount: str, words: str) -> None:
    assert to_words.parse(words, SYP) == Decimal(amount)


@pytest.mark.parametrize(
    ("text", "unit", "expected"),
    [
        ("مائة وخمسة وعشرون", None, 125),
        ("ثلاثمائة ألف", None, 300000),
        ("مِئَةٌ وَخَمْسَةٌ وَعِشْرُونَ", None, 125),
        ("أحد عشر ألفاً", None, 11000),
        ("احد عشر الف", None, 11000),
        ("مـئـة", None, 100),
        ("مئتين واثنين وعشرين", None, 222),
        ("ليرة سورية واحدة وقرش واحد", SYP, Decimal("1.01")),
        ("ثلاث ساعات", HOUR, 3),
        ("ساعتين", HOUR, 2),
        ("ثلاثة أيام", DAY, 3),
        ("دينار كويتي واحد وخمسمئة فلس", KWD, Decimal("1.5")),
        ("خمسون سنتًا", USD, Decimal("0.5")),
    ],
)
def test_parse(text: str, unit: Noun | None, expected: Decimal | int) -> None:
    assert to_words.parse(text, unit) == expected


def test_parse_strips_configured_affixes() -> None:
    tafqeet = Tafqeet(prefix="فقط", suffix="لا غير")

    assert tafqeet.parse("فقط مئة لا غير") == 100

    assert tafqeet.parse("مئة") == 100


@pytest.mark.parametrize(
    ("text", "unit"),
    [
        ("", None),
        ("سالب", None),
        ("مئة كتاب", None),
        ("مئة دولار", SYP),
        ("ألف قرش", SYP),  # 1000 qirsh is not less than one lira
    ],
)
def test_parse_errors(text: str, unit: Noun | None) -> None:
    with pytest.raises(ParseError):
        to_words.parse(text, unit)


_tafqeets = st.builds(
    Tafqeet,
    hundreds=st.sampled_from(["مئة", "مائة"]),
    case=st.sampled_from(Case),
    prefix=st.sampled_from(["", "فقط"]),
    suffix=st.sampled_from(["", "لا غير"]),
)


@given(st.integers(-MAX_INTEGER, MAX_INTEGER), _tafqeets)
def test_roundtrip_integers(n: int, tafqeet: Tafqeet) -> None:
    assert tafqeet.parse(tafqeet(n)) == n


@st.composite
def _money(draw: st.DrawFn) -> tuple[Currency, Decimal]:
    currency = draw(st.sampled_from(list(CURRENCIES.values())))

    whole = draw(st.integers(0, MAX_INTEGER))

    sub = draw(st.integers(0, currency.ratio - 1))

    sign = draw(st.sampled_from([1, -1]))

    return currency, sign * (whole + Decimal(sub) / currency.ratio)


@given(_money(), _tafqeets)
def test_roundtrip_money(money: tuple[Currency, Decimal], tafqeet: Tafqeet) -> None:
    currency, amount = money

    assert tafqeet.parse(tafqeet(amount, currency), currency) == amount


@given(st.integers(0, MAX_INTEGER), st.sampled_from([HOUR, DAY]), _tafqeets)
def test_roundtrip_counted_nouns(n: int, noun: Noun, tafqeet: Tafqeet) -> None:
    assert tafqeet.parse(tafqeet(n, noun), noun) == n
