# Reference

API pages, generated from the docstrings and type hints in the source:

- [Words (تفقيط)](words.md): `Tafqeet`, `to_words`, `Noun`, `Currency`, `Gender`, `Case`,
  `PluralForm`, `format_money`, and the grammar and parsing engines.
- [Digits](digits.md): digit conversion, `parse_number`, `format_number`, `format_percent`.
- [Normalize](normalize.md): `Normalizer`, the presets, the rules, `ar_equals`, `ar_key`.
- [Sort](sort.md): `ar_sort_key`, `ar_sorted`.
- [Ordinals](ordinals.md): `ordinal`, `ordinal_adverb`.
- [Dates](dates.md): `ArDate`, `ArDateTime`, `HijriDate`, `MonthNames`, `ar_since`,
  `ar_duration`.
- [Shape](shape.md): `shape`, `reshape_only`.

Formats and errors:

- [Date formats](date-formats.md): every `format()` / `strptime()` directive.
- [Exceptions](exceptions.md): the error hierarchy and when each one is raised.

## Top-level names

The most-used names are importable from `arapy` itself:

```python
import arapy

print(len(arapy.__all__))  # 37
print("to_words" in arapy.__all__, "PluralForm" in arapy.__all__)  # True False
```

| Area | Names in `arapy` |
| --- | --- |
| Words | `Tafqeet`, `to_words`, `Noun`, `Currency`, `Gender`, `Case`, `format_money` |
| Digits | `to_arabic_digits`, `to_latin_digits`, `to_persian_digits`, `parse_number`, `format_number`, `format_percent` |
| Normalize | `Normalizer`, `SEARCH`, `NAMES`, `ar_equals`, `ar_key` |
| Sort | `ar_sort_key`, `ar_sorted` |
| Ordinals | `ordinal`, `ordinal_adverb` |
| Dates | `ArDate`, `ArDateTime`, `HijriDate`, `MonthNames`, `ar_since`, `ar_duration` |
| Shape | `shape`, `reshape_only` |
| Errors | `ArapyError`, `InvalidNumberError`, `OutOfRangeError`, `ParseError`, `FormatError`, `MissingExtraError` |
| Metadata | `__version__` |

The rest live in their subpackage:

| Name | Import from |
| --- | --- |
| `PluralForm`, `Hundreds`, `noun_forms`, `plural_form` | `arapy.words` |
| `SORT`, `Rule` | `arapy.normalize` |
| `fold_alef`, `remove_tashkeel`, … (every rule) | `arapy.normalize.rules` |
| `MONTHS`, `WEEKDAYS`, `HIJRI_MONTHS`, `RelativeDeltaLike` | `arapy.dates` |
| `DigitSet`, `DecimalMark` | `arapy.digits` |
