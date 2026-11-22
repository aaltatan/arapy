import pytest
from hypothesis import given
from hypothesis import strategies as st

from arapy.normalize import NAMES, SEARCH, SORT, Normalizer


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("  أَحْمَدُ   إبراهيم ", "احمد ابراهيم"),
        ("مسؤول رئيس", "مسوول رييس"),
        ("مدرسة على ١٢", "مدرسه علي 12"),
        ("کتاب‏", "كتاب"),
        ("عبدالله", "عبدالله"),
    ],
)
def test_search(text: str, expected: str) -> None:
    assert SEARCH(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("عَبْدُالله", "عبد الله"),
        ("أبوبكر   الصدّيق", "ابو بكر الصديق"),
        ("فاطمة", "فاطمه"),
        ("مصطفى", "مصطفي"),
        ("مسؤول", "مسؤول"),
        ("‏مـحـمد", "محمد"),
    ],
)
def test_names(text: str, expected: str) -> None:
    assert NAMES(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("أَحْمَد  ١٢", "أحمد 12"),
        ("مدرسة", "مدرسة"),
    ],
)
def test_sort_preset(text: str, expected: str) -> None:
    assert SORT(text) == expected


_pieces = st.sampled_from(
    ["عبد", "ال", "ابو", "أبو", "له", "بكر", "ة", "ى", "ؤ", "ئ", "ی", "ـ", "َ", "ٰ", " ", "‏", "١"]
)
_arabic_text = st.one_of(
    st.lists(_pieces).map("".join),
    st.text(st.characters(min_codepoint=0x0600, max_codepoint=0x06FF) | st.sampled_from("  ")),
)


@pytest.mark.parametrize("preset", [SEARCH, NAMES, SORT], ids=["SEARCH", "NAMES", "SORT"])
@given(text=_arabic_text)
def test_idempotent(preset: Normalizer, text: str) -> None:
    once = preset(text)

    assert preset(once) == once
