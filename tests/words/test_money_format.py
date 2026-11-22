from decimal import Decimal

import pytest

from arapy import InvalidNumberError
from arapy.words import Currency, Gender, Noun, format_money, noun_forms
from arapy.words.currencies import CURRENCIES, KWD, SYP, USD


@pytest.mark.parametrize(
    ("value", "currency", "kw", "expected"),
    [
        (12500, SYP, {}, "١٢٬٥٠٠ ل.س"),
        (Decimal("12500.5"), SYP, {}, "١٢٬٥٠٠٫٥٠ ل.س"),
        (Decimal("12500.50"), SYP, {}, "١٢٬٥٠٠٫٥٠ ل.س"),
        ("١٢٥٠٠", SYP, {}, "١٢٬٥٠٠ ل.س"),
        (Decimal("1.5"), KWD, {}, "١٫٥٠٠ د.ك"),
        ("1.500", KWD, {}, "١٫٥٠٠ د.ك"),
        (Decimal("-3"), USD, {}, "-٣ $"),
        (
            Decimal("1250.5"),
            USD,
            {"digits": "latin", "grouping": ",", "decimal": "."},
            "1,250.50 $",
        ),
        (12500, SYP, {"places": 2}, "١٢٬٥٠٠٫٠٠ ل.س"),
    ],
)
def test_format_money(
    value: int | Decimal | str, currency: Currency, kw: dict[str, object], expected: str
) -> None:
    assert format_money(value, currency, **kw) == expected  # type: ignore[arg-type]


def test_never_rounds() -> None:
    with pytest.raises(InvalidNumberError):
        format_money(Decimal("1.005"), SYP)


def test_falls_back_to_code() -> None:
    custom = Currency(
        forms=noun_forms("نقطة", "نقطتان", "نقاط"),
        gender=Gender.FEMININE,
        code="XPT",
        subunit=Noun.create("جزء", "جزءان", "أجزاء", gender=Gender.MASCULINE),
    )

    assert format_money(7, custom) == "٧ XPT"


def test_every_builtin_has_a_symbol() -> None:
    assert all(c.symbol for c in CURRENCIES.values())
