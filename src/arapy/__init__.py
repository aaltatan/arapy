"""Strongly typed Arabic text, number and date tools."""

from importlib.metadata import version

from arapy.dates import ArDate, ArDateTime, HijriDate, MonthNames, ar_duration, ar_since
from arapy.digits import (
    format_number,
    format_percent,
    parse_number,
    to_arabic_digits,
    to_latin_digits,
    to_persian_digits,
)
from arapy.errors import (
    ArapyError,
    FormatError,
    InvalidNumberError,
    MissingExtraError,
    OutOfRangeError,
    ParseError,
)
from arapy.normalize import NAMES, SEARCH, Normalizer, ar_equals, ar_key
from arapy.ordinals import ordinal, ordinal_adverb
from arapy.shape import reshape_only, shape
from arapy.sort import ar_sort_key, ar_sorted
from arapy.words import Case, Currency, Gender, Noun, Tafqeet, format_money, to_words

__version__ = version("arapy")

__all__ = [
    "NAMES",
    "SEARCH",
    "ArDate",
    "ArDateTime",
    "ArapyError",
    "Case",
    "Currency",
    "FormatError",
    "Gender",
    "HijriDate",
    "InvalidNumberError",
    "MissingExtraError",
    "MonthNames",
    "Normalizer",
    "Noun",
    "OutOfRangeError",
    "ParseError",
    "Tafqeet",
    "__version__",
    "ar_duration",
    "ar_equals",
    "ar_key",
    "ar_since",
    "ar_sort_key",
    "ar_sorted",
    "format_money",
    "format_number",
    "format_percent",
    "ordinal",
    "ordinal_adverb",
    "parse_number",
    "reshape_only",
    "shape",
    "to_arabic_digits",
    "to_latin_digits",
    "to_persian_digits",
    "to_words",
]
