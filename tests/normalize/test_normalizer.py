from dataclasses import FrozenInstanceError

import pytest

from arapy.normalize import Normalizer
from arapy.normalize.rules import collapse_spaces, fold_alef, remove_tashkeel


def test_applies_rules_in_order() -> None:
    normalize = Normalizer([remove_tashkeel, fold_alef])

    assert normalize("أَحْمَد") == "احمد"


def test_rules_stored_as_tuple() -> None:
    assert Normalizer([fold_alef]).rules == (fold_alef,)


def test_add_rule_and_normalizer() -> None:
    base = Normalizer([fold_alef])

    assert (base + collapse_spaces).rules == (fold_alef, collapse_spaces)

    assert (base + Normalizer([remove_tashkeel])).rules == (fold_alef, remove_tashkeel)


def test_frozen() -> None:
    with pytest.raises(FrozenInstanceError):
        Normalizer([]).rules = ()  # type: ignore[misc]


def test_empty_is_identity() -> None:
    assert Normalizer([])("أَحمد") == "أَحمد"
