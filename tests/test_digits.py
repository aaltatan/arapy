from decimal import Decimal

import pytest
from hypothesis import given
from hypothesis import strategies as st

from arapy import InvalidNumberError
from arapy.digits import (
    DecimalMark,
    DigitSet,
    format_number,
    format_percent,
    parse_number,
    to_arabic_digits,
    to_latin_digits,
    to_persian_digits,
)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("٢٠٢٦ / ۲۰۲۶", "2026 / 2026"),
        ("المبلغ ١٢٥ ليرة", "المبلغ 125 ليرة"),
        ("no digits", "no digits"),
    ],
)
def test_to_latin_digits(text: str, expected: str) -> None:
    assert to_latin_digits(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("2026", "٢٠٢٦"),
        ("۲۰۲۶ و 7", "٢٠٢٦ و ٧"),
    ],
)
def test_to_arabic_digits(text: str, expected: str) -> None:
    assert to_arabic_digits(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("2026", "۲۰۲۶"),
        ("٢٠٢٦ و 7", "۲۰۲۶ و ۷"),
    ],
)
def test_to_persian_digits(text: str, expected: str) -> None:
    assert to_persian_digits(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("١٢٥٬٠٠٠٫٥", "125000.5"),
        ("١٢٥٬٠٠٠", "125000"),
        ("۲۰۲۶", "2026"),
        ("1,250.5", "1250.5"),
        ("1.250,5", "1250.5"),
        ("1,250,000", "1250000"),
        ("1.5", "1.5"),
        ("1،5", "1.5"),
        ("1٬250,5", "1250.5"),
        ("-12.5", "-12.5"),
        ("−٣", "-3"),
        ("+7", "7"),
        ("  42 ", "42"),
        ("0", "0"),
    ],
)
def test_parse_number(text: str, expected: str) -> None:
    assert parse_number(text) == Decimal(expected)


@pytest.mark.parametrize(
    ("text", "decimal", "expected"),
    [
        ("1,250", ".", "1250"),
        ("1,250", ",", "1.25"),
        ("12.500", ".", "12.5"),
        ("1،250", "،", "1.25"),
    ],
)
def test_parse_number_with_decimal_hint(text: str, decimal: DecimalMark, expected: str) -> None:
    assert parse_number(text, decimal=decimal) == Decimal(expected)


@pytest.mark.parametrize(
    "text",
    ["", "-", "abc", "1e5", "1,2,3", "1..5", "1.2.3", "1,25.000", "٫5", "5٫", "١٢٫٣٫٤", "١٬٢٣"],
)
def test_parse_number_rejects_invalid(text: str) -> None:
    with pytest.raises(InvalidNumberError, match="Not a valid number"):
        parse_number(text)


@pytest.mark.parametrize("text", ["1,250", "12.500", "١٢،٥٠٠"])
def test_parse_number_rejects_ambiguous(text: str) -> None:
    with pytest.raises(InvalidNumberError, match="Ambiguous"):
        parse_number(text)


@pytest.mark.parametrize(
    ("value", "kw", "expected"),
    [
        (Decimal("125000.5"), {}, "125,000.5"),
        (Decimal("125000.5"), {"digits": "arabic", "grouping": "٬", "decimal": "٫"}, "١٢٥٬٠٠٠٫٥"),
        (Decimal("125000.5"), {"digits": "persian", "grouping": "٬", "decimal": "٫"}, "۱۲۵٬۰۰۰٫۵"),
        (Decimal("125000.5"), {"grouping": None}, "125000.5"),
        (Decimal("125000.5"), {"places": 2}, "125,000.50"),
        (7, {"places": 2}, "7.00"),
        (Decimal("1.50"), {"places": 1}, "1.5"),
        ("١٢٥٬٠٠٠", {}, "125,000"),
        (Decimal("-1234.5"), {}, "-1,234.5"),
        (Decimal("1E+3"), {}, "1,000"),
    ],
)
def test_format_number(value: int | Decimal | str, kw: dict[str, object], expected: str) -> None:
    assert format_number(value, **kw) == expected  # type: ignore[arg-type]


def test_format_number_never_rounds() -> None:
    with pytest.raises(InvalidNumberError, match="more than 1 decimal places"):
        format_number(Decimal("1.25"), places=1)


@pytest.mark.parametrize("value", [Decimal("NaN"), Decimal("Infinity"), "abc"])
def test_format_number_rejects_invalid(value: Decimal | str) -> None:
    with pytest.raises(InvalidNumberError):
        format_number(value)


@pytest.mark.parametrize(
    ("value", "kw", "expected"),
    [
        (Decimal("0.25"), {}, "25٪"),
        (Decimal("0.125"), {"digits": "arabic", "decimal": "٫"}, "١٢٫٥٪"),
        (1, {}, "100٪"),
        (Decimal("0.25"), {"places": 1}, "25.0٪"),
        ("0.5", {}, "50٪"),
    ],
)
def test_format_percent(value: int | Decimal | str, kw: dict[str, object], expected: str) -> None:
    assert format_percent(value, **kw) == expected  # type: ignore[arg-type]


_numbers = st.decimals(
    min_value=-(10**15), max_value=10**15, places=4, allow_nan=False, allow_infinity=False
)
_digit_sets = st.sampled_from(["latin", "arabic", "persian"])


@given(_numbers, _digit_sets)
def test_roundtrip_latin_marks(x: Decimal, digits: DigitSet) -> None:
    assert parse_number(format_number(x, digits=digits), decimal=".") == x


@given(_numbers, _digit_sets)
def test_roundtrip_arabic_marks(x: Decimal, digits: DigitSet) -> None:
    assert parse_number(format_number(x, digits=digits, grouping="٬", decimal="٫")) == x
