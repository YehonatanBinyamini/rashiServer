from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import List

from app.services.zmanei_tfila import get_sunrise_sunset
from app.services.zmanim_adjust import apply_offsets
from app.services.pray_calc import calc_shacharit, calc_arvit


def _next_sunday(after_day: date) -> date:
    wd = after_day.weekday()
    days_ahead = (6 - wd) % 7
    if days_ahead == 0:
        days_ahead = 7
    return after_day + timedelta(days=days_ahead)


def _week_days_sun_to_thu(friday: date) -> List[date]:
    start = _next_sunday(friday)
    return [start + timedelta(days=i) for i in range(5)]


def _fmt_hhmm(dt: datetime) -> str:
    return dt.strftime("%H:%M")


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
        arvit_list.append(calc_arvit(sunrise_adj, sunset_adj))

    earliest_sunrise = min(sunrise_list)
    earliest_sunset = min(sunset_list)

    shacharit_week = calc_shacharit(earliest_sunrise)
    arvit_week = max(arvit_list)
    mincha_week = mincha_week = arvit_week - timedelta(minutes=40)

    return {
        "days": days,
        "shacharit": _fmt_hhmm(shacharit_week),
        "mincha": _fmt_hhmm(mincha_week),
        "arvit": _fmt_hhmm(arvit_week),
    }
