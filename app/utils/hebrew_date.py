from datetime import date, datetime
from convertdate import hebrew


HEB_MONTHS = {
    1: "ניסן",
    2: "אייר",
    3: "סיון",
    4: "תמוז",
    5: "אב",
    6: "אלול",
    7: "תשרי",
    8: "חשון",
    9: "כסלו",
    10: "טבת",
    11: "שבט",
    12: "אדר",
    13: "אדר ב׳",
}


HEB_NUM = {
    1: "א", 2: "ב", 3: "ג", 4: "ד", 5: "ה", 6: "ו", 7: "ז", 8: "ח", 9: "ט",
    10: "י", 11: "יא", 12: "יב", 13: "יג", 14: "יד", 15: "טו", 16: "טז",
    17: "יז", 18: "יח", 19: "יט", 20: "כ", 21: "כא", 22: "כב", 23: "כג",
    24: "כד", 25: "כה", 26: "כו", 27: "כז", 28: "כח", 29: "כט", 30: "ל",
}


HEB_YEARS = {
    # common recent years; fallback to numeric year string if missing
    5785: 'תשפ"ה',
    5786: 'תשפ"ו',
    5787: 'תשפ"ז',
    5788: 'תשפ"ח',
    5789: 'תשפ"ט',
    5790: 'תש"ץ',
}


def hebrew_day_to_hebrew_letters(d: int) -> str:
    return HEB_NUM.get(d, str(d))


def to_hebrew_date_str(dt: datetime | date | None) -> str | None:
    """
    Convert a `date` or `datetime` to a short Hebrew date string like "כב תמוז תשפ"ה".
    Returns None when `dt` is falsy.
    """
    if not dt:
        return None

    if isinstance(dt, datetime):
        g = dt.date()
    else:
        g = dt

    hy, hm, hd = hebrew.from_gregorian(g.year, g.month, g.day)

    month_name = HEB_MONTHS.get(hm, str(hm))
    year_str = HEB_YEARS.get(hy, str(hy))
    day_str = hebrew_day_to_hebrew_letters(hd)

    return f"{day_str} {month_name} {year_str}"
