import pytest

from arapy import _letters as L


def test_alef_forms() -> None:
    assert set("أإآٱ") == L.ALEF_FORMS

    assert L.ALEF not in L.ALEF_FORMS


def test_tashkeel() -> None:
    assert set("ًٌٍَُِّْ") == L.TASHKEEL

    assert L.TATWEEL == "ـ"


@pytest.mark.parametrize("digits", [L.LATIN_DIGITS, L.ARABIC_DIGITS, L.PERSIAN_DIGITS])
def test_digit_index_is_value(digits: str) -> None:
    assert [int(d) for d in digits] == list(range(10))
