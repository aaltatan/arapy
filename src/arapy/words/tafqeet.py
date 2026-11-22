"""The `Tafqeet` config object and the `to_words` shortcut."""

from dataclasses import dataclass
from decimal import Decimal

from arapy.digits import parse_number
from arapy.errors import InvalidNumberError
from arapy.words.grammar import Case, Hundreds, integer_to_words


@dataclass(frozen=True, slots=True)
class Tafqeet:
    """Write numbers in Arabic words (تفقيط).

    >>> Tafqeet(prefix="فقط", suffix="لا غير")(125)
    'فقط مئة وخمسة وعشرون لا غير'
    """

    hundreds: Hundreds = "مئة"
    case: Case = Case.NOMINATIVE
    prefix: str = ""
    suffix: str = ""

    def __call__(self, value: int | Decimal | str) -> str:
        number = parse_number(value) if isinstance(value, str) else Decimal(value)

        if not number.is_finite() or number != number.to_integral_value():
            raise InvalidNumberError(f"Only whole numbers can be written without a unit: {value!r}")

        words = integer_to_words(int(number), case=self.case, hundreds=self.hundreds)

        return " ".join(part for part in (self.prefix, words, self.suffix) if part)


to_words = Tafqeet()
