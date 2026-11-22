import pytest

from arapy.normalize import Rule
from arapy.normalize.rules import (
    collapse_spaces,
    fold_alef,
    fold_alef_maqsura,
    fold_digits,
    fold_hamza_carriers,
    fold_lookalikes,
    fold_teh_marbuta,
    remove_invisible,
    remove_quranic_marks,
    remove_tashkeel,
    remove_tatweel,
    split_compound_names,
)


@pytest.mark.parametrize(
    ("rule", "text", "expected"),
    [
        (fold_alef, "أحمد إبراهيم آمنة ٱلله", "احمد ابراهيم امنة الله"),
        (fold_alef_maqsura, "مصطفى على", "مصطفي علي"),
        (fold_teh_marbuta, "فاطمة مدرسة", "فاطمه مدرسه"),
        (fold_hamza_carriers, "مسؤول رئيس", "مسوول رييس"),
        (fold_lookalikes, "کتاب علی ہ", "كتاب علي ه"),
        (fold_digits, "٢٠٢٦ و ۲۰۲۶", "2026 و 2026"),
        (remove_tashkeel, "مُحَمَّدٌ", "محمد"),
        (remove_tatweel, "مـــحـمد", "محمد"),
        (remove_quranic_marks, "الرَّحْمَٰنِ ۖ", "الرَّحْمَنِ "),
        (remove_invisible, "‏محمد‌‫علي﻿", "محمدعلي"),
        (split_compound_names, "عبدالله", "عبد الله"),
        (split_compound_names, "عبدالرحمن عبدالعزيز", "عبد الرحمن عبد العزيز"),
        (split_compound_names, "أبوبكر ابوالفضل", "أبو بكر ابو الفضل"),
        (split_compound_names, "ابوعبدالله", "ابو عبد الله"),
        (split_compound_names, "عبد الله أبو بكر", "عبد الله أبو بكر"),
        (split_compound_names, "عبدو ابوه", "عبدو ابوه"),
        (collapse_spaces, "  محمد    علي\t", "محمد علي"),
    ],
)
def test_rule(rule: Rule, text: str, expected: str) -> None:
    assert rule(text) == expected
