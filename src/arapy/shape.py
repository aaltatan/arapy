"""Shape Arabic text for renderers that cannot (Pillow, ReportLab, ZPL). Needs `arapy[shape]`.

Such renderers draw each code point on its own and left to right, so Arabic comes out as
unjoined letters in the wrong order. `shape()` fixes both.
"""

from arapy._extras import require


def shape(text: str) -> str:
    """Join the letters and put the text in visual (left-to-right) order, ready to draw.

    ```python
    from arapy import shape

    print(ascii(shape("سلام")))  # '\\ufee1\\ufefc\\ufeb3'
    ```
    """
    bidi = require("shape", "bidi")

    return str(bidi.get_display(reshape_only(text)))


def reshape_only(text: str) -> str:
    """Join the letters (presentation forms and lam-alef ligatures) but keep logical order.

    Use it when the renderer applies the bidi algorithm itself. Tashkeel is removed, which is
    `arabic-reshaper`'s default.
    """
    arabic_reshaper = require("shape", "arabic_reshaper")

    return str(arabic_reshaper.reshape(text))
