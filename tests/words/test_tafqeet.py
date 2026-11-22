from dataclasses import FrozenInstanceError
from decimal import Decimal

import pytest

from arapy import InvalidNumberError, OutOfRangeError
from arapy.words import Case, Tafqeet, to_words


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (125, "مئة وخمسة وعشرون"),
        (Decimal("125"), "مئة وخمسة وعشرون"),
        (Decimal("125.00"), "مئة وخمسة وعشرون"),
        ("١٢٥٬٠٠٠", "مئة وخمسة وعشرون ألفًا"),
        (-3, "سالب ثلاثة"),
        (0, "صفر"),
    ],
)
def test_to_words(value: int | Decimal | str, expected: str) -> None:
    assert to_words(value) == expected


def test_prefix_suffix() -> None:
    assert Tafqeet(prefix="فقط", suffix="لا غير")(125) == "فقط مئة وخمسة وعشرون لا غير"


def test_options() -> None:
    assert Tafqeet(hundreds="مائة", case=Case.ACCUSATIVE)(222) == "مائتين واثنين وعشرين"


@pytest.mark.parametrize("value", [Decimal("1.5"), "12٫5", Decimal("NaN"), Decimal("Infinity")])
def test_rejects_fractions_and_non_finite(value: Decimal | str) -> None:
    with pytest.raises(InvalidNumberError):
        to_words(value)


def test_out_of_range() -> None:
    with pytest.raises(OutOfRangeError):
        to_words(10**15)


def test_frozen() -> None:
    with pytest.raises(FrozenInstanceError):
        to_words.prefix = "فقط"  # type: ignore[misc]
