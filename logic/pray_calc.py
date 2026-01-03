from math import ceil
from datetime import datetime, timedelta


def round_to_5_minutes(dt: datetime) -> datetime:
    minutes = dt.hour * 60 + dt.minute
    rounded = round(minutes / 5) * 5
    base = dt.replace(hour=0, minute=0, second=0, microsecond=0)
    return base + timedelta(minutes=rounded)


def round_up_to_5_minutes(dt: datetime) -> datetime:
    """
    Always round UP to the next 5-minute mark.
    """
    total_minutes = dt.hour * 60 + dt.minute
    rounded = ceil(total_minutes / 5) * 5

    base = dt.replace(hour=0, minute=0, second=0, microsecond=0)
    return base + timedelta(minutes=rounded)


def calc_shacharit(sunrise: datetime) -> datetime:
    raw = sunrise - timedelta(minutes=37)  # אמצע טווח 35–39
    return round_to_5_minutes(raw)


def calc_mincha(sunset: datetime) -> datetime:
    raw = sunset - timedelta(minutes=23)  # אמצע טווח 21–25
    return round_to_5_minutes(raw)


def calc_arvit(sunrise: datetime, sunset: datetime) -> datetime:
    day_len = sunset - sunrise
    minute_zmanit = day_len / 720
    raw = sunset + minute_zmanit * 13.5
    return round_up_to_5_minutes(raw)
