from __future__ import annotations
from app.services.pray_calc import calc_shacharit, calc_mincha, calc_arvit
from app.services.zmanim_adjust import apply_offsets
from datetime import date, datetime, timedelta
import requests


HEBCAL_ZMANIM_URL = "https://www.hebcal.com/zmanim"


def get_sunrise_sunset(
    on_date: date,
    *,
    geonameid: int = 293397,
    timeout: int = 10,
) -> tuple[datetime, datetime]:
    """
    Returns (sunrise_dt, sunset_dt) as timezone-aware datetimes (Hebcal returns +02:00/+03:00).
    """
    r = requests.get(
        HEBCAL_ZMANIM_URL,
        params={"cfg": "json", "geonameid": geonameid,
                "lg": "h", "date": on_date.isoformat()},
        timeout=timeout,
    )
    r.raise_for_status()
    data = r.json()

    times = data["times"]
    sunrise = datetime.fromisoformat(times["sunrise"])
    sunset = datetime.fromisoformat(times["sunset"])
    return sunrise, sunset


def shift_minutes(dt: datetime, minutes: int) -> datetime:
    """
    minutes: + forward, - backward
    """
    return dt + timedelta(minutes=minutes)


# d = date(2026, 1, 4)

# sunrise, sunset = get_sunrise_sunset(d)

# sunrise_adj, sunset_adj = apply_offsets(sunrise, sunset, d)

# print("sunrise:", sunrise_adj.strftime("%H:%M"))
# print("sunset:", sunset_adj.strftime("%H:%M"))
# sunrise = shift_minutes(sunrise, +2)   # זריחה +2 דקות
# sunset = shift_minutes(sunset,  -3)   # שקיעה -3 דקות


# shacharit = calc_shacharit(sunrise_adj, round_mode="nearest")
# mincha = calc_mincha(sunset_adj, round_mode="nearest")
# arvit = calc_arvit(sunrise_adj, sunset_adj, round_mode="nearest")

# print(shacharit.strftime("%-H:%M"))
# print(mincha.strftime("%-H:%M"))
# print(arvit.strftime("%-H:%M"))
