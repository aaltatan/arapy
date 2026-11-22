"""Golden month, weekday and date-format tables. Maintainer-reviewed: never edit to pass a test."""

from arapy.dates import MonthNames

MONTHS = {
    MonthNames.LEVANT: (
        "كانون الثاني", "شباط", "آذار", "نيسان", "أيار", "حزيران",
        "تموز", "آب", "أيلول", "تشرين الأول", "تشرين الثاني", "كانون الأول",
    ),
    MonthNames.EGYPTIAN: (
        "يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو",
        "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر",
    ),
    MonthNames.MAGHREB: (
        "جانفي", "فيفري", "مارس", "أفريل", "ماي", "جوان",
        "جويلية", "أوت", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر",
    ),
    MonthNames.LEVANT_WITH_EGYPTIAN: (
        "كانون الثاني (يناير)", "شباط (فبراير)", "آذار (مارس)", "نيسان (أبريل)",
        "أيار (مايو)", "حزيران (يونيو)", "تموز (يوليو)", "آب (أغسطس)",
        "أيلول (سبتمبر)", "تشرين الأول (أكتوبر)", "تشرين الثاني (نوفمبر)",
        "كانون الأول (ديسمبر)",
    ),
}  # fmt: skip

WEEKDAYS = ("الاثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد")

HIJRI_MONTHS = (
    "محرم", "صفر", "ربيع الأول", "ربيع الآخر", "جمادى الأولى", "جمادى الآخرة",
    "رجب", "شعبان", "رمضان", "شوال", "ذو القعدة", "ذو الحجة",
)  # fmt: skip

# (year, month, day, format, months, digits) → expected
FORMATS = [
    ((2026, 1, 5, "%O من %B %Y", MonthNames.LEVANT, "arabic"), "الخامس من كانون الثاني ٢٠٢٦"),
    ((2026, 1, 1, "%O من %B %Y", MonthNames.LEVANT, "arabic"), "الأول من كانون الثاني ٢٠٢٦"),
    ((2026, 3, 11, "%O من %B", MonthNames.EGYPTIAN, "latin"), "الحادي عشر من مارس"),
    ((2026, 5, 21, "%O من %B %Y", MonthNames.MAGHREB, "latin"), "الحادي والعشرون من ماي 2026"),
    ((2026, 12, 31, "%O من %B", MonthNames.LEVANT, "latin"), "الحادي والثلاثون من كانون الأول"),
    ((2026, 1, 5, "%A %d %B %Y", MonthNames.LEVANT, "arabic"), "الاثنين ٠٥ كانون الثاني ٢٠٢٦"),
    (
        (2026, 10, 2, "%A، %d %B %Y", MonthNames.LEVANT_WITH_EGYPTIAN, "latin"),
        "الجمعة، 02 تشرين الأول (أكتوبر) 2026",
    ),
    ((2026, 7, 4, "%Y/%m/%d", MonthNames.LEVANT, "persian"), "۲۰۲۶/۰۷/۰۴"),
    ((2026, 2, 1, "%d-%m-%y %j", MonthNames.LEVANT, "arabic"), "٠١-٠٢-٢٦ ٠٣٢"),
    ((2026, 8, 9, "%a %b", MonthNames.EGYPTIAN, "latin"), "الأحد أغسطس"),
    ((2026, 4, 1, "%d%% %B", MonthNames.MAGHREB, "latin"), "01% أفريل"),
]
