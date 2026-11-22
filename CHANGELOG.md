# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses
[Semantic Versioning](https://semver.org/).

## [0.1.0] - 2026-11-22

First usable release.

### Added

- `arapy.words`: amounts and counts in Arabic words (`to_words`, `Tafqeet`) with gender agreement,
  CLDR plurals, case, construct forms, currencies with subunits, and parsing words back to
  numbers; `Noun.create` and `Currency.create` to define your own units (no built-in currencies);
  `format_money`.
- `arapy.digits`: convert between Latin, Arabic-Indic and Persian digits; strict `parse_number`
  that rejects ambiguous separators; exact `format_number` and `format_percent`.
- `arapy.normalize`: composable normalization rules, the `SEARCH`, `NAMES` and `SORT` presets,
  `ar_equals` and `ar_key`.
- `arapy.sort`: Arabic alphabetical ordering with `ar_sort_key` and `ar_sorted`.
- `arapy.ordinals`: `ordinal` (definite, indefinite, every case, both genders) and
  `ordinal_adverb`.
- `arapy.dates`: `ArDate` and `ArDateTime` (`date`/`datetime` subclasses) with Arabic formatting,
  `%O` ordinal days and strict parsing in any digit set; Levantine, Egyptian and Maghrebi month
  names; `HijriDate` (Umm al-Qura, `arapy[hijri]`); `ar_since` and `ar_duration`.
- `arapy.shape`: `shape` and `reshape_only` for drawing Arabic text (`arapy[shape]`).
- Top-level re-exports of the most-used names, a bilingual README and a documentation site.

## [0.0.1] - 2026-11-22

### Added

- Placeholder release to reserve the name on PyPI.
- Error hierarchy (`ArapyError` and subclasses) and the package scaffold.

[0.1.0]: https://github.com/aaltatan/arapy/releases/tag/v0.1.0
[0.0.1]: https://github.com/aaltatan/arapy/releases/tag/v0.0.1
