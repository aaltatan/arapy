import sys

import pytest

from arapy import MissingExtraError
from arapy.shape import reshape_only, shape


@pytest.mark.parametrize("module", ["arabic_reshaper", "bidi"])
def test_missing_extra(monkeypatch: pytest.MonkeyPatch, module: str) -> None:
    monkeypatch.setitem(sys.modules, module, None)  # makes the import fail

    with pytest.raises(MissingExtraError, match="shape"):
        shape("سلام")


pytest.importorskip("arabic_reshaper")
pytest.importorskip("bidi")


@pytest.mark.parametrize(
    ("text", "reshaped", "shaped"),
    [
        # س initial, lam-alef final ligature, م isolated
        ("سلام", "ﺳﻼﻡ", "ﻡﻼﺳ"),
        # م initial, ر final, ح initial, ب medial, ا final; tashkeel removed
        ("مَرْحَبًا", "ﻣﺮﺣﺒﺎ", "ﺎﺒﺣﺮﻣ"),
        # Latin runs and digits keep their own direction
        ("رقم 123 ABC", "ﺭﻗﻢ 123 ABC", "ABC 123 ﻢﻗﺭ"),
        ("hello", "hello", "hello"),
        ("", "", ""),
    ],
)
def test_shape(text: str, reshaped: str, shaped: str) -> None:
    assert reshape_only(text) == reshaped

    assert shape(text) == shaped


def test_pillow_smoke() -> None:
    image_module = pytest.importorskip("PIL.Image")
    draw_module = pytest.importorskip("PIL.ImageDraw")
    font_module = pytest.importorskip("PIL.ImageFont")

    image = image_module.new("L", (200, 50), color=255)

    draw_module.Draw(image).text((10, 10), shape("سلام عليكم"), font=font_module.load_default(24))

    assert image.getextrema()[0] < 255  # something was drawn
