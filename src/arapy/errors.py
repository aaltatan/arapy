"""Exception hierarchy. Every error raised by arapy subclasses `ArapyError`."""


class ArapyError(Exception):
    """Base class for all arapy errors."""


class InvalidNumberError(ArapyError, ValueError):
    """A value cannot be read as a number."""


class OutOfRangeError(ArapyError, ValueError):
    """A number is outside the supported range."""


class ParseError(ArapyError, ValueError):
    """Text does not match the expected format."""


class MissingExtraError(ArapyError, ImportError):
    """An optional extra is needed but not installed."""

    def __init__(self, extra: str) -> None:
        self.extra = extra

        super().__init__(
            f"This feature needs the '{extra}' extra. "
            f'Install it with: `pip install "arapy[{extra}]"` or `uv add arapy[{extra}]`'
        )
