"""Composable rules for normalizing Arabic text, with matching helpers."""

from arapy.normalize.match import ar_equals, ar_key
from arapy.normalize.normalizer import Normalizer
from arapy.normalize.presets import NAMES, SEARCH, SORT
from arapy.normalize.rules import Rule

__all__ = ["NAMES", "SEARCH", "SORT", "Normalizer", "Rule", "ar_equals", "ar_key"]
