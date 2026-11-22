"""Run the examples in README.md and in the docstrings, so the docs cannot drift from the code."""

import doctest
import importlib
from pathlib import Path

import pytest

_ROOT = Path(__file__).parent.parent

_MODULES = [
    "arapy.dates.ardate",
    "arapy.dates.ardatetime",
    "arapy.dates.hijri",
    "arapy.shape",
    "arapy.words.tafqeet",
]


def test_readme_examples() -> None:
    pytest.importorskip("hijridate")

    result = doctest.testfile(str(_ROOT / "README.md"), module_relative=False, encoding="utf-8")

    assert result.attempted > 0

    assert result.failed == 0


@pytest.mark.parametrize("name", _MODULES)
def test_docstring_examples(name: str) -> None:
    pytest.importorskip("hijridate")

    pytest.importorskip("bidi")

    result = doctest.testmod(importlib.import_module(name))

    assert result.failed == 0
