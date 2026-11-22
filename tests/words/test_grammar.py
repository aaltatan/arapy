import pytest
from hypothesis import given
from hypothesis import strategies as st

from arapy import OutOfRangeError
from arapy.words import Case, Gender
from arapy.words.grammar import MAX_INTEGER, integer_to_words

from .golden_integers import (
    FEMININE_NOMINATIVE,
    FEMININE_OBLIQUE,
    MAIA_SPELLING,
    MASCULINE_NOMINATIVE,
    MASCULINE_OBLIQUE,
)


@pytest.mark.parametrize(("n", "expected"), MASCULINE_NOMINATIVE.items())
def test_masculine_nominative(n: int, expected: str) -> None:
    assert integer_to_words(n) == expected


@pytest.mark.parametrize(("n", "expected"), FEMININE_NOMINATIVE.items())
def test_feminine_nominative(n: int, expected: str) -> None:
    assert integer_to_words(n, gender=Gender.FEMININE) == expected


@pytest.mark.parametrize("case", [Case.ACCUSATIVE, Case.GENITIVE])
@pytest.mark.parametrize(("n", "expected"), MASCULINE_OBLIQUE.items())
def test_masculine_oblique(n: int, expected: str, case: Case) -> None:
    assert integer_to_words(n, case=case) == expected


@pytest.mark.parametrize("case", [Case.ACCUSATIVE, Case.GENITIVE])
@pytest.mark.parametrize(("n", "expected"), FEMININE_OBLIQUE.items())
def test_feminine_oblique(n: int, expected: str, case: Case) -> None:
    assert integer_to_words(n, gender=Gender.FEMININE, case=case) == expected


@pytest.mark.parametrize(("n", "expected"), MAIA_SPELLING.items())
def test_maia_spelling(n: int, expected: str) -> None:
    assert integer_to_words(n, hundreds="مائة") == expected


@pytest.mark.parametrize(("n", "expected"), [(-5, "سالب خمسة"), (-1000, "سالب ألف")])
def test_negative(n: int, expected: str) -> None:
    assert integer_to_words(n) == expected


@pytest.mark.parametrize("n", [MAX_INTEGER + 1, -(MAX_INTEGER + 1), 10**20])
def test_out_of_range(n: int) -> None:
    with pytest.raises(OutOfRangeError):
        integer_to_words(n)


@given(st.integers(-MAX_INTEGER, MAX_INTEGER), st.sampled_from(Gender), st.sampled_from(Case))
def test_well_formed(n: int, gender: Gender, case: Case) -> None:
    words = integer_to_words(n, gender=gender, case=case)

    assert words == words.strip()

    assert "  " not in words

    assert not words.endswith("و")
