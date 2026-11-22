"""Ready-made normalizers."""

from arapy.normalize.normalizer import Normalizer
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

_CLEAN = (remove_invisible, remove_tashkeel, remove_quranic_marks, remove_tatweel, fold_lookalikes)

SEARCH = Normalizer(
    (
        *_CLEAN,
        fold_alef,
        fold_alef_maqsura,
        fold_teh_marbuta,
        fold_hamza_carriers,
        fold_digits,
        collapse_spaces,
    )
)
"""Loose matching for search: folds letters, hamza carriers and digits."""

NAMES = Normalizer(
    (
        *_CLEAN,
        fold_alef,
        fold_alef_maqsura,
        fold_teh_marbuta,
        split_compound_names,
        collapse_spaces,
    )
)
"""Matching personal names: like SEARCH, but keeps hamza carriers and splits compound names."""

SORT = Normalizer((*_CLEAN, fold_digits, collapse_spaces))
"""Cleanup before sorting. Letter folding for order happens in `arapy.sort`."""
