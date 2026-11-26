# Normalization

People write the same Arabic word in many ways: with or without hamza, with ة or ه, with
tashkeel or tatweel, with Persian lookalike letters, with invisible bidi marks pasted from
another app. `arapy.normalize` folds those variants so the text can be searched, compared and
grouped.

## Presets

Three ready-made normalizers cover most needs:

| Preset | For | What it does |
| --- | --- | --- |
| `SEARCH` | loose search | cleans marks, folds alef, ى, ة, hamza carriers ؤ ئ and digits, collapses spaces |
| `NAMES` | personal names | like `SEARCH`, but keeps hamza carriers and digits, and splits compound names |
| `SORT` | before sorting | only cleans marks and folds digits; letter order is handled by [sorting](sort.md) |

"Cleans marks" means: remove invisible characters, tashkeel, Quranic marks and tatweel, and
fold Persian/Urdu lookalikes ی ک ہ to ي ك ه.

```python
from arapy import NAMES, SEARCH
from arapy.normalize import SORT

print(SEARCH("أَحْمَدُ   الطَّيِّبَة"))  # احمد الطيبه
print(SEARCH("إسـلام مؤمن ٢٠٢٦"))  # اسلام مومن 2026
print(NAMES("عبدالله  أبوبكر"))  # عبد الله ابو بكر
print(NAMES("مؤمن"))  # مؤمن
print(SORT("أَحْمَد ٢"))  # أحمد 2
```

Every preset is idempotent: normalizing twice gives the same result as normalizing once.

## Rules

A rule is any `str -> str` function (the `Rule` type). The built-in rules live in
`arapy.normalize.rules`:

| Rule | Does |
| --- | --- |
| `fold_alef` | أ إ آ ٱ → ا |
| `fold_alef_maqsura` | ى → ي |
| `fold_teh_marbuta` | ة → ه |
| `fold_hamza_carriers` | ؤ → و, ئ → ي |
| `fold_lookalikes` | Persian/Urdu ی ک ہ → Arabic ي ك ه |
| `fold_digits` | Arabic-Indic and Persian digits → Latin |
| `remove_tashkeel` | harakat, tanween, shadda and sukun |
| `remove_tatweel` | ـ |
| `remove_quranic_marks` | Quranic annotation signs and superscript alef |
| `remove_invisible` | zero-width characters and bidi controls |
| `split_compound_names` | عبدالله → عبد الله, ابوبكر → ابو بكر |
| `collapse_spaces` | runs of whitespace → one space, and strip both ends |

```python
from arapy.normalize.rules import fold_teh_marbuta, remove_tashkeel, split_compound_names

print(remove_tashkeel("مُحَمَّد"))  # محمد
print(fold_teh_marbuta("فاطمة"))  # فاطمه
print(split_compound_names("ابوعبدالله"))  # ابو عبد الله
```

## Building your own `Normalizer`

A `Normalizer` applies its rules in order. It is frozen and callable, so it is itself a rule.
Build one from a list of rules, or extend another with `+`, which accepts a rule or a whole
normalizer:

```python
from arapy import Normalizer
from arapy.normalize.rules import collapse_spaces, fold_alef, remove_tatweel

light = Normalizer([remove_tashkeel, fold_alef, collapse_spaces])
upper = SEARCH + str.upper
both = light + Normalizer([remove_tatweel])

print(light("أَحْمَد  إبراهيم"))  # احمد ابراهيم
print(upper("Café ـأحمد"))  # CAFÉ احمد
print(both("أحـــمد"))  # احمد
print(len(both.rules))  # 4
```

## Comparing and grouping

`ar_equals(a, b, preset=NAMES)` compares two strings after normalizing both. `ar_key(preset)`
returns a key function for dicts, sets and `sorted`:

```python
from arapy import ar_equals, ar_key

print(ar_equals("عبدالله", "عبد اللّه"))  # True
print(ar_equals("أسامة", "اسامه"))  # True
print(ar_equals("مؤمن", "مومن"))  # False
print(ar_equals("مؤمن", "مومن", SEARCH))  # True

key = ar_key(SEARCH)

print({key(name) for name in ["أحمد", "احمد", "أَحمد"]})  # {'احمد'}
```

Normalize for matching, but store and show the original text: folding is lossy («فاطمه» is not
how anyone wants their name printed).
