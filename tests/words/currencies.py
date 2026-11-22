"""Currencies used by the tests, defined the way users define their own."""

from collections.abc import Mapping
from types import MappingProxyType

from arapy.words import Currency, Gender, Noun

_M = Gender.MASCULINE
_F = Gender.FEMININE

_SYMBOLS = {
    "SYP": "ل.س",
    "USD": "$",
    "EUR": "€",
    "SAR": "ر.س",
    "AED": "د.إ",
    "EGP": "ج.م",
    "JOD": "د.أ",
    "LBP": "ل.ل",
    "TRY": "ل.ت",
    "KWD": "د.ك",
    "IQD": "د.ع",
    "QAR": "ر.ق",
    "BHD": "د.ب",
    "OMR": "ر.ع",
    "GBP": "£",
}


def _currency(
    code: str,
    names: tuple[str, str, str],
    gender: Gender,
    subunit: tuple[str, str, str],
    subunit_gender: Gender,
    ratio: int = 100,
) -> Currency:
    singular, dual, plural = names

    return Currency.create(
        code=code,
        singular=singular,
        dual=dual,
        plural=plural,
        gender=gender,
        subunit=Noun.create(*subunit, gender=subunit_gender),
        ratio=ratio,
        symbol=_SYMBOLS[code],
    )


_QIRSH = ("قرش", "قرشان", "قروش")
_CENT = ("سنت", "سنتان", "سنتات")
_FILS = ("فلس", "فلسان", "فلوس")

SYP = _currency("SYP", ("ليرة سورية", "ليرتان سوريتان", "ليرات سورية"), _F, _QIRSH, _M)
USD = _currency("USD", ("دولار أمريكي", "دولاران أمريكيان", "دولارات أمريكية"), _M, _CENT, _M)
EUR = _currency("EUR", ("يورو", "يوروان", "يوروهات"), _M, _CENT, _M)
SAR = _currency(
    "SAR", ("ريال سعودي", "ريالان سعوديان", "ريالات سعودية"), _M, ("هللة", "هللتان", "هللات"), _F
)
AED = _currency("AED", ("درهم إماراتي", "درهمان إماراتيان", "دراهم إماراتية"), _M, _FILS, _M)
EGP = _currency("EGP", ("جنيه مصري", "جنيهان مصريان", "جنيهات مصرية"), _M, _QIRSH, _M)
JOD = _currency("JOD", ("دينار أردني", "ديناران أردنيان", "دنانير أردنية"), _M, _FILS, _M, 1000)
LBP = _currency("LBP", ("ليرة لبنانية", "ليرتان لبنانيتان", "ليرات لبنانية"), _F, _QIRSH, _M)
TRY = _currency("TRY", ("ليرة تركية", "ليرتان تركيتان", "ليرات تركية"), _F, _QIRSH, _M)
KWD = _currency("KWD", ("دينار كويتي", "ديناران كويتيان", "دنانير كويتية"), _M, _FILS, _M, 1000)
IQD = _currency("IQD", ("دينار عراقي", "ديناران عراقيان", "دنانير عراقية"), _M, _FILS, _M, 1000)
QAR = _currency(
    "QAR", ("ريال قطري", "ريالان قطريان", "ريالات قطرية"), _M, ("درهم", "درهمان", "دراهم"), _M
)
BHD = _currency("BHD", ("دينار بحريني", "ديناران بحرينيان", "دنانير بحرينية"), _M, _FILS, _M, 1000)
OMR = _currency(
    "OMR",
    ("ريال عماني", "ريالان عمانيان", "ريالات عمانية"),
    _M,
    ("بيسة", "بيستان", "بيسات"),
    _F,
    1000,
)
GBP = _currency(
    "GBP",
    ("جنيه إسترليني", "جنيهان إسترلينيان", "جنيهات إسترلينية"),
    _M,
    ("بنس", "بنسان", "بنسات"),
    _M,
)

CURRENCIES: Mapping[str, Currency] = MappingProxyType(
    {c.code: c for c in (SYP, USD, EUR, SAR, AED, EGP, JOD, LBP, TRY, KWD, IQD, QAR, BHD, OMR, GBP)}
)
