# Ordinals

`arapy.ordinals` writes ordinal numbers from 1 to 100 (الأول … المئة) and list markers
(أولًا، ثانيًا …). Outside 1–100 both functions raise `OutOfRangeError`.

## `ordinal`

```py
ordinal(n, gender=Gender.MASCULINE, *, definite=True, case=Case.NOMINATIVE)
```

```python
from arapy import Case, Gender, ordinal

print(ordinal(1))  # الأول
print(ordinal(10))  # العاشر
print(ordinal(3, Gender.FEMININE))  # الثالثة
print(ordinal(1, gender=Gender.FEMININE))  # الأولى
print(ordinal(11))  # الحادي عشر
print(ordinal(11, Gender.FEMININE))  # الحادية عشرة
print(ordinal(21))  # الحادي والعشرون
print(ordinal(100))  # المئة
```

`case` changes the tens: العشرون in the nominative, العشرين otherwise.

```python
print(ordinal(20, case=Case.GENITIVE))  # العشرين
print(ordinal(25, case=Case.ACCUSATIVE))  # الخامس والعشرين
```

`definite=False` drops «ال». The indefinite form takes tanween in the accusative, and
ثانٍ/حادٍ lose their final ي in the nominative and genitive:

```python
print(ordinal(3, definite=False))  # ثالث
print(ordinal(3, definite=False, case=Case.ACCUSATIVE))  # ثالثًا
print(ordinal(2, definite=False))  # ثانٍ
print(ordinal(2, definite=False, case=Case.ACCUSATIVE))  # ثانيًا
```

## `ordinal_adverb`

List markers, for numbered clauses in contracts and decisions:

```python
from arapy import ordinal_adverb

print([ordinal_adverb(n) for n in range(1, 5)])  # ['أولًا', 'ثانيًا', 'ثالثًا', 'رابعًا']
print(ordinal_adverb(11))  # حادي عشر
print(ordinal_adverb(20))  # عشرون
print(ordinal_adverb(21))  # حادي وعشرون
```

## Ordinal days in dates

The `%O` directive of [`ArDate.format`](dates.md#formatting) writes the day as an ordinal:

```python
from arapy import ArDate

print(ArDate(2026, 1, 5).format("%O من %B"))  # الخامس من كانون الثاني
```
