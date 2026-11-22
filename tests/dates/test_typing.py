from pathlib import Path

from mypy import api


def test_ardate_results_are_typed_as_ardate() -> None:
    target = Path(__file__).with_name("typing_ardate.py")

    stdout, stderr, status = api.run(["--strict", "--no-incremental", str(target)])

    assert status == 0, stdout + stderr
