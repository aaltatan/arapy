"""Month and weekday names: Gregorian month styles, weekdays and Hijri months."""

from collections.abc import Mapping
from enum import StrEnum
from types import MappingProxyType
from typing import Final


class MonthNames(StrEnum):
    """Gregorian month-name styles."""

    LEVANT = "levant"  # كانون الثاني
    EGYPTIAN = "egyptian"  # يناير
    MAGHREB = "maghreb"  # جانفي
    LEVANT_WITH_EGYPTIAN = "levant_with_egyptian"  # كانون الثاني (يناير)


_LEVANT: Final = (
    "كانون الثاني", "شباط", "آذار", "نيسان", "أيار", "حزيران",
    "تموز", "آب", "أيلول", "تشرين الأول", "تشرين الثاني", "كانون الأول",
)  # fmt: skip
_EGYPTIAN: Final = (
    "يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو",
    "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر",
)  # fmt: skip
_MAGHREB: Final = (
    "جانفي", "فيفري", "مارس", "أفريل", "ماي", "جوان",
    "جويلية", "أوت", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر",
)  # fmt: skip

MONTHS: Final[Mapping[MonthNames, tuple[str, ...]]] = MappingProxyType(
    {
        MonthNames.LEVANT: _LEVANT,
        MonthNames.EGYPTIAN: _EGYPTIAN,
        MonthNames.MAGHREB: _MAGHREB,
        MonthNames.LEVANT_WITH_EGYPTIAN: tuple(
            f"{levant} ({egyptian})" for levant, egyptian in zip(_LEVANT, _EGYPTIAN, strict=True)
        ),
    }
)
"""Twelve month names per style, January first."""

WEEKDAYS: Final = ("الاثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد")
"""Weekday names, Monday first, matching `date.weekday()`."""

HIJRI_MONTHS: Final = (
    "محرم", "صفر", "ربيع الأول", "ربيع الآخر", "جمادى الأولى", "جمادى الآخرة",
    "رجب", "شعبان", "رمضان", "شوال", "ذو القعدة", "ذو الحجة",
)  # fmt: skip
"""Hijri month names, محرم first."""


def month_numbers(style: MonthNames | None = None) -> dict[str, int]:
    """Map month names to 1–12 for one style, or for every style when `style` is None."""
    styles = list(MonthNames) if style is None else [style]

    return {name: i for s in styles for i, name in enumerate(MONTHS[s], start=1)}
