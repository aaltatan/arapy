"""The `Tafqeet` config object and the `to_words` shortcut."""

from dataclasses import dataclass
from decimal import Decimal

from arapy.digits import parse_number
from arapy.errors import InvalidNumberError
from arapy.words.grammar import Case, Hundreds, integer_to_words
from arapy.words.nouns import Currency, Gender, Noun, PluralForm, plural_form


@dataclass(frozen=True, slots=True)
class Tafqeet:
    """Write numbers in Arabic words (تفقيط), optionally counting a noun or a currency.

    >>> from arapy.words.currencies import SYP
    >>> Tafqeet(prefix="فقط", suffix="لا غير")("1250.50", SYP)
    'فقط ألف ومئتان وخمسون ليرةً سوريةً وخمسون قرشًا لا غير'
    """

    hundreds: Hundreds = "مئة"
    case: Case = Case.NOMINATIVE
    prefix: str = ""
    suffix: str = ""

    def __call__(self, value: int | Decimal | str, unit: Noun | None = None) -> str:
        number = parse_number(value) if isinstance(value, str) else Decimal(value)

        if not number.is_finite():
            raise InvalidNumberError(f"Not a finite number: {value!r}")

        words = self._amount(number, unit, value)

        return " ".join(part for part in (self.prefix, words, self.suffix) if part)

    def _amount(self, number: Decimal, unit: Noun | None, value: object) -> str:
        whole = int(abs(number))

        fraction = abs(number) - whole

        if unit is None:
            if fraction:
                raise InvalidNumberError(f"A fraction needs a currency unit: {value!r}")

            return integer_to_words(int(number), case=self.case, hundreds=self.hundreds)

        sub = 0

        if fraction:
            if not isinstance(unit, Currency):
                raise InvalidNumberError(f"Only a Currency can have a fraction: {value!r}")

            scaled = fraction * unit.ratio

            if scaled != scaled.to_integral_value():
                raise InvalidNumberError(
                    f"{value!r} has more decimal places than {unit.code} subunits allow"
                )

            sub = int(scaled)

        parts = []

        if whole or not sub:
            parts.append(self._count(whole, unit))

        if sub:
            assert isinstance(unit, Currency)  # sub is only set for currencies

            parts.append(self._count(sub, unit.subunit))

        words = " و".join(parts)

        return "سالب " + words if number < 0 else words

    def _count(self, n: int, noun: Noun) -> str:
        """`n` of `noun` with number–noun agreement: «ثلاث ليرات», «أحد عشر دولارًا»."""
        oblique = self.case is not Case.NOMINATIVE

        category = plural_form(n)

        if category is PluralForm.ZERO:
            return f"صفر {noun.form(category)}"

        if category is PluralForm.ONE:
            one = "واحدة" if noun.gender is Gender.FEMININE else "واحد"

            return f"{noun.form(category)} {one}"

        if category is PluralForm.TWO:
            return noun.form(category, oblique=oblique)

        rest = n % 100

        if rest in (1, 2):
            # Repeat the noun: 101 → «مئة ليرة وليرة», 102 → «مئة ليرة وليرتان».
            tail = noun.form(PluralForm.ONE if rest == 1 else PluralForm.TWO, oblique=oblique)

            return f"{self._count(n - rest, noun)} و{tail}"

        number = integer_to_words(
            n, gender=noun.gender, case=self.case, hundreds=self.hundreds, construct=rest == 0
        )

        return f"{number} {noun.form(category)}"


to_words = Tafqeet()
