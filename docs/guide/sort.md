# Sorting

Python's `sorted` orders strings by code point, so the alef forms آ أ إ ا sort as different
letters and أحمد lands after آمنة. `arapy.sort` sorts by Arabic alphabetical order instead.

```python
from arapy import ar_sort_key, ar_sorted

names = ["يوسف", "أحمد", "زينب", "آمنة", "باسل", "إياد"]

print(sorted(names))  # ['آمنة', 'أحمد', 'إياد', 'باسل', 'زينب', 'يوسف']
print(ar_sorted(names))  # ['أحمد', 'آمنة', 'إياد', 'باسل', 'زينب', 'يوسف']
print(ar_sorted(names, reverse=True)[:2])  # ['يوسف', 'زينب']
```

## How the order works

`ar_sort_key(text)` returns a tuple:

1. the text cleaned by the `SORT` preset (no tashkeel, tatweel or invisible marks, Latin
   digits), with letter variants folded onto their base letter: أ إ آ ٱ → ا, ة → ت, ؤ → و,
   ئ and ى → ي;
2. the cleaned text before folding, so ties between folded letters (أحمد / احمد) break by
   spelling and the order is stable.

```python
print(ar_sort_key("أَحْمَد"))  # ('احمد', 'أحمد')
print(ar_sorted(["مدرسة", "مدرست", "مدرس"]))  # ['مدرس', 'مدرسة', 'مدرست']
```

## Sorting objects

`key=` picks the text to sort by from each item, as in `sorted`. `ar_sort_key` also works
directly as a key:

```python
employees = [("زينب", 3), ("باسل", 1), ("أحمد", 2)]

print(ar_sorted(employees, key=lambda e: e[0]))  # [('أحمد', 2), ('باسل', 1), ('زينب', 3)]
print(sorted(["ي", "ب"], key=ar_sort_key))  # ['ب', 'ي']
```

## A different cleanup

Both functions take `normalizer=` to replace the `SORT` preset. For example, to ignore the
«ال» of each name, add a rule:

```python
from arapy.normalize import SORT

no_article = SORT + (lambda text: text.removeprefix("ال"))

print(ar_sorted(["الياسمين", "باسل", "السيد"], normalizer=no_article))  # ['باسل', 'السيد', 'الياسمين']
```
