"""Golden ArDateTime, HijriDate and humanize tables. Maintainer-reviewed: never edit to pass."""

from datetime import timedelta

# (year, month, day, hour, minute, second, format, digits) → expected
DATETIME_FORMATS = [
    ((2026, 1, 5, 0, 5, 0, "%I:%M %p", "latin"), "12:05 صباحًا"),
    ((2026, 1, 5, 9, 30, 0, "%I:%M %p", "arabic"), "٠٩:٣٠ صباحًا"),
    ((2026, 1, 5, 12, 0, 0, "%I:%M %p", "latin"), "12:00 مساءً"),
    ((2026, 1, 5, 14, 30, 15, "%H:%M:%S", "arabic"), "١٤:٣٠:١٥"),
    ((2026, 1, 5, 23, 59, 0, "%I:%M %p", "persian"), "۱۱:۵۹ مساءً"),
    (
        (2026, 1, 5, 14, 30, 0, "%A %O من %B %Y، الساعة %I:%M %p", "arabic"),
        "الاثنين الخامس من كانون الثاني ٢٠٢٦، الساعة ٠٢:٣٠ مساءً",
    ),
]

# Gregorian (year, month, day) → Hijri (year, month, day), Umm al-Qura.
HIJRI_CONVERSIONS = [
    ((2025, 6, 26), (1447, 1, 1)),
    ((2026, 1, 5), (1447, 7, 16)),
    ((2026, 2, 18), (1447, 9, 1)),
    ((2026, 3, 20), (1447, 10, 1)),
]

# (year, month, day, format, digits) → expected
HIJRI_FORMATS = [
    ((1447, 9, 1, "%O من %B %Y هـ", "arabic"), "الأول من رمضان ١٤٤٧ هـ"),
    ((1447, 12, 10, "%A %d %B %Y", "latin"), "الأربعاء 10 ذو الحجة 1447"),
    ((1447, 4, 15, "%d %B %Y", "latin"), "15 ربيع الآخر 1447"),
    ((1447, 6, 1, "%d/%m/%Y هـ", "arabic"), "٠١/٠٦/١٤٤٧ هـ"),
]

# time before `now` → ar_since text. The same delta after `now` uses «بعد» instead of «منذ».
SINCE = [
    (timedelta(0), "الآن"),
    (timedelta(seconds=1), "منذ ثانية"),
    (timedelta(seconds=2), "منذ ثانيتين"),
    (timedelta(seconds=3), "منذ ثلاث ثوانٍ"),
    (timedelta(seconds=11), "منذ إحدى عشرة ثانيةً"),
    (timedelta(minutes=1), "منذ دقيقة"),
    (timedelta(minutes=2, seconds=30), "منذ دقيقتين"),
    (timedelta(minutes=25), "منذ خمس وعشرين دقيقةً"),
    (timedelta(hours=1), "منذ ساعة"),
    (timedelta(hours=5), "منذ خمس ساعات"),
    (timedelta(days=1), "منذ يوم"),
    (timedelta(days=2), "منذ يومين"),
    (timedelta(days=3), "منذ ثلاثة أيام"),
    (timedelta(days=7), "منذ أسبوع"),
    (timedelta(days=14), "منذ أسبوعين"),
    (timedelta(days=21), "منذ ثلاثة أسابيع"),
    (timedelta(days=31), "منذ شهر"),
    (timedelta(days=62), "منذ شهرين"),
    (timedelta(days=95), "منذ ثلاثة أشهر"),
    (timedelta(days=366), "منذ سنة"),
    (timedelta(days=731), "منذ سنتين"),
    (timedelta(days=1830), "منذ خمس سنوات"),
    (timedelta(days=4100), "منذ إحدى عشرة سنةً"),
]

# timedelta → ar_duration text
DURATIONS = [
    (timedelta(0), "صفر ثانية"),
    (timedelta(seconds=45), "خمس وأربعون ثانيةً"),
    (timedelta(hours=1, minutes=30), "ساعة وثلاثون دقيقةً"),
    (timedelta(hours=2), "ساعتان"),
    (timedelta(days=1), "يوم"),
    (timedelta(days=9), "أسبوع ويومان"),
    (timedelta(days=16, hours=3), "أسبوعان ويومان وثلاث ساعات"),
    (timedelta(days=70), "عشرة أسابيع"),
    (timedelta(days=77), "أحد عشر أسبوعًا"),
]

# (years, months, days, hours, minutes, seconds) → ar_duration text
CALENDAR_DURATIONS = [
    ((1, 3, 0, 0, 0, 0), "سنة وثلاثة أشهر"),
    ((2, 0, 0, 0, 0, 0), "سنتان"),
    ((3, 1, 10, 0, 0, 0), "ثلاث سنوات وشهر وأسبوع وثلاثة أيام"),
    ((0, 11, 0, 0, 0, 0), "أحد عشر شهرًا"),
    ((0, 0, 0, 0, 0, 0), "صفر ثانية"),
]
