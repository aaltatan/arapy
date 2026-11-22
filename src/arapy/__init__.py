"""Strongly typed Arabic text, number and date tools."""

from importlib.metadata import version

from arapy.errors import (
    ArapyError,
    InvalidNumberError,
    MissingExtraError,
    OutOfRangeError,
    ParseError,
)

__version__ = version("arapy")

__all__ = [
    "ArapyError",
    "InvalidNumberError",
    "MissingExtraError",
    "OutOfRangeError",
    "ParseError",
    "__version__",
]
