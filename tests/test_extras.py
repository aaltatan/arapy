import pytest

from arapy import MissingExtraError
from arapy._extras import require


def test_require_returns_module() -> None:
    assert require("hijri", "json").__name__ == "json"


def test_require_missing_raises() -> None:
    with pytest.raises(MissingExtraError, match=r"arapy\[shape\]") as info:
        require("shape", "arapy_no_such_module")

    assert isinstance(info.value.__cause__, ImportError)
