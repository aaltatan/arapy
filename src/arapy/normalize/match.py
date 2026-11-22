"""Matching helpers built on normalizers."""

from arapy.normalize.normalizer import Normalizer
from arapy.normalize.presets import NAMES
from arapy.normalize.rules import Rule


def ar_equals(a: str, b: str, preset: Normalizer = NAMES) -> bool:
    """Compare two strings after normalizing both: `ar_equals("عبدالله", "عبد الله")` is True."""
    return preset(a) == preset(b)


def ar_key(preset: Normalizer = NAMES) -> Rule:
    """Return a key function for dict keys, sets and `sorted`."""
    return preset
