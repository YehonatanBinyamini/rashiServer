from __future__ import annotations

from datetime import date, datetime, timedelta
import os

from sqlalchemy.dialects.postgresql import insert

from app import create_app, db
from app.models.pray_times import PrayTimes

from app.services.zmanei_tfila import get_sunrise_sunset
from app.services.zmanim_adjust import apply_offsets
from app.services.pray_calc import calc_shacharit, calc_mincha, calc_arvit


def _next_sunday(after_day: date) -> date:
    # Python: Monday=0 ... Sunday=6
    wd = after_day.weekday()
    days_ahead = (6 - wd) % 7
    if days_ahead == 0:
        days_ahead = 7
    return after_day + timedelta(days=days_ahead)


def _week_days_sun_to_thu(friday: date) -> list[date]:
    start = _next_sunday(friday)        # Sunday
    return [start + timedelta(days=i) for i in range(5)]  # Sun..Thu


def _fmt_hhmm(dt: datetime) -> str:
    return dt.strftime("%H:%M")  # מומלץ לשמור עם 0 מוביל ב-DB


def compute_weekly_pray_times(friday: date, geonameid: int = 293397) -> dict:
    days = _week_days_sun_to_thu(friday)

    sunrise_list: list[datetime] = []
    sunset_list: list[datetime] = []
    arvit_list: list[datetime] = []

    for d in days:
        sunrise, sunset = get_sunrise_sunset(d, geonameid=geonameid)
        sunrise_adj, sunset_adj = apply_offsets(sunrise, sunset, d)

        sunrise_list.append(sunrise_adj)
        sunset_list.append(sunset_adj)
        arvit_list.append(calc_arvit(sunrise_adj, sunset_adj)
                          )  # כבר עם עיגול למעלה אצלך

    earliest_sunrise = min(sunrise_list)
    earliest_sunset = min(sunset_list)

    shacharit_week = calc_shacharit(earliest_sunrise)
    mincha_week = calc_mincha(earliest_sunset)
    arvit_week = max(arvit_list)  # הכי מאוחר בשבוע

    return {
        "days": days,
        "shacharit": _fmt_hhmm(shacharit_week),
        "mincha": _fmt_hhmm(mincha_week),
        "arvit": _fmt_hhmm(arvit_week),
    }


def upsert_week_into_pray_times(friday: date, geonameid: int = 293397) -> None:
    res = compute_weekly_pray_times(friday, geonameid=geonameid)

    for d in res["days"]:
        stmt = insert(PrayTimes).values(
            date_gregorian=d,
            shacharit=res["shacharit"],
            mincha=res["mincha"],
            arvit=res["arvit"],
        ).on_conflict_do_update(
            index_elements=[PrayTimes.date_gregorian],
            set_={
                "shacharit": res["shacharit"],
                "mincha": res["mincha"],
                "arvit": res["arvit"],
            },
        )
        db.session.execute(stmt)

    db.session.commit()


def main():
    # אם רוצים להריץ ידנית: export RUN_DATE=2026-01-02
    run_date_str = os.getenv("RUN_DATE")
    friday = date.fromisoformat(run_date_str) if run_date_str else date.today()

    app = create_app()
    with app.app_context():
        upsert_week_into_pray_times(friday)


if __name__ == "__main__":
    main()
