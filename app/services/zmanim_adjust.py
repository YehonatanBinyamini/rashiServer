from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta


@dataclass(frozen=True)
class ZmanimOffsets:
    sunrise_min: int
    sunset_min: int


def _md(m: int, d: int) -> int:
    """Month-Day as sortable integer (MMDD)."""
    return m * 100 + d


def _in_range_md(md: int, start_md: int, end_md: int) -> bool:
    """
    Inclusive range check for MMDD.
    Supports ranges that may cross year boundary (e.g. Sep->Oct doesn't cross, but kept generic).
    """
    if start_md <= end_md:
        return start_md <= md <= end_md
    # crosses year end
    return md >= start_md or md <= end_md


def compute_offsets_for_date(day: date) -> ZmanimOffsets:
    md = _md(day.month, day.day)

    # --- Sunset rules ---
    # 16 Jan – 14 Feb OR 16 Sep – 15 Oct => no change
    if _in_range_md(md, _md(1, 16), _md(2, 14)) or _in_range_md(md, _md(9, 16), _md(10, 15)):
        sunset_offset = 0
    else:
        sunset_offset = 1  # all other dates: +1 minute

    # --- Sunrise rules ---
    # 15 Mar – 15 May OR 16 Aug – 15 Oct => +5
    if _in_range_md(md, _md(3, 15), _md(5, 15)) or _in_range_md(md, _md(8, 16), _md(10, 15)):
        sunrise_offset = 5
    # 16 May – 15 Aug => +4
    elif _in_range_md(md, _md(5, 16), _md(8, 15)):
        sunrise_offset = 4
    else:
        sunrise_offset = 6  # all other dates: +6 minutes

    return ZmanimOffsets(sunrise_min=sunrise_offset, sunset_min=sunset_offset)


def apply_offsets(sunrise: datetime, sunset: datetime, day: date) -> tuple[datetime, datetime]:
    """
    Apply the rules above to the given sunrise/sunset datetimes.
    """
    offsets = compute_offsets_for_date(day)
    return (
        sunrise + timedelta(minutes=offsets.sunrise_min),
        sunset + timedelta(minutes=offsets.sunset_min),
    )
