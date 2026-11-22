# PHASES.md — arapy build plan

Each phase is sized for one Claude Code session. A phase is done when its checklist is ticked and
`ruff check`, `ruff format --check`, `mypy --strict` and `pytest` all pass.

---

## Phase 0 — Scaffold

- [x] `uv init --lib arapy` with the `src/` layout, `py.typed`, Python `>=3.12`
- [x] pyproject: extras `hijri = ["hijridate"]`, `shape = ["arabic-reshaper", "python-bidi"]`, dev group (ruff, mypy, pytest, hypothesis)
- [x] ruff config (line length, isort, pyupgrade), mypy strict config
- [x] `errors.py`: `ArapyError`, `InvalidNumberError`, `OutOfRangeError`, `ParseError`, `MissingExtraError(extra: str)`
- [x] `_letters.py`: letter constants and character classes (tashkeel, tatweel, alef forms, Arabic-Indic and Persian digits)
- [x] `_extras.py`: `require(extra, module)` helper for lazy imports that raises `MissingExtraError`
- [x] GitHub Actions CI: lint, type check, tests on 3.12 and 3.13, with and without extras
- [x] Reserve the name on PyPI (0.0.1 placeholder)

## Phase 1 — digits

- [x] `to_latin_digits`, `to_arabic_digits`, `to_persian_digits`
- [x] `parse_number(text) -> Decimal` (Arabic ٬ ٫, Latin `,` `.`, Arabic comma ،, sign, ambiguity errors)
- [x] `format_number(...)` with digit set, grouping, decimal mark, places
- [x] `format_percent(...)` (٪)
- [x] Property test: `parse_number(format_number(x, ...)) == x`
- Note: `format_money` lands in Phase 5 inside `words/money.py`, once `Currency` exists (`digits` never imports `words`)

## Phase 2 — normalize + sort

- [x] `rules.py`: alef folding, yaa/alef maqsura, taa marbuta, hamza carriers, tashkeel, tatweel, Quranic marks, zero-width/bidi controls, Persian/Urdu lookalikes, compound names, space collapsing, digit folding
- [x] `Normalizer` (frozen, callable, composable: `Normalizer(rules) + rule`)
- [x] Presets `SEARCH`, `NAMES`
- [x] `ar_equals`, `ar_key`
- [x] `sort.py`: `ar_sort_key`, `ar_sorted`
- [x] Property test: every preset is idempotent

## Phase 3 — words: integer engine

- [x] `grammar.py`: integers 0 … 10^15 − 1 → words, masculine/feminine, `Case`, `hundreds` spelling
- [x] Teens, tens, compounds (أحد عشر / إحدى عشرة، اثنا عشر / اثنتا عشرة), hundreds (مئة، مئتان، ثلاثمئة), thousands/millions/billions/trillions with dual and plural (ألفان، آلاف، ملايين)
- [x] Golden table `tests/words/golden_integers.py` (maintainer reviews it before the phase closes) — reviewed and approved
- [x] `Tafqeet` config object (hundreds, case, prefix, suffix) and the `to_words` shortcut, without units yet
- [x] Negatives («سالب …»)

## Phase 4 — words: nouns, currencies, fractions

- [x] `nouns.py`: `Gender`, `PluralForm`, CLDR category function, `Noun` (+ builder helpers), `Currency`
- [x] Noun agreement: 1 and 2 as adjectives after the noun, 3–10 reversed gender + plural, 11–99 تمييز, 100+ singular
- [x] `currencies.py`: SYP, USD, EUR, SAR, AED, EGP, JOD, LBP, TRY, KWD, IQD, QAR, BHD, OMR, GBP (read-only mapping + module attributes)
- [x] Fractions → subunit words using `ratio`; error on too many decimal places
- [x] `str` input through `parse_number`
- [x] Golden table `tests/words/golden_money.py` (SYP feminine, USD masculine, KWD 1000 ratio) — reviewed and approved
- [x] Counted-noun examples (ساعة، موظف، يوم)

## Phase 5 — words: parse + format_money

- [x] `parse.py`: words → `Decimal` (both spellings, all cases, prefix/suffix, tashkeel tolerant, units and subunits)
- [x] Property test: `parse(to_words(n, unit)) == n` across ranges and currencies
- [x] `words/money.py`: `format_money(value, currency, ...)` → «١٢٬٥٠٠ ل.س»

## Phase 6 — ordinals

- [x] `ordinal(n, gender, definite=True, case=...)`: الأول/الأولى … الحادي عشر/الحادية عشرة … العشرون … المئة
- [x] Indefinite forms (أول، ثانٍ، ثالث)
- [x] `ordinal_adverb(n)` (أولًا، ثانيًا…)
- [x] Golden tables (`tests/golden_ordinals.py`) — reviewed and approved

## Phase 7 — dates: ArDate

- [ ] `months.py`: `MonthNames` styles LEVANT, EGYPTIAN, MAGHREB, LEVANT_WITH_EGYPTIAN; weekday names; Hijri month names
- [ ] `formatting.py`: shared formatter and strict parser (strftime directives + `%O` ordinal day, any digit set)
- [ ] `ArDate`: type-preserving `__add__`/`__radd__`/`__sub__`/`replace`/classmethods; `.format()`, `strptime()`, `weekday_name`, `month_name()`, `from_date()`
- [ ] Ordinal dates: «الخامس من كانون الثاني ٢٠٢٦»
- [ ] Property test: `ArDate.strptime(d.format(f), f) == d`
- [ ] mypy test file asserting `reveal_type(ArDate(...) + timedelta(1))` is `ArDate`

## Phase 8 — dates: ArDateTime, HijriDate, humanize

- [ ] `ArDateTime` with the same guarantees + `%p` → صباحًا/مساءً
- [ ] `HijriDate` (frozen, slotted, lazy `hijridate`): date-like API, arithmetic, comparison with `date`, `to_gregorian()`, `.format()`, `strptime()`; `ArDate.to_hijri()`
- [ ] `humanize.py`: `ar_since`, `ar_duration` using `words` + `Noun` (يوم، شهر، سنة، ساعة، دقيقة)
- [ ] Tests skipped without `[hijri]`

## Phase 9 — shape

- [ ] `shape(text)`, `reshape_only(text)` typed wrappers (lazy extras)
- [ ] Pillow smoke test (optional dev dependency)

## Phase 10 — Release 0.1.0

- [ ] Bilingual README (English + Arabic) with one example per module
- [ ] Docs site (mkdocs-material) with an API reference
- [ ] CHANGELOG, version bump, publish to PyPI with trusted publishing

## Phase 11+ — Integrations (separate phases, after 0.1.0)

- [ ] **11 — Jinja2:** `arapy.jinja` filters (`tafqeet`, `ar_date`, `ar_digits`, `ordinal`) for templify, uniscope, qrbar
- [ ] **12 — Parse preprocessors:** register normalize/digits rules with the argument-preprocessing package
- [ ] **13 — Django:** `arapy.django` template filters, form fields and validators that accept Arabic digits
- [ ] **14 — Excel:** xlwings UDFs (`=TAFQEET(A1, "SYP")`) and/or a CLI the VBA workbook can call
- [ ] **15 — arapy-cli:** separate typer package (`arapy words 125000 --currency SYP`, `arapy date …`, `arapy normalize …`)

---

## Open questions (maintainer decides)

1. ~~**101 / 102 with a unit:** «مئة ليرة وليرة» / «مئة وليرتان» vs «مئة وواحدة ليرة» / «مئة واثنتان ليرة»?~~ **Decided:** «مئة ليرة وليرة» / «مئة ليرة وليرتان».
2. ~~**Dual thousands before a noun:** «ألفا ليرة» (construct) vs «ألفان من الليرات» vs «ألفان ليرة»?~~ **Decided:** construct «ألفا ليرة».
3. ~~**Plain 1 and 2 with a unit:** always «ليرة سورية واحدة» or just «ليرة سورية»?~~ **Decided:** «ليرة سورية واحدة», «ليرتان سوريتان».
4. ~~**Tanween in output:** «قرشًا» / «دولارًا» always written, or only when `case` ≠ nominative?~~ **Decided:** always written (ًا).
5. ~~**ة → ه folding** in the `SEARCH` preset only, or also in `NAMES`?~~ **Decided:** both presets.
6. **Repo layout for arapy-cli:** same repo as a uv workspace, or a separate repo? (arapy itself stays a single package.)

## Decisions (Phase 2)

- ة → ه folding is in both `SEARCH` and `NAMES`.
- ؤ → و and ئ → ي folding is in `SEARCH` only (the rule is still available to add to any normalizer).
- Compound names are split with a space: عبدالله → عبد الله, ابوبكر → ابو بكر.
- Sorting: ة sorts as ت; alef forms as ا; ؤ as و; ئ and ى as ي.

## Decisions (Phase 3)

- Tanween is always written on the تمييز after 11–99: «أحد عشر ألفًا»، «خمسة وعشرون مليونًا».
- A scale group ending in 1 or 2 after a hundred repeats the scale word: 101,000 → «مئة ألف وألف», 102,000 → «مئة ألف وألفان».
- 10^9 is مليار (plural مليارات); 10^12 is تريليون (plural تريليونات).
- 800 is ثمانمئة; feminine 8 is always ثماني (ثماني عشرة، ثماني وعشرون).
- Hundreds in construct before a scale word drop the ن: 200,000 → «مئتا ألف» (oblique «مئتي ألف»).
- Scale words are masculine, so their counts use masculine agreement («ثلاثة آلاف»); only the last group (below 1000) follows the requested gender.
- `case` changes only the dual and sound-plural endings (اثنان/اثنين، اثنا/اثني، عشرون/عشرين، مئتان/مئتين، ألفان/ألفين). The تمييز after a number does not change.
- A bare number (no unit) is masculine.

## Decisions (Phase 4)

- 101 / 102 with a unit repeat the noun: «مئة ليرة سورية وليرة سورية», «مئة ليرة سورية وليرتان سوريتان» (same for 1001, 1,000,002, …).
- Before a noun, the last dual or hundred is in construct: «ألفا ليرة»، «مليونا ليرة»، «مئتا ليرة» (oblique «ألفي»، «مئتي»).
- Before a noun, a scale word after 11–99 loses its tanween: «أحد عشر ألف ليرة», «مئة وخمسة وعشرون ألف ليرة».
- Exactly 1 adds واحد/واحدة after the noun («ليرة سورية واحدة»); exactly 2 is the dual alone («ليرتان سوريتان»).
- Tanween is written on every word of the تمييز after 11–99: «إحدى عشرة ليرةً سوريةً», «أحد عشر دولارًا أمريكيًا»; words ending in ا/و/ى (يورو) take none.
- An amount below one main unit is written in the subunit only: 0.50 USD → «خمسون سنتًا».
- 0 with a unit: «صفر ليرة سورية».
- USD is «دولار أمريكي».
- For a currency with 1000 subunits, a string amount reads `.` as the decimal mark: `to_words("1.500", KWD)` → «دينار كويتي واحد وخمسمئة فلس»; "1,500" is 1500. `٫` is always the decimal mark, even when `parse_number` gets a `decimal` hint.

## Decisions (Phase 5)

- `Tafqeet.parse(text, unit=None)` takes the counted unit as an optional argument, so it can read unit and subunit words and use the currency's `ratio`. It strips only the `Tafqeet`'s own prefix and suffix.
- `Currency` gains `symbol: str = ""`. The built-ins use Arabic abbreviations (ل.س، ر.س، د.ك، …) and $ € £ for USD, EUR and GBP. Custom currencies with no symbol show their code.
- `format_money` defaults to Arabic digits with ٬ and ٫. With no `places`, whole amounts show no decimals and other amounts are padded to the subunit places (2, or 3 for 1000-ratio currencies).

## Decisions (Phase 6)

- `ordinal` and `ordinal_adverb` cover 1–100; anything else raises `OutOfRangeError`.
- 21st, 31st, …: «الحادي والعشرون» / «الحادية والعشرون»; 11th: «الحادي عشر» / «الحادية عشرة».
- Definite ordinals change only in the tens (العشرون / العشرين).
- Indefinite ordinals change with case: «ثانٍ»، «ثالث» (nominative/genitive) and «ثانيًا»، «ثالثًا» (accusative); «أول» and «أولى» never take tanween; feminine accusative takes tanween on ة («ثالثةً»). Indefinite 21–99: «حادٍ وعشرون», accusative «حاديًا وعشرين». Compounds 11–19 never change.
- `ordinal_adverb`: أولًا … عاشرًا, then «حادي عشر»، «ثاني عشر»، «عشرون»، «حادي وعشرون» with no tanween.
