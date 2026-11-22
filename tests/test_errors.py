import pytest

from arapy import (
    ArapyError,
    InvalidNumberError,
    MissingExtraError,
    OutOfRangeError,
    ParseError,
)


@pytest.mark.parametrize(
    ("error", "builtin"),
    [
        (InvalidNumberError, ValueError),
        (OutOfRangeError, ValueError),
        (ParseError, ValueError),
        (MissingExtraError, ImportError),
    ],
)
def test_hierarchy(error: type[ArapyError], builtin: type[Exception]) -> None:
    assert issubclass(error, ArapyError)

    assert issubclass(error, builtin)


def test_missing_extra_names_install_command() -> None:
    err = MissingExtraError("hijri")

    assert err.extra == "hijri"

    assert 'pip install "arapy[hijri]"' in str(err)
