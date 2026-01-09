from __future__ import annotations
from datetime import datetime, timedelta
from typing import Literal

RoundMode = Literal["down", "up", "nearest"]


def round_to_5_minutes(dt: datetime, mode: RoundMode = "nearest") -> datetime:
    """Round datetime to a 5-minute grid."""
    if dt.tzinfo is None:
        raise ValueError("dt must be timezone-aware")

    minutes = dt.hour * 60 + dt.minute
    rem = minutes % 5

    if rem == 0:
        return dt.replace(second=0, microsecond=0)

    if mode == "down":
        minutes -= rem
    elif mode == "up":
        minutes += (5 - rem)
    else:  # nearest
        minutes += (-rem if rem < 3 else (5 - rem))

    base = dt.replace(hour=0, minute=0, second=0, microsecond=0)
    return base + timedelta(minutes=minutes)


def round_up_to_5_minutes(dt: datetime) -> datetime:
    """
    Always round UP to the next 5-minute mark.
    """
    total_minutes = dt.hour * 60 + dt.minute
    rounded = ceil(total_minutes / 5) * 5

    base = dt.replace(hour=0, minute=0, second=0, microsecond=0)
    return base + timedelta(minutes=rounded)


def choose_time_in_window(
    anchor: datetime,
    *,
    min_before_minutes: int,
    max_before_minutes: int,
    round_mode: RoundMode = "nearest",
) -> datetime:
    """
    Choose a time T such that:
      - T is in [anchor - max_before, anchor - min_before]
      - T is on a 5-minute grid (after rounding)
    Strategy: take mid-point of window and round to 5 minutes.
    Then clamp inside the window if needed.
    """
    if anchor.tzinfo is None:
        raise ValueError("anchor must be timezone-aware")

    # closest to anchor
    latest = anchor - timedelta(minutes=min_before_minutes)
    earliest = anchor - timedelta(minutes=max_before_minutes)

    midpoint = anchor - \
        timedelta(minutes=(min_before_minutes + max_before_minutes) / 2.0)
    candidate = round_to_5_minutes(midpoint, mode=round_mode)

    # Ensure candidate stays inside the window.
    if candidate < earliest:
        candidate = round_to_5_minutes(earliest, mode="up")
    if candidate > latest:
        candidate = round_to_5_minutes(latest, mode="down")

    return candidate


def calc_shacharit(sunrise_adj: datetime, round_mode: RoundMode = "nearest") -> datetime:
    # 35–39 minutes before sunrise_adj, on 5-min grid
    return choose_time_in_window(
        sunrise_adj,
        min_before_minutes=35,
        max_before_minutes=39,
        round_mode=round_mode,
    )


def calc_mincha(sunset_adj: datetime, round_mode: RoundMode = "nearest") -> datetime:
    # 21–25 minutes before sunset_adj, on 5-min grid
    return choose_time_in_window(
        sunset_adj,
        min_before_minutes=21,
        max_before_minutes=25,
        round_mode=round_mode,
    )


def calc_arvit(sunrise_adj: datetime, sunset_adj: datetime, round_mode: RoundMode = "nearest") -> datetime:
    """
    Arvit = sunset + 13.5 'minutes zmaniyot'
    minute_zmanit = ((sunset - sunrise) / 12) / 60  = (sunset - sunrise) / 720
    so 13.5 minutes zmaniyot = (sunset - sunrise) * (13.5 / 720)
    """
    day_len = sunset_adj - sunrise_adj
    offset = day_len * (13.5 / 720.0)
    raw = sunset_adj + offset
    return round_up_to_5_minutes(raw)
