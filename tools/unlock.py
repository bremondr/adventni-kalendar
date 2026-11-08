"""Which calendar days are open on a given date (stdlib only).

Shared by tools/build.py and tools/check.py. The rule, in Prague time:
  - before 1 December of the calendar year: no day is open,
  - 1 to 24 December: days 1..<day of month> are open,
  - from 25 December on, and in later years: all 24 days.
"""
from __future__ import annotations

import datetime

YEAR = 2026
LAST_DAY = 24


def prague_today() -> datetime.date:
    try:
        from zoneinfo import ZoneInfo
        tz = ZoneInfo("Europe/Prague")
    except Exception:  # no tz database (e.g. Windows without tzdata): December is CET, UTC+1
        tz = datetime.timezone(datetime.timedelta(hours=1))
    return datetime.datetime.now(tz).date()


def days_open(today: datetime.date | None = None, year: int = YEAR) -> int:
    today = today or prague_today()
    if today.year < year:
        return 0
    if today.year > year:
        return LAST_DAY
    if today.month < 12:
        return 0
    return min(today.day, LAST_DAY)


def resolve(value: str, today: datetime.date | None = None, year: int = YEAR) -> int:
    """'all' -> every day, 'auto' -> the days open today, otherwise a number."""
    if value == "all":
        return LAST_DAY
    if value == "auto":
        return days_open(today, year)
    return max(0, min(int(value), LAST_DAY))
