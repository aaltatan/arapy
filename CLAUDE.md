# CLAUDE.md — arapy

## What this project is

**arapy** is a strongly typed Python library that brings Arabic text, number and date tools together in one package:

- **words (تفقيط):** amounts and counts in Arabic words, with correct gender, plural, case and currency handling.
- **digits:** convert, parse and format numbers in Arabic, Persian and Latin digits.
- **normalize:** composable rules for normalizing Arabic text, with matching helpers.
- **sort:** Arabic alphabetical ordering.
- **ordinals:** الأول/الأولى, أولًا, ordinal dates.
- **dates:** Pythonic `ArDate`, `ArDateTime` and `HijriDate` types, Arabic formatting and parsing, and relative durations.
- **shape:** reshaping and bidi for drawing Arabic text in images, PDFs and ZPL.

Main users: payment orders and reports (salariez, uniscope), document templates (templify), and stickers (qrbar). It is published on PyPI as `arapy`. Integrations (a CLI, Jinja2, Django, Excel) are independent packages built in their own projects.

## Principles

1. **Strong typing first.** Run `mypy --strict` with no `Any` in public APIs. Ship `py.typed`. Use `Literal`, `StrEnum` and `Protocol` instead of loose strings and duck typing.
2. **Simple design** (ArjanCodes style). Prefer small functions and frozen, slotted dataclasses, and choose composition over inheritance. Subclass `date`/`datetime` because interoperability requires it.
3. **Immutable and stateless.** Avoid global mutable state. Config objects are frozen. There are no built-in currencies: users define each `Currency` (with `Currency.create`) and pass it in as a value; nothing is registered globally.
4. **Zero dependencies in core.** Optional extras are imported lazily, and a missing extra raises `MissingExtraError` with the install command:
   - `arapy[hijri]` → `hijridate`
   - `arapy[shape]` → `arabic-reshaper`, `python-bidi`
5. **Exact numbers.** Use `Decimal` internally and never `float`. Public number inputs are `int | Decimal | str`, and strings are parsed through `arapy.digits.parse_number`.
6. **Explicit errors.** Every error subclasses `ArapyError`. Never silently round or truncate.
7. **Language.** Code, docstrings and error messages are in English. Examples and tests use real Arabic. The README is bilingual (English + Arabic).

## Tooling

- Python **3.12+**, managed with **uv** (`uv sync`, `uv run`).
- **ruff** handles linting and formatting. **mypy --strict** must pass with zero errors.
- **pytest** for tests, plus **hypothesis** for property tests (for example, `parse(to_words(n)) == n`).
- Use the `src/` layout. Tests mirror the modules.
- Before finishing any task: `uv run ruff check . && uv run ruff format --check . && uv run mypy src && uv run pytest`.

## Package layout

```
src/arapy/
  __init__.py          # version, re-exports of the most-used names
  py.typed
  errors.py            # ArapyError, InvalidNumberError, OutOfRangeError, ParseError, MissingExtraError
  _letters.py          # Arabic letter constants and character classes (shared)
  digits.py
  normalize/
    __init__.py
    rules.py           # individual rule functions (Rule = Callable[[str], str])
    normalizer.py      # Normalizer pipeline
    presets.py         # SEARCH, NAMES, …
    match.py           # ar_equals, ar_key
  sort.py
  words/
    __init__.py        # Tafqeet, to_words, Case, Noun, Currency, PluralForm
    grammar.py         # integer → words engine (gender, case, hundreds spelling)
    nouns.py           # PluralForm, Gender, Noun, Currency
    tafqeet.py         # Tafqeet config object + to_words shortcut
    parse.py           # words → number
    money.py           # format_money (digits + Currency)
  ordinals.py
  dates/
    __init__.py
    months.py          # MonthNames styles
    formatting.py      # format/parse engine shared by the types
    ardate.py          # ArDate
    ardatetime.py      # ArDateTime
    hijri.py           # HijriDate (lazy hijridate)
    humanize.py        # relative times and durations
  shape.py             # lazy arabic-reshaper + python-bidi
```

## Module specs

### digits

```python
to_arabic_digits("2026") -> "٢٠٢٦"
to_latin_digits("٢٠٢٦ / ۲۰۲۶") -> "2026 / 2026"
to_persian_digits(...)
parse_number("١٢٥٬٠٠٠٫٥") -> Decimal("125000.5")    # also "1,250.5", Arabic comma ، as separator
format_number(value, *, digits: DigitSet = "latin", grouping: str | None = ",",
              decimal: str = ".", places: int | None = None) -> str
format_percent(...)  # ٪ sign
```

`format_money` lives in `words` and not here, because it needs `Currency`. `digits` must never import `words`: `words` already depends on `digits`, so that import would be circular.

`DigitSet = Literal["latin", "arabic", "persian"]`. Parsing must be unambiguous: reject inputs where a separator could mean either the decimal point or the thousands separator, unless the caller says which one it is.

### normalize

- A `Rule` is a `Callable[[str], str]`. Rules are small, pure and individually tested.
- **Letter folding:** alef forms (أ إ آ ٱ → ا), ى → ي, ة → ه, and hamza carriers ؤ ئ (configurable).
- **Mark removal:** tashkeel, tatweel (ـ), Quranic marks, zero-width and bidi control characters.
- **Lookalikes:** Persian/Urdu ی ک ہ → ي ك ه.
- **Names:** consistent compound names (عبد الله، أبو بكر), and collapsing spaces.
- **Digits:** folding digits to Latin, using `digits`.
- `Normalizer(rules: Sequence[Rule])` is frozen and callable, with presets `SEARCH` and `NAMES`.
- **Matching:** `ar_equals(a, b, preset=NAMES)` and `ar_key(preset)` for use with dict, set and sorted.

### sort

`ar_sort_key(text, *, normalizer=...)` follows Arabic alphabetical order, not raw codepoint order, and works on top of normalize. `ar_sorted(iterable, key=...)` is a convenience wrapper.

### words (تفقيط)

```python
class Case(StrEnum):
    NOMINATIVE, ACCUSATIVE, GENITIVE


class Gender(StrEnum):
    MASCULINE, FEMININE


class PluralForm(StrEnum):
    ZERO, ONE, TWO, FEW, MANY, OTHER  # Arabic CLDR categories


@dataclass(frozen=True, slots=True)
class Noun:
    forms: Mapping[PluralForm, str]  # adjective agreement lives in each form
    gender: Gender
    dual_oblique: str | None = None  # ليرتين سوريتين for accusative/genitive
    # + classmethod helpers to build a Noun easily


@dataclass(frozen=True, slots=True)
class Currency(Noun):
    code: str  # ISO 4217, "SYP"
    subunit: Noun  # قرش
    ratio: int = 100  # 1000 for KWD/JOD/BHD/OMR/IQD subunits


@dataclass(frozen=True, slots=True)
class Tafqeet:
    hundreds: Literal["مئة", "مائة"] = "مئة"
    case: Case = Case.NOMINATIVE
    prefix: str = ""  # e.g. "فقط"
    suffix: str = ""  # e.g. "لا غير"

    def __call__(self, value: int | Decimal | str, unit: Noun | None = None) -> str: ...
    def parse(self, text: str) -> Decimal: ...


to_words = Tafqeet()
```

- Plural category follows CLDR Arabic: 0 → ZERO, 1 → ONE, 2 → TWO, n%100 in 3..10 → FEW, n%100 in 11..99 → MANY, everything else → OTHER.
- Number words agree with the noun's gender (ثلاث ليرات / ثلاثة دولارات). 1 and 2 follow the noun as adjectives (ليرة سورية واحدة، ليرتان سوريتان).
- **Fractions:** written in subunit words (… وخمسون قرشًا). The fraction must fit `ratio`. Too many decimal places raises an error, with no rounding.
- **Negatives:** «سالب …».
- **Range:** v1 supports up to 10^15 − 1 (trillions). Beyond that raises `OutOfRangeError`.
- **Currencies:** none are built in. Users define them with `Currency.create(*, code, singular, dual, plural, gender, subunit, ratio=100, symbol="", many=None)` (keyword-only). Tests use the fixtures in `tests/words/currencies.py`.
- **Without a unit:** a bare number. With a `Noun`: counted nouns (ثلاث ساعات، خمسة موظفين).
- **Parse:** accepts both spellings (مئة/مائة), all cases, with or without prefix and suffix, and ignores tashkeel.

### ordinals

```python
ordinal(3, gender=Gender.FEMININE) -> "الثالثة"
ordinal(11) -> "الحادي عشر"
ordinal(3, definite=False) -> "ثالث"
ordinal_adverb(3) -> "ثالثًا"        # list markers: أولًا، ثانيًا…
```

### dates

- `MonthNames` styles: `LEVANT` (كانون الثاني), `EGYPTIAN` (يناير), `MAGHREB` (جانفي), `LEVANT_WITH_EGYPTIAN` (كانون الثاني (يناير)), plus Hijri month names.
- **`ArDate(date)`:** overrides `__add__`, `__radd__`, `__sub__`, `replace`, `today`, `fromisoformat`, `fromordinal` and `fromtimestamp` so the result stays an `ArDate`. `date - date` still returns `timedelta`. `strftime` and `__format__` keep their **standard** behaviour.
  - `.format(fmt, *, months=MonthNames.LEVANT, digits="latin")` produces Arabic output. It supports the strftime directives plus `%O` for the ordinal day (الخامس).
  - `ArDate.strptime(text, fmt, *, months=None)` is strict. With `months=None` it accepts any month-name style. It accepts any digit set.
  - Properties: `weekday_name`, `month_name(style)`, `to_hijri()`.
  - `ArDate.from_date(d)` converts from a plain date.
- **`ArDateTime(datetime)`:** follows the same rules. Adds `%p` → صباحًا / مساءً and Arabic time formatting.
- **`HijriDate`:** a frozen, slotted class (not a `date` subclass) that mirrors date's API: `year/month/day`, `weekday()`, `isoformat()`, `±timedelta`, rich comparison with `HijriDate` and `date` (through the ordinal), `to_gregorian()`, `.format()` and `strptime`. Needs `arapy[hijri]`. `hijridate` is an internal detail and never appears in the public API.
- **humanize:** `ar_since(dt, now=...)` → «منذ ثلاثة أيام», «بعد شهرين». `ar_duration(timedelta | relativedelta-like)` → «سنة وثلاثة أشهر». Built on `words` + `Noun`.

### shape

`shape(text) -> str` returns reshaped text in visual order, ready for Pillow, ReportLab or ZPL. `reshape_only(text)` skips the bidi step. Needs `arapy[shape]`, and both functions are typed wrappers around the extras.

## Testing rules

- Every rule, form and directive gets table-driven tests (`pytest.mark.parametrize`) with real Arabic expected strings.
- Golden tafqeet tables live in `tests/words/golden_*.py`. **Never change an expected string to make a test pass.** If the grammar looks wrong, stop and ask the maintainer.
- Property tests:
  - `parse(to_words(n)) == n`
  - `parse_number(format_number(x)) == x`
  - `ArDate.strptime(d.format(f), f) == d`
  - normalizers are idempotent
- Tests for the extras are skipped when the extra isn't installed (`pytest.importorskip`).

## Working style

- Work phase by phase from `PHASES.md`. At the end of each phase, run all checks and update the phase checklist.
- When an Arabic grammar or spelling choice isn't covered here, **ask; don't guess.** List it under "Open questions" in `PHASES.md`.
- Keep public names stable once released. Mark internals with a leading underscore.
