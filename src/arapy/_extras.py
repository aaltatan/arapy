"""Lazy imports for optional extras."""

from importlib import import_module
from types import ModuleType
from typing import Literal

from arapy.errors import MissingExtraError

type Extra = Literal["hijri", "shape"]


def require(extra: Extra, module: str) -> ModuleType:
    """Import `module`, or raise `MissingExtraError` naming the extra that provides it."""
    try:
        return import_module(module)
    except ImportError as err:
        raise MissingExtraError(extra) from err
