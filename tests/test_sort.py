from dataclasses import dataclass

import pytest

from arapy.sort import ar_sort_key, ar_sorted


@pytest.mark.parametrize(
    ("words", "expected"),
    [
        # Alef forms sort as ا (in codepoint order آ أ إ all come before ا).
        (["يوسف", "باسل", "أحمد", "زياد"], ["أحمد", "باسل", "زياد", "يوسف"]),
        (["إيمان", "اسماء", "آمنة", "بشير"], ["اسماء", "آمنة", "إيمان", "بشير"]),
        # ة sorts as ت.
        (["مدرسه", "مدرسة", "مدرسب"], ["مدرسب", "مدرسة", "مدرسه"]),
        # ى and ئ sort as ي, ؤ as و.
        (["هدى", "هدن"], ["هدن", "هدى"]),
        (["سؤال", "سهل"], ["سهل", "سؤال"]),
        # Tashkeel and tatweel are ignored.
        (["مُحَمَّد", "مازن"], ["مازن", "مُحَمَّد"]),
        (["مـحمد", "مجد"], ["مجد", "مـحمد"]),
    ],
)
def test_ar_sorted(words: list[str], expected: list[str]) -> None:
    assert ar_sorted(words) == expected


def test_ties_break_by_spelling() -> None:
    assert ar_sort_key("أحمد")[0] == ar_sort_key("احمد")[0]

    assert ar_sorted(["أحمد", "احمد"]) == ar_sorted(["احمد", "أحمد"])


def test_reverse() -> None:
    assert ar_sorted(["باسل", "أحمد"], reverse=True) == ["باسل", "أحمد"]


@dataclass
class Employee:
    name: str


def test_key() -> None:
    staff = [Employee("يوسف"), Employee("أحمد")]

    assert [e.name for e in ar_sorted(staff, key=lambda e: e.name)] == ["أحمد", "يوسف"]
