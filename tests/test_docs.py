"""Run the examples in README.md and in the docstrings, so the docs cannot drift from the code.

Examples are ```python blocks, run in order in one namespace per file or module. Every
`print(...)  # expected` call must print exactly `expected`; a comment ending in `…` only
has to match the start of the output. Blocks fenced as ```py are illustrations that need fonts
or other packages, and are not run.
"""

import ast
import importlib
import inspect
import re
import textwrap
from collections.abc import Iterator
from pathlib import Path
from types import ModuleType

import pytest

_ROOT = Path(__file__).parent.parent

_BLOCK = re.compile(r"^( *)```python\n(.*?)^\1```", re.MULTILINE | re.DOTALL)

_MODULES = [
    "arapy.dates.ardate",
    "arapy.dates.ardatetime",
    "arapy.dates.hijri",
    "arapy.shape",
    "arapy.words.nouns",
    "arapy.words.tafqeet",
]


def _expected(code: str) -> list[str]:
    """The `# expected` comment after each print() call, in source order."""
    lines = code.splitlines()

    calls = [
        node
        for node in ast.walk(ast.parse(code))
        if isinstance(node, ast.Call) and ast.unparse(node.func) == "print"
    ]

    expected = []

    for call in sorted(calls, key=lambda node: node.lineno):
        line = lines[(call.end_lineno or call.lineno) - 1]

        assert "  # " in line, f"print() without an expected comment: {line!r}"

        expected.append(line.split("  # ", 1)[1])

    return expected


def _run(text: str, source: str) -> int:
    """Run every ```python block in `text` and check its printed output; return the count."""
    printed: list[str] = []

    namespace: dict[str, object] = {"print": lambda *args: printed.append(" ".join(map(str, args)))}

    blocks = [textwrap.dedent(code) for _, code in _BLOCK.findall(text)]

    for code in blocks:
        printed.clear()

        exec(compile(code, source, "exec"), namespace)

        expected = _expected(code)

        assert len(printed) == len(expected), code

        for out, want in zip(printed, expected, strict=True):
            assert out.startswith(want[:-1]) if want.endswith("…") else out == want, (out, want)

    return len(blocks)


def _docstrings(module: ModuleType) -> Iterator[str]:
    yield module.__doc__ or ""

    for obj in vars(module).values():
        if getattr(obj, "__module__", None) != module.__name__:
            continue

        yield inspect.getdoc(obj) or ""

        if isinstance(obj, type):
            for member in vars(obj).values():
                yield inspect.getdoc(getattr(member, "__func__", member)) or ""


def test_readme_examples() -> None:
    pytest.importorskip("hijridate")

    pytest.importorskip("bidi")

    assert _run((_ROOT / "README.md").read_text(encoding="utf-8"), "README.md") > 0


@pytest.mark.parametrize("name", _MODULES)
def test_docstring_examples(name: str) -> None:
    pytest.importorskip("hijridate")

    pytest.importorskip("bidi")

    module = importlib.import_module(name)

    assert _run("\n".join(_docstrings(module)), name) > 0
