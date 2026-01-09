from datetime import date, timedelta
from zoneinfo import ZoneInfo

from flask import Blueprint, jsonify
from sqlalchemy import func

from app import db
from app.models.pray_times import PrayTimes  # עדכן נתיב אם שונה

bp = Blueprint("pray_times_api", __name__, url_prefix="/api/pray-times")


def _week_range_sun_to_thu(today_il: date) -> tuple[date, date]:
    """
    מחזיר טווח א'-ה' "פעיל":
    - אם היום א'-ה' -> אותו שבוע (א'-ה')
    - אם היום ו'/ש' -> השבוע הבא (א'-ה' הבא)
    """
    iso = today_il.isoweekday()  # Mon=1 ... Sun=7

    if iso in (5, 6):  # Fri=5, Sat=6 => next Sunday
        days_until_sun = (7 - iso) % 7  # Fri->2, Sat->1
        start = today_il + timedelta(days=days_until_sun)
    else:
        # Sun=7 -> 0 ימים אחורה; Mon=1 -> 1 יום אחורה; ... Thu=4 -> 4 ימים אחורה
        days_since_sun = 0 if iso == 7 else iso
        start = today_il - timedelta(days=days_since_sun)

    end = start + timedelta(days=4)  # Thu
    return start, end


@bp.get("/week")
def get_week_pray_times():
    today_il = date.today()  # אם השרת מכוון Asia/Jerusalem זה מספיק
    # אם אתה רוצה להיות חסין גם כשהשרת לא מכוון:
    # today_il = datetime.now(ZoneInfo("Asia/Jerusalem")).date()

    start, end = _week_range_sun_to_thu(today_il)

    row = (
        db.session.query(
            func.max(PrayTimes.arvit).label("arvit_time"),
            func.min(PrayTimes.mincha).label("mincha_time"),
            func.min(PrayTimes.shacharit).label("shacharit_time"),
        )
        .filter(PrayTimes.date_gregorian.between(start, end))
        .one()
    )

    return jsonify({
        "range": {"start": start.isoformat(), "end": end.isoformat()},
        "shacharit": row.shacharit_time,
        "mincha": row.mincha_time,
        "arvit": row.arvit_time,
    })
