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
- [ ] Reserve the name on PyPI (0.0.1 placeholder)

## Phase 1 — digits

- [ ] `to_latin_digits`, `to_arabic_digits`, `to_persian_digits`
- [ ] `parse_number(text) -> Decimal` (Arabic ٬ ٫, Latin `,` `.`, Arabic comma ،, sign, ambiguity errors)
- [ ] `format_number(...)` with digit set, grouping, decimal mark, places
- [ ] `format_percent(...)` (٪)
- [ ] Property test: `parse_number(format_number(x, ...)) == x`
- Note: `format_money` lands in Phase 5 inside `words/money.py`, once `Currency` exists (`digits` never imports `words`)

## Phase 2 — normalize + sort

- [ ] `rules.py`: alef folding, yaa/alef maqsura, taa marbuta, hamza carriers, tashkeel, tatweel, Quranic marks, zero-width/bidi controls, Persian/Urdu lookalikes, compound names, space collapsing, digit folding
- [ ] `Normalizer` (frozen, callable, composable: `Normalizer(rules) + rule`)
- [ ] Presets `SEARCH`, `NAMES`
- [ ] `ar_equals`, `ar_key`
- [ ] `sort.py`: `ar_sort_key`, `ar_sorted`
- [ ] Property test: every preset is idempotent

## Phase 3 — words: integer engine

- [ ] `grammar.py`: integers 0 … 10^15 − 1 → words, masculine/feminine, `Case`, `hundreds` spelling
- [ ] Teens, tens, compounds (أحد عشر / إحدى عشرة، اثنا عشر / اثنتا عشرة), hundreds (مئة، مئتان، ثلاثمئة), thousands/millions/billions/trillions with dual and plural (ألفان، آلاف، ملايين)
- [ ] Golden table `tests/words/golden_integers.py` (maintainer reviews it before the phase closes)
- [ ] `Tafqeet` config object (hundreds, case, prefix, suffix) and the `to_words` shortcut, without units yet
- [ ] Negatives («سالب …»)

## Phase 4 — words: nouns, currencies, fractions

- [ ] `nouns.py`: `Gender`, `PluralForm`, CLDR category function, `Noun` (+ builder helpers), `Currency`
- [ ] Noun agreement: 1 and 2 as adjectives after the noun, 3–10 reversed gender + plural, 11–99 تمييز, 100+ singular
- [ ] `currencies.py`: SYP, USD, EUR, SAR, AED, EGP, JOD, LBP, TRY, KWD, IQD, QAR, BHD, OMR, GBP (read-only mapping + module attributes)
- [ ] Fractions → subunit words using `ratio`; error on too many decimal places
- [ ] `str` input through `parse_number`
- [ ] Golden table `tests/words/golden_money.py` (SYP feminine, USD masculine, KWD 1000 ratio)
- [ ] Counted-noun examples (ساعة، موظف، يوم)

## Phase 5 — words: parse + format_money

- [ ] `parse.py`: words → `Decimal` (both spellings, all cases, prefix/suffix, tashkeel tolerant, units and subunits)
- [ ] Property test: `parse(to_words(n, unit)) == n` across ranges and currencies
- [ ] `words/money.py`: `format_money(value, currency, ...)` → «١٢٬٥٠٠ ل.س»

## Phase 6 — ordinals

- [ ] `ordinal(n, gender, definite=True, case=...)`: الأول/الأولى … الحادي عشر/الحادية عشرة … العشرون … المئة
- [ ] Indefinite forms (أول، ثانٍ، ثالث)
- [ ] `ordinal_adverb(n)` (أولًا، ثانيًا…)
- [ ] Golden tables

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

1. **101 / 102 with a unit:** «مئة ليرة وليرة» / «مئة وليرتان» vs «مئة وواحدة ليرة» / «مئة واثنتان ليرة»?
2. **Dual thousands before a noun:** «ألفا ليرة» (construct) vs «ألفان من الليرات» vs «ألفان ليرة»?
3. **Plain 1 and 2 with a unit:** always «ليرة سورية واحدة» or just «ليرة سورية»?
4. **Tanween in output:** «قرشًا» / «دولارًا» always written, or only when `case` ≠ nominative?
5. **ة → ه folding** in the `SEARCH` preset only, or also in `NAMES`?
6. **Repo layout for arapy-cli:** same repo as a uv workspace, or a separate repo? (arapy itself stays a single package.)
