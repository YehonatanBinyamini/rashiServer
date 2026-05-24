from __future__ import annotations

from datetime import date, datetime, timedelta
import os

from sqlalchemy.dialects.postgresql import insert

from app import create_app, db
from app.models.pray_times import PrayTimes

from app.services.zmanei_tfila import get_sunrise_sunset
from app.services.zmanim_adjust import apply_offsets
from app.services.pray_calc import calc_shacharit, calc_mincha, calc_arvit
from app.utils.zman_image import create_zman_image
from app.services.email_sender import send_email_with_attachment
import os


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
    # mincha_week = calc_mincha(earliest_sunset)
    arvit_week = max(arvit_list)  # הכי מאוחר בשבוע
    mincha_week = arvit_week.replace(minute=arvit_week.minute - 40)

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
        # Generate image for the computed weekly times
        try:
            res = compute_weekly_pray_times(friday)
            shacharit = res.get("shacharit")
            mincha = res.get("mincha")
            arvit = res.get("arvit")

            output_path = os.getenv("ZMANIM_IMAGE_PATH", "zmanim_output.jpg")
            logo_path = os.getenv("ZMANIM_LOGO_PATH", "rashiLogo.PNG")

            img_file = create_zman_image(shacharit, mincha, arvit, output_path=output_path, logo_path=logo_path)
            print(f"Created image: {img_file}")

            # send email
            to_addr = os.getenv("EMAIL_TO") or os.getenv("EMAIL_USER") or "yonile2106@gmail.com"
            subject = f"זמני תפילות - שבוע של {friday.isoformat()}"
            body = f"מצורפת תמונה עם זמני התפילות לשבוע שמתחיל אחרי {friday.isoformat()}\n\nשחרית: {shacharit}\nמנחה: {mincha}\nערבית: {arvit}"

            send_email_with_attachment(subject, body, [to_addr], img_file)
            print(f"Email sent to: {to_addr}")
        except Exception as e:
            print(f"Failed to create/send image: {e}")


if __name__ == "__main__":
    main()
