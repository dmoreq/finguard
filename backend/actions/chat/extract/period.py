"""Rule-based query period extraction from user text."""

from __future__ import annotations

import re

_VALID_PERIODS = frozenset({"this_month", "last_month", "last_7d", "last_30d", "last_3m", "ytd"})

_PERIOD_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("last_month", re.compile(r"last month", re.I)),
    ("this_month", re.compile(r"this month|current month", re.I)),
    ("last_7d", re.compile(r"last 7 days|past week|last week", re.I)),
    ("last_30d", re.compile(r"last 30 days|past month", re.I)),
    ("last_3m", re.compile(r"last 3 months|past quarter", re.I)),
    ("ytd", re.compile(r"year to date|ytd|this year", re.I)),
]


def parse_period_from_text(text: str, default: str = "this_month") -> str:
    for period, pattern in _PERIOD_PATTERNS:
        if pattern.search(text):
            return period
    return default if default in _VALID_PERIODS else "this_month"


def parse_category_hint(text: str) -> str | None:
    lower = text.lower()
    for cat in (
        "groceries",
        "grocery",
        "dining",
        "transport",
        "entertainment",
        "utilities",
        "shopping",
        "health",
        "bills",
        "travel",
        "salary",
        "freelance",
    ):
        if cat in lower:
            return "groceries" if cat == "grocery" else cat
    return None
