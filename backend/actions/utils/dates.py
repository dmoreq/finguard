"""
Date parsing utilities for financial transactions.
Converts CALM slot values (relative or absolute) to resolved pendulum DateTime.
"""

from __future__ import annotations

import pendulum
from loguru import logger
from pendulum import DateTime

# Relative date aliases CALM may extract
_RELATIVE_MAP: dict[str, int] = {
    "today": 0,
    "yesterday": -1,
    "day before yesterday": -2,
}


def parse_relative_date(raw: str | None, timezone: str = "UTC") -> DateTime:
    """
    Parse a slot value that may be:
      - None / empty  → today
      - "today"       → today
      - "yesterday"   → yesterday
      - "last Tuesday"→ most recent Tuesday
      - ISO date str  → parsed as-is

    Always returns a timezone-aware DateTime in the user's timezone.
    """
    tz = pendulum.timezone(timezone)
    now = pendulum.now(tz)

    if not raw or raw.lower() in ("today", "now", ""):
        return now

    lower = raw.lower().strip()

    # Check simple relative aliases
    if lower in _RELATIVE_MAP:
        return now.add(days=_RELATIVE_MAP[lower])

    # "last <weekday>"
    if lower.startswith("last "):
        weekday_name = lower[5:].strip()
        result = _last_weekday(weekday_name, now)
        if result:
            return result

    # Try ISO format (CALM often resolves to ISO)
    try:
        parsed = pendulum.parse(raw, tz=tz, strict=False)
        if not isinstance(parsed, DateTime):
            parsed = DateTime.instance(parsed)
        logger.debug("date_parsed", raw=raw, parsed=parsed.to_date_string())
        return parsed
    except Exception as e:
        logger.warning("date_parse_fallback_to_today", raw=raw, error=str(e))
        return now


def _last_weekday(name: str, now: DateTime) -> DateTime | None:
    """Return the most recent occurrence of a named weekday."""
    weekdays = {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6,
    }
    target = weekdays.get(name)
    if target is None:
        return None

    diff = (now.day_of_week - target) % 7 or 7
    return now.subtract(days=diff)


def period_to_date_range(period: str, timezone: str = "UTC") -> tuple[str, str]:
    """
    Convert a period alias to (start_date, end_date) ISO date strings.

    Examples:
      "this_month"  → ("2026-05-01", "2026-05-27")
      "last_month"  → ("2026-04-01", "2026-04-30")
      "last_7d"     → ("2026-05-20", "2026-05-27")
      "ytd"         → ("2026-01-01", "2026-05-27")
    """
    tz = pendulum.timezone(timezone)
    now = pendulum.now(tz)

    match period.lower():
        case "this_month":
            start = now.start_of("month")
            end = now
        case "last_month":
            start = now.subtract(months=1).start_of("month")
            end = now.subtract(months=1).end_of("month")
        case "last_7d":
            start = now.subtract(days=7)
            end = now
        case "last_30d":
            start = now.subtract(days=30)
            end = now
        case "last_3m":
            start = now.subtract(months=3)
            end = now
        case "ytd":
            start = now.start_of("year")
            end = now
        case _:
            logger.warning("unknown_period_defaulting_to_month", period=period)
            start = now.start_of("month")
            end = now

    return start.to_date_string(), end.to_date_string()
