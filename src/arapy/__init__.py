"""Strongly typed Arabic text, number and date tools."""

from importlib.metadata import version

from arapy.errors import (
    ArapyError,
    FormatError,
    InvalidNumberError,
    MissingExtraError,
    OutOfRangeError,
    ParseError,
)

__version__ = version("arapy")

__all__ = [
    "ArapyError",
    "FormatError",
    "InvalidNumberError",
    "MissingExtraError",
    "OutOfRangeError",
    "ParseError",
    "__version__",
]
