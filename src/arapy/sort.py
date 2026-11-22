"""Arabic alphabetical ordering."""

from collections.abc import Callable, Iterable
from typing import overload

from arapy._letters import (
    ALEF,
    ALEF_FORMS,
    ALEF_MAQSURA,
    TEH,
    TEH_MARBUTA,
    WAW,
    WAW_HAMZA,
    YEH,
    YEH_HAMZA,
)
from arapy.normalize import SORT, Normalizer

# Unicode already orders the base letters ء ا ب ت … ن ه و ي alphabetically, so folding the
# variants onto their base letter is enough.
_ORDER = str.maketrans(
    {
        **dict.fromkeys(ALEF_FORMS, ALEF),
        TEH_MARBUTA: TEH,
        WAW_HAMZA: WAW,
        YEH_HAMZA: YEH,
        ALEF_MAQSURA: YEH,
    }
)


def ar_sort_key(text: str, *, normalizer: Normalizer = SORT) -> tuple[str, str]:
    """Key for Arabic alphabetical order. Ties between folded letters (أ/ا) break by spelling."""
    clean = normalizer(text)

    return clean.translate(_ORDER), clean


@overload
def ar_sorted(
    items: Iterable[str], *, normalizer: Normalizer = ..., reverse: bool = ...
) -> list[str]: ...


@overload
def ar_sorted[T](
    items: Iterable[T],
    *,
    key: Callable[[T], str],
    normalizer: Normalizer = ...,
    reverse: bool = ...,
) -> list[T]: ...


def ar_sorted[T](
    items: Iterable[T],
    *,
    key: Callable[[T], str] | None = None,
    normalizer: Normalizer = SORT,
    reverse: bool = False,
) -> list[T]:
    """Sort in Arabic alphabetical order; `key` picks the text to sort by from each item."""
    get_text: Callable[[T], str] = key or str

    return sorted(
        items,
        key=lambda item: ar_sort_key(get_text(item), normalizer=normalizer),
        reverse=reverse,
    )
