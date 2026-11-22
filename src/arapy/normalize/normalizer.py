"""The `Normalizer` pipeline."""

from collections.abc import Sequence
from dataclasses import dataclass

from arapy.normalize.rules import Rule


@dataclass(frozen=True, slots=True)
class Normalizer:
    """Apply rules in order. Frozen and callable, so it is itself a `Rule`.

    Extend one with `+`: `SEARCH + my_rule` or `SEARCH + other_normalizer`.
    """

    rules: Sequence[Rule]

    def __post_init__(self) -> None:
        object.__setattr__(self, "rules", tuple(self.rules))

    def __call__(self, text: str) -> str:
        for rule in self.rules:
            text = rule(text)

        return text

    def __add__(self, other: Rule) -> "Normalizer":
        extra = other.rules if isinstance(other, Normalizer) else (other,)
        return Normalizer((*self.rules, *extra))
