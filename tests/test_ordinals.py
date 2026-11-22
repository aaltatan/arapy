import pytest

from arapy import OutOfRangeError
from arapy.ordinals import ordinal, ordinal_adverb
from arapy.words import Case, Gender

from . import golden_ordinals as G

_M, _F = Gender.MASCULINE, Gender.FEMININE
_NOM, _ACC, _GEN = Case.NOMINATIVE, Case.ACCUSATIVE, Case.GENITIVE


def _rows(
    table: dict[int, str], gender: Gender, definite: bool, *cases: Case
) -> list[tuple[int, Gender, bool, Case, str]]:
    return [(n, gender, definite, case, text) for case in cases for n, text in table.items()]


@pytest.mark.parametrize(
    ("n", "gender", "definite", "case", "expected"),
    _rows(G.DEFINITE_MASCULINE, _M, True, _NOM)
    + _rows(G.DEFINITE_FEMININE, _F, True, _NOM)
    + _rows(G.DEFINITE_MASCULINE_OBLIQUE, _M, True, _ACC, _GEN)
    + _rows(G.DEFINITE_FEMININE_OBLIQUE, _F, True, _ACC, _GEN)
    + _rows(G.INDEFINITE_MASCULINE_NOMINATIVE, _M, False, _NOM)
    + _rows(G.INDEFINITE_MASCULINE_ACCUSATIVE, _M, False, _ACC)
    + _rows(G.INDEFINITE_MASCULINE_GENITIVE, _M, False, _GEN)
    + _rows(G.INDEFINITE_FEMININE_NOMINATIVE, _F, False, _NOM)
    + _rows(G.INDEFINITE_FEMININE_ACCUSATIVE, _F, False, _ACC),
)
def test_ordinal(n: int, gender: Gender, definite: bool, case: Case, expected: str) -> None:
    assert ordinal(n, gender, definite=definite, case=case) == expected


@pytest.mark.parametrize(("n", "expected"), G.ADVERBS.items())
def test_ordinal_adverb(n: int, expected: str) -> None:
    assert ordinal_adverb(n) == expected


def test_spec_examples() -> None:
    assert ordinal(3, gender=Gender.FEMININE) == "الثالثة"

    assert ordinal(11) == "الحادي عشر"

    assert ordinal(3, definite=False) == "ثالث"

    assert ordinal_adverb(3) == "ثالثًا"


@pytest.mark.parametrize("n", [0, -1, 101])
def test_out_of_range(n: int) -> None:
    with pytest.raises(OutOfRangeError):
        ordinal(n)

    with pytest.raises(OutOfRangeError):
        ordinal_adverb(n)


@pytest.mark.parametrize("n", range(1, 101))
def test_every_ordinal_is_well_formed(n: int) -> None:
    for gender in Gender:
        text = ordinal(n, gender)

        assert text.startswith("ال")

        assert "  " not in text
