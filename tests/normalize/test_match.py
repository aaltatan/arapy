import pytest

from arapy.normalize import SEARCH, ar_equals, ar_key


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [
        ("عبدالله", "عبد الله", True),
        ("أحمد", "احمد", True),
        ("فاطمة", "فاطمه", True),
        ("مسؤول", "مسوول", False),
        ("أحمد", "محمد", False),
    ],
)
def test_ar_equals_names(a: str, b: str, expected: bool) -> None:
    assert ar_equals(a, b) is expected


def test_ar_equals_search_folds_hamza_carriers() -> None:
    assert ar_equals("مسؤول", "مسوول", preset=SEARCH)


def test_ar_key_groups_variants() -> None:
    key = ar_key()

    assert len({key(name) for name in ["عبدالله", "عبد الله", "عَبْدُ اللّه"]}) == 1

    assert {key("أحمد"): 1}[key("احمد")] == 1
