# Shaping for images and PDFs

Arabic letters change shape with their position in a word, and Arabic runs right to left.
Browsers, word processors and most GUI toolkits handle both. Pillow, ReportLab and ZPL label
printers do not: they draw each code point on its own, left to right, so Arabic comes out as
unjoined letters in reverse order.

`arapy.shape` fixes that. It needs `arapy[shape]` (`arabic-reshaper` and `python-bidi`).

| Function | Joins letters | Visual order | Use with |
| --- | --- | --- | --- |
| `shape(text)` | yes | yes | Pillow, ReportLab, ZPL, anything that draws left to right |
| `reshape_only(text)` | yes | no | renderers that apply the bidi algorithm themselves |

```python
from arapy import reshape_only, shape

print(reshape_only("سلام"))  # ﺳﻼﻡ
print(shape("سلام"))  # ﻡﻼﺳ
print(shape("رقم 123"))  # 123 ﻢﻗﺭ
```

`shape` returns presentation forms (and lam-alef ligatures) in visual order. Tashkeel is
removed, which is `arabic-reshaper`'s default. Shape text only at the point of drawing: the
result is no longer searchable or sortable Arabic.

## With Pillow

```py
from PIL import Image, ImageDraw, ImageFont

from arapy import shape

image = Image.new("RGB", (400, 100), "white")
font = ImageFont.truetype("NotoNaskhArabic-Regular.ttf", 40)

ImageDraw.Draw(image).text((20, 20), shape("مرحبًا بالعالم"), font=font, fill="black")

image.save("hello.png")
```

## With ReportLab

```py
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from arapy import shape

pdfmetrics.registerFont(TTFont("Naskh", "NotoNaskhArabic-Regular.ttf"))

pdf = canvas.Canvas("invoice.pdf")
pdf.setFont("Naskh", 16)
pdf.drawRightString(550, 800, shape("فاتورة رقم ١٢٥"))
pdf.save()
```

Use a font that has the Arabic presentation forms (Noto Naskh Arabic, Amiri, Cairo, …), and
align right with `drawRightString` so lines end at the right margin.

## With a ZPL label printer

ZPL needs a Unicode font on the printer and `^CI28` (UTF-8). Send the shaped text in `^FD`:

```py
from arapy import shape

zpl = f"^XA^CI28^CF0,40^FO50,50^FD{shape('صنع في سوريا')}^FS^XZ"
```
