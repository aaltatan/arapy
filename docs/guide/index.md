# User guide

arapy is a set of small modules. Each page covers one of them with examples you can paste
and run: every `python` block in these docs is executed by the test suite, and the comment
after each `print()` is its output.

| Module | What it does | Page |
| --- | --- | --- |
| `arapy.words` | numbers, counted nouns and money in words (تفقيط), and back | [Amounts in words](words.md) |
| `arapy.digits` | Arabic, Persian and Latin digits; exact parsing and formatting | [Digits and numbers](digits.md) |
| `arapy.normalize` | composable rules that fold letters and strip marks; matching | [Normalization](normalize.md) |
| `arapy.sort` | Arabic alphabetical order | [Sorting](sort.md) |
| `arapy.ordinals` | الأول، الأولى، الحادي عشر، أولًا | [Ordinals](ordinals.md) |
| `arapy.dates` | `ArDate`, `ArDateTime`, `HijriDate`, Arabic formatting and parsing | [Dates](dates.md) |
| `arapy.dates` | «منذ ثلاثة أيام», «سنة وثلاثة أشهر» | [Relative times and durations](humanize.md) |
| `arapy.shape` | joined, visually ordered text for Pillow, ReportLab and ZPL | [Shaping](shape.md) |

## Conventions across the package

- **Imports.** The names you use most are importable from `arapy` itself. Less common ones
  live in their module: `arapy.words.PluralForm`, `arapy.normalize.rules.fold_alef`,
  `arapy.dates.HIJRI_MONTHS`.
- **Numbers in.** Functions that take a number accept `int`, `Decimal` or a string in any digit
  set. Strings go through [`parse_number`](digits.md#parsing-numbers), so `"١٢٥٠٫٥"` and
  `"1,250.5"` both work. `float` is not accepted: it cannot hold money exactly.
- **Nothing is rounded.** A value with more decimal places than the output allows raises
  `InvalidNumberError` instead of being rounded or cut.
- **Frozen config objects.** `Tafqeet`, `Noun`, `Currency`, `Normalizer` and `HijriDate` are
  immutable. Build them once, at module level, and pass them around.
- **No global registry.** arapy ships no currencies and registers nothing. You define the
  currencies and nouns you need as values.
- **Errors.** Every error subclasses `ArapyError` and the matching built-in exception. See
  [Errors](../reference/exceptions.md).
