# Exceptions

Every error arapy raises subclasses `ArapyError`, and also the matching built-in exception, so
`except ValueError` and `except ImportError` keep working.

```text
Exception
└── ArapyError
    ├── InvalidNumberError   (also ValueError)
    ├── OutOfRangeError      (also ValueError)
    ├── ParseError           (also ValueError)
    ├── FormatError          (also ValueError)
    └── MissingExtraError    (also ImportError)
```

| Error | Raised when | Examples |
| --- | --- | --- |
| `InvalidNumberError` | a number is malformed, ambiguous, not finite, or has more decimal places than allowed | `parse_number("1,250")`, `to_words(Decimal("10.005"), SYP)`, `format_number("1.234", places=2)`, `to_words("1.5")` |
| `OutOfRangeError` | a value is outside the supported range | `to_words(10**15)`, `ordinal(101)`, a Hijri date outside 1343–1500 AH |
| `ParseError` | text cannot be read as words or as a date | `to_words.parse("")`, `ArDate.strptime("٣٠ شباط ٢٠٢٦", "%d %B %Y")` |
| `FormatError` | a format string uses an unsupported directive | `ArDate(2026, 1, 5).format("%Z")` |
| `MissingExtraError` | an optional extra is not installed | `shape("سلام")` without `arapy[shape]` |

`ArapyError` itself is raised directly when a `Noun` is built without all six plural forms.

```python
from arapy import ArapyError, ArDate, FormatError, OutOfRangeError, ordinal, to_words

try:
    to_words(10**15)
except OutOfRangeError as error:
    print(error)  # 1000000000000000 is outside the supported range ±999999999999999

try:
    ordinal(101)
except ValueError as error:
    print(error)  # Ordinals are supported from 1 to 100, not 101

try:
    ArDate(2026, 1, 5).format("%Z")
except FormatError as error:
    print(error)  # Unsupported directive %Z in '%Z'

try:
    ArDate.strptime("٣٠ شباط ٢٠٢٦", "%d %B %Y")
except ArapyError as error:
    print(type(error).__name__)  # ParseError
```

`MissingExtraError` has an `extra` attribute naming the missing extra (`"hijri"` or
`"shape"`), and its message gives the install command.

::: arapy.errors
